"""Kiểm thử các bộ lọc tối thiểu và loại trừ dùng chung cho API LaptopDSS."""

from types import SimpleNamespace

import pytest
from pydantic import ValidationError

from src.api import EvaluateRequest, PredictPriceRequest, RobustnessRequest, apply_catalog_filters, apply_ml_assisted_ranking, build_prediction_vector, get_ml_valuation, is_reference_gap, summarize_filter_data_quality


def test_minimum_memory_storage_and_excluded_brand_filters():
    rows = [
        {"product_name_raw": "ASUS A", "ram_gb": "16", "storage_total_gb": "512"},
        {"product_name_raw": "ASUS B", "ram_gb": "32", "storage_total_gb": "1024"},
        {"product_name_raw": "Apple C", "ram_gb": "32", "storage_total_gb": "1024"},
    ]
    req = SimpleNamespace(brand=None, cpu_family=None, ram_gb=None, min_ram_gb=16, storage_gb=None, min_storage_gb=512, excluded_brands=["Apple"], screen_size=None, panel_type=None, min_brightness_nits=None, require_rj45_lan=None, require_ram_upgradeable=None, require_type_c_charging=None, require_thunderbolt=None)
    assert [row["product_name_raw"] for row in apply_catalog_filters(rows, req)] == ["ASUS A", "ASUS B"]


@pytest.mark.parametrize("payload", [
    {"min_ram_gb": -1}, {"min_budget_vnd": float("nan")},
    {"max_budget_vnd": float("inf")}, {"min_budget_vnd": 2, "max_budget_vnd": 1},
])
def test_evaluate_request_rejects_invalid_numeric_constraints(payload):
    with pytest.raises(ValidationError):
        EvaluateRequest(**payload)


def test_prediction_request_rejects_impossible_hardware():
    with pytest.raises(ValidationError):
        PredictPriceRequest(ram_gb=-16)
    with pytest.raises(ValidationError):
        PredictPriceRequest(is_discrete_gpu=False, gpu_vram_gb=8)
    assert PredictPriceRequest(brand="ASUS").brand == "Asus"
    with pytest.raises(ValidationError):
        PredictPriceRequest(brand="Unknown")


def test_evaluate_request_rejects_unknown_brand_but_accepts_ui_casing():
    with pytest.raises(ValidationError):
        EvaluateRequest(brand="Foo")
    assert EvaluateRequest(brand="ASUS").brand == "ASUS"
    with pytest.raises(ValidationError):
        EvaluateRequest(excluded_brands=["Unknown brand"])


@pytest.mark.parametrize("payload", [{"simulations": 24}, {"simulations": 1001}, {"concentration": 0}, {"concentration": float("inf")}])
def test_robustness_request_bounds_expensive_simulation(payload):
    with pytest.raises(ValidationError):
        RobustnessRequest(**payload)


@pytest.mark.parametrize("payload", [
    {"required_os": "Linux"}, {"panel_type": "CRT"}, {"screen_size": "99 inch"}, {"cpu_family": "Xeon"},
])
def test_evaluate_request_rejects_unknown_filter_enums(payload):
    with pytest.raises(ValidationError):
        EvaluateRequest(**payload)


def test_prediction_vector_is_mapped_by_feature_name_not_position():
    req = PredictPriceRequest(cpu_benchmark_multi=12000, ram_gb=16, brand="ASUS")
    feature_names = ["brand_Asus", "ram_gb", "cpu_benchmark_multi", "cpu_benchmark_missing"]
    vector = build_prediction_vector(req, feature_names)[0]
    assert vector.tolist() == [1.0, 16.0, 12000.0, 0.0]


def test_ml_valuation_reference_gap_is_complete_and_uses_new_label():
    response = get_ml_valuation()
    summary = response["reference_gap_summary"]
    assert response["available"] is True
    assert "good_deals_summary" not in response
    assert summary["screened_count"] == 9
    assert len(summary["top_reference_gaps"]) == 9
    assert all(item["is_reference_gap"] is True and "is_good_deal" not in item for item in summary["top_reference_gaps"])
    assert all("brand" not in item for item in summary["top_reference_gaps"])


def test_reference_gap_price_window_boundaries():
    # Predicted 20M and sigma=0.1 gives a lower bound of about 16.44M.
    assert is_reference_gap(14_990_000, 20_000_000, 0.1) is False
    assert is_reference_gap(15_000_000, 20_000_000, 0.1) is True
    assert is_reference_gap(40_000_000, 50_000_000, 0.1) is True
    assert is_reference_gap(40_010_000, 50_000_000, 0.1) is False


def test_ml_assisted_ranking_uses_oof_value_score_but_keeps_topsis_visible():
    rankings = [
        {"source_product_id": "a", "rank": 1, "topsis_score": 0.70, "sale_price_vnd": 20_000_000, "ml_predicted_price_vnd": 20_000_000},
        {"source_product_id": "b", "rank": 2, "topsis_score": 0.69, "sale_price_vnd": 15_000_000, "ml_predicted_price_vnd": 20_000_000},
    ]
    assert apply_ml_assisted_ranking(rankings, enabled=True, weight=0.15, ml_available=True) is True
    assert rankings[0]["source_product_id"] == "b"
    assert rankings[0]["topsis_rank"] == 2
    assert rankings[0]["recommendation_score"] > rankings[1]["recommendation_score"]
    assert rankings[0]["ml_ranking_eligible"] is True


def test_ml_ranking_weight_is_bounded():
    with pytest.raises(ValidationError):
        EvaluateRequest(ml_ranking_weight=0.31)


def test_zero_ml_weight_remains_topsis_only():
    rankings = [{"rank": 1, "topsis_score": 0.7, "sale_price_vnd": 20_000_000, "ml_predicted_price_vnd": 25_000_000}]
    assert apply_ml_assisted_ranking(rankings, enabled=True, weight=0.0, ml_available=True) is False
    assert rankings[0]["recommendation_score"] == rankings[0]["topsis_score"]


def test_verified_only_filter_reports_unknown_instead_of_silently_equating_it_to_false():
    rows = [
        {"product_name_raw": "Has LAN", "lan_present": "true"},
        {"product_name_raw": "No LAN", "lan_present": "false"},
        {"product_name_raw": "Unknown LAN", "lan_present": ""},
    ]
    req = SimpleNamespace(
        brand=None, cpu_family=None, ram_gb=None, min_ram_gb=None, storage_gb=None,
        min_storage_gb=None, excluded_brands=None, screen_size=None, panel_type=None,
        require_rj45_lan=True, require_type_c_charging=False, require_thunderbolt=False,
        require_ram_upgradeable=False, min_brightness_nits=None,
    )
    summary = summarize_filter_data_quality(rows, req)
    assert summary == [{"filter": "require_rj45_lan", "label": "Cổng mạng LAN RJ45", "policy": "verified_only", "verified_count": 1, "known_false_count": 1, "unknown_count": 1}]
    assert [item["product_name_raw"] for item in apply_catalog_filters(rows, req)] == ["Has LAN"]
