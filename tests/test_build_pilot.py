"""Kiểm thử chuẩn hóa và mức đầy đủ dữ liệu pilot FPT Shop."""

import sys
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from legacy.build_pilot import normalize, main as build_pilot_main
from legacy.audit_pilot_completeness import present
from report_criteria_readiness import main as readiness_main


def test_normalize_fpt_sample():
    record = normalize({
        "source": "FPT Shop",
        "prices": {"sale_price_vnd": "22.990.000đ"},
        "specifications": {
            "Hãng CPU": "Intel", "Công nghệ CPU": "Core 5", "Loại CPU": "120U",
            "Dung lượng RAM": "16 GB", "Ổ cứng": "SSD PCIe 512GB", "Pin": "3 Cell 41Wh",
            "Độ mỏng": "1.57 cm", "Tên đầy đủ (Card onboard)": "Intel Graphics"
        },
    })
    assert record["sale_price_vnd"] == "22990000"
    assert record["cpu_name_normalized"] == "Intel Core 5 120U"
    assert record["storage_primary_type"] == "NVME_SSD"
    assert record["battery_capacity_wh"] == "41"
    assert record["thickness_mm"] == "15.7"
    assert record["gpu_type"] == "integrated"


def test_raw_seller_fields_and_full_export(tmp_path):
    raw_file = ROOT / "data" / "raw" / "fpt_shop" / "msi_cyborg_15_b13wfkg_658vn.json"
    if raw_file.exists():
        msi_raw = json.loads(raw_file.read_text(encoding="utf-8"))
        assert msi_raw["specifications"]["Chất liệu"] == "Nhựa; Kim loại"
        assert msi_raw["specifications"]["Số khe RAM còn lại"] == "1"

    full_output = tmp_path / "fpt_shop_pilot_full.csv"
    build_pilot_main(tmp_path / "fpt_shop_pilot.csv", full_output)
    with full_output.open(encoding="utf-8", newline="") as file:
        full_rows = list(csv.DictReader(file))
    assert len(full_rows) == 10
    assert "Công nghệ đèn bàn phím" in full_rows[0]
    msi_full = next(row for row in full_rows if row["source_product_id"] == "00923911")
    assert msi_full["Chất liệu"] == "Nhựa; Kim loại"


def test_audit_field_presence():
    assert present({"prices": {"sale_price_vnd": "1đ"}}, ("prices.sale_price_vnd",))
    assert not present({"specifications": {}}, ("Wi-Fi", "Wifi"))
    assert present({"specifications": {"Wifi": "Wifi 6"}}, ("Wi-Fi", "Wifi"))


def test_criteria_readiness_report(tmp_path):
    output = tmp_path / "fpt_shop_criteria_readiness.csv"
    readiness_main(output)
    with output.open(encoding="utf-8", newline="") as file:
        readiness_rows = list(csv.DictReader(file))
    assert len(readiness_rows) == 16
    assert next(row for row in readiness_rows if row["criterion"] == "Tần số quét")["decision"] == "display_only"
