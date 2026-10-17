# BÁO CÁO PHÂN TÍCH KHÁM PHÁ DỮ LIỆU (EDA REPORT)
## Giai Đoạn 3: Khảo Sát Dữ Liệu & Chốt Tiêu Chí Học Thuật (513 Laptops)

**Ngày thực hiện:** 11/10/2026  
**Quy mô tập mẫu:** 513 laptop chuẩn hóa (CellphoneS + FPT Shop)  
**Tiêu chuẩn khoa học:** Tuân thủ DECISIONS.md (D05, D06, D08, D14, D20, D21) & Chuongtrinh.md GĐ3.

---

## 1. Phân Phối Thống Kê Giá Bán & Thông Số Kỹ Thuật

| Chỉ số kỹ thuật | Số lượng mẫu | Giá trị Min | Giá trị Max | Trung bình (Mean) | Trung vị (Median) | Độ lệch chuẩn (Std) | Độ trải giữa (IQR) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Giá bán (`sale_price_vnd`)** | 513 | 8,790,000 đ | 199,990,000 đ | 37,263,587 đ | 29,590,000 đ | 22,450,906 đ | 18,000,000 đ |
| **Dung lượng RAM (`ram_gb`)** | 513 | 8 GB | 128 GB | 19.6 GB | 16 GB | 11.8 GB | 0 GB |
| **Dung lượng SSD (`storage_total_gb`)** | 513 | 256 GB | 2048 GB | 633.8 GB | 512 GB | 272.7 GB | 0 GB |
| **Trọng lượng (`weight_kg`)** | 513 | 0.89 kg | 98.00 kg | 2.96 kg | 1.66 kg | 10.70 kg | 0.59 kg |
| **CPU Geekbench 6 Multi-Core** | 439 | 3,100 | 26,000 | 11,390 | 10,500 | 3,281 | 3,550 |
| **CPU Geekbench 6 Single-Core** | 439 | 980 | 3,900 | 2,486 | 2,500 | 357 | 330 |

> [!NOTE]
> Phân phối giá bán có trung vị **29,590,000 VNĐ** và IQR **18,000,000 VNĐ** (Q1: 23,990,000 VNĐ đến Q3: 41,990,000 VNĐ). Mẫu bao phủ hoàn chỉnh từ phân khúc phổ thông sinh viên (8,790,000 VNĐ) cho đến phân khúc máy trạm / gaming đỉnh cao (199,990,000 VNĐ). 100% số liệu được tính toán động trực tiếp từ tập mẫu thực tế.

---

## 2. Phân Tích Tương Quan & Bằng Chứng Học Thuật

### 2.1. Tương quan Đơn nhân vs. Đa nhân (Geekbench 6)
* **Hệ số tương quan Pearson:** $\rho = 0.8727$ (Tương quan dương rất mạnh).
* **Kết luận phương pháp luận (Bảo vệ DECISIONS.md D20 & D08):**
  - Do $\rho \approx 0.8727 \ge 0.85$, nếu đưa đồng thời cả CPU Single-Core và CPU Multi-Core vào cùng một ma trận AHP, hệ thống sẽ phạm lỗi **đa cộng tuyến (multicollinearity)** và đếm trùng tác động của bộ vi xử lý lên gấp đôi.
  - Giải pháp khoa học đã thực hiện: **Thay thế chứ không bổ sung** — Profile *Sinh viên & Kinh tế* sử dụng Single-Core (phù hợp tải văn phòng/duyệt web); Profile *Kỹ thuật & Lập trình* và *Gaming* sử dụng Multi-Core (phù hợp tải biên dịch mã nguồn và render 3D).

### 2.2. Tương quan Giá bán vs. Sức mạnh Phần cứng
* **Tương quan Giá bán & CPU Multi-Core:** $\rho = 0.6859$.
* Giá bán có xu hướng tăng tỷ lệ thuận với năng lực tính toán của CPU và sự xuất hiện của GPU rời công suất cao.

---

## 3. Cân Bằng Thị Trường: Thương Hiệu & Hệ Điều Hành

### 3.1. Phân bổ thương hiệu
- **Asus:** 137 máy (26.7%)
- **Lenovo:** 132 máy (25.7%)
- **Acer:** 65 máy (12.7%)
- **HP:** 55 máy (10.7%)
- **Dell:** 49 máy (9.6%)
- **MSI:** 48 máy (9.4%)
- **Gigabyte:** 11 máy (2.1%)
- **Apple:** 10 máy (1.9%)
- **Khác:** 6 máy (1.2%)

### 3.2. Phân bổ hệ điều hành
- **Windows:** 504 máy (98.2%)
- **macOS:** 9 máy (1.8%)

---

## 4. Bảng Tổng Hợp Tiêu Chí Chính Thức (Chốt Tiêu Chuẩn V1)

Dựa trên ngưỡng phủ $\ge 80\%$ theo DECISIONS.md D14:

| Mã | Tiêu chí | Độ phủ thật | Đạt chuẩn D14 | Vai trò trong DSS | Lý do khoa học |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **C01** | Giá bán hiện tại (sale_price_vnd) | 100.0% (513/513) | **YES** | core_topsis | Ràng buộc ngân sách và tiêu chí cost cốt lõi trong toàn bộ preset. |
| **C02** | Hiệu năng CPU đa nhân (cpu_benchmark_multi_core) | 85.6% (439/513) | **YES** | core_topsis | Geekbench 6 Multi-Core. Trừ 74 máy chip chưa công bố/unreleased để trống theo D14. |
| **C02b** | Hiệu năng CPU đơn nhân (cpu_benchmark_single_core) | 85.6% (439/513) | **YES** | core_topsis | Geekbench 6 Single-Core. Áp dụng cho profile Sinh viên/Kinh tế theo D20. |
| **C03** | Hiệu năng GPU đồ họa (gpu_benchmark_time_spy) | 99.4% (163/164 (dGPU)) | **YES** | profile_core | 3DMark Time Spy Graphics. 100% máy Windows dGPU có điểm theo TGP. |
| **C04** | Dung lượng RAM (ram_gb) | 100.0% (513/513) | **YES** | core_topsis | Chuẩn hóa theo hàm hữu dụng Fit (bão hòa theo nhu cầu, tránh thiên vị vô lý). |
| **C05** | Khả năng nâng cấp RAM (ram_slots) | 78.4% (402/513) | **NO** | display_only | Độ phủ ~60%. Dùng làm bộ lọc tiện ích (Secondary Filter), chưa đưa vào ma trận AHP lõi. |
| **C06** | Dung lượng lưu trữ SSD (storage_total_gb) | 100.0% (513/513) | **YES** | core_topsis | Dung lượng thật (bỏ qua thông số nâng cấp tối đa). Hàm hữu dụng Fit. |
| **C07** | Công nghệ lưu trữ (storage_primary_type) | 95.3% (489/513) | **YES** | display_only | Hầu hết là SSD NVMe PCIe; hiển thị chi tiết. |
| **C08** | Độ phân giải màn hình (screen_width_px) | 100.0% (513/513) | **YES** | hard_filter | Dùng làm tiêu chí lọc giao diện (FHD, WUXGA, 2K, 3K), không gán điểm cảm tính. |
| **C09** | Kích thước màn hình (screen_size_inch) | 99.8% (512/513) | **YES** | hard_filter | Dùng làm bộ lọc kích thước (14 inch, 15.6 inch, 16 inch). |
| **C10** | Tần số quét màn hình (refresh_rate_hz) | 84.0% (431/513) | **YES** | hard_filter | Hard filter bắt buộc (>= 144Hz) cho preset Gaming. |
| **C11** | Dung lượng pin danh định (battery_capacity_wh) | 96.9% (497/513) | **YES** | display_only | D07/D16 không chấm điểm thời lượng pin bằng Wh danh định trong V1. |
| **C12** | Trọng lượng máy (weight_kg) | 100.0% (513/513) | **YES** | core_topsis | Tiêu chí cost cho sinh viên; hard filter <= 1.45kg cho profile Mỏng nhẹ. |
| **C13** | Độ sáng màn hình (brightness_nits) | 79.1% (406/513) | **NO** | display_only | Dùng làm bộ lọc tiện ích (>= 300 nits) theo D21. |
| **C14** | Công nghệ tấm nền OLED (panel_type) | 95.3% (489/513) | **YES** | hard_filter | Không đạt 80% D14 -> Dùng làm bộ lọc tùy chọn OLED cho người dùng có nhu cầu. |
| **C15** | Hệ điều hành tích hợp (os_name) | 100.0% (513/513) | **YES** | hard_filter | Hard filter tiên quyết cho phần mềm chuyên ngành (Windows vs macOS). |
| **C16** | Cổng kết nối phong phú (hdmi_present) | 99.8% (512/513) | **YES** | display_only | Hiển thị chi tiết cổng Type-C, Type-A, HDMI, Jack Audio. |
| **C17** | Thời gian bảo hành (warranty_months) | 99.0% (508/513) | **YES** | display_only | Hiển thị chính sách bảo hành chính hãng 12-24 tháng. |
| **C18** | Định giá ML / P/P (ml_price_pred) | 0.0% (0/513) | **NO** | excluded_v1 | DECISIONS.md D10: Giữ ở mô hình ML độc lập, cấm đưa vào TOPSIS tránh đếm đôi giá. |
| **C19** | Năng lực AI on-device (NPU) (npu_tops) | 44.6% (229/513) | **NO** | display_only | D15: Thang đo chưa chuẩn hóa chéo hãng -> Bộ lọc/Mô tả. |
