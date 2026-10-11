"""Kiểm thử các bộ lọc tối thiểu và loại trừ dùng chung cho API LaptopDSS."""

from types import SimpleNamespace

from src.api import apply_catalog_filters


def test_minimum_memory_storage_and_excluded_brand_filters():
    rows = [
        {"product_name_raw": "ASUS A", "ram_gb": "16", "storage_total_gb": "512"},
        {"product_name_raw": "ASUS B", "ram_gb": "32", "storage_total_gb": "1024"},
        {"product_name_raw": "Apple C", "ram_gb": "32", "storage_total_gb": "1024"},
    ]
    req = SimpleNamespace(brand=None, cpu_family=None, ram_gb=None, min_ram_gb=16, storage_gb=None, min_storage_gb=512, excluded_brands=["Apple"], screen_size=None, panel_type=None, min_brightness_nits=None, require_rj45_lan=None, require_ram_upgradeable=None, require_type_c_charging=None, require_thunderbolt=None)
    assert [row["product_name_raw"] for row in apply_catalog_filters(rows, req)] == ["ASUS A", "ASUS B"]
