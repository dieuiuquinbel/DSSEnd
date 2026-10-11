"""Báo cáo các trường pilot đủ điều kiện dùng trong DSS V1.

Only a feature with at least 80% observed coverage may enter a score.  A
feature can still be useful as a displayed fact or a user filter.
"""

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "data" / "processed" / "fpt_shop_pilot.csv"
OUTPUT = ROOT / "data" / "processed" / "fpt_shop_criteria_readiness.csv"
THRESHOLD = 80.0

CRITERIA = (
    ("Giá bán", "sale_price_vnd", "cost", "score_v1", "Đủ dữ liệu; tiêu chí chi phí."),
    ("Dung lượng RAM", "ram_gb", "benefit", "score_v1", "Đủ dữ liệu; phản ánh cấu hình hiện có."),
    ("Dung lượng lưu trữ", "storage_total_gb", "benefit", "score_v1", "Đủ dữ liệu; phản ánh dung lượng hiện có."),
    ("Trọng lượng", "weight_kg", "cost", "score_v1", "Đủ dữ liệu; dùng cho nhu cầu di động."),
    ("Kích thước màn hình", "screen_size_inch", "fit", "filter", "Đủ dữ liệu nhưng là sở thích, không có hướng tốt/xấu chung."),
    ("Hệ điều hành", "os_name", "fit", "filter", "Đủ dữ liệu nhưng là ràng buộc tương thích, không cộng điểm."),
    ("Bảo hành", "warranty_months", "benefit", "score_v1", "Đủ dữ liệu; phải cho người dùng bật/tắt trong preset."),
    ("RAM có thể nâng cấp", "max_ram_gb;ram_slots_free", "benefit", "filter", "Dung lượng tối đa đủ, nhưng số khe trống chưa đủ coverage để chấm điểm công bằng."),
    ("Tần số quét", "refresh_rate_hz", "benefit", "display_only", "Coverage chưa đạt 80%; chỉ hiển thị/lọc thô."),
    ("Độ sáng", "brightness_nits", "benefit", "score_v1", "Đủ ngưỡng coverage; chỉ bật trong preset ưu tiên màn hình."),
    ("Màu màn hình", "color_gamut_raw", "benefit", "display_only", "Dù đủ dữ liệu, %NTSC, sRGB và DCI-P3 không cùng thang để cộng điểm trực tiếp."),
    ("Dung lượng pin", "battery_capacity_wh", "benefit", "display_only", "Thông số Wh không thay thế thời lượng dùng thực tế."),
    ("Cổng kết nối", "usb_a_count;usb_c_count;hdmi_present", "fit", "filter", "Dùng để lọc theo cổng bắt buộc; không cộng thành một điểm chung."),
    ("Wi-Fi/Bluetooth", "wifi_raw;bluetooth_raw", "fit", "display_only", "Dữ liệu có nhưng chủ yếu để mô tả tương thích."),
    ("Hiệu năng CPU", "cpu_name_normalized", "benefit", "blocked", "Đã có tên CPU, còn thiếu benchmark chuẩn theo từng CPU."),
    ("Hiệu năng GPU", "gpu_name_normalized", "benefit", "blocked", "Đã có tên GPU, còn thiếu benchmark/TGP chuẩn theo từng máy."),
)


def coverage(rows, fields):
    return min(
        sum(bool(row.get(field, "").strip()) for row in rows) * 100 / len(rows)
        for field in fields
    )


def main():
    with INPUT.open(encoding="utf-8", newline="") as file:
        products = list(csv.DictReader(file))

    rows = []
    for criterion, field_text, direction, initial_action, rationale in CRITERIA:
        fields = field_text.split(";")
        value = round(coverage(products, fields), 1)
        action = initial_action
        if action == "score_v1" and value < THRESHOLD:
            action = "display_only"
        rows.append({
            "criterion": criterion,
            "normalized_fields": field_text,
            "coverage_percent": value,
            "threshold_percent": THRESHOLD,
            "direction": direction,
            "decision": action,
            "reason": rationale,
        })

    with OUTPUT.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {len(rows)} criterion decision(s) to {OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
