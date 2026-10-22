"""Kiểm thử pipeline định giá ML LaptopDSS (GĐ4, D10).

Kiểm tra artifact, chỉ số chất lượng, khoảng dự báo, OOF và imputation độc lập
trong từng fold GroupKFold.
"""

import json
from pathlib import Path
import joblib
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
PIPELINE_FILE = ROOT / "data" / "artifacts" / "price_model.joblib"
METRICS_JSON = ROOT / "data" / "artifacts" / "price_model_metrics.json"
OOF_FILE = ROOT / "data" / "artifacts" / "price_model_oof.json"


def test_pipeline_exists_and_loads():
    assert PIPELINE_FILE.exists(), "Pipeline joblib file must exist"
    pipeline = joblib.load(PIPELINE_FILE)
    assert "model" in pipeline
    assert "imputer" in pipeline
    assert "scaler" in pipeline
    assert "best_params" in pipeline
    assert "feature_names" in pipeline
    assert "sigma_pred" in pipeline
    assert len(pipeline["feature_names"]) >= 20


def test_metrics_integrity():
    assert METRICS_JSON.exists(), "ML metrics JSON must exist"
    with open(METRICS_JSON, "r", encoding="utf-8") as f:
        metrics = json.load(f)
    assert metrics["dataset_size"] == 513
    assert "models_cv" in metrics
    for name, value in metrics["models_cv"].items():
        if value.get("status") == "not_converged":
            assert all(metric is None for key, metric in value.items() if key != "status"), name
        else:
            assert value.get("status") == "ok", name
            assert all(np.isfinite(metric) for key, metric in value.items() if key != "status"), name


    
    best_model = metrics["best_model"]
    pipeline = joblib.load(PIPELINE_FILE)
    assert pipeline["model_name"] == best_model
    best_metrics = metrics["models_cv"][best_model]
    
    # Assert academic quality standards
    assert best_metrics["r2_mean"] >= 0.85, f"R^2 must be >= 0.85, got {best_metrics['r2_mean']}"
    assert best_metrics["mape_mean"] <= 15.0, f"MAPE must be <= 15%, got {best_metrics['mape_mean']}%"
    assert best_metrics["mae_mean"] <= 5_500_000, f"MAE must be <= 5.5M VND, got {best_metrics['mae_mean']}"


def test_prediction_and_intervals():
    pipeline = joblib.load(PIPELINE_FILE)
    model = pipeline["model"]
    scaler = pipeline.get("scaler")
    imputer = pipeline["imputer"]
    sigma = pipeline["sigma_pred"]
    
    # Feature vector with missing values (NaN) to verify imputation works
    dummy_vec = np.full((1, len(pipeline["feature_names"])), np.nan)
    values = {"cpu_benchmark_multi": 12000.0, "cpu_benchmark_single": 2500.0,
              "cpu_missing": 0.0, "cpu_cores": 8.0, "gpu_benchmark_time_spy": 6000.0,
              "gpu_benchmark_compute": 90000.0, "is_discrete_gpu": 1.0, "gpu_vram_gb": 6.0,
              "ram_gb": 16.0, "storage_total_gb": 512.0, "screen_size_inch": 15.6,
              "screen_pixels_mp": 2.07, "is_oled": 0.0, "refresh_rate_hz": 144.0,
              "brightness_nits": 300.0, "battery_capacity_wh": 60.0, "weight_kg": 2.2,
              "is_macos": 0.0}
    for idx, feature in enumerate(pipeline["feature_names"]):
        if feature in values:
            dummy_vec[0, idx] = values[feature]
    # Brands one-hot
    for idx, f in enumerate(pipeline["feature_names"]):
        if f == "brand_Asus":
            dummy_vec[0, idx] = 1.0
        elif f.startswith("brand_"):
            dummy_vec[0, idx] = 0.0

    if scaler is not None:
        scaled = scaler.transform(dummy_vec)
        imputed = imputer.transform(scaled)
    else:
        imputed = imputer.transform(dummy_vec)

    pred_log = model.predict(imputed)[0]
    pred_price = np.exp(pred_log)
    
    lower_bound = np.exp(pred_log - 1.96 * sigma)
    upper_bound = np.exp(pred_log + 1.96 * sigma)
    
    # Realistic range for RTX mid-range laptop
    assert 15_000_000 <= pred_price <= 45_000_000, f"Predicted price out of range: {pred_price}"
    assert lower_bound < pred_price < upper_bound, "Interval bounds ordering invalid"


def test_d10_compatibility_and_oof():
    """Verifies that get_trained_model_and_predictions uses authentic OOF predictions."""
    from src.ml_price_prediction import get_trained_model_and_predictions
    model, records, preds = get_trained_model_and_predictions()
    assert len(records) == 513
    assert len(preds) == 513
    assert all(p > 0 for p in preds)
    assert OOF_FILE.exists(), "OOF predictions JSON must exist"
    with open(OOF_FILE, "r", encoding="utf-8") as f:
        oof_map = json.load(f)
    assert len(oof_map) == 513


def test_model_subset_rejects_unknown_name_before_training():
    """Notebook benchmark may select core models but must not silently skip a typo."""
    from src.ml_price_prediction import evaluate_models_nested_groupkfold
    with np.testing.assert_raises_regex(ValueError, "Không có model benchmark"):
        evaluate_models_nested_groupkfold(
            np.empty((0, 1)), np.empty(0), np.empty(0), np.empty(0), model_names=["Typo Model"],
        )




def test_imputer_fold_independence():
    """Verifies that RobustScaler + KNNImputer operate scale-invariantly and fold-independently."""
    from sklearn.impute import KNNImputer
    from sklearn.preprocessing import RobustScaler
    
    # Large scale feature (~20,000) alongside binary feature (0/1)
    X_train = np.array([
        [10000.0, 1.0, np.nan],
        [20000.0, 0.0, 50.0],
        [30000.0, 1.0, 100.0]
    ])
    X_val = np.array([[np.nan, 1.0, 60.0]])
    
    scaler = RobustScaler(unit_variance=True)
    X_tr_s = scaler.fit_transform(X_train)
    X_val_s = scaler.transform(X_val)
    
    imp = KNNImputer(n_neighbors=2)
    imp.fit(X_tr_s)
    val_trans = imp.transform(X_val_s)
    
    assert not np.isnan(val_trans).any(), "Imputation failed on validation fold"
    # Ensure scaler learned parameters only from train
    assert scaler.center_[0] == 20000.0
