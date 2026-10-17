"""Tạo CSV pilot chuẩn hóa từ JSON sản phẩm FPT Shop thô."""

import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = ROOT / "data" / "raw" / "fpt_shop"
OUTPUT = ROOT / "data" / "archive" / "legacy" / "fpt_shop_pilot.csv"
FULL_OUTPUT = ROOT / "data" / "archive" / "legacy" / "fpt_shop_pilot_full.csv"

FIELDS = [
    "source", "source_product_id", "product_name_raw", "source_url", "collected_at", "currency",
    "listed_price_vnd", "sale_price_vnd", "special_price_vnd", "cpu_name_normalized", "cpu_cores",
    "cpu_threads", "cpu_base_ghz", "cpu_boost_ghz", "gpu_name_normalized", "gpu_type", "gpu_vram_gb",
    "ram_gb", "ram_type", "ram_slots", "ram_slots_free", "max_ram_gb", "storage_total_gb",
    "storage_primary_type", "screen_size_inch", "screen_width_px", "screen_height_px", "panel_type",
    "refresh_rate_hz", "brightness_nits", "color_gamut_raw", "battery_capacity_wh", "battery_cells",
    "charger_w", "weight_kg", "thickness_mm", "dimensions_raw", "material_raw", "color_raw", "usb_a_count", "usb_c_count", "hdmi_present",
    "hdmi_version", "lan_present", "audio_jack_present", "wifi_raw", "bluetooth_raw", "webcam_raw",
    "os_name", "warranty_months",
]


def number(value, pattern):
    match = re.search(pattern, value or "", re.I)
    return match.group(1).replace(",", ".") if match else ""


def price(value):
    return re.sub(r"\D", "", value or "")


def spec(specs, label):
    return specs.get(label, "")


def first_spec(specs, *labels):
    return next((spec(specs, label) for label in labels if spec(specs, label)), "")


def normalize(raw):
    specs = raw.get("specifications", {})
    cpu_vendor = spec(specs, "Hãng CPU")
    cpu_tech = spec(specs, "Công nghệ CPU")
    cpu_type = spec(specs, "Loại CPU")
    gpu = first_spec(specs, "GPU", "Tên đầy đủ (Card rời)", "Tên đầy đủ (Card onboard)", "Tên đầy đủ (Card onbroad)")
    storage = first_spec(specs, "Ổ cứng", "Dung lượng SSD")
    screen = spec(specs, "Độ phân giải")
    cg = first_spec(specs, "Cổng giao tiếp", "Cổng kết nối")
    match_a = re.search(r"(\d+)\s*(?:cổng\s*)?USB[^;]*Type-A", cg, re.I)
    match_c = re.search(r"(\d+)\s*(?:cổng\s*)?(?:USB[^;]*Type-?\s*C|Thunderbolt)", cg, re.I)
    usb_a_count = match_a.group(1) if match_a else number(spec(specs, "USB-A"), r"(\d+)")
    usb_c_count = match_c.group(1) if match_c else number(spec(specs, "USB-C"), r"(\d+)")
    hdmi_present = "true" if re.search(r"HDMI", cg or spec(specs, "HDMI"), re.I) else ""
    hdmi_version = number(cg or spec(specs, "HDMI"), r"HDMI\s*([\d.]+[a-z]?)")
    lan_present = "true" if re.search(r"RJ45|LAN|Ethernet", cg or spec(specs, "LAN"), re.I) else ""
    audio_jack = "true" if re.search(r"Jack|3\.5|headphone", cg or first_spec(specs, "Jack tai nghe", "Jack 3.5 mm"), re.I) else ""

    row = {field: "" for field in FIELDS}
    row.update({
        "source": raw.get("source", ""),
        "source_product_id": raw.get("source_product_id", ""),
        "product_name_raw": raw.get("product_name_raw", ""),
        "source_url": raw.get("source_url", ""),
        "collected_at": raw.get("collected_at", ""),
        "currency": "VND",
        "listed_price_vnd": price(raw.get("prices", {}).get("listed_price_vnd")),
        "sale_price_vnd": price(raw.get("prices", {}).get("sale_price_vnd")),
        "special_price_vnd": price(raw.get("prices", {}).get("special_price_vnd")),
        "cpu_name_normalized": " ".join(x for x in (cpu_vendor, cpu_tech, cpu_type) if x),
        "cpu_cores": number(first_spec(specs, "Số nhân", "Số nhân / luồng"), r"(\d+)") or number(spec(specs, "Loại CPU"), r"(\d+)-Core"),
        "cpu_threads": number(spec(specs, "Số luồng"), r"(\d+)") or number(spec(specs, "Số nhân / luồng"), r"(\d+)\s*luồng"),
        "cpu_base_ghz": number(spec(specs, "Tốc độ CPU tối thiểu"), r"([\d.,]+)"),
        "cpu_boost_ghz": number(spec(specs, "Tốc độ tối đa"), r"([\d.,]+)"),
        "gpu_name_normalized": gpu,
        "gpu_type": "discrete" if re.search(r"nvidia|geforce|rtx|radeon rx", gpu, re.I) else "integrated" if gpu else "",
        "gpu_vram_gb": number(first_spec(specs, "Bộ nhớ", "Dung lượng VRAM"), r"(\d+)\s*GB") or number(gpu, r"(\d+)\s*GB"),
        "ram_gb": number(spec(specs, "Dung lượng RAM"), r"(\d+)\s*GB"),
        "ram_type": spec(specs, "Loại RAM"),
        "ram_slots": number(spec(specs, "Số khe cắm rời"), r"(\d+)"),
        "ram_slots_free": number(spec(specs, "Số khe RAM còn lại"), r"(\d+)"),
        "max_ram_gb": number(spec(specs, "Hỗ trợ RAM tối đa"), r"(\d+)\s*GB"),
        "storage_total_gb": number(storage, r"(\d+)\s*GB") or str(int(number(storage, r"(\d+)\s*TB")) * 1024) if number(storage, r"(\d+)\s*GB") or number(storage, r"(\d+)\s*TB") else "",
        "storage_primary_type": "NVME_SSD" if re.search(r"pcie|nvme", storage, re.I) else "SSD" if "SSD" in storage.upper() else "",
        "screen_size_inch": number(spec(specs, "Kích thước màn hình"), r"([\d.,]+)"),
        "screen_width_px": number(screen, r"(\d+)\s*[x×]"),
        "screen_height_px": number(screen, r"[x×]\s*(\d+)"),
        "panel_type": re.search(r"IPS|OLED|SVA|VA|TN", spec(specs, "Tấm nền"), re.I).group(0).upper() if re.search(r"IPS|OLED|SVA|VA|TN", spec(specs, "Tấm nền"), re.I) else "",
        "refresh_rate_hz": number(spec(specs, "Tần số quét"), r"([1-9]\d{1,2})"),
        "brightness_nits": number(spec(specs, "Độ sáng"), r"(\d+)\s*nits?"),
        "color_gamut_raw": first_spec(specs, "Dải màu", "Độ phủ màu"),
        "battery_capacity_wh": number(first_spec(specs, "Pin", "Dung lượng pin"), r"([\d.,]+)\s*Wh"),
        "battery_cells": number(first_spec(specs, "Pin", "Loại PIN"), r"(\d+)\s*(?:Cell|viên)"),
        "charger_w": number(spec(specs, "Sạc"), r"(\d+)\s*W"),
        "weight_kg": number(first_spec(specs, "Trọng lượng", "Trọng lượng sản phẩm"), r"([\d.,]+)\s*kg") or (str(float(number(first_spec(specs, "Trọng lượng", "Trọng lượng sản phẩm"), r"(\d+)\s*g")) / 1000) if number(first_spec(specs, "Trọng lượng", "Trọng lượng sản phẩm"), r"(\d+)\s*g") else ""),
        "thickness_mm": format(float(number(spec(specs, "Độ mỏng"), r"([\d.,]+)")) * 10, "g") if spec(specs, "Độ mỏng") else "",
        "dimensions_raw": first_spec(specs, "Kích thước", "Kích thước sản phẩm"),
        "material_raw": spec(specs, "Chất liệu"),
        "color_raw": first_spec(specs, "Màu sắc", "Màu"),
        "usb_a_count": usb_a_count,
        "usb_c_count": usb_c_count,
        "hdmi_present": hdmi_present,
        "hdmi_version": hdmi_version,
        "lan_present": lan_present,
        "audio_jack_present": audio_jack,
        "wifi_raw": first_spec(specs, "Wi-Fi", "Wifi"),
        "bluetooth_raw": spec(specs, "Bluetooth"),
        "webcam_raw": spec(specs, "Webcam"),
        "os_name": first_spec(specs, "Hệ điều hành", "OS", "Version"),
        "warranty_months": number(first_spec(specs, "Bảo hành", "Thời gian bảo hành theo chính sách hãng"), r"(\d+)\s*tháng"),
    })
    return row


def main():
    raw_records = [json.loads(path.read_text(encoding="utf-8")) for path in sorted(RAW_DIR.glob("*.json"))]
    records = [normalize(raw) for raw in raw_records]
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(records)

    # A wide, auditable view: every label displayed by the seller is its own
    # column. This preserves details before we decide which fields become
    # comparison criteria.
    raw_spec_fields = sorted({
        label for raw in raw_records for label in raw.get("specifications", {})
    })
    full_fields = [
        "source", "source_product_id", "product_name_raw", "source_url", "collected_at",
        "listed_price_vnd", "sale_price_vnd", "special_price_vnd",
        *raw_spec_fields,
    ]
    full_records = []
    for raw in raw_records:
        full_records.append({
            "source": raw.get("source", ""),
            "source_product_id": raw.get("source_product_id", ""),
            "product_name_raw": raw.get("product_name_raw", ""),
            "source_url": raw.get("source_url", ""),
            "collected_at": raw.get("collected_at", ""),
            "listed_price_vnd": price(raw.get("prices", {}).get("listed_price_vnd")),
            "sale_price_vnd": price(raw.get("prices", {}).get("sale_price_vnd")),
            "special_price_vnd": price(raw.get("prices", {}).get("special_price_vnd")),
            **raw.get("specifications", {}),
        })
    with FULL_OUTPUT.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=full_fields)
        writer.writeheader()
        writer.writerows(full_records)
    print(f"Wrote {len(records)} record(s) to {OUTPUT.relative_to(ROOT)} and {FULL_OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
