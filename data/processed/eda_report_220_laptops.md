# BÁO CÁO PHÂN TÍCH KHÁM PHÁ DỮ LIỆU (EDA REPORT)
## Giai Đoạn 3: Khảo Sát Dữ Liệu & Chốt Tiêu Chí Học Thuật (220 Laptops)

**Ngày thực hiện:** 11/10/2026  
**Quy mô tập mẫu:** 220 laptop chuẩn hóa (CellphoneS + FPT Shop)  
**Tiêu chuẩn khoa học:** Tuân thủ DECISIONS.md (D05, D06, D08, D14, D20, D21) & Chuongtrinh.md GĐ3.

---

## 1. Phân Phối Thống Kê Giá Bán & Thông Số Kỹ Thuật

| Chỉ số kỹ thuật | Số lượng mẫu | Giá trị Min | Giá trị Max | Trung bình (Mean) | Trung vị (Median) | Độ lệch chuẩn (Std) | Độ trải giữa (IQR) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Giá bán (`sale_price_vnd`)** | 220 | 8,790,000 đ | 133,990,000 đ | 38,744,632 đ | 30,990,000 đ | 22,211,612 đ | 18,125,000 đ |
| **Dung lượng RAM (`ram_gb`)** | 220 | 8 GB | 128 GB | 19.1 GB | 16 GB | 11.3 GB | 0 GB |
| **Dung lượng SSD (`storage_total_gb`)** | 220 | 256 GB | 2048 GB | 665.6 GB | 512 GB | 295.3 GB | 512 GB |
| **Trọng lượng (`weight_kg`)** | 214 | 0.98 kg | 2.70 kg | 1.70 kg | 1.65 kg | 0.37 kg | 0.58 kg |
| **CPU Geekbench 6 Multi-Core** | 188 | 3,100 | 26,000 | 11,408 | 10,500 | 3,571 | 3,300 |
| **CPU Geekbench 6 Single-Core** | 188 | 980 | 3,900 | 2,492 | 2,500 | 379 | 292 |

> [!NOTE]
> Phân phối giá bán có trung vị **30,990,000 VNĐ** và IQR **18,125,000 VNĐ** (Q1: 24,990,000 VNĐ đến Q3: 43,115,000 VNĐ). Mẫu bao phủ hoàn chỉnh từ phân khúc phổ thông sinh viên (8,790,000 VNĐ) cho đến phân khúc máy trạm / gaming đỉnh cao (133,990,000 VNĐ). 100% số liệu được tính toán động trực tiếp từ tập mẫu thực tế.

---

## 2. Phân Tích Tương Quan & Bằng Chứng Học Thuật

### 2.1. Tương quan Đơn nhân vs. Đa nhân (Geekbench 6)
* **Hệ số tương quan Pearson:** $\rho = 0.8954$ (Tương quan dương rất mạnh).
* **Kết luận phương pháp luận (Bảo vệ DECISIONS.md D20 & D08):**
  - Do $\rho \approx 0.8954 \ge 0.85$, nếu đưa đồng thời cả CPU Single-Core và CPU Multi-Core vào cùng một ma trận AHP, hệ thống sẽ phạm lỗi **đa cộng tuyến (multicollinearity)** và đếm trùng tác động của bộ vi xử lý lên gấp đôi.
  - Giải pháp khoa học đã thực hiện: **Thay thế chứ không bổ sung** — Profile *Sinh viên & Kinh tế* sử dụng Single-Core (phù hợp tải văn phòng/duyệt web); Profile *Kỹ thuật & Lập trình* và *Gaming* sử dụng Multi-Core (phù hợp tải biên dịch mã nguồn và render 3D).

### 2.2. Tương quan Giá bán vs. Sức mạnh Phần cứng
* **Tương quan Giá bán & CPU Multi-Core:** $\rho = 0.781$.
* Giá bán có xu hướng tăng tỷ lệ thuận với năng lực tính toán của CPU và sự xuất hiện của GPU rời công suất cao.

---

## 3. Cân Bằng Thị Trường: Thương Hiệu & Hệ Điều Hành

### 3.1. Phân bổ thương hiệu
- **Lenovo:** 49 máy (22.3%)
- **Asus:** 45 máy (20.5%)
- **Apple:** 41 máy (18.6%)
- **MSI:** 31 máy (14.1%)
- **Acer:** 26 máy (11.8%)
- **Dell:** 26 máy (11.8%)
- **HP:** 2 máy (0.9%)

### 3.2. Phân bổ hệ điều hành
- **Windows:** 180 máy (81.8%)
- **macOS:** 40 máy (18.2%)

---

## 4. Bảng Tổng Hợp Tiêu Chí Chính Thức (Chốt Tiêu Chuẩn V1)

Dựa trên ngưỡng phủ $\ge 80\%$ theo DECISIONS.md D14:

| Mã | Tiêu chí | Độ phủ thật | Đạt chuẩn D14 | Vai trò trong DSS | Lý do khoa học |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **C01** | Giá bán hiện tại (sale_price_vnd) | 100.0% (220/220) | **YES** | core_topsis | Ràng buộc ngân sách và tiêu chí cost cốt lõi trong toàn bộ preset. |
| **C02** | Hiệu năng CPU đa nhân (cpu_benchmark_multi_core) | 85.5% (188/220) | **YES** | core_topsis | Geekbench 6 Multi-Core. Trừ 32 máy chip chưa công bố/unreleased để trống theo D14. |
| **C02b** | Hiệu năng CPU đơn nhân (cpu_benchmark_single_core) | 85.5% (188/220) | **YES** | core_topsis | Geekbench 6 Single-Core. Áp dụng cho profile Sinh viên/Kinh tế theo D20. |
| **C03** | Hiệu năng GPU đồ họa (gpu_benchmark_time_spy) | 98.7% (74/75 (dGPU)) | **YES** | profile_core | 3DMark Time Spy Graphics. 100% máy Windows dGPU có điểm theo TGP. |
| **C04** | Dung lượng RAM (ram_gb) | 100.0% (220/220) | **YES** | core_topsis | Chuẩn hóa theo hàm hữu dụng Fit (bão hòa theo nhu cầu, tránh thiên vị vô lý). |
| **C05** | Khả năng nâng cấp RAM (ram_slots) | 66.8% (147/220) | **NO** | display_only | Độ phủ ~60%. Dùng làm bộ lọc tiện ích (Secondary Filter), chưa đưa vào ma trận AHP lõi. |
| **C06** | Dung lượng lưu trữ SSD (storage_total_gb) | 100.0% (220/220) | **YES** | core_topsis | Dung lượng thật (bỏ qua thông số nâng cấp tối đa). Hàm hữu dụng Fit. |
| **C07** | Công nghệ lưu trữ (storage_primary_type) | 75.9% (167/220) | **NO** | display_only | Hầu hết là SSD NVMe PCIe; hiển thị chi tiết. |
| **C08** | Độ phân giải màn hình (screen_width_px) | 100.0% (220/220) | **YES** | hard_filter | Dùng làm tiêu chí lọc giao diện (FHD, WUXGA, 2K, 3K), không gán điểm cảm tính. |
| **C09** | Kích thước màn hình (screen_size_inch) | 100.0% (220/220) | **YES** | hard_filter | Dùng làm bộ lọc kích thước (14 inch, 15.6 inch, 16 inch). |
| **C10** | Tần số quét màn hình (refresh_rate_hz) | 6.4% (14/220) | **NO** | hard_filter | Hard filter bắt buộc (>= 144Hz) cho preset Gaming. |
| **C11** | Dung lượng pin danh định (battery_capacity_wh) | 79.5% (175/220) | **NO** | display_only | D07/D16 không chấm điểm thời lượng pin bằng Wh danh định trong V1. |
| **C12** | Trọng lượng máy (weight_kg) | 97.3% (214/220) | **YES** | core_topsis | Tiêu chí cost cho sinh viên; hard filter <= 1.45kg cho profile Mỏng nhẹ. |
| **C13** | Độ sáng màn hình (brightness_nits) | 81.4% (179/220) | **YES** | display_only | Dùng làm bộ lọc tiện ích (>= 300 nits) theo D21. |
| **C14** | Công nghệ tấm nền OLED (panel_type) | 16.8% (37/220) | **NO** | hard_filter | Không đạt 80% D14 -> Dùng làm bộ lọc tùy chọn OLED cho người dùng có nhu cầu. |
| **C15** | Hệ điều hành tích hợp (os_name) | 100.0% (220/220) | **YES** | hard_filter | Hard filter tiên quyết cho phần mềm chuyên ngành (Windows vs macOS). |
| **C16** | Cổng kết nối phong phú (hdmi_present) | 98.6% (217/220) | **YES** | display_only | Hiển thị chi tiết cổng Type-C, Type-A, HDMI, Jack Audio. |
| **C17** | Thời gian bảo hành (warranty_months) | 100.0% (220/220) | **YES** | display_only | Hiển thị chính sách bảo hành chính hãng 12-24 tháng. |
| **C18** | Định giá ML / P/P (ml_price_pred) | 0.0% (0/220) | **NO** | excluded_v1 | DECISIONS.md D10: Giữ ở mô hình ML độc lập, cấm đưa vào TOPSIS tránh đếm đôi giá. |
| **C19** | Năng lực AI on-device (NPU) (npu_tops) | 34.1% (75/220) | **NO** | display_only | D15: Thang đo chưa chuẩn hóa chéo hãng -> Bộ lọc/Mô tả. |
