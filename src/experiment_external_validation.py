"""Đánh giá ngoài theo nguồn và giao thức chọn mô hình ML của LaptopDSS.

Vai trò: kiểm tra tính chuyển giao của Gradient Boosting sau Nested GroupKFold
nội bộ. Script giữ một nhà bán lẻ làm tập kiểm tra, so sánh cặp OOF Gradient
Boosting/XGBoost bằng bootstrap và đo coverage khoảng dự báo 95%.

Lưu ý khoa học: FPT Shop chỉ có 10 quan sát trong snapshot hiện tại; kết quả
retailer holdout là stress test theo nguồn (quasi-external), không thay thế tập
ngoại kiểm độc lập hoặc snapshot thời gian sau.
"""

import csv
import json
import math
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

sys.stdout.reconfigure(encoding='utf-8')

import numpy as np
from sklearn.ensemble import GradientBoostingRegressor
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

ROOT = Path(__file__).resolve().parents[1]
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
    y_true: np.ndarray, gradient_predictions: np.ndarray, xgboost_predictions: np.ndarray,
    iterations: int = 2_000, seed: int = RANDOM_SEED,
) -> Dict[str, float]:
    """Bootstrap cặp cho delta = MAE(XGBoost) - MAE(Gradient Boosting)."""
    rng = np.random.default_rng(seed)
    gb_errors = np.abs(y_true - gradient_predictions)
    xgb_errors = np.abs(y_true - xgboost_predictions)
    indices = rng.integers(0, len(y_true), size=(iterations, len(y_true)))
    deltas = xgb_errors[indices].mean(axis=1) - gb_errors[indices].mean(axis=1)
    return {
        "delta_mae_xgb_minus_gb_vnd": round(float(np.mean(deltas)), 2),
        "ci95_low_vnd": round(float(np.quantile(deltas, 0.025)), 2),
        "ci95_high_vnd": round(float(np.quantile(deltas, 0.975)), 2),
        "interpretation": "Gradient Boosting tốt hơn trên MAE" if np.quantile(deltas, 0.025) > 0 else "Chưa đủ bằng chứng phân biệt Gradient Boosting và XGBoost",
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


def fixed_oof_predictions(X: np.ndarray, y_log: np.ndarray, groups: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """OOF sau chọn mô hình với tham số đã khóa; không tuning lại trên validation fold."""
    gb_oof = np.zeros(len(X))
    xgb_oof = np.zeros(len(X))
    for train_idx, test_idx in GroupKFold(n_splits=5).split(X, y_log, groups):
        X_train, X_test = transform_train_test(X[train_idx], X[test_idx])
        gb = GradientBoostingRegressor(random_state=RANDOM_SEED, n_estimators=150, max_depth=3, learning_rate=0.05)
        xgb_model = xgb.XGBRegressor(random_state=RANDOM_SEED, verbosity=0, n_estimators=150, max_depth=4, learning_rate=0.05)
        gb_oof[test_idx] = np.exp(gb.fit(X_train, y_log[train_idx]).predict(X_test))
        xgb_oof[test_idx] = np.exp(xgb_model.fit(X_train, y_log[train_idx]).predict(X_test))
    return gb_oof, xgb_oof


def retailer_holdout(X: np.ndarray, y_raw: np.ndarray, y_log: np.ndarray, sources: np.ndarray) -> Dict[str, Any]:
    """Huấn luyện CellphoneS, kiểm FPT Shop khi mỗi nguồn có đủ mẫu."""
    results: Dict[str, Any] = {}
    for held_out in sorted(set(sources)):
        test_mask = sources == held_out
        train_mask = ~test_mask
        if test_mask.sum() < 5 or train_mask.sum() < 30:
            results[held_out] = {"status": "skipped", "reason": "Không đủ mẫu train/test"}
            continue
        X_train, X_test = transform_train_test(X[train_mask], X[test_mask])
        gb = GradientBoostingRegressor(random_state=RANDOM_SEED, n_estimators=150, max_depth=3, learning_rate=0.05)
        pred = np.exp(gb.fit(X_train, y_log[train_mask]).predict(X_test))
        results[held_out] = {"status": "completed", **metric_summary(y_raw[test_mask], pred)}
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

    gb_oof, xgb_oof = fixed_oof_predictions(X, y_log, groups)
    with ML_METRICS_JSON.open(encoding="utf-8") as file:
        sigma = float(json.load(file)["sigma_pred_log"])
    price_segment = np.where(y_raw < 15_000_000, "<15M", np.where(y_raw < 25_000_000, "15–25M", np.where(y_raw < 40_000_000, "25–40M", "≥40M")))

    result = {
        "dataset_size": len(records),
        "source_counts": {source: int((sources == source).sum()) for source in sorted(set(sources))},
        "selection_protocol": {
            "primary_metric": "MAE trên VND gốc",
            "secondary_metrics": ["MAPE", "R²", "độ ổn định bootstrap", "coverage khoảng dự báo"],
            "selected_model": "Gradient Boosting (tạm thời)",
            "decision_rule": "Giữ Gradient Boosting nếu dẫn đầu MAE nội bộ; không tuyên bố vượt trội thống kê nếu CI bootstrap chứa 0.",
        },
        "post_selection_oof": {"gradient_boosting": metric_summary(y_raw, gb_oof), "xgboost": metric_summary(y_raw, xgb_oof)},
        "paired_bootstrap": bootstrap_mae_difference(y_raw, gb_oof, xgb_oof),
        "retailer_holdout": retailer_holdout(X, y_raw, y_log, sources),
        "interval_coverage": interval_coverage(y_raw, gb_oof, sigma, price_segment),
        "limitations": [
            "Retailer holdout không phải external validation độc lập: hai nguồn cùng snapshot thị trường.",
            "FPT Shop chỉ có 10 mẫu; không dùng kết quả này để xếp hạng mô hình cuối cùng.",
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

Gradient Boosting được giữ làm mô hình triển khai **tạm thời** vì dẫn đầu artifact Nested GroupKFold nội bộ. Kết quả dưới đây không cho phép gọi nó là tối ưu tuyệt đối nếu bootstrap chưa tách biệt nó khỏi XGBoost.

## So sánh OOF hậu chọn (tham số đã khóa)

| Mô hình | MAE (VND) | MAPE (%) | R² |
|---|---:|---:|---:|
| Gradient Boosting | {result['post_selection_oof']['gradient_boosting']['mae_vnd']:,.0f} | {result['post_selection_oof']['gradient_boosting']['mape_percent']:.2f} | {result['post_selection_oof']['gradient_boosting']['r2']:.4f} |
| XGBoost | {result['post_selection_oof']['xgboost']['mae_vnd']:,.0f} | {result['post_selection_oof']['xgboost']['mape_percent']:.2f} | {result['post_selection_oof']['xgboost']['r2']:.4f} |

Bootstrap cặp: ΔMAE(XGBoost − Gradient Boosting) = {boot['delta_mae_xgb_minus_gb_vnd']:,.0f} VND, CI95% [{boot['ci95_low_vnd']:,.0f}; {boot['ci95_high_vnd']:,.0f}]. **{boot['interpretation']}**.

## Retailer holdout (quasi-external)

| Nguồn giữ lại làm test | Trạng thái | n | MAE (VND) | MAPE (%) |
|---|---|---:|---:|---:|
{holdout_rows}

## Calibration khoảng dự báo 95%

Coverage tổng thể: **{cov['overall_percent']}%** (mục tiêu danh nghĩa 95%). Kết quả này phải được đọc cùng cỡ mẫu từng phân khúc; nếu lệch đáng kể cần cân nhắc conformal prediction.

## Giới hạn

- Retailer holdout không thay thế tập ngoài độc lập hoặc temporal holdout.
- FPT Shop chỉ có 10 mẫu; đây là stress test, không là tiêu chí chọn mô hình.
- Bước tiếp theo là thu snapshot giá mới hoặc nguồn thứ ba và chỉ đánh giá pipeline đã khóa.
""",
        encoding="utf-8",
    )
    return result


if __name__ == "__main__":
    output = run_external_validation()
    print(f"Đã ghi {RESULT_FILE.relative_to(ROOT)} và {REPORT_FILE.relative_to(ROOT)}; {output['paired_bootstrap']['interpretation']}.")
