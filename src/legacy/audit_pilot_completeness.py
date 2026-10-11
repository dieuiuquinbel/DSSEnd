"""Kiểm tra bản ghi pilot còn thiếu thông số cần bổ sung."""

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = ROOT / "data" / "raw" / "fpt_shop"
OUTPUT = ROOT / "data" / "processed" / "fpt_shop_completeness_audit.csv"

CORE = {
    "price": ("prices.sale_price_vnd",),
    "cpu": ("Hãng CPU", "Loại CPU"),
    "ram": ("Dung lượng RAM",),
    "storage": ("Dung lượng SSD", "Ổ cứng", "Kiểu ổ cứng"),
    "screen": ("Kích thước màn hình", "Độ phân giải"),
    "weight": ("Trọng lượng", "Trọng lượng sản phẩm"),
    "os": ("Hệ điều hành", "OS", "Version"),
    "warranty": ("Bảo hành", "Thời gian bảo hành theo chính sách hãng"),
}
SUPPLEMENTAL = {
    "ram_upgrade": ("Số khe cắm rời", "Số khe RAM còn lại", "Hỗ trợ RAM tối đa"),
    "battery": ("Pin", "Dung lượng pin"),
    "ports": ("Cổng giao tiếp", "USB-A", "USB-C"),
    "connectivity": ("Wi-Fi", "Wifi", "Bluetooth"),
    "webcam": ("Webcam",),
}


def present(raw, labels):
    specs = raw.get("specifications", {})
    if labels == ("prices.sale_price_vnd",):
        return bool(raw.get("prices", {}).get("sale_price_vnd"))
    return any(specs.get(label, "").strip() for label in labels)


def main():
    rows = []
    for path in sorted(RAW_DIR.glob("*.json")):
        raw = json.loads(path.read_text(encoding="utf-8"))
        row = {"source_product_id": raw.get("source_product_id", ""), "product_name_raw": raw.get("product_name_raw", "")}
        for name, labels in CORE.items():
            row[f"core_{name}"] = "present" if present(raw, labels) else "missing"
        for name, labels in SUPPLEMENTAL.items():
            row[f"supplemental_{name}"] = "present" if present(raw, labels) else "missing"
        missing = [name for name, labels in CORE.items() if not present(raw, labels)]
        row["core_complete"] = "yes" if not missing else "no"
        row["core_missing_fields"] = "; ".join(missing)
        rows.append(row)
    with OUTPUT.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {len(rows)} record(s) to {OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
