"""[DEPRECATED PROTOTYPE]: Ứng dụng Streamlit này là nguyên mẫu thử nghiệm ban đầu (DECISIONS.md D11).
Sản phẩm chính thức đã chuyển sang kiến trúc hiện đại Decoupled Backend FastAPI (src/api.py) + Frontend React 18 (frontend/).
File này chỉ lưu giữ phục vụ mục đích kiểm thử đối chiếu nội bộ.
"""

import sys
from pathlib import Path
import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from dss_ranking import (
    PRESETS,
    compute_ahp_weights,
    evaluate,
    load_standardized_laptops,
)
from laptop_images import get_laptop_image_info

# ---------------------------------------------------------------------------
# Cấu hình trang Streamlit
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="LaptopDSS — Chọn Laptop Sinh Viên",
    page_icon="💻",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ---------------------------------------------------------------------------
# CSS Tinh Gọn (Không dùng HTML lồng phức tạp để tránh lỗi escape)
# ---------------------------------------------------------------------------
st.markdown("""
<style>
/* Ẩn header và footer mặc định */
#MainMenu, footer, header { visibility: hidden !important; }
.block-container {
    padding-top: 1rem !important;
    padding-bottom: 2rem !important;
    max-width: 1320px !important;
}

body, [class*="css"] {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif !important;
    color: #0f172a !important;
}

/* Header thương hiệu */
.header-box {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 14px 20px;
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    margin-bottom: 20px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.02);
}
.header-logo-badge {
    background: #d70018;
    color: #ffffff;
    width: 36px;
    height: 36px;
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 18px;
    font-weight: 800;
}

/* Card sản phẩm */
.product-card-box {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 16px;
    height: 100%;
    transition: all 0.2s ease;
}
.product-card-box:hover {
    border-color: #d70018;
    box-shadow: 0 6px 18px rgba(215, 0, 24, 0.08);
}

.spec-summary-bar {
    background: #f8fafc;
    border: 1px solid #f1f5f9;
    border-radius: 6px;
    padding: 6px 8px;
    font-size: 11.5px;
    font-weight: 700;
    color: #1e293b;
    text-align: center;
    margin: 8px 0;
}

.sale-price-text {
    font-size: 18px;
    font-weight: 800;
    color: #d70018;
}
.listed-price-text {
    font-size: 12px;
    color: #94a3b8;
    text-decoration: line-through;
    margin-left: 6px;
}

.badge-discount {
    background: #fff1f2;
    color: #e11d48;
    font-size: 11px;
    font-weight: 700;
    padding: 2px 6px;
    border-radius: 4px;
}

.badge-rank-gold {
    background: #fef08a;
    color: #854d0e;
    font-size: 11px;
    font-weight: 800;
    padding: 2px 8px;
    border-radius: 4px;
    border: 1px solid #facc15;
}
.badge-rank-silver {
    background: #f1f5f9;
    color: #334155;
    font-size: 11px;
    font-weight: 800;
    padding: 2px 8px;
    border-radius: 4px;
    border: 1px solid #cbd5e1;
}
.badge-rank-bronze {
    background: #fed7aa;
    color: #7c2d12;
    font-size: 11px;
    font-weight: 800;
    padding: 2px 8px;
    border-radius: 4px;
    border: 1px solid #fb923c;
}
.badge-rank-normal {
    background: #f8fafc;
    color: #64748b;
    font-size: 11px;
    font-weight: 700;
    padding: 2px 8px;
    border-radius: 4px;
    border: 1px solid #e2e8f0;
}

.spec-detail-box {
    background: #ffffff;
    border: 2px solid #d70018;
    border-radius: 14px;
    padding: 20px;
    margin-bottom: 24px;
    box-shadow: 0 8px 24px rgba(215, 0, 24, 0.08);
}

.spec-table-row {
    display: flex;
    justify-content: space-between;
    padding: 9px 0;
    border-bottom: 1px solid #f1f5f9;
    font-size: 13px;
}
.spec-table-row:last-child { border-bottom: none; }
.spec-table-label { color: #64748b; font-weight: 500; }
.spec-table-value { color: #0f172a; font-weight: 600; text-align: right; }
</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Nạp Dữ Liệu
# ---------------------------------------------------------------------------
@st.cache_data
def get_laptops():
    data = load_standardized_laptops()
    return data, pd.DataFrame(data)

laptops_raw, df_all = get_laptops()

def format_vnd(val):
    try:
        return f"{int(float(val)):,}₫".replace(",", ".")
    except (ValueError, TypeError):
        return "—"

def format_discount(listed, sale):
    if not listed or not sale:
        return None
    try:
        l_val = float(listed)
        s_val = float(sale)
        if l_val > s_val and l_val > 0:
            return f"-{(1 - s_val / l_val) * 100:.0f}%"
    except:
        pass
    return None

def build_specs_line(row):
    specs = []
    cpu = row.get("cpu_name_normalized", "")
    for prefix in ["Intel Core ", "Intel ", "AMD Ryzen ", "AMD ", "Qualcomm Snapdragon ", "Apple "]:
        cpu = cpu.replace(prefix, "")
    if cpu:
        specs.append(cpu[:15])

    gpu = row.get("gpu_name_normalized", "")
    if gpu and row.get("gpu_type") == "discrete":
        gpu_short = gpu.replace("NVIDIA GeForce ", "").replace(" GDDR6", "")[:12]
        specs.append(gpu_short)

    ram = row.get("ram_gb", "")
    if ram:
        specs.append(f"{ram}GB")

    ssd = row.get("storage_total_gb", "")
    if ssd:
        specs.append(f"{int(float(ssd))}GB")

    screen = row.get("screen_size_inch", "")
    hz = row.get("refresh_rate_hz", "")
    if screen and hz:
        specs.append(f'{screen}" {hz}Hz')
    elif screen:
        specs.append(f'{screen}"')

    return " · ".join(specs)

# Từ điển hiển thị tiếng Việt thân thiện cho các tiêu chí
CRITERIA_VN_MAP = {
    "gpu_benchmark_time_spy": "Hiệu năng đồ họa (GPU)",
    "cpu_benchmark_multi_core": "Hiệu năng xử lý (CPU)",
    "sale_price_vnd": "Giá bán tiết kiệm",
    "ram_gb": "Dung lượng RAM",
    "storage_total_gb": "Dung lượng lưu trữ SSD",
    "weight_kg": "Trọng lượng mỏng nhẹ",
    "warranty_months": "Thời hạn bảo hành",
}


# ---------------------------------------------------------------------------
# 1. HEADER CHÍNH
# ---------------------------------------------------------------------------
st.markdown("""
<div class="header-box">
    <div style="display: flex; align-items: center; gap: 12px;">
        <div class="header-logo-badge">💻</div>
        <div>
            <div style="font-size: 17px; font-weight: 800; color: #0f172a;">LaptopDSS — Hệ Thống Đề Xuất Laptop Cho Sinh Viên</div>
            <div style="font-size: 12px; color: #64748b;">Hỗ trợ tìm kiếm và xếp hạng laptop tối ưu theo ngân sách và nhu cầu học tập</div>
        </div>
    </div>
    <div style="font-size: 12px; color: #64748b; background: #f8fafc; padding: 6px 12px; border-radius: 6px; border: 1px solid #e2e8f0;">
        Dữ liệu chính hãng FPT Shop · 10 cấu hình mẫu
    </div>
</div>
""", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# 2. BỘ LỌC TÌM KIẾM (CHUẨN CELLPHONES)
# ---------------------------------------------------------------------------
with st.container():
    # Hàng 1: Nhu cầu sử dụng
    st.markdown("<div style='font-size: 13px; font-weight: 700; color: #334155; margin-bottom: 6px;'>🎯 CHỌN THEO NHU CẦU SỬ DỤNG:</div>", unsafe_allow_html=True)
    c_p1, c_p2, c_p3 = st.columns(3)
    
    if "preset_selected" not in st.session_state:
        st.session_state["preset_selected"] = "coding"

    with c_p1:
        if st.button("💻  Lập trình & Kỹ thuật", key="btn_coding", use_container_width=True,
                     type="primary" if st.session_state["preset_selected"] == "coding" else "secondary"):
            st.session_state["preset_selected"] = "coding"
            st.session_state["detail_laptop_id"] = None
            st.rerun()
    with c_p2:
        if st.button("🎮  Gaming & Đồ họa 3D", key="btn_gaming", use_container_width=True,
                     type="primary" if st.session_state["preset_selected"] == "gaming" else "secondary"):
            st.session_state["preset_selected"] = "gaming"
            st.session_state["detail_laptop_id"] = None
            st.rerun()
    with c_p3:
        if st.button("💼  Văn phòng & Di động", key="btn_office", use_container_width=True,
                     type="primary" if st.session_state["preset_selected"] == "office" else "secondary"):
            st.session_state["preset_selected"] = "office"
            st.session_state["detail_laptop_id"] = None
            st.rerun()

    st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

    # Hàng 2: Ngân sách từ 0 đến 50 triệu & Các bộ lọc nhanh
    col_budget, col_brand, col_os = st.columns([2, 1.2, 1])

    with col_budget:
        st.markdown("<div style='font-size: 13px; font-weight: 700; color: #334155; margin-bottom: 4px;'>💰 MỨC NGÂN SÁCH TỐI ĐA BẠN MUỐN CHI:</div>", unsafe_allow_html=True)
        max_budget = st.slider(
            "Ngân sách tối đa",
            min_value=0,
            max_value=50_000_000,
            value=35_000_000,
            step=2_000_000,
            format="%d",
            label_visibility="collapsed",
        )
        st.caption(f"Đang lọc các máy có giá từ **0₫** đến **{format_vnd(max_budget)}**")

    with col_brand:
        st.markdown("<div style='font-size: 13px; font-weight: 700; color: #334155; margin-bottom: 4px;'>🏷️ HÃNG SẢN XUẤT:</div>", unsafe_allow_html=True)
        brand_filter = st.selectbox(
            "Hãng",
            ["Tất cả", "ASUS", "Lenovo", "MSI", "HP", "Acer", "Apple"],
            index=0,
            label_visibility="collapsed",
        )

    with col_os:
        st.markdown("<div style='font-size: 13px; font-weight: 700; color: #334155; margin-bottom: 4px;'>🖥️ HỆ ĐIỀU HÀNH:</div>", unsafe_allow_html=True)
        os_filter = st.selectbox(
            "Hệ điều hành",
            ["Tất cả", "Windows", "macOS"],
            index=0,
            label_visibility="collapsed",
        )


# ---------------------------------------------------------------------------
# 3. THỰC THI THUẬT TOÁN DSS
# ---------------------------------------------------------------------------
current_preset = st.session_state.get("preset_selected", "coding")

# Lọc sơ bộ theo hãng nếu có
candidate_pool = laptops_raw
if brand_filter != "Tất cả":
    candidate_pool = [l for l in candidate_pool if brand_filter.lower() in l.get("product_name_raw", "").lower()]

eval_result = evaluate(
    candidates=candidate_pool,
    preset_key=current_preset,
    min_budget_vnd=0.0,
    max_budget_vnd=float(max_budget),
    min_refresh_rate_hz=None,
    required_os=os_filter if os_filter != "Tất cả" else None,
)

ranked_list = eval_result["rankings"]
excluded_list = eval_result["excluded"]


# ---------------------------------------------------------------------------
# 4. TABPANE THÔNG SỐ KỸ THUẬT CHI TIẾT (CHỈ XUẤT HIỆN KHI NGƯỜI DÙNG BẤM XEM)
# ---------------------------------------------------------------------------
if "detail_laptop_id" not in st.session_state:
    st.session_state["detail_laptop_id"] = None

selected_id = st.session_state.get("detail_laptop_id")

if selected_id:
    # Tìm laptop đang được chọn
    detail_laptop = next((l for l in laptops_raw if l.get("source_product_id") == selected_id), None)
    
    if detail_laptop:
        st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
        
        with st.container():
            # Nút đóng
            col_d_title, col_d_close = st.columns([5, 1])
            with col_d_title:
                st.markdown(f"### 📋 Thông số kỹ thuật chi tiết: {detail_laptop.get('product_name_raw', '')}")
            with col_d_close:
                if st.button("✕ Đóng chi tiết", key="btn_close_detail", use_container_width=True):
                    st.session_state["detail_laptop_id"] = None
                    st.rerun()

            img_data = get_laptop_image_info(selected_id, detail_laptop.get("product_name_raw", ""))

            # Layout 2 cột: Ảnh lớn + 4 Tabs chi tiết
            c_img, c_tabs = st.columns([1, 2], gap="large")

            with c_img:
                st.image(img_data["image_path"], use_container_width=True)
                st.markdown(f"""
                <div style="text-align: center; margin-top: 8px;">
                    <span style="font-size: 11px; color: #64748b; background: #f8fafc; padding: 3px 8px; border-radius: 4px; border: 1px solid #e2e8f0;">
                        {img_data['label']}
                    </span>
                    <div style="font-size: 22px; font-weight: 800; color: #d70018; margin-top: 8px;">
                        {format_vnd(detail_laptop.get('sale_price_vnd', ''))}
                    </div>
                </div>
                """, unsafe_allow_html=True)

            with c_tabs:
                tab_cfg, tab_screen, tab_ports, tab_pin = st.tabs([
                    "⚙️ Cấu hình & Bộ nhớ",
                    "🖥️ Màn hình",
                    "🔌 Cổng kết nối",
                    "📦 Thiết kế & Pin"
                ])

                with tab_cfg:
                    # Ghi chú benchmark trung thực
                    cpu_b = detail_laptop.get("cpu_benchmark_multi_core", "")
                    cpu_lvl = detail_laptop.get("cpu_benchmark_match_level", "")
                    if cpu_b:
                        cpu_txt = f"{int(float(cpu_b)):,} điểm"
                    elif cpu_lvl == "unreleased_hardware":
                        cpu_txt = "Chưa phát hành (Mã giả định)"
                    elif cpu_lvl == "unavailable":
                        cpu_txt = "Chưa có mẫu kiểm chứng Geekbench 6 độc lập"
                    else:
                        cpu_txt = "Chưa có dữ liệu"

                    gpu_b = detail_laptop.get("gpu_benchmark_time_spy", "")
                    gpu_lvl = detail_laptop.get("gpu_benchmark_match_level", "")
                    if gpu_b:
                        gpu_txt = f"{int(float(gpu_b)):,} điểm 3DMark Time Spy ({gpu_lvl})"
                    else:
                        gpu_txt = "Không áp dụng card rời (Đồ họa tích hợp)"

                    specs_1 = [
                        ("Bộ vi xử lý (CPU)", detail_laptop.get("cpu_name_normalized", "—")),
                        ("Số nhân / Số luồng", f"{detail_laptop.get('cpu_cores', '—')} nhân / {detail_laptop.get('cpu_threads', '—')} luồng"),
                        ("Xung nhịp CPU", f"{detail_laptop.get('cpu_base_ghz', '—')} – {detail_laptop.get('cpu_boost_ghz', '—')} GHz"),
                        ("Điểm hiệu năng CPU", cpu_txt),
                        ("Card đồ họa (GPU)", detail_laptop.get("gpu_name_normalized", "—")),
                        ("Bộ nhớ đồ họa (VRAM)", f"{detail_laptop.get('gpu_vram_gb', '—')} GB" if detail_laptop.get("gpu_vram_gb") else "Chia sẻ hệ thống"),
                        ("Điểm hiệu năng đồ họa", gpu_txt),
                        ("Dung lượng RAM", f"{detail_laptop.get('ram_gb', '—')} GB {detail_laptop.get('ram_type', '')}"),
                        ("Khả năng nâng cấp RAM", f"{detail_laptop.get('ram_slots', '—')} khe (Trống: {detail_laptop.get('ram_slots_free', '—')})"),
                        ("Ổ cứng SSD", f"{detail_laptop.get('storage_total_gb', '—')} GB {detail_laptop.get('storage_primary_type', '')}"),
                    ]
                    for label, val in specs_1:
                        st.markdown(f'<div class="spec-table-row"><span class="spec-table-label">{label}</span><span class="spec-table-value">{val}</span></div>', unsafe_allow_html=True)

                with tab_screen:
                    specs_2 = [
                        ("Kích thước màn hình", f'{detail_laptop.get("screen_size_inch", "—")}" inch'),
                        ("Độ phân giải", f'{detail_laptop.get("screen_width_px", "—")} × {detail_laptop.get("screen_height_px", "—")}'),
                        ("Công nghệ tấm nền", detail_laptop.get("panel_type", "—") or "Hãng không công bố"),
                        ("Tần số quét màn hình", f'{detail_laptop.get("refresh_rate_hz", "—")} Hz' if detail_laptop.get("refresh_rate_hz") else "Hãng không công bố"),
                        ("Độ sáng màn hình", f'{detail_laptop.get("brightness_nits", "—")} nits' if detail_laptop.get("brightness_nits") else "Hãng không công bố"),
                        ("Độ phủ không gian màu", detail_laptop.get("color_gamut_raw", "—") or "Hãng không công bố"),
                    ]
                    for label, val in specs_2:
                        st.markdown(f'<div class="spec-table-row"><span class="spec-table-label">{label}</span><span class="spec-table-value">{val}</span></div>', unsafe_allow_html=True)

                with tab_ports:
                    specs_3 = [
                        ("Cổng USB Type-A", f"{detail_laptop.get('usb_a_count', '—')} cổng" if detail_laptop.get('usb_a_count') else "Hãng không công bố"),
                        ("Cổng USB Type-C", f"{detail_laptop.get('usb_c_count', '—')} cổng" if detail_laptop.get('usb_c_count') else "Hãng không công bố"),
                        ("Cổng xuất hình HDMI", "Có tích hợp" if detail_laptop.get("hdmi_present") == "true" else ("Không có" if detail_laptop.get("hdmi_present") == "false" else "Hãng không công bố")),
                        ("Cổng mạng LAN RJ45", "Có tích hợp" if detail_laptop.get("lan_present") == "true" else ("Không có" if detail_laptop.get("lan_present") == "false" else "Hãng không công bố")),
                        ("Jack tai nghe 3.5mm", "Có tích hợp" if detail_laptop.get("audio_jack_present") == "true" else ("Không có" if detail_laptop.get("audio_jack_present") == "false" else "Hãng không công bố")),
                        ("Kết nối Wi-Fi", detail_laptop.get("wifi_raw", "—") or "Hãng không công bố"),
                        ("Kết nối Bluetooth", detail_laptop.get("bluetooth_raw", "—") or "Hãng không công bố"),
                    ]
                    for label, val in specs_3:
                        st.markdown(f'<div class="spec-table-row"><span class="spec-table-label">{label}</span><span class="spec-table-value">{val}</span></div>', unsafe_allow_html=True)

                with tab_pin:
                    specs_4 = [
                        ("Trọng lượng thân máy", f'{detail_laptop.get("weight_kg", "—")} kg'),
                        ("Độ dày máy", f'{detail_laptop.get("thickness_mm", "—")} mm' if detail_laptop.get("thickness_mm") else "Hãng không công bố"),
                        ("Chất liệu vỏ máy", detail_laptop.get("material_raw", "—") or "Hãng không công bố"),
                        ("Màu sắc sản phẩm", detail_laptop.get("color_raw", "—") or "Hãng không công bố"),
                        ("Dung lượng Pin", f'{detail_laptop.get("battery_capacity_wh", "—")} Wh ({detail_laptop.get("battery_cells", "—")} cell)' if detail_laptop.get("battery_capacity_wh") else "Hãng không công bố"),
                        ("Công suất củ sạc kèm", f'{detail_laptop.get("charger_w", "—")} W' if detail_laptop.get("charger_w") else "Hãng không công bố"),
                        ("Hệ điều hành tích hợp", detail_laptop.get("os_name", "—")),
                        ("Thời gian bảo hành", f'{detail_laptop.get("warranty_months", "—")} tháng'),
                    ]
                    for label, val in specs_4:
                        st.markdown(f'<div class="spec-table-row"><span class="spec-table-label">{label}</span><span class="spec-table-value">{val}</span></div>', unsafe_allow_html=True)

        st.markdown("---")


# ---------------------------------------------------------------------------
# 5. DANH SÁCH SẢN PHẨM ĐỀ XUẤT (LƯỚI 3 CỘT RỘNG RÃI)
# ---------------------------------------------------------------------------
st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
st.markdown(f"#### 🏆 Kết quả đề xuất phù hợp ({len(ranked_list)} laptop đạt chuẩn)")

if not ranked_list:
    st.info("💡 Không có laptop nào thỏa mãn ngân sách hoặc bộ lọc hiện tại. Bạn vui lòng tăng ngân sách hoặc chọn lại hãng.", icon="ℹ️")
else:
    # Chia lưới 3 card mỗi hàng
    rows = [ranked_list[i:i+3] for i in range(0, len(ranked_list), 3)]

    for row_items in rows:
        cols = st.columns(3)
        for idx, item in enumerate(row_items):
            with cols[idx]:
                pid = item.get("source_product_id", "")
                pname = item.get("product_name_raw", "Laptop")
                sale_vnd = item.get("sale_price_vnd", "")
                listed_vnd = item.get("listed_price_vnd", "")
                rank_num = item.get("rank", 1)
                topsis_score = item.get("topsis_score", 0.0)

                # Huy hiệu thứ hạng
                if rank_num == 1:
                    badge_rank = '<span class="badge-rank-gold">TOP #1 LỰA CHỌN</span>'
                elif rank_num == 2:
                    badge_rank = '<span class="badge-rank-silver">TOP #2 ĐỀ XUẤT</span>'
                elif rank_num == 3:
                    badge_rank = '<span class="badge-rank-bronze">TOP #3 PHÙ HỢP</span>'
                else:
                    badge_rank = f'<span class="badge-rank-normal">HẠNG #{rank_num}</span>'

                # Giảm giá
                disc_badge = format_discount(listed_vnd, sale_vnd)
                disc_html = f'<span class="badge-discount">{disc_badge}</span>' if disc_badge else ""

                # Thông tin ảnh local
                img_info = get_laptop_image_info(pid, pname)

                # Dải thông số tóm tắt
                spec_str = build_specs_line(item)

                # Ưu thế & Tổn thất được diễn đạt tự nhiên
                expl = item.get("explanation", {})
                adv_raw = expl.get("top_advantage", "").split("(")[0].strip()
                pen_raw = expl.get("top_penalty", "").split("(")[0].strip()
                adv_vn = CRITERIA_VN_MAP.get(adv_raw, adv_raw)
                pen_vn = CRITERIA_VN_MAP.get(pen_raw, pen_raw)

                # Độ phù hợp tính theo %
                fit_percent = int(topsis_score * 100)

                with st.container():
                    st.markdown(f"""
                    <div class="product-card-box">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                            {badge_rank}
                            {disc_html}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                    # Hiển thị ảnh local (0% lỗi vỡ)
                    st.image(img_info["image_path"], use_container_width=True)

                    st.markdown(f"""
                    <div style="margin-top: -6px;">
                        <div class="spec-summary-bar">{spec_str}</div>
                        <div style="font-size: 14px; font-weight: 700; color: #0f172a; line-height: 1.35; min-height: 38px; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;">
                            {pname}
                        </div>
                        <div style="margin: 8px 0 6px 0;">
                            <span class="sale-price-text">{format_vnd(sale_vnd)}</span>
                            <span class="listed-price-text">{format_vnd(listed_vnd) if disc_badge else ''}</span>
                        </div>
                        <div style="display: flex; align-items: center; justify-content: space-between; font-size: 12px; margin-bottom: 8px;">
                            <span style="color: #64748b;">Độ phù hợp nhu cầu:</span>
                            <span style="font-weight: 800; color: #059669;">{fit_percent}%</span>
                        </div>
                        <div style="font-size: 11.5px; color: #475569; margin-bottom: 12px; line-height: 1.4;">
                            <div><span style="color: #047857; font-weight: 700;">✓ Ưu điểm:</span> {adv_vn}</div>
                            <div><span style="color: #b91c1c; font-weight: 700;">✗ Điểm trừ:</span> {pen_vn}</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                    # Nút bấm mở chi tiết
                    if st.button("🔍 Xem thông số chi tiết", key=f"view_btn_{pid}", use_container_width=True):
                        st.session_state["detail_laptop_id"] = pid
                        st.rerun()


# ---------------------------------------------------------------------------
# 6. KHU VỰC BẢO VỆ ĐỒ ÁN & CƠ SỞ KHOA HỌC (EXPANDER GỌN GÀNG Ở CUỐI TRANG)
# ---------------------------------------------------------------------------
st.markdown("<div style='height: 30px;'></div>", unsafe_allow_html=True)

with st.expander("📐 Dành cho hội đồng thẩm định: Cơ sở toán học AHP + TOPSIS & Báo cáo kỹ thuật", expanded=False):
    st.markdown("### Mô hình Hỗ trợ Quyết định (Decision Support System)")
    st.caption("Thuật toán kết hợp Phân tích thứ bậc AHP (Saaty) và Tiếp cận phương án lý tưởng TOPSIS có kiểm soát chất lượng dữ liệu.")

    c_m1, c_m2, c_m3 = st.columns(3)
    c_m1.metric("Tỷ số nhất quán AHP (CR)", f"{eval_result['ahp_cr']:.4f}", "Đạt chuẩn (< 0.10)")
    c_m2.metric("Số tiêu chí kích hoạt", f"{len(eval_result['active_criteria'])} tiêu chí")
    c_m3.metric("Số máy bị loại trừ do thiếu chuẩn", f"{len(excluded_list)} máy")

    st.markdown("#### Trọng số ưu tiên chuẩn hóa của các tiêu chí:")
    for crit_name, crit_dir, weight in eval_result["active_criteria"]:
        crit_vn = CRITERIA_VN_MAP.get(crit_name, crit_name)
        dir_text = "càng cao càng tốt" if crit_dir == "benefit" else "càng thấp càng tốt" if crit_dir == "cost" else "hàm bão hòa Fit"
        st.markdown(f"- **{crit_vn}** (`{crit_name}` - {dir_text}): **{weight * 100:.1f}%**")

    if eval_result["dropped_criteria"]:
        st.markdown("#### Tiêu chí bị loại trừ tự động theo quy tắc D14 (Độ phủ < 80%):")
        for dc in eval_result["dropped_criteria"]:
            st.markdown(f"- `{dc['criterion']}`: Độ phủ chỉ đạt **{dc['coverage_percent']}%** (dưới ngưỡng 80%).")

    if excluded_list:
        st.markdown("#### Danh sách máy bị loại trừ khỏi lần xếp hạng này:")
        for ex in excluded_list:
            st.markdown(f"- **{ex['product_name_raw'][:50]}**: _{ex['reason']}_")
