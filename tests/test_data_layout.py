"""Kiểm tra layout dữ liệu chạy chính thức và hai luồng DSS/ML."""

import csv
from pathlib import Path

from src.api import PredictPriceRequest, predict_price
from src.dss_ranking import STANDARDIZED_CSV, load_standardized_laptops


ROOT = Path(__file__).resolve().parents[1]


def test_runtime_uses_one_catalog_and_price_model_artifact():
    assert STANDARDIZED_CSV == ROOT / "data" / "catalog" / "laptops.csv"
    with STANDARDIZED_CSV.open(encoding="utf-8", newline="") as file:
        assert len(list(csv.DictReader(file))) == 513

    result = predict_price(PredictPriceRequest(
        cpu_benchmark_multi=12000,
        cpu_benchmark_single=2500,
        ram_gb=16,
        storage_total_gb=512,
        brand="Asus",
    ))
    assert result["lower_bound_95_vnd"] < result["predicted_price_vnd"] < result["upper_bound_95_vnd"]
    assert len(load_standardized_laptops()) == 513


def test_catalog_cache_returns_caller_owned_rows():
    first = load_standardized_laptops()
    original_name = first[0]["product_name_raw"]
    first[0]["product_name_raw"] = "mutated only in this caller"
    assert load_standardized_laptops()[0]["product_name_raw"] == original_name


