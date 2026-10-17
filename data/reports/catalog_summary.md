# BÁO CÁO TỔNG HỢP DỮ LIỆU & HIỆU NĂNG HỆ THỐNG DSS LAPTOP

Báo cáo tổng hợp toàn diện về danh mục dữ liệu 513 laptop thực tế, tỷ lệ bao phủ thông số kỹ thuật thu thập, cấu hình động cơ ra quyết định DSS (AHP-TOPSIS) và chỉ số mô hình học máy (Machine Learning).

---

## 1. Phân Bố Nguồn Dữ Liệu & Thương Hiệu (513 Laptops)

Dữ liệu được thu thập trực tiếp từ các chuỗi bán lẻ hàng đầu tại Việt Nam, trải qua quy trình xác thực SKU và chuẩn hóa nghiêm ngặt (tuân thủ nguyên tắc Không Bịa Đặt — Zero Fabrication, Strict NULL).

| Thương hiệu | CellphoneS | FPT Shop (Pilot) | Tổng số máy | Tỷ lệ (%) | Mức giá thấp nhất | Mức giá cao nhất |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **ASUS** | 134 | 3 | 137 | 26.71% | 8,990,000 đ | 119,990,000 đ |
| **Lenovo** | 126 | 1 | 127 | 24.76% | 8,990,000 đ | 99,990,000 đ |
| **Acer** | 64 | 1 | 65 | 12.67% | 9,490,000 đ | 69,990,000 đ |
| **HP** | 58 | 2 | 60 | 11.70% | 8,790,000 đ | 74,990,000 đ |
| **Dell** | 49 | 0 | 49 | 9.55% | 8,990,000 đ | 89,990,000 đ |
| **MSI** | 47 | 1 | 48 | 9.36% | 11,990,000 đ | 109,990,000 đ |
| **Gigabyte** | 11 | 0 | 11 | 2.14% | 16,990,000 đ | 49,990,000 đ |
| **Apple** | 10 | 0 | 10 | 1.95% | 18,490,000 đ | 199,990,000 đ |
| **Khác (LG, v.v.)** | 6 | 0 | 6 | 1.17% | 14,990,000 đ | 39,990,000 đ |
| **TỔNG CỘNG** | **505** | **8** | **513** | **100.00%** | **8,790,000 đ** | **199,990,000 đ** |

---

## 2. Tỷ Lệ Bao Phủ Thông Số Kỹ Thuật (Data Coverage Rates)

Số liệu đối chiếu thực tế sau khi làm giàu dữ liệu từ Nuxt State tĩnh (CellphoneS 505 sản phẩm):

| Trường thông số kỹ thuật | Số lượng có dữ liệu thật | Tỷ lệ bao phủ (%) | Phương thức trích xuất | Trạng thái bảo tồn |
| :--- | :---: | :---: | :--- | :--- |
| **Giá bán niêm yết & khuyến mãi** | 505 / 505 | 100.00% | DOM / JSON-LD / Nuxt State | Bắt buộc, không null |
| **Tên sản phẩm & SKU** | 505 / 505 | 100.00% | Catalog chính thức | Chuẩn hóa regex |
| **Kích thước màn hình (Screen size)** | 504 / 505 | 99.80% | Nuxt State `screen_size` | Strict NULL nếu thiếu |
| **Webcam** | 503 / 505 | 99.60% | Nuxt State `webcam` | Giữ nguyên độ phân giải thật |
| **Bluetooth version** | 501 / 505 | 99.21% | Nuxt State `bluetooth` | Trích xuất phiên bản (5.0 - 5.4) |
| **Thời hạn bảo hành (Warranty)** | 500 / 505 | 99.01% | Nuxt State `warranty` | Tháng bảo hành chính hãng (12 - 36) |
| **Loại tấm nền (Panel type - IPS/OLED/TN)** | 481 / 505 | 95.25% | Nuxt State spec groups | Trích xuất chuẩn (IPS, OLED, mini-LED) |
| **Tần số quét (Refresh rate Hz)** | 424 / 505 | 83.96% | Nuxt State display group | 60Hz, 120Hz, 144Hz, 165Hz, 240Hz |
| **Số khe RAM (RAM slots & upgradeability)** | 396 / 505 | 78.42% | Nuxt State memory group | Số khe rời / Onboard |
| **CPU Benchmark (Geekbench 6)** | 511 / 513 | 99.61% | Bảng mapping benchmark CPU | Khớp mã chip chuẩn |
| **GPU Benchmark (3DMark Time Spy)** | 511 / 513 | 99.61% | Bảng mapping benchmark GPU | Khớp mã GPU rời / iGPU |

---

## 3. Cấu Hình Động Cơ Ra Quyết Định DSS (AHP-TOPSIS Presets)

Hệ thống cung cấp 4 cấu hình nhu cầu chuyên biệt (Presets). Ma trận so sánh cặp đôi AHP được tính toán với Tỷ số Nhất quán ($CR < 0.10$) đảm bảo tính khoa học:

| Nhu cầu (Preset) | Tiêu chí đánh giá & Trọng số AHP | Tỷ số nhất quán ($CR$) | Ràng buộc loại trừ (Hard Constraints) |
| :--- | :--- | :---: | :--- |
| **1. Sinh viên & Kinh tế**<br>`student_budget` | - Giá bán (`cost`): **41.8%**<br>- CPU Single-Core (`benefit`): **26.2%**<br>- Dung lượng RAM (`fit`): **13.5%**<br>- Trọng lượng (`cost`): **12.4%**<br>- Ổ cứng SSD (`fit`): **6.1%** | $CR = 0.0074$<br>*(Đạt chuẩn < 0.10)* | Loại trừ máy có GPU rời nặng trên 1.85kg. Ưu tiên máy nhẹ, giá tiết kiệm, CPU đơn nhân mượt mà. |
| **2. Mỏng nhẹ & Di động**<br>`slim_mobility` | - Trọng lượng (`cost`): **41.9%**<br>- Giá bán (`cost`): **26.1%**<br>- CPU Multi-Core (`benefit`): **16.0%**<br>- Dung lượng RAM (`fit`): **9.8%**<br>- Ổ cứng SSD (`fit`): **6.2%** | $CR = 0.0164$<br>*(Đạt chuẩn < 0.10)* | **Trọng lượng $\le 1.45$ kg**. Ưu tiên di động tối đa cho giới văn phòng và doanh nhân. |
| **3. Kỹ thuật & Lập trình**<br>`technical_coding` | - CPU Multi-Core (`benefit`): **44.3%**<br>- Dung lượng RAM (`fit`): **26.2%**<br>- Giá bán (`cost`): **14.2%**<br>- Ổ cứng SSD (`fit`): **9.3%**<br>- Trọng lượng (`cost`): **6.0%** | $CR = 0.0157$<br>*(Đạt chuẩn < 0.10)* | **RAM tối thiểu 16 GB**. Ưu tiên hiệu năng đa nhân biên dịch mã nguồn, chạy máy ảo và container. |
| **4. Gaming & Đồ họa**<br>`gaming` | - GPU Time Spy (`benefit`): **45.7%**<br>- CPU Multi-Core (`benefit`): **25.2%**<br>- Tần số quét màn hình (`benefit`): **14.1%**<br>- Giá bán (`cost`): **9.5%**<br>- Dung lượng RAM (`fit`): **5.5%** | $CR = 0.0125$<br>*(Đạt chuẩn < 0.10)* | **Bắt buộc có GPU rời (`gpu_type == 'discrete'`)**, tần số quét màn hình $\ge 120$ Hz, hệ điều hành Windows. |

---

## 4. Hiệu Năng Mô Hình Học Máy Định Giá Thị Trường (Machine Learning)

Mô hình học máy hồi quy dự báo giá máy thị trường theo không gian logarit mục tiêu $\ln(\text{sale\_price\_vnd})$, thẩm định chéo bằng **Nested GroupKFold (5-Fold Outer, 3-Fold Inner)** chống rò rỉ dữ liệu cấu hình:

| Mô hình hồi quy | $R^2$ (VND gốc) | $R^2$ (Log Scale) | Sai số tuyệt đối trung bình (MAE) | Sai số phần trăm tuyệt đối (MAPE) |
| :--- | :---: | :---: | :---: | :---: |
| **Baseline (Mean Log-Price)** | -0.0477 | -0.0265 | 14,201,323 đ | 36.51% |
| **Ridge Regression** | +0.8301 | +0.8397 | 5,350,938 đ | 13.96% |
| **Random Forest Regressor** | +0.8732 | +0.8610 | 4,650,295 đ | 12.42% |
| **Gradient Boosting (Production)** | **+0.8823** | **+0.8709** | **4,602,138 đ** | **12.16%** |
| **XGBoost Regressor** | +0.8811 | +0.8667 | 4,590,869 đ | 12.13% |
| **LightGBM Regressor** | +0.8258 | +0.8510 | 5,050,677 đ | 12.82% |

### Top 5 đặc trưng ảnh hưởng giá thị trường lớn nhất (SHAP Values):
1. **Độ sáng màn hình (`brightness_nits`)**: Điểm SHAP 0.0896 — phản ánh phân khúc màn hình cao cấp (OLED, HDR, >400 nits).
2. **Hiệu năng tính toán GPU (`gpu_benchmark_compute`)**: Điểm SHAP 0.0701 — dòng GPU RTX 40-series quyết định giá bán lớn.
3. **Hiệu năng CPU đa nhân (`cpu_benchmark_multi`)**: Điểm SHAP 0.0649 — phân cấp Core i5/i7/i9 hoặc Ryzen 5/7/9.
4. **Dung lượng RAM (`ram_gb`)**: Điểm SHAP 0.0547 — các bản 16GB/32GB/64GB chênh lệch giá rõ rệt.
5. **Dung lượng pin (`battery_capacity_wh`)**: Điểm SHAP 0.0484 — thể hiện phân khúc máy mỏng nhẹ cao cấp / workstation.
