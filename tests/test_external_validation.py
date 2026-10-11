"""Kiểm thử các phép tính đánh giá ngoài, không chạy huấn luyện nặng."""

import numpy as np

from src.experiment_external_validation import bootstrap_mae_difference, interval_coverage, metric_summary


def test_bootstrap_reports_gradient_boosting_advantage_when_errors_are_lower():
    result = bootstrap_mae_difference(np.array([10.0, 20.0]), np.array([10.0, 20.0]), np.array([20.0, 30.0]), iterations=200)
    assert result["ci95_low_vnd"] > 0


def test_interval_coverage_and_metrics_have_expected_schema():
    metrics = metric_summary(np.array([100.0, 200.0]), np.array([100.0, 200.0]))
    coverage = interval_coverage(np.array([100.0, 200.0]), np.array([100.0, 200.0]), 0.1, np.array(["A", "B"]))
    assert metrics["mae_vnd"] == 0.0
    assert coverage["overall_percent"] == 100.0
