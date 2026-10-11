"""Kiểm thử đơn vị AHP-TOPSIS bằng dữ liệu tổng hợp và biên.

Xác minh AHP, TOPSIS, D05, D14, lọc ngân sách, Direct Rating và độ nhạy mà
không sửa dữ liệu nghiệp vụ.
"""

import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from dss_ranking import (
    compute_fit_score,
    compute_ahp_weights,
    evaluate,
    PRESETS,
    analyze_budget_sensitivity,
    analyze_weight_sensitivity,
)


def test_fit_function_boundary_points():
    """Verify explicit Fit piecewise utility function at exact required boundary points."""
    # 1. RAM for Gaming/Coding (threshold=16, cap=32, cap_bonus=0.20, tail_rate=0.05)
    params_ram_coding = {"threshold": 16.0, "cap": 32.0, "cap_bonus": 0.20, "tail_rate": 0.05}
    assert compute_fit_score(0.0, **params_ram_coding) == 0.0
    assert compute_fit_score(8.0, **params_ram_coding) == 0.5
    assert compute_fit_score(16.0, **params_ram_coding) == 1.0
    assert compute_fit_score(32.0, **params_ram_coding) == 1.2
    assert round(compute_fit_score(64.0, **params_ram_coding), 4) == 1.25

    # 2. RAM for Office (threshold=16, cap=16, cap_bonus=0.0, tail_rate=0.02)
    params_ram_office = {"threshold": 16.0, "cap": 16.0, "cap_bonus": 0.0, "tail_rate": 0.02}
    assert compute_fit_score(0.0, **params_ram_office) == 0.0
    assert compute_fit_score(8.0, **params_ram_office) == 0.5
    assert compute_fit_score(16.0, **params_ram_office) == 1.0
    assert round(compute_fit_score(32.0, **params_ram_office), 4) == 1.02
    assert round(compute_fit_score(64.0, **params_ram_office), 4) == 1.06

    # 3. Storage for Gaming/Coding (threshold=512, cap=1024, cap_bonus=0.20, tail_rate=0.05)
    params_ssd = {"threshold": 512.0, "cap": 1024.0, "cap_bonus": 0.20, "tail_rate": 0.05}
    assert compute_fit_score(0.0, **params_ssd) == 0.0
    assert compute_fit_score(256.0, **params_ssd) == 0.5
    assert compute_fit_score(512.0, **params_ssd) == 1.0
    assert compute_fit_score(1024.0, **params_ssd) == 1.2
    assert round(compute_fit_score(2048.0, **params_ssd), 4) == 1.25


def test_ahp_reciprocity_and_consistency():
    """Verify that all AHP pairwise matrices exhibit exact reciprocity and CR < 0.10."""
    for pkey, preset in PRESETS.items():
        mat = preset["matrix"]
        n = len(mat)
        for i in range(n):
            for j in range(n):
                product = mat[i][j] * mat[j][i]
                assert abs(product - 1.0) < 1e-4, f"AHP reciprocity failed at ({i},{j}) in preset {pkey}"

        weights, lambda_max, cr = compute_ahp_weights(mat)
        assert abs(sum(weights) - 1.0) < 1e-4, f"Weights of {pkey} must sum to 1.0"
        assert cr < 0.10, f"Preset {pkey} CR ({cr:.4f}) must be strictly < 0.10"


def test_synthetic_topsis_math():
    """Test pure TOPSIS logic with 2 synthetic candidates where Option A dominates Option B."""
    candidates = [
        {
            "product_name_raw": "Laptop Dominant",
            "os_name": "Windows",
            "gpu_type": "discrete",
            "gpu_benchmark_time_spy": "10000",
            "cpu_benchmark_multi_core": "15000",
            "sale_price_vnd": "20000000",
            "ram_gb": "32",
            "storage_total_gb": "1024",
            "refresh_rate_hz": "144",
        },
        {
            "product_name_raw": "Laptop Inferior",
            "os_name": "Windows",
            "gpu_type": "discrete",
            "gpu_benchmark_time_spy": "4000",
            "cpu_benchmark_multi_core": "8000",
            "sale_price_vnd": "35000000",
            "ram_gb": "8",
            "storage_total_gb": "512",
            "refresh_rate_hz": "144",
        },
    ]

    res = evaluate(candidates, preset_key="gaming")
    assert res["status"] == "success"
    assert len(res["rankings"]) == 2
    assert res["rankings"][0]["product_name_raw"] == "Laptop Dominant"
    assert res["rankings"][0]["topsis_score"] > res["rankings"][1]["topsis_score"]
    assert res["rankings"][0]["rank"] == 1
    assert res["rankings"][1]["rank"] == 2


def test_missing_data_strict_exclusion_no_zero_coercion():
    """Verify that when a criterion has >= 80% coverage, any record missing it is strictly excluded."""
    candidates = [
        {
            "product_name_raw": f"Laptop Valid {i}",
            "os_name": "Windows",
            "gpu_type": "discrete",
            "gpu_benchmark_time_spy": "8000",
            "cpu_benchmark_multi_core": "12000",
            "sale_price_vnd": "25000000",
            "ram_gb": "16",
            "storage_total_gb": "512",
            "refresh_rate_hz": "144",
        }
        for i in range(4)
    ]
    candidates.append({
        "product_name_raw": "Laptop Missing CPU Benchmark",
        "os_name": "Windows",
        "gpu_type": "discrete",
        "gpu_benchmark_time_spy": "8000",
        "cpu_benchmark_multi_core": "",  # Missing! (coverage = 4/5 = 80%)
        "sale_price_vnd": "25000000",
        "ram_gb": "16",
        "storage_total_gb": "512",
        "refresh_rate_hz": "144",
    })

    res = evaluate(candidates, preset_key="gaming", coverage_threshold=0.80)
    assert len(res["rankings"]) == 4
    assert len(res["dropped_criteria"]) == 0  # CPU benchmark was kept (80% >= 80%)

    # Missing machine must be explicitly recorded in excluded list with field name
    excluded_names = [e["product_name_raw"] for e in res["excluded"]]
    assert "Laptop Missing CPU Benchmark" in excluded_names
    ex_entry = next(e for e in res["excluded"] if e["product_name_raw"] == "Laptop Missing CPU Benchmark")
    assert "cpu_benchmark_multi_core" in ex_entry["reason"]


def test_budget_hard_filter():
    """Verify that max_budget_vnd strictly excludes expensive laptops before scoring."""
    candidates = [
        {
            "product_name_raw": "Laptop Cheap",
            "os_name": "Windows",
            "sale_price_vnd": "18000000",
            "cpu_benchmark_multi_core": "10000",
            "ram_gb": "16",
            "storage_total_gb": "512",
            "weight_kg": "1.5",
        },
        {
            "product_name_raw": "Laptop Over Budget",
            "os_name": "Windows",
            "sale_price_vnd": "30000000",
            "cpu_benchmark_multi_core": "14000",
            "ram_gb": "16",
            "storage_total_gb": "512",
            "weight_kg": "1.5",
        },
    ]

    res = evaluate(candidates, preset_key="coding", max_budget_vnd=25000000)
    assert len(res["rankings"]) == 1
    assert res["rankings"][0]["product_name_raw"] == "Laptop Cheap"
    ex_entry = next(e for e in res["excluded"] if e["product_name_raw"] == "Laptop Over Budget")
    assert "Vượt ngân sách tối đa" in ex_entry["reason"]


def test_d14_criterion_coverage_guard():
    """Verify that a criterion with coverage < 80% is dropped and weights re-normalized."""
    # 5 machines, only 2 have storage_total_gb (coverage = 2/5 = 40% < 80%)
    candidates = [
        {"product_name_raw": f"Lap {i}", "os_name": "Windows", "sale_price_vnd": "20000000",
         "cpu_benchmark_multi_core": "10000", "ram_gb": "16", "weight_kg": "1.5",
         "storage_total_gb": "512" if i < 2 else ""}
        for i in range(5)
    ]

    res = evaluate(candidates, preset_key="coding", coverage_threshold=0.80)
    dropped_names = [dc["criterion"] for dc in res["dropped_criteria"]]
    assert "storage_total_gb" in dropped_names

    # Remaining active criteria weights must still sum to 1.0
    active_weights = [w for _, _, w in res["active_criteria"]]
    assert abs(sum(active_weights) - 1.0) < 1e-4
    assert len(res["rankings"]) == 5  # No laptop excluded because storage was dropped!


def test_edge_cases_single_and_zero_candidate():
    """Verify safe behavior when candidate count is 0 or 1."""
    # 1. Zero candidate
    res_zero = evaluate([], preset_key="coding")
    assert res_zero["status"] == "no_suitable_laptop"
    assert res_zero["rankings"] == []
    assert "suggestion" in res_zero

    # 2. Single candidate
    cand_one = [{
        "product_name_raw": "Sole Survivor",
        "os_name": "Windows",
        "sale_price_vnd": "20000000",
        "cpu_benchmark_multi_core": "10000",
        "ram_gb": "16",
        "storage_total_gb": "512",
        "weight_kg": "1.5",
    }]
    res_one = evaluate(cand_one, preset_key="coding")
    assert res_one["status"] == "single_candidate"
    assert len(res_one["rankings"]) == 1
    assert res_one["rankings"][0]["rank"] == 1
    assert res_one["rankings"][0]["topsis_score"] == 1.0


def test_explainability_consistency():
    """Verify that top_advantage and top_penalty criterion names match best_j/worst_j."""
    candidates = [
        {
            "product_name_raw": "Laptop High GPU",
            "os_name": "Windows",
            "gpu_type": "discrete",
            "gpu_benchmark_time_spy": "12000",
            "cpu_benchmark_multi_core": "10000",
            "sale_price_vnd": "35000000",
            "ram_gb": "16",
            "storage_total_gb": "512",
            "refresh_rate_hz": "144",
        },
        {
            "product_name_raw": "Laptop Cheap Balanced",
            "os_name": "Windows",
            "gpu_type": "discrete",
            "gpu_benchmark_time_spy": "5000",
            "cpu_benchmark_multi_core": "10000",
            "sale_price_vnd": "18000000",
            "ram_gb": "16",
            "storage_total_gb": "512",
            "refresh_rate_hz": "144",
        },
    ]

    res = evaluate(candidates, preset_key="gaming")
    assert res["status"] == "success"

    # Laptop High GPU should have gpu_benchmark_time_spy as top_advantage
    high_gpu = next(r for r in res["rankings"] if r["product_name_raw"] == "Laptop High GPU")
    assert "gpu_benchmark_time_spy" in high_gpu["explanation"]["top_advantage"]
    assert "sale_price_vnd" in high_gpu["explanation"]["top_penalty"]

    # Laptop Cheap Balanced should have sale_price_vnd as top_advantage
    cheap = next(r for r in res["rankings"] if r["product_name_raw"] == "Laptop Cheap Balanced")
    assert "sale_price_vnd" in cheap["explanation"]["top_advantage"]
    assert "gpu_benchmark_time_spy" in cheap["explanation"]["top_penalty"]


def test_refresh_rate_filter_no_silent_default():
    """Verify that a missing refresh rate is strictly excluded when min_refresh_rate is specified."""
    candidates = [
        {
            "product_name_raw": "Laptop 144Hz",
            "os_name": "Windows",
            "sale_price_vnd": "20000000",
            "cpu_benchmark_multi_core": "10000",
            "ram_gb": "16",
            "storage_total_gb": "512",
            "weight_kg": "1.5",
            "refresh_rate_hz": "144",
        },
        {
            "product_name_raw": "Laptop Unlisted Hz",
            "os_name": "Windows",
            "sale_price_vnd": "20000000",
            "cpu_benchmark_multi_core": "10000",
            "ram_gb": "16",
            "storage_total_gb": "512",
            "weight_kg": "1.5",
            "refresh_rate_hz": "",  # Unlisted!
        },
    ]

    res = evaluate(candidates, preset_key="coding", min_refresh_rate_hz=120)
    assert len(res["rankings"]) == 1
    assert res["rankings"][0]["product_name_raw"] == "Laptop 144Hz"
    ex_unlisted = next(e for e in res["excluded"] if e["product_name_raw"] == "Laptop Unlisted Hz")
    assert "Thiếu thông tin tần số quét" in ex_unlisted["reason"]


def test_budget_sensitivity_usurper_detection():
    """Verify that Budget Sensitivity (§8.4) correctly detects when a pricier laptop usurps Top 1."""
    candidates = [
        {
            "source_product_id": "001",
            "product_name_raw": "Laptop Budget King",
            "os_name": "Windows",
            "gpu_type": "integrated",
            "sale_price_vnd": "18000000",
            "cpu_benchmark_multi_core": "10000",
            "cpu_benchmark_single_core": "2000",
            "ram_gb": "16",
            "storage_total_gb": "512",
            "weight_kg": "1.4",
        },
        {
            "source_product_id": "002",
            "product_name_raw": "Laptop Premium Over Budget",
            "os_name": "Windows",
            "gpu_type": "integrated",
            "sale_price_vnd": "22000000",
            "cpu_benchmark_multi_core": "16000",
            "cpu_benchmark_single_core": "2800",
            "ram_gb": "32",
            "storage_total_gb": "1024",
            "weight_kg": "1.2",
            "panel_type": "OLED",
        },
    ]

    sens = analyze_budget_sensitivity(
        candidates,
        preset_key="student_budget",
        current_max_budget=20_000_000,
        steps=[1_000_000, 3_000_000],
    )

    assert sens["baseline_top1"]["source_product_id"] == "001"
    # At +1M (21M budget): 002 is still over budget, 001 remains
    assert sens["scenarios"][0]["is_usurped"] is False
    assert sens["scenarios"][0]["new_top1"]["source_product_id"] == "001"

    # At +3M (23M budget): 002 becomes eligible and dominates
    assert sens["scenarios"][1]["is_usurped"] is True
    assert sens["scenarios"][1]["new_top1"]["source_product_id"] == "002"
    assert "CPU khỏe hơn" in sens["scenarios"][1]["upgrade_benefit"]


def test_weight_sensitivity_stability_score():
    """Verify that OAT Weight Sensitivity (§8.4) measures rank robustness under ±10%, ±20% variations."""
    candidates = [
        {
            "source_product_id": "001",
            "product_name_raw": "Laptop High Spec High Price",
            "os_name": "Windows",
            "gpu_type": "discrete",
            "gpu_benchmark_time_spy": "10000",
            "cpu_benchmark_multi_core": "14000",
            "sale_price_vnd": "35000000",
            "ram_gb": "32",
            "storage_total_gb": "1024",
            "refresh_rate_hz": "144",
        },
        {
            "source_product_id": "002",
            "product_name_raw": "Laptop Balanced",
            "os_name": "Windows",
            "gpu_type": "discrete",
            "gpu_benchmark_time_spy": "6000",
            "cpu_benchmark_multi_core": "10000",
            "sale_price_vnd": "22000000",
            "ram_gb": "16",
            "storage_total_gb": "512",
            "refresh_rate_hz": "144",
        },
    ]

    sens = analyze_weight_sensitivity(
        candidates,
        preset_key="gaming",
        variation_percentages=[-0.20, -0.10, 0.10, 0.20],
    )

    assert sens["status"] == "success"
    assert sens["stability_rate_percent"] >= 0.0
    assert len(sens["criteria_evaluations"]) == len(PRESETS["gaming"]["criteria"])
    for crit_eval in sens["criteria_evaluations"]:
        assert len(crit_eval["variations"]) == 4


def test_strict_benchmark_mode_d05_exclusion():
    """Verify that strict_benchmark=True strictly excludes laptops with approximate benchmarks (D05)."""
    candidates = [
        {
            "product_name_raw": "Laptop Exact Verified",
            "os_name": "Windows",
            "sale_price_vnd": "20000000",
            "cpu_benchmark_multi_core": "12000",
            "cpu_benchmark_match_level": "exact_sku",
            "ram_gb": "16",
            "storage_total_gb": "512",
            "weight_kg": "1.4",
        },
        {
            "product_name_raw": "Laptop Architecture Estimated",
            "os_name": "Windows",
            "sale_price_vnd": "20000000",
            "cpu_benchmark_multi_core": "13000",
            "cpu_benchmark_match_level": "approximate",
            "ram_gb": "16",
            "storage_total_gb": "512",
            "weight_kg": "1.4",
        },
    ]

    # Non-strict mode: both laptops ranked, approximate laptop gets warning
    res_normal = evaluate(candidates, preset_key="coding", strict_benchmark=False)
    assert len(res_normal["rankings"]) == 2
    approx_laptop = next(r for r in res_normal["rankings"] if r["product_name_raw"] == "Laptop Architecture Estimated")
    assert len(approx_laptop["explanation"]["warnings"]) > 0

    # Strict mode (D05): approximate laptop strictly excluded!
    res_strict = evaluate(candidates, preset_key="coding", strict_benchmark=True)
    assert len(res_strict["rankings"]) == 1
    assert res_strict["rankings"][0]["product_name_raw"] == "Laptop Exact Verified"
    assert len(res_strict["excluded"]) == 1
    assert "D05" in res_strict["excluded"][0]["reason"]


def test_custom_weights_validation():
    """Verify that invalid custom_weights (wrong length, negative, NaN, zero sum) are strictly rejected."""
    candidates = [
        {
            "product_name_raw": "Laptop Test",
            "os_name": "Windows",
            "sale_price_vnd": "20000000",
            "cpu_benchmark_multi_core": "12000",
            "ram_gb": "16",
            "storage_total_gb": "512",
            "weight_kg": "1.4",
        }
    ]

    import pytest

    # 1. Sai độ dài
    with pytest.raises(ValueError, match="không khớp với số tiêu chí"):
        evaluate(candidates, preset_key="coding", custom_weights=[0.5, 0.5])

    # 2. Chứa trọng số âm
    with pytest.raises(ValueError, match="Trọng số phải là số thực không âm"):
        evaluate(candidates, preset_key="coding", custom_weights=[-0.2, 0.3, 0.3, 0.3, 0.3])

    # 3. Chứa NaN
    with pytest.raises(ValueError, match="Trọng số phải là số thực không âm"):
        evaluate(candidates, preset_key="coding", custom_weights=[float("nan"), 0.25, 0.25, 0.25, 0.25])

    # 4. Tổng bằng 0
    with pytest.raises(ValueError, match="Tổng trọng số tùy chỉnh phải lớn hơn 0"):
        evaluate(candidates, preset_key="coding", custom_weights=[0.0, 0.0, 0.0, 0.0, 0.0])

    # 5. Hợp lệ: được chuẩn hóa tự động
    res = evaluate(candidates, preset_key="coding", custom_weights=[10, 20, 30, 20, 20])
    assert res["status"] in ("success", "single_candidate")
    assert abs(sum(w for _, _, w in res["active_criteria"]) - 1.0) < 1e-4


def test_minimum_ram_and_storage_are_engine_constraints():
    """Ngưỡng NLP phải còn hiệu lực khi gọi engine trực tiếp, không chỉ qua API."""
    candidates = [
        {"source_product_id": "low", "product_name_raw": "Low", "sale_price_vnd": "20000000", "ram_gb": "8", "storage_total_gb": "256", "cpu_benchmark_multi_core": "10000", "weight_kg": "1.5"},
        {"source_product_id": "high", "product_name_raw": "High", "sale_price_vnd": "21000000", "ram_gb": "16", "storage_total_gb": "512", "cpu_benchmark_multi_core": "11000", "weight_kg": "1.4"},
    ]

    res = evaluate(candidates, preset_key="coding", min_ram_gb=16, min_storage_gb=512)

    assert [item["source_product_id"] for item in res["rankings"]] == ["high"]
    assert any("RAM thấp hơn" in item["reason"] for item in res["excluded"])


if __name__ == "__main__":
    test_fit_function_boundary_points()
    test_ahp_reciprocity_and_consistency()
    test_synthetic_topsis_math()
    test_missing_data_strict_exclusion_no_zero_coercion()
    test_budget_hard_filter()
    test_d14_criterion_coverage_guard()
    test_edge_cases_single_and_zero_candidate()
    test_explainability_consistency()
    test_refresh_rate_filter_no_silent_default()
    test_budget_sensitivity_usurper_detection()
    test_weight_sensitivity_stability_score()
    test_strict_benchmark_mode_d05_exclusion()
    test_custom_weights_validation()
    print("All synthetic and rigorous DSS tests passed!")

