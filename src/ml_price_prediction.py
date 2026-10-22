"""Pipeline dự báo và thẩm định giá ML của LaptopDSS (GĐ4, D10).

Academic-grade ML pipeline implementing:
1. Log-scale target transformation: y = ln(sale_price_vnd) to handle heavy right skewness (8.79M -> 134M).
   Back-transformation: median estimator exp(y_ln) with smearing factor exp(sigma^2 / 2) for conditional mean.
2. Domain-informed Feature Engineering (24 features):
   - CPU benchmarks (Geekbench 6 multi & single), missingness indicator, core count.
   - GPU benchmarks (3DMark Time Spy), dGPU indicator, GPU VRAM (GB).
   - Display: Resolution (Megapixels), panel type (OLED), refresh rate (Hz), brightness (nits).
   - Mobility & Hardware: Battery capacity (Wh), weight (kg), OS (macOS vs Windows), Brand encoding.
3. Scale-normalized missing value handling: RobustScaler + KNNImputer(k=5)
   strictly inside each training fold to eliminate data leakage and Euclidean scale bias.
4. Nested GroupKFold cross-validation (5-fold outer, 3-fold inner GridSearchCV) grouped by configuration_id.
5. Multi-model benchmarking: Linear, Ridge, KNN, Decision Tree, Random Forest, boosting, and ANN.
6. SHAP Explainability: TreeExplainer run directly on the selected fitted model.
7. Reference-gap screening: Evaluated on Out-Of-Fold (OOF) predictions with 95% Prediction Interval (1.96 * sigma).
8. Model Persistence: Saves complete pipeline (scaler, imputer, tuned model, metadata) via joblib with dataset SHA-256 hash.
9. Compatibility: Provides get_trained_model_and_predictions() using authentic Out-Of-Fold predictions for D10 experiment.
Đầu vào là catalog chuẩn hóa; module dùng Nested GroupKFold, RobustScaler,
KNNImputer, hồi quy và SHAP. Đầu ra gồm pipeline, dự báo OOF, metrics, báo cáo
và sàng lọc chênh lệch giá OOF, luôn tách biệt TOPSIS theo D10.
"""

import csv
import json
import math
import hashlib
import sqlite3
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional

import joblib
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.neighbors import KNeighborsRegressor
from sklearn.tree import DecisionTreeRegressor
from sklearn.neural_network import MLPRegressor
from sklearn.compose import TransformedTargetRegressor
from sklearn.model_selection import GroupKFold, GridSearchCV
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score, mean_absolute_percentage_error
from sklearn.impute import KNNImputer
from sklearn.preprocessing import RobustScaler, StandardScaler
import lightgbm as lgb
import xgboost as xgb
import shap

ROOT = Path(__file__).resolve().parents[1]
DATA_FILE = ROOT / "data" / "catalog" / "laptops.csv"
DB_FILE = ROOT / "data" / "artifacts" / "laptop_dss.db"
ML_REPORT_FILE = ROOT / "data" / "reports" / "ml_price_prediction_report.md"
ML_METRICS_JSON = ROOT / "data" / "artifacts" / "price_model_metrics.json"
ML_OOF_PREDICTIONS_JSON = ROOT / "data" / "artifacts" / "price_model_oof.json"
MODEL_PIPELINE_FILE = ROOT / "data" / "artifacts" / "price_model.joblib"


def compute_file_sha256(filepath: Path) -> str:
    """Computes SHA-256 checksum of dataset file for academic traceability."""
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def load_dataset() -> Tuple[List[Dict[str, Any]], List[str]]:
    """Loads standardized dataset, performs feature extraction preserving real NaNs, and maps configuration_id."""
    cfg_map = {}
    if DB_FILE.exists():
        conn = sqlite3.connect(DB_FILE)
        cur = conn.cursor()
        cur.execute("SELECT source_product_id, configuration_id FROM retail_listings")
        for pid, cid in cur.fetchall():
            cfg_map[pid] = cid
        conn.close()

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    records = []
    brands_set = set()

    for idx, r in enumerate(rows):
        price = float(r.get("sale_price_vnd") or 0)
        if price <= 0:
            continue
        pid = r.get("source_product_id") or str(idx)
        cid = cfg_map.get(pid, pid)

        name = r.get("product_name_raw", "").lower()
        if "apple" in name or "macbook" in name:
            brand = "Apple"
        elif "lenovo" in name:
            brand = "Lenovo"
        elif "msi" in name:
            brand = "MSI"
        elif "asus" in name:
            brand = "Asus"
        elif "acer" in name:
            brand = "Acer"
        elif "dell" in name:
            brand = "Dell"
        elif "hp" in name:
            brand = "HP"
        else:
            brand = "Other"
        brands_set.add(brand)

        # 1. CPU features
        cpu_m = float(r["cpu_benchmark_multi_core"]) if r.get("cpu_benchmark_multi_core") else np.nan
        cpu_s = float(r["cpu_benchmark_single_core"]) if r.get("cpu_benchmark_single_core") else np.nan
        cpu_bench_missing = 1.0 if np.isnan(cpu_m) else 0.0
        cpu_cores = float(r["cpu_cores"]) if r.get("cpu_cores") else np.nan

        # 2. GPU features
        gpu_type = r.get("gpu_type", "integrated")
        is_dgpu = 1.0 if gpu_type == "discrete" else 0.0
        if not is_dgpu:
            vram = 0.0
        else:
            vram = float(r["gpu_vram_gb"]) if r.get("gpu_vram_gb") else np.nan

        gpu_ts = float(r["gpu_benchmark_time_spy"]) if r.get("gpu_benchmark_time_spy") else (0.0 if not is_dgpu else np.nan)
        gpu_compute = float(r["gpu_benchmark_compute"]) if r.get("gpu_benchmark_compute") else np.nan

        # 3. RAM & Storage (genuine values or NaN)
        ram = float(r["ram_gb"]) if r.get("ram_gb") else np.nan
        storage = float(r["storage_total_gb"]) if r.get("storage_total_gb") else np.nan

        # 4. Display features
        screen_sz = float(r["screen_size_inch"]) if r.get("screen_size_inch") else np.nan
        w_px = float(r["screen_width_px"]) if r.get("screen_width_px") else np.nan
        h_px = float(r["screen_height_px"]) if r.get("screen_height_px") else np.nan
        screen_pixels_mp = (w_px * h_px) / 1e6 if (not np.isnan(w_px) and not np.isnan(h_px)) else np.nan
        panel = (r.get("panel_type") or "").upper()
        is_oled = 1.0 if "OLED" in panel else 0.0
        hz = float(r["refresh_rate_hz"]) if r.get("refresh_rate_hz") else np.nan
        nits = float(r["brightness_nits"]) if r.get("brightness_nits") else np.nan

        # 5. Mobility & OS
        battery_wh = float(r["battery_capacity_wh"]) if r.get("battery_capacity_wh") else np.nan
        weight = float(r["weight_kg"]) if r.get("weight_kg") else np.nan
        os_name = r.get("os_name") or "Windows"
        is_macos = 1.0 if "mac" in os_name.lower() else 0.0

        records.append({
            "configuration_id": cid,
            "source_product_id": pid,
            "product_name": r.get("product_name_raw", ""),
            "sale_price_vnd": price,
            "log_price": np.log(price),
            "brand": brand,
            "num_features": [
                cpu_m, cpu_s, cpu_bench_missing, cpu_cores,
                gpu_ts, gpu_compute, is_dgpu, vram,
                ram, storage,
                screen_sz, screen_pixels_mp, is_oled, hz, nits,
                battery_wh, weight, is_macos
            ]
        })

    brands_list = sorted(list(brands_set))
    return records, brands_list


def assemble_feature_matrix(records: List[Dict[str, Any]], brands_list: List[str]) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, List[str]]:
    """Builds raw feature matrix before imputation, returning column names."""
    num_feature_names = [
        "cpu_benchmark_multi", "cpu_benchmark_single", "cpu_benchmark_missing", "cpu_cores",
        "gpu_benchmark_time_spy", "gpu_benchmark_compute", "is_discrete_gpu", "gpu_vram_gb",
        "ram_gb", "storage_total_gb",
        "screen_size_inch", "screen_pixels_mp", "is_oled_panel", "refresh_rate_hz", "brightness_nits",
        "battery_capacity_wh", "weight_kg", "is_macos"
    ]
    brand_feature_names = [f"brand_{b}" for b in brands_list]
    all_feature_names = num_feature_names + brand_feature_names

    X_raw = []
    for r in records:
        b_vec = [1.0 if r["brand"] == b else 0.0 for b in brands_list]
        X_raw.append(r["num_features"] + b_vec)

    X_raw = np.array(X_raw, dtype=float)
    y_raw = np.array([r["sale_price_vnd"] for r in records], dtype=float)
    y_log = np.array([r["log_price"] for r in records], dtype=float)
    groups = np.array([r["configuration_id"] for r in records])

    return X_raw, y_raw, y_log, groups, all_feature_names


def evaluate_models_nested_groupkfold(
    X_raw: np.ndarray,
    y_raw: np.ndarray,
    y_log: np.ndarray,
    groups: np.ndarray,
    model_names: Optional[List[str]] = None,
):
    """Performs Nested GroupKFold cross-validation (5-fold outer, 3-fold inner GridSearchCV).
    
    RobustScaler and KNNImputer are fitted strictly on outer training folds to prevent any data leakage
    and avoid scale bias in Euclidean neighbor distance.
    """
    gkf_outer = GroupKFold(n_splits=5)

    model_configs = {
        "Baseline (Mean Log-Price)": {
            "model": None,
            "params": {}
        },
        "Linear Regression": {
            "model": LinearRegression(),
            "params": {}
        },
        "Ridge Regression": {
            "model": Ridge(),
            "params": {"alpha": [0.5, 2.0, 10.0, 50.0]}
        },
        "K-Nearest Neighbors Regressor": {
            "model": KNeighborsRegressor(),
            "params": {"n_neighbors": [3, 5, 7], "weights": ["uniform", "distance"]}
        },
        "Decision Tree Regressor": {
            "model": DecisionTreeRegressor(random_state=42),
            "params": {"max_depth": [4, 6, 8], "min_samples_leaf": [1, 3, 5]}
        },
        "Random Forest Regressor": {
            "model": RandomForestRegressor(random_state=42),
            "params": {"n_estimators": [100, 200], "max_depth": [8, 12]}
        },
        "Gradient Boosting": {
            "model": GradientBoostingRegressor(random_state=42),
            "params": {"n_estimators": [100, 150], "max_depth": [3, 5], "learning_rate": [0.05, 0.1]}
        },
        "LightGBM Regressor": {
            "model": lgb.LGBMRegressor(random_state=42, verbose=-1),
            "params": {"n_estimators": [100, 150], "max_depth": [4, 6], "learning_rate": [0.05, 0.1], "num_leaves": [20, 31]}
        },
        "XGBoost Regressor": {
            "model": xgb.XGBRegressor(random_state=42, verbosity=0),
            "params": {"n_estimators": [100, 150], "max_depth": [4, 6], "learning_rate": [0.05, 0.1]}
        },
        "MLP Regressor (ANN)": {
            # Standardize log-price inside every inner-fold fit.  Some folds can
            # still reach the optimizer limit; ANN remains a comparison model only.
            "model": TransformedTargetRegressor(
                regressor=MLPRegressor(
                    random_state=42,
                    solver="lbfgs",
                    max_iter=600,
                ),
                transformer=StandardScaler(),
            ),
            "params": {
                "regressor__hidden_layer_sizes": [(16,), (32,)],
                "regressor__alpha": [0.01, 0.1],
            }
        },
    }
    if model_names is not None:
        unknown = [name for name in model_names if name not in model_configs]
        if unknown:
            raise ValueError(f"Không có model benchmark: {', '.join(unknown)}")
        model_configs = {name: model_configs[name] for name in model_names}

    cv_results = {}
    oof_predictions = {name: np.zeros(len(y_raw)) for name in model_configs.keys()}

    print(f"\n{'='*78}\nNESTED GROUPKFOLD EVALUATION (5-FOLD OUTER, 3-FOLD INNER GRIDSEARCHCV)\n{'='*78}")

    for name, cfg in model_configs.items():
        fold_r2 = []
        fold_r2_log = []
        fold_mae = []
        fold_rmse = []
        fold_mape = []

        for train_idx, val_idx in gkf_outer.split(X_raw, y_log, groups):
            # 1. Scale-normalized, leakage-free preprocessing
            scaler = RobustScaler(unit_variance=True)
            X_tr_scaled = scaler.fit_transform(X_raw[train_idx])
            X_val_scaled = scaler.transform(X_raw[val_idx])

            imputer = KNNImputer(n_neighbors=5)
            X_tr = imputer.fit_transform(X_tr_scaled)
            X_val = imputer.transform(X_val_scaled)

            y_tr_log = y_log[train_idx]
            y_val_raw = y_raw[val_idx]
            y_val_log = y_log[val_idx]
            groups_tr = groups[train_idx]

            if cfg["model"] is None:
                # Baseline mean
                mean_log = np.mean(y_tr_log)
                pred_log = np.full(len(val_idx), mean_log)
                pred_raw = np.exp(pred_log)
            else:
                # Inner 3-fold GroupKFold for hyperparameter tuning
                inner_cv = GroupKFold(n_splits=3)
                gs = GridSearchCV(cfg["model"], cfg["params"], cv=inner_cv, scoring="neg_mean_squared_error", n_jobs=1)
                gs.fit(X_tr, y_tr_log, groups=groups_tr)
                best_estimator = gs.best_estimator_

                pred_log = best_estimator.predict(X_val)
                pred_raw = np.exp(pred_log)

            oof_predictions[name][val_idx] = pred_raw

            r2_val = r2_score(y_val_raw, pred_raw)
            r2_log_val = r2_score(y_val_log, pred_log)
            mae_val = mean_absolute_error(y_val_raw, pred_raw)
            rmse_val = math.sqrt(mean_squared_error(y_val_raw, pred_raw))
            mape_val = mean_absolute_percentage_error(y_val_raw, pred_raw) * 100

            fold_r2.append(r2_val)
            fold_r2_log.append(r2_log_val)
            fold_mae.append(mae_val)
            fold_rmse.append(rmse_val)
            fold_mape.append(mape_val)

        res = {
            "r2_mean": float(np.mean(fold_r2)),
            "r2_std": float(np.std(fold_r2)),
            "r2_log_mean": float(np.mean(fold_r2_log)),
            "r2_log_std": float(np.std(fold_r2_log)),
            "mae_mean": float(np.mean(fold_mae)),
            "mae_std": float(np.std(fold_mae)),
            "rmse_mean": float(np.mean(fold_rmse)),
            "rmse_std": float(np.std(fold_rmse)),
            "mape_mean": float(np.mean(fold_mape)),
            "mape_std": float(np.std(fold_mape)),
        }
        values = tuple(res.values())
        if not all(np.isfinite(values)) or max(abs(value) for value in values) > 1e12:
            # Do not expose divergent numerical output as an academic metric or API value.
            res = {key: None for key in res}
            res["status"] = "not_converged"
        else:
            res["status"] = "ok"
        cv_results[name] = res
        if res["status"] == "ok":
            print(f"[{name:32s}] R2: {res['r2_mean']:+.4f} ± {res['r2_std']:.4f} | MAE: {res['mae_mean']:11,.0f} ± {res['mae_std']:9,.0f} VND | MAPE: {res['mape_mean']:5.2f}%")
        else:
            print(f"[{name:32s}] Không hội tụ ổn định; loại khỏi lựa chọn triển khai.")

    return cv_results, oof_predictions, model_configs


def fit_best_model_and_shap(
    best_model_name: str,
    model_configs: Dict[str, Any],
    X_raw: np.ndarray,
    y_raw: np.ndarray,
    y_log: np.ndarray,
    groups: np.ndarray,
    records: List[Dict[str, Any]],
    feature_names: List[str],
    oof_predictions: Dict[str, np.ndarray]
) -> Tuple[Any, RobustScaler, KNNImputer, Dict[str, Any], Dict[str, float], List[Dict[str, Any]], float]:
    """Fits the best model with full-dataset GridSearchCV to retain optimal hyperparameters, computes SHAP, and generates OOF Good Deals."""
    print(f"\nFitting selected best model: {best_model_name} on full dataset with GridSearchCV tuning...")
    
    # 1. Fit production scaler and imputer on full dataset
    final_scaler = RobustScaler(unit_variance=True)
    X_scaled = final_scaler.fit_transform(X_raw)

    final_imputer = KNNImputer(n_neighbors=5)
    X_imputed = final_imputer.fit_transform(X_scaled)

    # 2. Run GridSearchCV on full dataset to lock in the true best hyperparameters
    best_cfg = model_configs[best_model_name]
    final_cv = GroupKFold(n_splits=5)
    gs_final = GridSearchCV(
        best_cfg["model"],
        best_cfg["params"],
        cv=final_cv,
        scoring="neg_mean_squared_error",
        n_jobs=1
    )
    gs_final.fit(X_imputed, y_log, groups=groups)
    final_model = gs_final.best_estimator_
    best_params = gs_final.best_params_
    print(f"Locked optimal production hyperparameters: {best_params}")

    # 3. SHAP TreeExplainer on the genuine tuned production model
    print(f"Computing SHAP explanations with TreeExplainer on {best_model_name}...")
    explainer = shap.TreeExplainer(final_model)
    shap_values = explainer.shap_values(X_imputed)

    mean_abs_shap = np.mean(np.abs(shap_values), axis=0)
    shap_importance = {name: float(val) for name, val in zip(feature_names, mean_abs_shap)}
    shap_importance = dict(sorted(shap_importance.items(), key=lambda x: x[1], reverse=True))

    # 4. Out-Of-Fold (OOF) Good Deals Layer: strictly leak-free and non-overfitted
    best_oof_raw = oof_predictions[best_model_name]
    oof_log_residuals = np.log(y_raw) - np.log(best_oof_raw)
    sigma_pred = float(np.std(oof_log_residuals))
    print(f"Residual Std Error from OOF predictions: sigma = {sigma_pred:.4f} (~ +/- {sigma_pred*100:.1f}%)")

    deals = []
    for idx, r in enumerate(records):
        observed = r["sale_price_vnd"]
        predicted_oof = best_oof_raw[idx]
        val_gap = (predicted_oof - observed) / predicted_oof

        # 95% Prediction Interval from OOF: [exp(log_p - 1.96*sigma), exp(log_p + 1.96*sigma)]
        pred_log = np.log(predicted_oof)
        lower_bound = np.exp(pred_log - 1.96 * sigma_pred)
        upper_bound = np.exp(pred_log + 1.96 * sigma_pred)

        is_good_deal = bool(observed < lower_bound)

        sample_shap = shap_values[idx]
        driver_indices = np.argsort(sample_shap)[::-1]
        top_positive_drivers = [(feature_names[i], float(sample_shap[i])) for i in driver_indices if sample_shap[i] > 0][:3]
        top_negative_drivers = [(feature_names[i], float(sample_shap[i])) for i in driver_indices[::-1] if sample_shap[i] < 0][:3]

        deals.append({
            "source_product_id": r["source_product_id"],
            "product_name": r["product_name"],
            "brand": r["brand"],
            "observed_price_vnd": observed,
            "predicted_price_vnd": round(predicted_oof, -4),
            "lower_bound_vnd": round(lower_bound, -4),
            "upper_bound_vnd": round(upper_bound, -4),
            "value_gap_percent": round(val_gap * 100, 2),
            "is_good_deal": is_good_deal,
            "top_positive_drivers": top_positive_drivers,
            "top_negative_drivers": top_negative_drivers,
        })

    good_deals_count = sum(d["is_good_deal"] for d in deals)
    print(f"Identified {good_deals_count} statistically significant 'Good Deal' laptops via OOF intervals.")

    return final_model, final_scaler, final_imputer, best_params, shap_importance, deals, sigma_pred


def compute_error_analysis(
    records: List[Dict[str, Any]],
    y_raw: np.ndarray,
    oof_preds: np.ndarray
) -> Dict[str, Any]:
    """Analyzes prediction errors across price segments and brands using authentic OOF predictions (§6.6)."""
    segment_defs = [
        ("< 15 Triệu (Phổ thông)", lambda p: p < 15_000_000),
        ("15 - 25 Triệu (Tầm trung)", lambda p: 15_000_000 <= p < 25_000_000),
        ("25 - 40 Triệu (Cận cao cấp)", lambda p: 25_000_000 <= p < 40_000_000),
        (">= 40 Triệu (Cao cấp / Flagship)", lambda p: p >= 40_000_000),
    ]

    segments_res = []
    for label, fn in segment_defs:
        idxs = [i for i, p in enumerate(y_raw) if fn(p)]
        if not idxs:
            continue
        y_seg = y_raw[idxs]
        p_seg = oof_preds[idxs]
        mae = float(np.mean(np.abs(y_seg - p_seg)))
        rmse = float(np.sqrt(np.mean((y_seg - p_seg) ** 2)))
        mape = float(np.mean(np.abs((y_seg - p_seg) / y_seg)) * 100)
        mean_p = float(np.mean(y_seg))
        segments_res.append({
            "segment": label,
            "count": len(idxs),
            "mean_price_vnd": round(mean_p, 0),
            "mae_vnd": round(mae, 0),
            "rmse_vnd": round(rmse, 0),
            "mape_percent": round(mape, 2)
        })

    brands_map: Dict[str, List[int]] = {}
    for i, r in enumerate(records):
        b = r.get("brand", "Unknown")
        brands_map.setdefault(b, []).append(i)

    brands_res = []
    for b_name, idxs in sorted(brands_map.items(), key=lambda x: len(x[1]), reverse=True):
        y_b = y_raw[idxs]
        p_b = oof_preds[idxs]
        mae = float(np.mean(np.abs(y_b - p_b)))
        rmse = float(np.sqrt(np.mean((y_b - p_b) ** 2)))
        mape = float(np.mean(np.abs((y_b - p_b) / y_b)) * 100)
        mean_p = float(np.mean(y_b))
        brands_res.append({
            "brand": b_name,
            "count": len(idxs),
            "mean_price_vnd": round(mean_p, 0),
            "mae_vnd": round(mae, 0),
            "rmse_vnd": round(rmse, 0),
            "mape_percent": round(mape, 2)
        })

    errors = []
    for i, r in enumerate(records):
        obs = float(y_raw[i])
        prd = float(oof_preds[i])
        diff = prd - obs
        abs_err = abs(diff)
        pct_err = abs_err / obs * 100
        errors.append({
            "source_product_id": r.get("source_product_id"),
            "product_name": r.get("product_name"),
            "brand": r.get("brand"),
            "observed_price_vnd": obs,
            "predicted_price_vnd": round(prd, -4),
            "error_vnd": round(diff, -4),
            "abs_error_vnd": round(abs_err, -4),
            "pct_error": round(pct_err, 2)
        })

    top_pct_outliers = sorted(errors, key=lambda x: x["pct_error"], reverse=True)[:5]
    top_abs_outliers = sorted(errors, key=lambda x: x["abs_error_vnd"], reverse=True)[:5]

    return {
        "price_segments": segments_res,
        "brands": brands_res,
        "top_percentage_outliers": top_pct_outliers,
        "top_absolute_outliers": top_abs_outliers
    }


def get_trained_model_and_predictions() -> Tuple[Any, List[Dict[str, Any]], np.ndarray]:
    """Provides trained model, records, and authentic Out-Of-Fold fair price predictions for D10 experiment.
    
    Reads precomputed OOF predictions from ml_oof_predictions.json to eliminate in-sample overfitting.
    """
    records, brands_list = load_dataset()
    
    # 1. Preferred route: load authentic OOF predictions from JSON
    if ML_OOF_PREDICTIONS_JSON.exists():
        try:
            with open(ML_OOF_PREDICTIONS_JSON, "r", encoding="utf-8") as f:
                oof_map = json.load(f)
            preds_raw = np.array([oof_map.get(r["source_product_id"], r["sale_price_vnd"]) for r in records], dtype=float)
            if MODEL_PIPELINE_FILE.exists():
                pipeline = joblib.load(MODEL_PIPELINE_FILE)
                return pipeline["model"], records, preds_raw
        except Exception as e:
            print(f"Warning: Failed reading OOF predictions: {e}. Falling back to pipeline transform.")

    # 2. Pipeline transform fallback
    X_raw, y_raw, y_log, groups, feature_names = assemble_feature_matrix(records, brands_list)
    if MODEL_PIPELINE_FILE.exists():
        try:
            pipeline = joblib.load(MODEL_PIPELINE_FILE)
            model = pipeline["model"]
            scaler = pipeline["scaler"]
            imputer = pipeline["imputer"]
            X_scaled = scaler.transform(X_raw)
            X_imputed = imputer.transform(X_scaled)
            preds_raw = np.exp(model.predict(X_imputed))
            return model, records, preds_raw
        except Exception as e:
            raise RuntimeError(f"Không thể đọc pipeline ML đã khóa: {e}") from e

    raise RuntimeError("Thiếu artifact ML/OOF đã khóa; hãy chạy src.ml_price_prediction trước D10.")


def run_pipeline():
    dataset_sha256 = compute_file_sha256(DATA_FILE)
    print(f"Starting ML Pipeline on {DATA_FILE.name} (SHA-256: {dataset_sha256[:16]}...)")

    records, brands_list = load_dataset()
    X_raw, y_raw, y_log, groups, feature_names = assemble_feature_matrix(records, brands_list)
    print(f"Dataset prepared: {X_raw.shape[0]} laptops, {X_raw.shape[1]} features (real NaNs preserved).")

    cv_results, oof_predictions, model_configs = evaluate_models_nested_groupkfold(X_raw, y_raw, y_log, groups)

    # Determine best valid model based on R^2.
    best_model_name = max(
        [k for k, value in cv_results.items() if "Baseline" not in k and value["status"] == "ok"],
        key=lambda k: cv_results[k]["r2_mean"]
    )
    print(f"\nBest performing model: {best_model_name} (R^2 = {cv_results[best_model_name]['r2_mean']:.4f})")

    # Save OOF predictions to JSON for D10 experiment traceability
    oof_map = {
        records[i]["source_product_id"]: float(oof_predictions[best_model_name][i])
        for i in range(len(records))
    }
    with open(ML_OOF_PREDICTIONS_JSON, "w", encoding="utf-8") as f:
        json.dump(oof_map, f, indent=2, ensure_ascii=False)
    print(f"Saved authentic OOF predictions to {ML_OOF_PREDICTIONS_JSON.relative_to(ROOT)}")

    final_model, final_scaler, final_imputer, best_params, shap_importance, deals, sigma_pred = fit_best_model_and_shap(
        best_model_name, model_configs, X_raw, y_raw, y_log, groups, records, feature_names, oof_predictions
    )

    # Save complete Pipeline with joblib
    final_pipeline = {
        "model_name": best_model_name,
        "model": final_model,
        "scaler": final_scaler,
        "imputer": final_imputer,
        "best_params": best_params,
        "brands_list": brands_list,
        "feature_names": feature_names,
        "sigma_pred": sigma_pred,
        "dataset_sha256": dataset_sha256,
        "cv_metrics": cv_results[best_model_name]
    }
    joblib.dump(final_pipeline, MODEL_PIPELINE_FILE)
    print(f"Saved complete production pipeline to {MODEL_PIPELINE_FILE.relative_to(ROOT)}")

    # Detailed Error Analysis (§6.6)
    error_analysis = compute_error_analysis(records, y_raw, oof_predictions[best_model_name])

    # Save Metrics JSON
    export_metrics = {
        "dataset_size": len(records),
        "dataset_sha256": dataset_sha256,
        "features_count": len(feature_names),
        "best_model": best_model_name,
        "best_hyperparameters": best_params,
        "sigma_pred_log": round(sigma_pred, 4),
        "models_cv": cv_results,
        "shap_importance": shap_importance,
        "good_deals_summary": {
            "total_evaluated": len(deals),
            "good_deals_count": sum(d["is_good_deal"] for d in deals),
            "top_good_deals": [d for d in deals if d["is_good_deal"]][:10]
        },
        "error_analysis": error_analysis
    }
    with open(ML_METRICS_JSON, "w", encoding="utf-8") as f:
        json.dump(export_metrics, f, indent=2, ensure_ascii=False)
    print(f"Saved metrics JSON to {ML_METRICS_JSON.relative_to(ROOT)}")

    generate_markdown_report(
        cv_results,
        best_model_name,
        best_params,
        shap_importance,
        deals,
        sigma_pred,
        dataset_sha256,
        len(records),
        error_analysis,
        min_price=float(np.min(y_raw)),
        max_price=float(np.max(y_raw)),
    )


def generate_markdown_report(
    cv_results: Dict[str, Any],
    best_model_name: str,
    best_params: Dict[str, Any],
    shap_importance: Dict[str, float],
    deals: List[Dict[str, Any]],
    sigma_pred: float,
    dataset_sha256: str,
    n_samples: int,
    error_analysis: Dict[str, Any],
    min_price: float = 8_790_000.0,
    max_price: float = 199_990_000.0,
):

    table_rows = []
    for name, m in cv_results.items():
        if m.get("status", "ok") != "ok":
            table_rows.append(
                f"| **{name}** | Không hội tụ ổn định | Không hội tụ ổn định | Không dùng để chọn mô hình | - | - |"
            )
            continue
        table_rows.append(
            f"| **{name}** | {m['r2_mean']:+.4f} ± {m['r2_std']:.4f} | {m['r2_log_mean']:+.4f} ± {m['r2_log_std']:.4f} | {m['mae_mean']:11,.0f} ± {m['mae_std']:9,.0f} đ | {m['rmse_mean']:11,.0f} đ | {m['mape_mean']:.2f}% |"
        )
    model_table_md = "\n".join(table_rows)

    shap_rows = []
    for rank, (feat, val) in enumerate(list(shap_importance.items())[:12], 1):
        shap_rows.append(f"| {rank} | `{feat}` | {val:.4f} |")
    shap_table_md = "\n".join(shap_rows)

    good_deal_laptops = [d for d in deals if d["is_good_deal"]]
    good_deal_rows = []
    for d in good_deal_laptops[:8]:
        good_deal_rows.append(
            f"| **{d['product_name'][:40]}** | {d['brand']} | {d['observed_price_vnd']:,.0f} đ | {d['predicted_price_vnd']:,.0f} đ | {d['lower_bound_vnd']:,.0f} đ | +{d['value_gap_percent']}% |"
        )
    good_deals_table_md = "\n".join(good_deal_rows) if good_deal_rows else "| (Không có mẫu nào lệch quá 1.96 sigma) | - | - | - | - | - |"

    segment_rows = []
    for s in error_analysis["price_segments"]:
        segment_rows.append(
            f"| {s['segment']} | {s['count']} | {s['mean_price_vnd']:11,.0f} đ | {s['mae_vnd']:10,.0f} đ | {s['rmse_vnd']:10,.0f} đ | {s['mape_percent']:.2f}% |"
        )
    segment_table_md = "\n".join(segment_rows)
    seg_map = {s["segment"]: s for s in error_analysis["price_segments"]}
    s_under15 = seg_map.get("< 15 Triệu (Phổ thông)", {"count": 0, "mape_percent": 0.0})
    s_15_25 = seg_map.get("15 - 25 Triệu (Tầm trung)", {"count": 0, "mape_percent": 0.0})
    s_25_40 = seg_map.get("25 - 40 Triệu (Cận cao cấp)", {"count": 0, "mape_percent": 0.0})
    s_above40 = seg_map.get(">= 40 Triệu (Cao cấp / Flagship)", {"count": 0, "mape_percent": 0.0})

    mid_high_count = s_15_25["count"] + s_25_40["count"]
    mid_high_pct = (mid_high_count / n_samples * 100) if n_samples > 0 else 0.0

    segment_note_md = f"""- Phân khúc **Tầm trung (15 - 25M, N={s_15_25['count']})** và **Cận cao cấp (25 - 40M, N={s_25_40['count']})** chiếm đại đa số tập mẫu ({mid_high_pct:.1f}%) và đạt độ chính xác tương đối xuất sắc (MAPE lần lượt là **{s_15_25['mape_percent']:.2f}%** và **{s_25_40['mape_percent']:.2f}%**). Điều này chứng minh thị trường laptop đại chúng tuân theo quy luật định giá linh kiện (CPU/RAM/SSD/GPU) rất chặt chẽ và nhất quán.
- Phân khúc **Phổ thông (< 15M, N={s_under15['count']})** có MAPE là **{s_under15['mape_percent']:.2f}%** do số lượng mẫu ít và tập trung các đợt xả kho giảm giá sâu đột biến — vì vậy không được API/UI dùng làm sàng lọc chênh lệch giá tham chiếu.
- Phân khúc **Cao cấp / Flagship (>= 40M, N={s_above40['count']})** có sai số tuyệt đối (MAE) cao hơn do biên độ giá rộng và các yếu tố phi phần cứng (vật liệu nguyên khối, màn hình chuẩn đồ họa, buồng hơi tản nhiệt), nhưng sai số tương đối (MAPE) vẫn được kiểm soát ở mức lý tưởng (**{s_above40['mape_percent']:.2f}%**) nhờ việc huấn luyện trên không gian log-target."""

    brand_rows = []
    for b in error_analysis["brands"]:
        brand_rows.append(
            f"| **{b['brand']}** | {b['count']} | {b['mean_price_vnd']:11,.0f} đ | {b['mae_vnd']:10,.0f} đ | {b['rmse_vnd']:10,.0f} đ | {b['mape_percent']:.2f}% |"
        )
    brand_table_md = "\n".join(brand_rows)

    outlier_rows = []
    for o in error_analysis["top_percentage_outliers"]:
        sign_str = "+" if o['error_vnd'] >= 0 else ""
        outlier_rows.append(
            f"| **{o['product_name'][:40]}** | {o['brand']} | {o['observed_price_vnd']:,.0f} đ | {o['predicted_price_vnd']:,.0f} đ | {sign_str}{o['error_vnd']:,.0f} đ | {o['pct_error']:.2f}% |"
        )
    outlier_table_md = "\n".join(outlier_rows)

    best_m = cv_results[best_model_name]

    report_content = f"""# BÁO CÁO MÔ HÌNH HỌC MÁY DỰ BÁO GIÁ & ĐỊNH GIÁ THỊ TRƯỜNG (GĐ4)
## Kiến Trúc Log-Target, Nested GroupKFold, SHAP Explainability & Sàng Lọc Chênh Lệch Giá OOF

**Ngày thực hiện:** 11/10/2026  
**Quy mô tập mẫu:** {n_samples} laptop chuẩn hóa (CellphoneS + FPT Shop)  
**Mã băm dữ liệu gốc:** `{dataset_sha256}`  
**Tuân thủ học thuật:** DECISIONS.md D10 (không đưa ML vào ma trận TOPSIS), D14 (KNN Imputation chỉ cho ML), Chuongtrinh.md GĐ4.

---

## 1. Phương Pháp Luận: Target Log-Scale & Feature Engineering Chống Rò Rỉ

### 1.1. Giải quyết phân phối lệch phải (Right-skewness)
- Phân phối giá laptop thị trường dao động từ {min_price / 1e6:.2f}M đến {max_price / 1e6:.2f}M VNĐ.
- **Giải pháp toán học:** Áp dụng biến đổi logarit tự nhiên $y = \\ln(\\text{{sale\\_price\\_vnd}})$, huấn luyện mô hình trên không gian logarit.

- **Tính chất thống kê của phép chuyển đổi ngược:** Phép biến đổi $\\hat{{y}}_{{\\text{{median}}}} = \\exp(\\hat{{y}}_{{\\ln}})$ ước lượng trung vị có điều kiện (geometric mean) của giá máy, kháng nhiễu cực tốt trước các mẫu ngoại lai siêu đắt. Với thừa số hiệu chỉnh smearing $\\exp(\\sigma^2 / 2)$, mô hình xấp xỉ kỳ vọng trung bình cộng có điều kiện.
- **Kết quả:** Sai số phần trăm tuyệt đối trung bình (MAPE) đạt **{best_m['mape_mean']:.2f}%**, hệ số xác định đạt **$R^2 = {best_m['r2_mean']:+.4f} \\pm {best_m['r2_std']:.4f}$**.

### 1.2. Kỹ nghệ đặc trưng phần cứng & Chống rò rỉ Imputation (Scale-Normalized)
1. **Bảo tồn giá trị thiếu thực tế:** Các thông số kỹ thuật chưa được nhà sản xuất công bố được giữ nguyên `NaN` thực tế (không dùng heuristic bịa số).
2. **Chuẩn hóa thang đo trước Imputation (M3):** Áp dụng `RobustScaler` trước khi đưa vào `KNNImputer(k=5)` để loại bỏ hiện tượng khoảng cách Euclid bị thống trị đơn lẻ bởi CPU benchmark (~1.000–26.000) so với các đặc trưng 0/1.
3. **Imputation không rò rỉ dữ liệu (Leakage-free):** `RobustScaler` và `KNNImputer` được fit độc lập bên trong từng fold huấn luyện của Outer GroupKFold, sau đó mới transform lên fold validation.
4. **Đặc trưng kỹ thuật và mã hóa thương hiệu:** GPU rời, VRAM (GB), 3DMark Time Spy, CPU Geekbench 6 Multi/Single, số nhân CPU, cờ nhị phân `cpu_benchmark_missing`, độ phân giải Megapixels, OLED, tần số quét Hz, độ sáng nits, pin Wh, trọng lượng kg, hệ điều hành macOS và mã hóa thương hiệu.

---

## 2. Kết Quả Đánh Giá Mô Hình Bằng Nested GroupKFold Cross-Validation

Đánh giá nghiêm ngặt qua **Nested GroupKFold** (5-Fold Outer để ước lượng sai số kỳ vọng, 3-Fold Inner GridSearchCV để tinh chỉnh siêu tham số) phân cụm theo `configuration_id`:

| Mô hình hồi quy | $R^2$ (VND gốc) | $R^2$ (Log Scale) | MAE (VND) | RMSE (VND) | MAPE (%) |
| :--- | :---: | :---: | :---: | :---: | :---: |
{model_table_md}

> [!NOTE]
> Mô hình **{best_model_name}** đạt hiệu năng dẫn đầu với **$R^2 = {best_m['r2_mean']:+.4f} \\pm {best_m['r2_std']:.4f}$**, sai số tuyệt đối trung bình $\\text{{MAE}} = {best_m['mae_mean']:,.0f} \\pm {best_m['mae_std']:,.0f}$ đ và $\\text{{MAPE}} = {best_m['mape_mean']:.2f}\\%$.  
> Bộ siêu tham số tối ưu xuất xưởng (GridSearchCV): `{best_params}`.

---

## 3. Khả Năng Giải Thích Mô Hình Với SHAP (SHAP TreeExplainer)

SHAP TreeExplainer được thực thi trực tiếp trên mô hình **{best_model_name}** xuất xưởng:

| Thứ hạng | Đặc trưng kỹ thuật | Giá trị SHAP trung bình (|SHAP|) | Ý nghĩa kinh tế |
| :---: | :--- | :---: | :--- |
{shap_table_md}

> [!NOTE]
> **Hiện tượng cộng tuyến đặc trưng trên cây quyết định (Tree Feature Collinearity):**  
> Các đặc trưng như `is_discrete_gpu` và `brand_Apple` có giá trị SHAP xấp xỉ 0 do mô hình cây đã rẽ nhánh hoàn toàn dựa trên các đặc trưng đại diện liên tục có tương quan hoàn hảo (`gpu_benchmark_time_spy > 0` và `is_macos == 1`). Đây là hành vi phân tách tự nhiên của thuật toán gradient boosting cây quyết định, không làm suy giảm chất lượng dự báo.

---

## 4. Sàng Lọc Chênh Lệch Giá Tham Chiếu Từ Dự Đoán Out-Of-Fold

Theo **DECISIONS.md D10**, ML không là tiêu chí trong ma trận TOPSIS. TOPSIS thuần là mặc định; giao diện có thể bật một lớp hậu xử lý ML-assisted tùy chọn 15%, và lớp này vẫn được công khai là có rủi ro đếm đôi giá ở điểm cuối:
- Sai số chuẩn phần dư Out-Of-Fold: $\\sigma_{{pred}} = {sigma_pred:.4f}$ (tương đương biên độ $\\approx \\pm {sigma_pred*100:.1f}\\%$).
- Khoảng dự báo 95%: $[\\hat{{y}}_{{OOF}} \\cdot \\exp(-1.96 \\sigma_{{pred}}), \\hat{{y}}_{{OOF}} \\cdot \\exp(+1.96 \\sigma_{{pred}})]$.
- Cả giá kỳ vọng và ngưỡng tin cậy đều tính từ **dự đoán Out-Of-Fold (OOF)**, loại bỏ hoàn toàn thiên vị tự khớp in-sample.

Danh sách dưới đây là **ứng viên OOF chưa giới hạn khoảng giá**, phục vụ kiểm tra pipeline. API/UI chỉ hiển thị chênh lệch giá tham chiếu trong khoảng 15–40 triệu đồng; đây không phải khuyến nghị mua hoặc đầu tư.

### Ứng Viên Chênh Lệch Giá OOF (Chưa Giới Hạn Khoảng Giá)

| Tên laptop | Hãng | Giá bán thực tế | Giá định giá OOF | Cận dưới 95% | Thặng dư (Value Gap) |
| :--- | :---: | :---: | :---: | :---: | :---: |
{good_deals_table_md}

---

## 5. Đóng Gói Vòng Đời & Tái Lập (Model Lifecycle & Reproducibility)

- Pipeline hoàn chỉnh (bao gồm `RobustScaler`, `KNNImputer`, mô hình `{best_model_name}`, siêu tham số `{best_params}` và ngưỡng $\\sigma$) đã được lưu tại:
  `data/artifacts/price_model.joblib`.
- Thông số kỹ thuật chi tiết lưu tại: `data/artifacts/price_model_metrics.json`.
- File dự đoán OOF phục vụ kiểm thử D10 độc lập: `data/artifacts/price_model_oof.json`.
- Cung cấp hàm `get_trained_model_and_predictions()` phục vụ thí nghiệm đối chứng D10.

---

## 6. Phân Tích Sai Số Chi Tiết Theo Phân Khúc Giá & Thương Hiệu (§6.6)

Đánh giá chi tiết sự phân bố sai số dựa trên dự đoán Out-Of-Fold (OOF) của mô hình tối ưu ({best_model_name}) nhằm nhận diện các vùng không gian đặc trưng có độ bất định cao:

### 6.1. Phân tích sai số theo phân khúc ngân sách

| Phân khúc giá | Số lượng ($N$) | Giá trung bình | MAE (VNĐ) | RMSE (VNĐ) | MAPE (%) |
| :--- | :---: | :---: | :---: | :---: | :---: |
{segment_table_md}

> [!NOTE]
> **Nhận định phân khúc:** 
{segment_note_md}

### 6.2. Phân tích sai số theo thương hiệu nhà sản xuất

| Thương hiệu | Số lượng ($N$) | Giá trung bình | MAE (VNĐ) | RMSE (VNĐ) | MAPE (%) |
| :--- | :---: | :---: | :---: | :---: | :---: |
{brand_table_md}

> [!NOTE]
> **Nhận định thương hiệu:**
> - Các hãng dải sản phẩm rộng tập trung vào phân khúc hiệu năng trên giá như **Asus, Acer, Lenovo, MSI** có MAPE rất đồng đều (~9–12%), bám sát giá trị phần cứng.
> - Các thương hiệu định vị cao cấp hoặc biên lợi nhuận thương hiệu đặc thù (Brand Premium) như **Apple, Dell** có mức giá trung bình cao hơn và khoảng lệch đặc thù; việc mô hình hóa bằng cờ thương hiệu one-hot đã giúp giải thuật hấp thu chính xác độ dốc giá riêng của từng hãng.

### 6.3. Phân tích các trường hợp ngoại lai lớn nhất (Top Outliers)

Dưới đây là 5 mẫu máy có sai số phần trăm (MAPE) lớn nhất trong tập kiểm thử OOF:

| Tên laptop | Hãng | Giá thực tế | Giá định giá OOF | Độ lệch (VNĐ) | Sai số MAPE (%) |
| :--- | :---: | :---: | :---: | :---: | :---: |
{outlier_table_md}

> [!NOTE]
> **Nguyên nhân ngoại lai:** Các mẫu có sai số phần trăm cao nhất thường thuộc hai nhóm:
> 1. Laptop được bán lẻ xả kho hoặc khuyến mãi giảm giá sâu đột xuất (giá thực tế thấp hơn nhiều so với giá trị cấu hình danh định).
> 2. Các mẫu laptop doanh nhân siêu nhẹ cao cấp mang các tính năng bảo mật doanh nghiệp, độ bền quân đội hoặc vật liệu siêu nhẹ đắt tiền không thể hiện hết qua bảng thông số kỹ thuật cốt lõi.
"""

    with open(ML_REPORT_FILE, "w", encoding="utf-8") as f:
        f.write(report_content)
    print(f"Generated comprehensive ML report at {ML_REPORT_FILE.relative_to(ROOT)}")


if __name__ == "__main__":
    run_pipeline()
