"""Lập báo cáo mức sẵn sàng tiêu chí học thuật cho LaptopDSS.

Evaluates coverage and readiness of all 18 criteria across the unified 110-laptop dataset.
Adheres strictly to DECISIONS.md D14, Data.md, and Chuongtrinh.md.
Outputs:
- data/processed/criteria_readiness.csv
"""

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
UNIFIED_CSV = ROOT / "data" / "processed" / "laptops_standardized.csv"
OUT_CSV = ROOT / "data" / "processed" / "criteria_readiness.csv"

# 18 Standard Criteria according to Data.md and Chuongtrinh.md
CRITERIA_METADATA = [
    {
        "code": "C01",
        "name_vi": "Giá bán hiện tại (sale_price_vnd)",
        "field": "sale_price_vnd",
        "nature": "cost",
        "d14_role": "core_topsis",
        "status_v1": "ready_score",
        "note": "Ràng buộc ngân sách và tiêu chí cost cốt lõi trong toàn bộ preset.",
    },
    {
        "code": "C02",
        "name_vi": "Hiệu năng CPU đa nhân (cpu_benchmark_multi_core)",
        "field": "cpu_benchmark_multi_core",
        "nature": "benefit",
        "d14_role": "core_topsis",
        "status_v1": "ready_score",
        "note": "Geekbench 6 Multi-Core. Phần cứng chưa phát hành (Mac M5/Neo) bị loại theo D14; ~20 chip mới gắn nhãn approximate kèm cảnh báo.",
    },
    {
        "code": "C03",
        "name_vi": "Hiệu năng GPU đồ họa (gpu_benchmark_time_spy)",
        "field": "gpu_benchmark_time_spy",
        "nature": "benefit",
        "d14_role": "profile_core",
        "status_v1": "ready_score",
        "note": "3DMark Time Spy Graphics. Chỉ áp dụng cho máy Windows dGPU trong preset Gaming; 100% máy dGPU đã có điểm.",
    },
    {
        "code": "C04",
        "name_vi": "Dung lượng RAM (ram_gb)",
        "field": "ram_gb",
        "nature": "fit",
        "d14_role": "core_topsis",
        "status_v1": "ready_score",
        "note": "Chuẩn hóa theo hàm hữu dụng Fit (bão hòa theo nhu cầu, tránh 64GB thắng 16GB vô điều kiện).",
    },
    {
        "code": "C05",
        "name_vi": "Khả năng nâng cấp RAM (ram_slots)",
        "field": "ram_slots",
        "nature": "benefit",
        "d14_role": "display_only",
        "status_v1": "display_only",
        "note": "Độ phủ 60-70% tùy nhà bán lẻ. Đủ để hiển thị tư vấn mua hàng, chưa đủ tiêu chuẩn đưa vào ma trận AHP lõi.",
    },
    {
        "code": "C06",
        "name_vi": "Dung lượng lưu trữ SSD (storage_total_gb)",
        "field": "storage_total_gb",
        "nature": "fit",
        "d14_role": "core_topsis",
        "status_v1": "ready_score",
        "note": "Dung lượng ổ cứng ban đầu của máy (bỏ qua thông số nâng cấp tối đa). Áp dụng hàm hữu dụng Fit.",
    },
    {
        "code": "C07",
        "name_vi": "Công nghệ lưu trữ (storage_type)",
        "field": "storage_primary_type",
        "nature": "fit",
        "d14_role": "display_only",
        "status_v1": "display_only",
        "note": "Hầu hết là SSD NVMe PCIe; không ép điểm cảm tính.",
    },
    {
        "code": "C08",
        "name_vi": "Độ phân giải màn hình (screen_res)",
        "field": "screen_width_px",
        "nature": "fit",
        "d14_role": "hard_filter",
        "status_v1": "filter_display",
        "note": "Dùng làm tiêu chí lọc giao diện (FHD, WUXGA, 2K, 3K), không chấm điểm đơn lẻ.",
    },
    {
        "code": "C09",
        "name_vi": "Kích thước màn hình (screen_size_inch)",
        "field": "screen_size_inch",
        "nature": "fit",
        "d14_role": "hard_filter",
        "status_v1": "filter_display",
        "note": "Dùng làm bộ lọc kích thước (14 inch, 15.6 inch, 16 inch) phục vụ nhu cầu người mua.",
    },
    {
        "code": "C10",
        "name_vi": "Tần số quét màn hình (refresh_rate_hz)",
        "field": "refresh_rate_hz",
        "nature": "benefit",
        "d14_role": "hard_filter",
        "status_v1": "ready_filter",
        "note": "Độ phủ 100%. Dùng làm Hard filter bắt buộc (>= 144Hz) cho preset Gaming.",
    },
    {
        "code": "C11",
        "name_vi": "Dung lượng pin danh định (battery_capacity_wh)",
        "field": "battery_capacity_wh",
        "nature": "fit",
        "d14_role": "display_only",
        "status_v1": "display_only",
        "note": "D07/D14 không chấm điểm thời lượng pin trong V1; hiển thị số Wh thực tế từ thông số kỹ thuật.",
    },
    {
        "code": "C12",
        "name_vi": "Trọng lượng máy (weight_kg)",
        "field": "weight_kg",
        "nature": "cost",
        "d14_role": "core_topsis",
        "status_v1": "ready_score",
        "note": "Tiêu chí cost quan trọng cho sinh viên di chuyển; hard filter <= 1.45kg cho profile Mỏng nhẹ.",
    },
    {
        "code": "C13",
        "name_vi": "Độ sáng màn hình (brightness_nits)",
        "field": "brightness_nits",
        "nature": "benefit",
        "d14_role": "display_only",
        "status_v1": "display_only",
        "note": "Độ phủ ~82%. Dùng hiển thị tab Màn hình, chưa chấm điểm TOPSIS tránh vi phạm D09 (display_score).",
    },
    {
        "code": "C14",
        "name_vi": "Công nghệ tấm nền (panel_type)",
        "field": "panel_type",
        "nature": "fit",
        "d14_role": "hard_filter",
        "status_v1": "filter_display",
        "note": "Bộ lọc tấm nền (OLED vs IPS) trên giao diện theo D09.",
    },
    {
        "code": "C15",
        "name_vi": "Hệ điều hành tích hợp (os_name)",
        "field": "os_name",
        "nature": "constraint",
        "d14_role": "hard_filter",
        "status_v1": "ready_filter",
        "note": "Hard filter tiên quyết cho phần mềm chuyên ngành (Windows vs macOS).",
    },
    {
        "code": "C16",
        "name_vi": "Cổng kết nối USB-C / Type-A / HDMI",
        "field": "hdmi_present",
        "nature": "fit",
        "d14_role": "display_only",
        "status_v1": "display_only",
        "note": "DATA-14: Dữ liệu phong phú hiển thị tab Cổng kết nối; không đưa vào hàm chấm điểm lõi.",
    },
    {
        "code": "C17",
        "name_vi": "Thời gian bảo hành chính hãng (warranty_months)",
        "field": "warranty_months",
        "nature": "benefit",
        "d14_role": "display_only",
        "status_v1": "display_only",
        "note": "Hiển thị minh bạch chính sách bảo hành 12-24 tháng.",
    },
    {
        "code": "C18",
        "name_vi": "Định giá ML / P/P (Value for Money)",
        "field": "ml_price_pred",
        "nature": "benefit",
        "d14_role": "excluded_v1",
        "status_v1": "excluded_v1",
        "note": "DECISIONS.md D10 cấm đưa vào V1 để tránh đếm trùng giá 2 lần.",
    },
]


def generate_readiness_report():
    with open(UNIFIED_CSV, 'r', encoding='utf-8') as f:
        laptops = list(csv.DictReader(f))

    total = len(laptops)
    discrete_count = sum(1 for l in laptops if l.get('gpu_type') == 'discrete')

    report_rows = []
    for meta in CRITERIA_METADATA:
        field = meta["field"]
        if field == "gpu_benchmark_time_spy":
            filled = sum(1 for l in laptops if l.get('gpu_type') == 'discrete' and l.get(field, '').strip())
            denom = discrete_count
            coverage_pct = round(filled / denom * 100, 1) if denom > 0 else 0.0
            cov_str = f"{filled}/{denom} (dGPU)"
        elif field in ("ml_price_pred", "storage_primary_type"):
            filled = sum(1 for l in laptops if l.get(field, '').strip())
            denom = total
            coverage_pct = round(filled / denom * 100, 1)
            cov_str = f"{filled}/{denom}"
        else:
            filled = sum(1 for l in laptops if l.get(field, '').strip() and l.get(field) not in ('', '0'))
            denom = total
            coverage_pct = round(filled / denom * 100, 1)
            cov_str = f"{filled}/{denom}"

        report_rows.append({
            "criteria_code": meta["code"],
            "criteria_name": meta["name_vi"],
            "target_field": field,
            "direction": meta["nature"],
            "coverage_count": cov_str,
            "coverage_percent": coverage_pct,
            "meets_d14_80pct": "YES" if coverage_pct >= 80.0 else "NO",
            "role_in_dss": meta["d14_role"],
            "engine_status": meta["status_v1"],
            "academic_notes": meta["note"],
        })

    # Save to OUT_CSV
    keys = list(report_rows[0].keys())
    with open(OUT_CSV, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(report_rows)

    print(f"Generated criteria readiness report for {total} laptops -> {OUT_CSV}")
    return report_rows


if __name__ == "__main__":
    generate_readiness_report()
