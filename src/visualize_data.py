"""Sinh biểu đồ EDA tái lập từ catalog chuẩn hóa.

Chạy: python -X utf8 -m src.visualize_data
Đầu ra: data/reports/figures/*.png
"""

import csv
import json
from collections import Counter
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # Chạy được trên máy không có giao diện đồ họa.
import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "data" / "catalog" / "laptops.csv"
METRICS = ROOT / "data" / "artifacts" / "price_model_metrics.json"
OUTPUT_DIR = ROOT / "data" / "reports" / "figures"


def number(row, field):
    try:
        return float(row[field])
    except (KeyError, TypeError, ValueError):
        return None


def brand(name):
    name = (name or "").lower()
    for needle, label in (("apple", "Apple"), ("macbook", "Apple"), ("lenovo", "Lenovo"),
                          ("asus", "Asus"), ("acer", "Acer"), ("msi", "MSI"),
                          ("dell", "Dell"), ("hp ", "HP"), ("gigabyte", "Gigabyte")):
        if needle in name:
            return label
    return "Khác"


def save(fig, filename):
    path = OUTPUT_DIR / filename
    fig.tight_layout()
    fig.savefig(path, dpi=160, bbox_inches="tight")
    plt.close(fig)
    return path


def generate_figures():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    with CATALOG.open(encoding="utf-8-sig", newline="") as source:
        rows = list(csv.DictReader(source))
    if not rows:
        raise ValueError("Catalog rỗng, không thể trực quan hóa.")

    paths = []
    prices_million = [number(row, "sale_price_vnd") / 1_000_000 for row in rows if number(row, "sale_price_vnd")]
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.hist(prices_million, bins=24, color="#2563eb", edgecolor="white")
    ax.set(title="Phân phối giá bán laptop", xlabel="Giá bán (triệu VNĐ)", ylabel="Số laptop")
    paths.append(save(fig, "01_price_distribution.png"))

    counts = Counter(brand(row.get("product_name_raw")) for row in rows)
    labels, values = zip(*counts.most_common())
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.bar(labels, values, color="#0f766e")
    ax.set(title="Phân bổ thương hiệu trong catalog", ylabel="Số laptop")
    ax.tick_params(axis="x", rotation=30)
    paths.append(save(fig, "02_brand_distribution.png"))

    pairs = [(number(row, "cpu_benchmark_multi_core"), number(row, "sale_price_vnd") / 1_000_000)
             for row in rows if number(row, "cpu_benchmark_multi_core") and number(row, "sale_price_vnd")]
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.scatter(*zip(*pairs), s=18, alpha=0.55, color="#7c3aed")
    ax.set(title="Giá bán và hiệu năng CPU đa nhân", xlabel="Geekbench 6 Multi-Core", ylabel="Giá bán (triệu VNĐ)")
    paths.append(save(fig, "03_price_vs_cpu.png"))

    fields = ["ram_gb", "storage_total_gb", "weight_kg", "refresh_rate_hz", "brightness_nits", "ram_slots"]
    coverage = [sum(bool(row.get(field, "").strip()) for row in rows) * 100 / len(rows) for field in fields]
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.barh(fields, coverage, color=["#16a34a" if value >= 80 else "#f59e0b" for value in coverage])
    ax.axvline(80, color="#dc2626", linestyle="--", label="Ngưỡng D14: 80%")
    ax.set(title="Độ phủ các trường dữ liệu", xlabel="Độ phủ (%)", xlim=(0, 100))
    ax.legend(loc="lower right")
    paths.append(save(fig, "04_field_coverage.png"))

    if METRICS.exists():
        metrics = json.loads(METRICS.read_text(encoding="utf-8"))
        candidates = metrics.get("models_cv", metrics.get("model_metrics", metrics.get("models", {})))
        scores = [
            (name, value.get("r2_mean", value.get("r2")))
            for name, value in candidates.items()
            if isinstance(value, dict) and isinstance(value.get("r2_mean", value.get("r2")), (int, float))
        ]
        if scores:
            labels, values = zip(*scores)
            fig, ax = plt.subplots(figsize=(9, 4.5))
            ax.bar(labels, values, color="#db2777")
            ax.set(title="So sánh R² của các mô hình giá", ylabel="R²", ylim=(min(-0.1, min(values) - 0.05), 1))
            ax.tick_params(axis="x", rotation=35)
            paths.append(save(fig, "05_model_comparison_r2.png"))

    if len(paths) < 4:
        raise AssertionError("Phải sinh ít nhất 4 biểu đồ EDA.")
    print("Generated figures:")
    for path in paths:
        print(path.relative_to(ROOT))
    return paths


if __name__ == "__main__":
    generate_figures()
