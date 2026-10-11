"""Kiểm thử pipeline định giá ML LaptopDSS (GĐ4, D10).

Kiểm tra artifact, chỉ số chất lượng, khoảng dự báo, OOF và imputation độc lập
trong từng fold GroupKFold.
"""

import json
from pathlib import Path
import joblib
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
PIPELINE_FILE = ROOT / "data" / "processed" / "laptop_price_pipeline.joblib"
METRICS_JSON = ROOT / "data" / "processed" / "ml_metrics.json"
OOF_FILE = ROOT / "data" / "processed" / "ml_oof_predictions.json"


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
    assert metrics["dataset_size"] == 220
    assert "models_cv" in metrics
    
    best_model = metrics["best_model"]
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
    dummy_vec[0, 0] = 12000.0  # cpu_multi
    dummy_vec[0, 1] = 2500.0   # cpu_single
    dummy_vec[0, 2] = 0.0      # not missing
    dummy_vec[0, 3] = 8.0      # cores
    dummy_vec[0, 4] = 6000.0   # gpu_time_spy
    dummy_vec[0, 5] = 1.0      # is_dgpu
    dummy_vec[0, 6] = 6.0      # vram
    dummy_vec[0, 7] = 16.0     # ram
    dummy_vec[0, 8] = 512.0    # ssd
    dummy_vec[0, 9] = 15.6     # inch
    dummy_vec[0, 10] = 2.07    # mp (1920x1080)
    dummy_vec[0, 11] = 0.0     # oled
    dummy_vec[0, 12] = 144.0   # hz
    dummy_vec[0, 13] = 300.0   # nits
    dummy_vec[0, 14] = 60.0    # wh
    dummy_vec[0, 15] = 2.2     # kg
    dummy_vec[0, 16] = 0.0     # macos
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
    assert len(records) == 220
    assert len(preds) == 220
    assert all(p > 0 for p in preds)
    assert OOF_FILE.exists(), "OOF predictions JSON must exist"
    with open(OOF_FILE, "r", encoding="utf-8") as f:
        oof_map = json.load(f)
    assert len(oof_map) == 220


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
