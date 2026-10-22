"""Đánh giá stress test theo nguồn cho model đã triển khai của LaptopDSS.

Model được lấy từ artifact thay vì hard-code. Retailer holdout loại các cấu
hình trùng train/test; đây vẫn chỉ là quasi-external stress test, không phải
ngoại kiểm độc lập hoặc temporal validation.
"""

import csv
import json
import math
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

sys.stdout.reconfigure(encoding='utf-8')
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import numpy as np
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.impute import KNNImputer
from sklearn.metrics import mean_absolute_error, mean_absolute_percentage_error, r2_score
from sklearn.model_selection import GroupKFold
from sklearn.preprocessing import RobustScaler
import xgboost as xgb

from ml_price_prediction import (
    DATA_FILE,
    ML_METRICS_JSON,
    ML_OOF_PREDICTIONS_JSON,
    assemble_feature_matrix,
    load_dataset,
)

REPORT_FILE = ROOT / "data" / "reports" / "external_validation_report.md"
RESULT_FILE = ROOT / "data" / "reports" / "external_validation_metrics.json"
RANDOM_SEED = 42


def metric_summary(y_true: np.ndarray, predicted: np.ndarray) -> Dict[str, float]:
    """Trả các chỉ số hồi quy, tránh diễn giải R² khi test set chỉ có một mẫu."""
    return {
        "n": int(len(y_true)),
        "mae_vnd": round(float(mean_absolute_error(y_true, predicted)), 2),
        "mape_percent": round(float(mean_absolute_percentage_error(y_true, predicted) * 100), 3),
        "r2": round(float(r2_score(y_true, predicted)), 4) if len(y_true) >= 2 else None,
    }


def bootstrap_mae_difference(
    y_true: np.ndarray, selected_predictions: np.ndarray, comparator_predictions: np.ndarray,
    selected_name: str = "Gradient Boosting", comparator_name: str = "XGBoost Regressor",
    iterations: int = 2_000, seed: int = RANDOM_SEED,
) -> Dict[str, float]:
    """Bootstrap cặp cho delta = MAE(comparator) - MAE(selected)."""
    rng = np.random.default_rng(seed)
    selected_errors = np.abs(y_true - selected_predictions)
    comparator_errors = np.abs(y_true - comparator_predictions)
    indices = rng.integers(0, len(y_true), size=(iterations, len(y_true)))
    deltas = comparator_errors[indices].mean(axis=1) - selected_errors[indices].mean(axis=1)
    return {
        "delta_mae_comparator_minus_selected_vnd": round(float(np.mean(deltas)), 2),
        "ci95_low_vnd": round(float(np.quantile(deltas, 0.025)), 2),
        "ci95_high_vnd": round(float(np.quantile(deltas, 0.975)), 2),
        "interpretation": f"{selected_name} tốt hơn trên MAE" if np.quantile(deltas, 0.025) > 0 else f"Chưa đủ bằng chứng phân biệt {selected_name} và {comparator_name}",
    }


def source_labels() -> Dict[str, str]:
    """Ánh xạ source_product_id sang nguồn bán lẻ của CSV chuẩn hóa."""
    with DATA_FILE.open(encoding="utf-8", newline="") as file:
        return {row["source_product_id"]: row.get("source", "Không rõ") for row in csv.DictReader(file)}


def transform_train_test(X_train: np.ndarray, X_test: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """Fit scaler/imputer chỉ trên train để tránh leakage trong retailer holdout."""
    scaler = RobustScaler(unit_variance=True)
    train_scaled = scaler.fit_transform(X_train)
    test_scaled = scaler.transform(X_test)
    imputer = KNNImputer(n_neighbors=5)
    return imputer.fit_transform(train_scaled), imputer.transform(test_scaled)


def build_model(name: str, params: Dict[str, Any]):
    if name == "Gradient Boosting":
        return GradientBoostingRegressor(random_state=RANDOM_SEED, **params)
    if name == "Random Forest Regressor":
        return RandomForestRegressor(random_state=RANDOM_SEED, **params)
    if name == "XGBoost Regressor":
        return xgb.XGBRegressor(random_state=RANDOM_SEED, verbosity=0, **params)
    raise ValueError(f"Retailer holdout chưa hỗ trợ model triển khai: {name}")


def fixed_oof_predictions(X: np.ndarray, y_log: np.ndarray, groups: np.ndarray, selected_name: str, selected_params: Dict[str, Any]) -> Tuple[np.ndarray, np.ndarray, str]:
    """OOF sau chọn mô hình với tham số đã khóa; không tuning lại trên validation fold."""
    selected_oof = np.zeros(len(X))
    comparator_name = "XGBoost Regressor" if selected_name != "XGBoost Regressor" else "Random Forest Regressor"
    comparator_params = {"n_estimators": 150, "max_depth": 4, "learning_rate": 0.05} if comparator_name == "XGBoost Regressor" else {"n_estimators": 100, "max_depth": 12}
    comparator_oof = np.zeros(len(X))
    for train_idx, test_idx in GroupKFold(n_splits=5).split(X, y_log, groups):
        X_train, X_test = transform_train_test(X[train_idx], X[test_idx])
        selected = build_model(selected_name, selected_params)
        comparator = build_model(comparator_name, comparator_params)
        selected_oof[test_idx] = np.exp(selected.fit(X_train, y_log[train_idx]).predict(X_test))
        comparator_oof[test_idx] = np.exp(comparator.fit(X_train, y_log[train_idx]).predict(X_test))
    return selected_oof, comparator_oof, comparator_name


def retailer_holdout(X: np.ndarray, y_raw: np.ndarray, y_log: np.ndarray, sources: np.ndarray, groups: np.ndarray, selected_name: str, selected_params: Dict[str, Any]) -> Dict[str, Any]:
    """Huấn luyện CellphoneS, kiểm FPT Shop khi mỗi nguồn có đủ mẫu."""
    results: Dict[str, Any] = {}
    for held_out in sorted(set(sources)):
        test_mask = sources == held_out
        train_mask = ~test_mask
        overlapping_groups = set(groups[train_mask]) & set(groups[test_mask])
        test_mask &= ~np.isin(groups, list(overlapping_groups))
        if test_mask.sum() < 5 or train_mask.sum() < 30:
            results[held_out] = {"status": "skipped", "reason": "Không đủ mẫu train/test sau khi loại cấu hình trùng", "excluded_overlap_count": len(overlapping_groups)}
            continue
        X_train, X_test = transform_train_test(X[train_mask], X[test_mask])
        pred = np.exp(build_model(selected_name, selected_params).fit(X_train, y_log[train_mask]).predict(X_test))
        results[held_out] = {"status": "completed", "excluded_overlap_count": len(overlapping_groups), **metric_summary(y_raw[test_mask], pred)}
    return results


def interval_coverage(y_raw: np.ndarray, predicted: np.ndarray, sigma_log: float, labels: np.ndarray) -> Dict[str, Any]:
    """Đo tần suất giá quan sát nằm trong khoảng exp(log(pred) ± 1.96 sigma)."""
    lower = np.exp(np.log(predicted) - 1.96 * sigma_log)
    upper = np.exp(np.log(predicted) + 1.96 * sigma_log)
    covered = (y_raw >= lower) & (y_raw <= upper)
    output: Dict[str, Any] = {"overall_percent": round(float(covered.mean() * 100), 2), "target_percent": 95.0, "by_segment": {}}
    for label in sorted(set(labels)):
        mask = labels == label
        output["by_segment"][str(label)] = {"n": int(mask.sum()), "coverage_percent": round(float(covered[mask].mean() * 100), 2)}
    return output


def run_external_validation() -> Dict[str, Any]:
    """Chạy thí nghiệm, ghi JSON và Markdown để đưa trực tiếp vào báo cáo đồ án."""
    records, brands = load_dataset()
    X, y_raw, y_log, groups, _ = assemble_feature_matrix(records, brands)
    sources_by_id = source_labels()
    sources = np.array([sources_by_id.get(record["source_product_id"], "Không rõ") for record in records])

    with ML_METRICS_JSON.open(encoding="utf-8") as file:
        artifact_metrics = json.load(file)
    selected_name = artifact_metrics["best_model"]
    selected_params = artifact_metrics["best_hyperparameters"]
    selected_oof, comparator_oof, comparator_name = fixed_oof_predictions(X, y_log, groups, selected_name, selected_params)
    sigma = float(artifact_metrics["sigma_pred_log"])
    price_segment = np.where(y_raw < 15_000_000, "<15M", np.where(y_raw < 25_000_000, "15–25M", np.where(y_raw < 40_000_000, "25–40M", "≥40M")))

    result = {
        "dataset_size": len(records),
        "source_counts": {source: int((sources == source).sum()) for source in sorted(set(sources))},
        "selection_protocol": {
            "primary_metric": "MAE trên VND gốc",
            "secondary_metrics": ["MAPE", "R²", "độ ổn định bootstrap", "coverage khoảng dự báo"],
            "selected_model": selected_name,
            "decision_rule": "Chọn model theo R² Nested GroupKFold trong artifact; bootstrap chỉ mô tả bất định MAE so với model đối chứng.",
        },
        "post_selection_oof": {"selected": metric_summary(y_raw, selected_oof), "comparator": metric_summary(y_raw, comparator_oof)},
        "paired_bootstrap": bootstrap_mae_difference(y_raw, selected_oof, comparator_oof, selected_name, comparator_name),
        "retailer_holdout": retailer_holdout(X, y_raw, y_log, sources, groups, selected_name, selected_params),
        "interval_coverage": interval_coverage(y_raw, selected_oof, sigma, price_segment),
        "limitations": [
            "Retailer holdout không phải external validation độc lập: hai nguồn cùng snapshot thị trường.",
            "FPT Shop chỉ có 8 mẫu trước khi loại cấu hình trùng; không dùng kết quả này để xếp hạng mô hình cuối cùng.",
            "Cần snapshot thời gian sau hoặc nguồn thứ ba trước khi khẳng định khả năng tổng quát hóa.",
        ],
    }
    RESULT_FILE.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    holdout_rows = "\n".join(f"| {source} | {item.get('status')} | {item.get('n', '—')} | {item.get('mae_vnd', '—')} | {item.get('mape_percent', '—')} |" for source, item in result["retailer_holdout"].items())
    source_summary = ", ".join(f"{source}: {count}" for source, count in result["source_counts"].items())
    boot = result["paired_bootstrap"]
    cov = result["interval_coverage"]
    REPORT_FILE.write_text(
        f"""# ĐÁNH GIÁ NGOÀI THEO NGUỒN VÀ CHỌN MÔ HÌNH ML

**Quy mô:** {len(records)} cấu hình; nguồn: {source_summary}.

## Kết luận chọn mô hình

**{selected_name}** là model triển khai vì dẫn đầu $R^2$ trong artifact Nested GroupKFold nội bộ. Kết quả dưới đây không cho phép gọi nó là tối ưu tuyệt đối nếu bootstrap chưa tách biệt nó khỏi model đối chứng.

## So sánh OOF hậu chọn (tham số đã khóa)

| Mô hình | MAE (VND) | MAPE (%) | R² |
|---|---:|---:|---:|
| {selected_name} | {result['post_selection_oof']['selected']['mae_vnd']:,.0f} | {result['post_selection_oof']['selected']['mape_percent']:.2f} | {result['post_selection_oof']['selected']['r2']:.4f} |
| {comparator_name} | {result['post_selection_oof']['comparator']['mae_vnd']:,.0f} | {result['post_selection_oof']['comparator']['mape_percent']:.2f} | {result['post_selection_oof']['comparator']['r2']:.4f} |

Bootstrap cặp: ΔMAE({comparator_name} − {selected_name}) = {boot['delta_mae_comparator_minus_selected_vnd']:,.0f} VND, CI95% [{boot['ci95_low_vnd']:,.0f}; {boot['ci95_high_vnd']:,.0f}]. **{boot['interpretation']}**.

## Retailer holdout (quasi-external)

| Nguồn giữ lại làm test | Trạng thái | n | MAE (VND) | MAPE (%) |
|---|---|---:|---:|---:|
{holdout_rows}

## Calibration khoảng dự báo 95%

Coverage tổng thể: **{cov['overall_percent']}%** (mục tiêu danh nghĩa 95%). Kết quả này phải được đọc cùng cỡ mẫu từng phân khúc; nếu lệch đáng kể cần cân nhắc conformal prediction.

## Giới hạn

- Retailer holdout không thay thế tập ngoài độc lập hoặc temporal holdout.
- FPT Shop chỉ có 8 mẫu trước khi loại cấu hình trùng; đây là stress test, không là tiêu chí chọn mô hình.
- Bước tiếp theo là thu snapshot giá mới hoặc nguồn thứ ba và chỉ đánh giá pipeline đã khóa.
""",
        encoding="utf-8",
    )
    return result


if __name__ == "__main__":
    output = run_external_validation()
    print(f"Đã ghi {RESULT_FILE.relative_to(ROOT)} và {REPORT_FILE.relative_to(ROOT)}; {output['paired_bootstrap']['interpretation']}.")
