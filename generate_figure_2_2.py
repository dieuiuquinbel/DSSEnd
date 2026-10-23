import matplotlib.pyplot as plt
import matplotlib.patches as patches

# Setup font
plt.rcParams['font.family'] = 'Segoe UI'
plt.rcParams['font.sans-serif'] = ['Segoe UI', 'Arial', 'DejaVu Sans']

# Canvas setup
fig, ax = plt.subplots(figsize=(14, 8), dpi=300)
ax.set_xlim(0, 140)
ax.set_ylim(0, 80)
ax.axis('off')

# Background
fig.patch.set_facecolor('#FFFFFF')
ax.set_facecolor('#FFFFFF')

def draw_box(ax, x, y, w, h, bg_color, border_color, title, lines=None, title_size=11, line_size=9, corner=1.6):
    box = patches.FancyBboxPatch(
        (x, y), w, h,
        boxstyle=f"round,pad=0,rounding_size={corner}",
        facecolor=bg_color,
        edgecolor=border_color,
        linewidth=1.8,
        zorder=3
    )
    ax.add_patch(box)
    
    # Title
    t_y = y + h - 2.5
    ax.text(x + w/2, t_y, title, ha='center', va='center', fontsize=title_size, fontweight='bold', color="#0F172A", zorder=4)
    
    # Text lines
    if lines:
        avail_h = h - 4.2
        step = avail_h / max(len(lines), 1)
        for i, line in enumerate(lines):
            ax.text(x + w/2, t_y - 2.3 - i * step, line, ha='center', va='center', fontsize=line_size, color="#334155", zorder=4)

def draw_arrow(ax, x1, y1, x2, y2, color="#475569", lw=1.8):
    ax.annotate(
        "", xy=(x2, y2), xytext=(x1, y1),
        arrowprops=dict(
            arrowstyle="->,head_length=0.4,head_width=0.25",
            color=color,
            lw=lw,
            shrinkA=2,
            shrinkB=2,
            mutation_scale=12
        ),
        zorder=2
    )

# Section / Stage Bounding Containers
def draw_stage(ax, x, y, w, h, label, bg="#F8FAFC", border="#CBD5E1"):
    stage = patches.FancyBboxPatch(
        (x, y), w, h,
        boxstyle="round,pad=0,rounding_size=2.2",
        facecolor=bg,
        edgecolor=border,
        linewidth=1.2,
        linestyle="--",
        zorder=1
    )
    ax.add_patch(stage)
    ax.text(x + 2.5, y + h - 2.5, label, fontsize=10, fontweight='bold', color="#475569", zorder=2)

# 1. STAGE 1: ĐẦU VÀO & LỌC CỨNG (x: 4 -> 42)
draw_stage(ax, 4, 12, 38, 62, "GIAI ĐOẠN 1: ĐẦU VÀO & LỌC CỨNG", bg="#FEF2F2", border="#FCA5A5")

draw_box(ax, 7, 56, 32, 13, "#FFFFFF", "#EF4444", "Yêu cầu & Ràng buộc cứng", [
    "• Ngân sách tối đa - tối thiểu",
    "• Hãng yêu thích, RAM tối thiểu",
    "• Ổ cứng tối thiểu, trọng lượng..."
])

draw_box(ax, 7, 36, 32, 14, "#FFFFFF", "#EF4444", "Bộ lọc cứng (Hard Filter)", [
    "• Đối soát với Catalog 513 laptop",
    "• Loại bỏ máy không đạt ràng buộc",
    "→ Thu được m phương án hợp lệ (m ≤ 513)"
])

draw_arrow(ax, 23, 56, 23, 50)

# STAGE 2: XÁC ĐỊNH TRỌNG SỐ AHP (dưới Giai đoạn 1)
draw_box(ax, 7, 15, 32, 16, "#FFFFFF", "#8B5CF6", "Xác định trọng số AHP", [
    "• Chọn hồ sơ nhu cầu (Kinh tế, CNTT...)",
    "• Ma trận so sánh cặp Saaty (n tiêu chí)",
    "• Tính vector trọng số w = [w1, ..., wn]",
    "• Kiểm tra tính nhất quán: CR < 0.10"
])

# Arrow from Filter to TOPSIS
draw_arrow(ax, 39, 43, 49, 43, color="#DC2626", lw=2.2)

# Arrow from AHP to TOPSIS
ax.annotate(
    "", xy=(49, 32), xytext=(39, 23),
    arrowprops=dict(
        arrowstyle="->,head_length=0.4,head_width=0.25",
        connectionstyle="arc3,rad=-0.15",
        color="#7C3AED",
        lw=2.2,
        mutation_scale=12
    ),
    zorder=2
)
ax.text(45, 25, "Trọng số w_j", fontsize=8.5, fontweight='bold', color="#7C3AED")

# 2. STAGE 2: QUY TRÌNH XẾP HẠNG TOPSIS (x: 48 -> 106)
draw_stage(ax, 48, 12, 57, 62, "GIAI ĐOẠN 2: THUẬT TOÁN TOPSIS", bg="#F0FDF4", border="#86EFAC")

draw_box(ax, 51, 56, 51, 13, "#FFFFFF", "#10B981", "1. Lập ma trận quyết định", [
    "X = [x_ij] kích thước m phương án × n tiêu chí",
    "(Thông số cấu hình: CPU, GPU, RAM, ROM, Pin, Trọng lượng, Giá...)"
])

draw_arrow(ax, 76.5, 56, 76.5, 52)

draw_box(ax, 51, 39, 51, 13, "#FFFFFF", "#10B981", "2. Chuẩn hóa & Nhân trọng số AHP", [
    "• Chuẩn hóa vector:  r_ij = x_ij / √(∑_i x_ij²)",
    "• Nhân trọng số AHP:  v_ij = w_j × r_ij"
])

draw_arrow(ax, 76.5, 39, 76.5, 35)

draw_box(ax, 51, 15, 51, 20, "#FFFFFF", "#059669", "3. Nghiệm lý tưởng & Khoảng cách Euclid", [
    "• Xác định nghiệm lý tưởng tốt A+ và xấu A-:",
    "  A+ = {max Benefit, min Cost} | A- = {min Benefit, max Cost}",
    "• Khoảng cách Euclid đến A+ và A-:",
    "  S_i+ = √∑(v_ij - v_j+)²   |   S_i- = √∑(v_ij - v_j-)²",
    "• Điểm phù hợp tương đối:   C_i = S_i- / (S_i+ + S_i-) trong [0, 1]"
])

# Arrow from TOPSIS to Output
draw_arrow(ax, 102, 25, 110, 25, color="#059669", lw=2.2)

# 3. STAGE 3: KẾT QUẢ XẾP HẠNG (x: 109 -> 136)
draw_stage(ax, 109, 12, 27, 62, "GIAI ĐOẠN 3: ĐỀ XUẤT", bg="#EFF6FF", border="#93C5FD")

draw_box(ax, 111, 46, 23, 23, "#FFFFFF", "#2563EB", "Xếp hạng Laptop", [
    "Sắp xếp theo C_i giảm dần:",
    "C_1 ≥ C_2 ≥ ... ≥ C_m",
    "-------------------",
    "Điểm C_i thể hiện",
    "mức độ tối ưu tương đối",
    "so với hồ sơ nhu cầu"
])

draw_arrow(ax, 122.5, 46, 122.5, 40)

draw_box(ax, 111, 15, 23, 25, "#FFFFFF", "#2563EB", "Top Khuyến nghị", [
    "• Top 1: Laptop tối ưu nhất",
    "• Top 2, Top 3...",
    "-------------------",
    "Hỗ trợ xem giải thích",
    "và tùy chọn kết hợp ML",
    "(0.85×TOPSIS + 0.15×ML)"
])

# Title caption underneath
ax.text(
    70, 5.5,
    "Hình 2.2. Quy trình lọc cứng, xác định trọng số AHP và xếp hạng TOPSIS",
    ha='center', va='center',
    fontsize=12, fontweight='bold', color='#0F172A'
)

plt.tight_layout()
out1 = "data/reports/figures/02_quy_trinh_loc_cung_ahp_topsis.png"
plt.savefig(out1, dpi=300, bbox_inches='tight')
print(f"Saved to {out1}")
