"""Ghép benchmark Geekbench 6 và 3DMark Time Spy vào catalog chuẩn hóa."""

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BENCHMARKS_CSV = ROOT / "data" / "processed" / "benchmarks.csv"
PILOT_CSV = ROOT / "data" / "processed" / "fpt_shop_pilot.csv"
STANDARDIZED_OUTPUT = ROOT / "data" / "processed" / "fpt_shop_pilot_standardized.csv"


def load_benchmarks(benchmarks_path: Path = BENCHMARKS_CSV):
    """Load CPU and GPU benchmarks index from CSV."""
    cpu_benchmarks = {}
    gpu_benchmarks = {}

    if not benchmarks_path.exists():
        return cpu_benchmarks, gpu_benchmarks

    with benchmarks_path.open(encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)
        for row in reader:
            comp_type = row.get("component_type", "").strip().upper()
            comp_name = row.get("component_name", "").strip()
            bench_name = row.get("benchmark_name", "").strip()
            score_str = row.get("score", "").strip()
            score = float(score_str) if score_str else None

            entry = {
                "benchmark_name": bench_name,
                "score": score,
                "source_url": row.get("source_url", "").strip(),
                "sample_count": row.get("sample_count", "").strip(),
                "match_level": row.get("match_level", "").strip(),
                "note": row.get("note", "").strip(),
            }

            if comp_type == "CPU":
                if comp_name not in cpu_benchmarks:
                    cpu_benchmarks[comp_name] = {}
                cpu_benchmarks[comp_name][bench_name] = entry
            elif comp_type == "GPU":
                if comp_name not in gpu_benchmarks:
                    gpu_benchmarks[comp_name] = {}
                gpu_benchmarks[comp_name][bench_name] = entry

    return cpu_benchmarks, gpu_benchmarks


def match_cpu(cpu_name: str, cpu_benchmarks: dict):
    """Find Geekbench 6 Multi-Core and Single-Core scores for CPU."""
    if not cpu_name or cpu_name not in cpu_benchmarks:
        return None, None, None, None

    entries = cpu_benchmarks[cpu_name]
    multi = entries.get("Geekbench 6 Multi-Core", {})
    single = entries.get("Geekbench 6 Single-Core", {})

    multi_score = multi.get("score")
    single_score = single.get("score")
    url = multi.get("source_url") or single.get("source_url")
    match_level = multi.get("match_level") or single.get("match_level")

    return multi_score, single_score, url, match_level


def match_gpu(gpu_name: str, gpu_type: str, os_name: str, gpu_benchmarks: dict):
    """Find 3DMark Time Spy Graphics score for Windows laptops with discrete GPU only.
    
    Apple and Qualcomm iGPUs are strictly excluded and will return None.
    """
    if os_name != "Windows" or gpu_type != "discrete" or not gpu_name:
        return None, None, None

    if gpu_name not in gpu_benchmarks:
        return None, None, None

    entries = gpu_benchmarks[gpu_name]
    ts = entries.get("3DMark Time Spy Graphics", {})
    return ts.get("score"), ts.get("source_url"), ts.get("match_level")


def enrich_and_standardize_pilot(
    input_csv: Path = PILOT_CSV,
    benchmarks_csv: Path = BENCHMARKS_CSV,
    output_csv: Path = STANDARDIZED_OUTPUT,
):
    """Produce standardized dataset with typed numeric fields and benchmark scores."""
    cpu_benchmarks, gpu_benchmarks = load_benchmarks(benchmarks_csv)

    with input_csv.open(encoding="utf-8", newline="") as file:
        rows = list(csv.DictReader(file))

    enriched_rows = []
    for row in rows:
        out = dict(row)

        # 1. Benchmark Matching
        cpu_multi, cpu_single, cpu_url, cpu_match = match_cpu(
            row.get("cpu_name_normalized", ""), cpu_benchmarks
        )
        gpu_ts, gpu_url, gpu_match = match_gpu(
            row.get("gpu_name_normalized", ""),
            row.get("gpu_type", ""),
            row.get("os_name", ""),
            gpu_benchmarks,
        )

        out["cpu_benchmark_multi_core"] = str(int(cpu_multi)) if cpu_multi is not None else ""
        out["cpu_benchmark_single_core"] = str(int(cpu_single)) if cpu_single is not None else ""
        out["cpu_benchmark_source_url"] = cpu_url or ""
        out["cpu_benchmark_match_level"] = cpu_match or ""

        out["gpu_benchmark_time_spy"] = str(int(gpu_ts)) if gpu_ts is not None else ""
        out["gpu_benchmark_source_url"] = gpu_url or ""
        out["gpu_benchmark_match_level"] = gpu_match or ""

        # Gaming eligibility: Windows + discrete GPU + valid Time Spy score
        is_gaming = (
            row.get("os_name") == "Windows"
            and row.get("gpu_type") == "discrete"
            and gpu_ts is not None
        )
        out["is_gaming_eligible"] = "true" if is_gaming else "false"

        enriched_rows.append(out)

    fieldnames = list(rows[0].keys()) + [
        "cpu_benchmark_multi_core",
        "cpu_benchmark_single_core",
        "cpu_benchmark_source_url",
        "cpu_benchmark_match_level",
        "gpu_benchmark_time_spy",
        "gpu_benchmark_source_url",
        "gpu_benchmark_match_level",
        "is_gaming_eligible",
    ]

    output_csv.parent.mkdir(parents=True, exist_ok=True)
    with output_csv.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(enriched_rows)

    return enriched_rows


if __name__ == "__main__":
    enriched = enrich_and_standardize_pilot()
    print(f"Enriched and wrote {len(enriched)} records successfully.")
