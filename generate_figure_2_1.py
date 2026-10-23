import matplotlib.pyplot as plt
import matplotlib.patches as patches

# Setup figure with high resolution
plt.rcParams['font.family'] = 'Segoe UI'
plt.rcParams['font.sans-serif'] = ['Segoe UI', 'Arial', 'DejaVu Sans']

fig, ax = plt.subplots(figsize=(13.5, 6.2), dpi=300)
ax.set_xlim(0, 135)
ax.set_ylim(0, 62)
ax.axis('off')

# Background
fig.patch.set_facecolor('#FFFFFF')
ax.set_facecolor('#FFFFFF')

# Helper function to draw rounded boxes
def draw_card(ax, x, y, w, h, bg_color, border_color, title, subtitle_list, title_color="#0F172A", title_size=11, corner_radius=1.8):
    box = patches.FancyBboxPatch(
        (x, y), w, h,
        boxstyle=f"round,pad=0,rounding_size={corner_radius}",
        facecolor=bg_color,
        edgecolor=border_color,
        linewidth=1.6,
        zorder=2
    )
    ax.add_patch(box)
    
    # Title
    t_y = y + h - 2.8
    ax.text(x + w/2, t_y, title, ha='center', va='center', fontsize=title_size, fontweight='bold', color=title_color, zorder=3)
    
    # Subtitle / bullet items
    if subtitle_list:
        start_y = t_y - 2.8
        line_height = (h - 5.5) / max(len(subtitle_list), 1)
        for i, text in enumerate(subtitle_list):
            curr_y = start_y - i * line_height
            ax.text(x + w/2, curr_y, text, ha='center', va='center', fontsize=9.2, color='#334155', zorder=3)

# Arrow helper
def draw_arrow(ax, x1, y1, x2, y2, color="#64748B"):
    ax.annotate(
        "", xy=(x2, y2), xytext=(x1, y1),
        arrowprops=dict(
            arrowstyle="->,head_length=0.45,head_width=0.3",
            color=color,
            lw=1.8,
            shrinkA=2,
            shrinkB=2,
            mutation_scale=14
        ),
        zorder=1
    )

# 1. NGUỒN DỮ LIỆU (Sources)
draw_card(ax, 3, 33, 22, 13, "#EFF6FF", "#3B82F6", "CellphoneS", ["505 cấu hình laptop", "Thông số bán lẻ & giá"])
draw_card(ax, 3, 16, 22, 13, "#EFF6FF", "#3B82F6", "FPT Shop", ["8 cấu hình laptop", "Bổ sung phân khúc"])

# Combined Source Bracket / Merge node
draw_arrow(ax, 25, 39.5, 32, 31)
draw_arrow(ax, 25, 22.5, 32, 31)

# 2. THU THẬP & CHUẨN HÓA (Processing)
draw_card(
    ax, 32, 16, 25, 30,
    "#F0FDF4", "#16A34A",
    "Thu thập & Chuẩn hóa",
    [
        "Hợp nhất dữ liệu (513 mẫu)",
        "Đồng nhất đơn vị đo:",
        "• RAM, ROM → GB",
        "• Trọng lượng → kg",
        "• Giá bán → VNĐ",
        "Giữ nguyên giá trị thiếu (NaN)"
    ]
)

draw_arrow(ax, 57, 31, 64, 31)

# 3. CATALOG LAPTOPS.CSV
draw_card(
    ax, 64, 21, 22, 20,
    "#FEF3C7", "#D97706",
    "Catalog Chuẩn hóa",
    [
        "laptops.csv",
        "(513 bản ghi cấu hình)",
        "Dữ liệu dạng bảng",
        "Sẵn sàng nạp & xử lý"
    ]
)

draw_arrow(ax, 86, 31, 93, 31)

# 4. SQLITE DATABASE
draw_card(
    ax, 93, 21, 16, 20,
    "#F3E8FF", "#9333EA",
    "Cơ sở dữ liệu",
    [
        "SQLite DB",
        "laptop_dss.db",
        "Lưu trữ quan hệ",
        "Truy vấn & lọc nhanh"
    ]
)

# Arrows to 3 downstream branches
draw_arrow(ax, 109, 36, 115, 45)
draw_arrow(ax, 109, 31, 115, 31)
draw_arrow(ax, 109, 26, 115, 17)

# 5. KHAI THÁC & ỨNG DỤNG (Applications)
draw_card(
    ax, 115, 40, 18, 12,
    "#F1F5F9", "#475569",
    "EDA & Trực quan hóa",
    ["Phân tích phân phối giá", "Độ phủ đặc trưng, hãng"],
    title_size=10
)

draw_card(
    ax, 115, 25, 18, 12,
    "#ECFDF5", "#059669",
    "Mô hình AHP - TOPSIS",
    ["Xác định trọng số tiêu chí", "Xếp hạng tối ưu cấu hình"],
    title_size=10
)

draw_card(
    ax, 115, 10, 18, 12,
    "#FFF1F2", "#E11D48",
    "Mô hình Học máy (ML)",
    ["Xử lý missing: KNNImputer", "Dự báo giá bán laptop"],
    title_size=10
)

# Caption underneath
ax.text(
    67.5, 4,
    "Hình 2.1. Quy trình thu thập, chuẩn hóa và sử dụng dữ liệu LaptopDSS",
    ha='center', va='center',
    fontsize=11.5, fontweight='bold', color='#1E293B'
)

plt.tight_layout()
output_path = "data/reports/figures/00_data_pipeline.png"
plt.savefig(output_path, dpi=300, bbox_inches='tight')
print(f"Saved figure to {output_path}")
