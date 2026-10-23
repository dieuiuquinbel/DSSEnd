import matplotlib.pyplot as plt
import matplotlib.patches as patches

# Setup figure with high resolution
plt.rcParams['font.family'] = 'Segoe UI'
plt.rcParams['font.sans-serif'] = ['Segoe UI', 'Arial', 'DejaVu Sans']

fig, ax = plt.subplots(figsize=(15, 8.5), dpi=300)
ax.set_xlim(0, 150)
ax.set_ylim(0, 85)
ax.axis('off')

# Background
fig.patch.set_facecolor('#FFFFFF')
ax.set_facecolor('#FFFFFF')

def draw_card(ax, x, y, w, h, bg_color, border_color, title, subtitle_list=None, title_color="#0F172A", title_size=10.5, text_size=8.8, corner_radius=1.8):
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
        start_y = t_y - 2.6
        avail_h = h - 4.5
        line_height = avail_h / max(len(subtitle_list), 1)
        for i, text in enumerate(subtitle_list):
            curr_y = start_y - i * line_height
            ax.text(x + w/2, curr_y, text, ha='center', va='center', fontsize=text_size, color='#334155', zorder=3)

def draw_arrow(ax, x1, y1, x2, y2, color="#64748B", style="->", rad=0.0):
    conn = f"arc3,rad={rad}" if rad != 0.0 else "arc3"
    ax.annotate(
        "", xy=(x2, y2), xytext=(x1, y1),
        arrowprops=dict(
            arrowstyle="->,head_length=0.42,head_width=0.28",
            connectionstyle=conn,
            color=color,
            lw=1.8,
            shrinkA=2,
            shrinkB=2,
            mutation_scale=13
        ),
        zorder=1
    )

# Header Section Boxes / Background zones
def draw_phase_zone(ax, x, y, w, h, bg_color, border_color, label):
    zone = patches.FancyBboxPatch(
        (x, y), w, h,
        boxstyle="round,pad=0,rounding_size=2.5",
        facecolor=bg_color,
        edgecolor=border_color,
        linewidth=1.2,
        linestyle="--",
        alpha=0.6,
        zorder=0
    )
    ax.add_patch(zone)
    ax.text(x + 3, y + h - 2.8, label, fontsize=10.5, fontweight='bold', color=border_color, zorder=1)

# Zone 1: Giai đoạn 1 & 2 (Lọc cứng & AHP)
draw_phase_zone(ax, 3, 10, 42, 68, "#F8FAFC", "#64748B", "PHẦN 1: TIỀN XỬ LÝ & TRỌNG SỐ")

# Zone 2: Quy trình TOPSIS
draw_phase_zone(ax, 48, 10, 68, 68, "#F0FDF4", "#16A34A", "PHẦN 2: QUY TRÌNH THUẬT TOÁN TOPSIS")

# Zone 3: Kết quả xếp hạng
draw_phase_zone(ax, 119, 10, 28, 68, "#EFF6FF", "#2563EB", "PHẦN 3: KẾT QUẢ ĐỀ XUẤT")

# --- 1. Nhánh Lọc cứng (Hard Constraints) ---
draw_card(ax, 6, 61, 36, 12, "#FEF2F2", "#DC2626", "1. Yêu cầu & Ràng buộc cứng", [
    "Ngân sách (min - max)",
    "Hãng, RAM min, Ổ cứng min, Trọng lượng..."
])

draw_card(ax, 6, 44, 36, 13, "#FFF7ED", "#EA580C", "2. Bộ lọc cứng (Hard Filter)", [
    "Lọc trên Catalog 513 cấu hình laptop",
    "Loại bỏ các máy vi phạm ràng buộc",
    "→ Thu được m phương án hợp lệ (m ≤ 513)"
])

draw_arrow(ax, 24, 61, 24, 57)

# --- 2. Nhánh AHP xác định trọng số ---
draw_card(ax, 6, 13, 36, 26, "#FAF5FF", "#9333EA", "3. Xác định trọng số AHP", [
    "Chọn 1 trong 4 Hồ sơ nhu cầu",
    "(Kinh tế / CNTT / Đồ họa / Văn phòng)",
    "Ma trận so sánh cặp (Saaty) các tiêu chí",
    "Tính vector riêng chuẩn hóa:",
    "W = [w_1, w_2, ..., w_n] với ∑ w_j = 1",
    "Kiểm tra nhất quán: CR = CI / RI < 0.10"
])

# Arrow from Filtered Alternatives to Decision Matrix
draw_arrow(ax, 42, 50.5, 51, 50.5, color="#EA580C")

# --- 3. QUY TRÌNH TOPSIS (Cột giữa) ---
# Bước 1: Ma trận quyết định
draw_card(ax, 51, 44, 30, 13, "#FFFFFF", "#0284C7", "Bước 1: Ma trận quyết định", [
    "X = [x_ij] (m phương án × n tiêu chí)",
    "CPU, GPU, RAM, Ổ cứng,",
    "Trọng lượng, Pin, Giá bán..."
])

# Arrow from AHP weights to Step 3
# Arrow Step 1 to Step 2
draw_arrow(ax, 66, 44, 66, 38)

# Bước 2: Chuẩn hóa vector
draw_card(ax, 51, 25, 30, 13, "#FFFFFF", "#0284C7", "Bước 2: Chuẩn hóa vector", [
    "r_ij = x_ij / √(∑_i x_ij²)",
    "Đưa tất cả tiêu chí về khoảng [0, 1]",
    "Khử đơn vị đo lường khác nhau"
])

# Arrow from Step 2 to Step 3
draw_arrow(ax, 81, 31.5, 87, 31.5)
# Arrow from AHP to Step 3
draw_arrow(ax, 42, 24, 87, 24, color="#9333EA", rad=-0.15)

# Bước 3: Nhân trọng số AHP
draw_card(ax, 87, 21, 26, 15, "#FFFFFF", "#16A34A", "Bước 3: Ma trận có trọng số", [
    "v_ij = w_j × r_ij",
    "Kết hợp ma trận chuẩn hóa r_ij",
    "với vector trọng số AHP (w_j)"
])

# Arrow Step 3 up to Step 4
draw_arrow(ax, 100, 36, 100, 42)

# Bước 4: Nghiệm lý tưởng A+ và A-
draw_card(ax, 85, 42, 28, 16, "#FFFFFF", "#16A34A", "Bước 4: Nghiệm lý tưởng", [
    "• Lý tưởng tốt (A+):",
    "  max Benefit, min Cost (Giá)",
    "• Lý tưởng xấu (A-):",
    "  min Benefit, max Cost (Giá)"
])

# Arrow Step 4 up to Step 5
draw_arrow(ax, 100, 58, 100, 62)

# Bước 5 & 6: Tính khoảng cách & Điểm phù hợp
draw_card(ax, 51, 62, 62, 13, "#FFFFFF", "#059669", "Bước 5 & 6: Khoảng cách Euclid & Điểm phù hợp C_i", [
    "Khoảng cách:  S_i+ = √∑(v_ij - v_j+)²   |   S_i- = √∑(v_ij - v_j-)²",
    "Độ gần lý tưởng tương đối:   C_i = S_i- / (S_i+ + S_i-) trong [0, 1]",
    "C_i càng gần 1 -> Máy càng tiệm cận cấu hình lý tưởng tốt nhất"
])

# Arrow from Step 4 to Step 5-6
draw_arrow(ax, 99, 58, 99, 62)

# Arrow from Step 5-6 to Phase 3 (Output)
draw_arrow(ax, 113, 68.5, 122, 68.5, color="#2563EB")

# --- 4. KẾT QUẢ ĐỀ XUẤT (Cột phải) ---
draw_card(ax, 122, 47, 22, 26, "#EFF6FF", "#2563EB", "Xếp hạng TOPSIS", [
    "Sắp xếp giảm dần:",
    "C_1 ≥ C_2 ≥ ... ≥ C_m",
    "-------------------",
    "Điểm C_i phản ánh",
    "mức độ phù hợp nhu cầu",
    "và ràng buộc người dùng"
])

draw_arrow(ax, 133, 47, 133, 41)

draw_card(ax, 122, 17, 22, 24, "#F8FAFC", "#475569", "Danh sách khuyến nghị", [
    "#1: Laptop tối ưu nhất",
    "#2, #3: Phương án kế tiếp",
    "-------------------",
    "(Tùy chọn kết hợp ML:",
    "0.85×TOPSIS + 0.15×ML",
    "khi bật định giá)"
])

# Caption underneath
ax.text(
    75, 4,
    "Hình 2.x. Quy trình lọc cứng, xác định trọng số AHP và xếp hạng TOPSIS trong LaptopDSS",
    ha='center', va='center',
    fontsize=12, fontweight='bold', color='#1E293B'
)

plt.tight_layout()
output_path = "data/reports/figures/06_ahp_topsis_process.png"
plt.savefig(output_path, dpi=300, bbox_inches='tight')
print(f"Saved figure to {output_path}")
