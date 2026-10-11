"""Kiểm thử schema benchmark và quy tắc ghép dữ liệu hiệu năng."""

import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from legacy.benchmark_matching import load_benchmarks, enrich_and_standardize_pilot, BENCHMARKS_CSV, STANDARDIZED_OUTPUT


def test_benchmarks_schema_and_rules():
    assert BENCHMARKS_CSV.exists(), "benchmarks.csv must exist"
    with BENCHMARKS_CSV.open(encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)
        rows = list(reader)

    expected_cols = [
        "component_type", "component_name", "benchmark_name",
        "score", "source_url", "sample_count", "match_level", "note"
    ]
    assert reader.fieldnames == expected_cols

    for row in rows:
        comp_type = row["component_type"]
        bench_name = row["benchmark_name"]
        match_level = row["match_level"]

        assert comp_type in ("CPU", "GPU")
        if comp_type == "CPU":
            assert bench_name in ("Geekbench 6 Multi-Core", "Geekbench 6 Single-Core"), (
                f"CPU benchmark must only be Geekbench 6, found {bench_name}"
            )
            assert match_level in ("chip_only", "approximate", "unreleased_hardware", "unavailable")
        elif comp_type == "GPU":
            assert bench_name == "3DMark Time Spy Graphics", (
                f"GPU benchmark must only be 3DMark Time Spy Graphics, found {bench_name}"
            )
            assert match_level in ("exact_laptop_or_tgp", "approximate", "chip_only", "unavailable")
            # GPU rows with verified data must have positive score
            if match_level != "unavailable":
                assert float(row["score"]) > 0
            else:
                assert row["score"] == "", "unavailable GPU must have blank score"


def test_standardized_pilot_gaming_filter_and_matching():
    enriched = enrich_and_standardize_pilot()
    assert len(enriched) == 10

    for row in enriched:
        os_name = row["os_name"]
        gpu_type = row["gpu_type"]
        is_gaming = row["is_gaming_eligible"] == "true"
        gpu_ts = row["gpu_benchmark_time_spy"]

        # Mac and Snapdragon must NEVER be eligible for discrete Windows gaming
        if os_name == "macOS" or "Snapdragon" in row["cpu_name_normalized"]:
            assert not is_gaming, f"{row['product_name_raw']} must not be gaming eligible"
            assert gpu_ts == "", "Mac and Snapdragon must not have 3DMark Time Spy scores"

        # Integrated GPUs must never have 3DMark Time Spy score
        if gpu_type == "integrated":
            assert not is_gaming
            assert gpu_ts == ""

        # Discrete Windows gaming laptops must have positive Time Spy score
        if os_name == "Windows" and gpu_type == "discrete":
            assert is_gaming
            assert float(gpu_ts) >= 4000

        # Unreleased hardware must not fabricate scores
        if "M5" in row["cpu_name_normalized"] or "A18 Pro" in row["cpu_name_normalized"]:
            assert row["cpu_benchmark_multi_core"] == ""
            assert row["cpu_benchmark_match_level"] == "unreleased_hardware"

        # Verified matched benchmark CPUs
        if "Ryzen 7 155" in row["cpu_name_normalized"]:
            assert float(row["cpu_benchmark_multi_core"]) > 9000
            assert row["cpu_benchmark_match_level"] == "approximate"
        if "Snapdragon" in row["cpu_name_normalized"]:
            assert float(row["cpu_benchmark_multi_core"]) > 9000
            assert row["cpu_benchmark_match_level"] == "chip_only"


if __name__ == "__main__":
    test_benchmarks_schema_and_rules()
    test_standardized_pilot_gaming_filter_and_matching()
    print("All benchmark tests passed!")
