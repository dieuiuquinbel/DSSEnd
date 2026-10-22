# BÁO CÁO TỔNG HỢP DỮ LIỆU & HIỆU NĂNG HỆ THỐNG DSS LAPTOP

Báo cáo tổng hợp toàn diện về danh mục dữ liệu 513 laptop thực tế, tỷ lệ bao phủ thông số kỹ thuật thu thập, cấu hình động cơ ra quyết định DSS (AHP-TOPSIS) và chỉ số mô hình học máy (Machine Learning).

---

## 1. Phân Bố Nguồn Dữ Liệu & Thương Hiệu (513 Laptops)

Dữ liệu được thu thập trực tiếp từ các chuỗi bán lẻ hàng đầu tại Việt Nam, trải qua quy trình xác thực SKU và chuẩn hóa nghiêm ngặt (tuân thủ nguyên tắc Không Bịa Đặt — Zero Fabrication, Strict NULL). Bảng dưới dùng quy tắc nhận diện thương hiệu của báo cáo EDA và tách Gigabyte thành một nhóm hiển thị riêng.

| Thương hiệu | CellphoneS | FPT Shop (Pilot) | Tổng số máy | Tỷ lệ (%) | Mức giá thấp nhất | Mức giá cao nhất |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **ASUS** | 134 | 3 | 137 | 26.71% | 15,290,000 đ | 199,990,000 đ |
| **Lenovo** | 131 | 1 | 132 | 25.73% | 14,590,000 đ | 119,000,000 đ |
| **Acer** | 64 | 1 | 65 | 12.67% | 13,490,000 đ | 115,000,000 đ |
| **HP** | 52 | 2 | 54 | 10.53% | 14,990,000 đ | 62,990,000 đ |
| **Dell** | 49 | 0 | 49 | 9.55% | 8,790,000 đ | 46,290,000 đ |
| **MSI** | 47 | 1 | 48 | 9.36% | 11,790,000 đ | 127,990,000 đ |
| **Gigabyte** | 12 | 0 | 12 | 2.34% | 26,990,000 đ | 42,590,000 đ |
| **Apple** | 10 | 0 | 10 | 1.95% | 18,590,000 đ | 102,490,000 đ |
| **Khác (LG, v.v.)** | 6 | 0 | 6 | 1.17% | 13,490,000 đ | 39,490,000 đ |
| **TỔNG CỘNG** | **505** | **8** | **513** | **100.00%** | **8,790,000 đ** | **199,990,000 đ** |

---

## 2. Tỷ Lệ Bao Phủ Thông Số Kỹ Thuật (Data Coverage Rates)

Số liệu đối chiếu thực tế sau khi làm giàu dữ liệu từ Nuxt State tĩnh. Các hàng ghi `505` chỉ áp dụng cho nguồn CellphoneS; các hàng ghi `513` là độ phủ trên toàn catalog chuẩn hóa.

| Trường thông số kỹ thuật | Số lượng có dữ liệu thật | Tỷ lệ bao phủ (%) | Phương thức trích xuất | Trạng thái bảo tồn |
| :--- | :---: | :---: | :--- | :--- |
| **Giá bán niêm yết & khuyến mãi** | 505 / 505 | 100.00% | DOM / JSON-LD / Nuxt State | Bắt buộc, không null |
| **Tên sản phẩm & SKU** | 505 / 505 | 100.00% | Catalog chính thức | Chuẩn hóa regex |
| **Kích thước màn hình (Screen size)** | 504 / 505 | 99.80% | Nuxt State `screen_size` | Strict NULL nếu thiếu |
| **Webcam** | 503 / 505 | 99.60% | Nuxt State `webcam` | Giữ nguyên độ phân giải thật |
| **Bluetooth version** | 501 / 505 | 99.21% | Nuxt State `bluetooth` | Trích xuất phiên bản (5.0 - 5.4) |
| **Thời hạn bảo hành (Warranty)** | 500 / 505 | 99.01% | Nuxt State `warranty` | Tháng bảo hành chính hãng (12 - 36) |
| **Loại tấm nền (Panel type - IPS/OLED/TN)** | 481 / 505 | 95.25% | Nuxt State spec groups | Trích xuất chuẩn (IPS, OLED, mini-LED) |
| **Tần số quét (Refresh rate Hz)** | 430 / 513 | 83.82% | Catalog chuẩn hóa | 60Hz, 120Hz, 144Hz, 165Hz, 240Hz |
| **Số khe RAM (RAM slots & upgradeability)** | 396 / 505 | 78.42% | Nuxt State memory group | Số khe rời / Onboard |
| **CPU Benchmark (Geekbench 6)** | 439 / 513 | 85.58% | Bảng mapping benchmark CPU | Chỉ chấm điểm khi có benchmark; 74 mẫu chưa có điểm được loại theo D14 khi CPU là tiêu chí lõi. |
| **GPU Benchmark (3DMark Time Spy)** | 163 / 513 tổng thể; 163 / 164 máy dGPU | 31.77% tổng thể; 99.39% dGPU | Bảng mapping benchmark GPU | Time Spy chỉ áp dụng GPU rời Windows; không gán điểm giả cho iGPU/macOS. |

---

## 3. Cấu Hình Động Cơ Ra Quyết Định DSS (AHP-TOPSIS Presets)

Hệ thống cung cấp 4 cấu hình nhu cầu chuyên biệt (Presets). Ma trận so sánh cặp đôi AHP được tính toán với Tỷ số Nhất quán ($CR < 0.10$) đảm bảo tính khoa học:

| Nhu cầu (Preset) | Tiêu chí đánh giá & Trọng số AHP | Tỷ số nhất quán ($CR$) | Ràng buộc loại trừ (Hard Constraints) |
| :--- | :--- | :---: | :--- |
| **1. Sinh viên & Kinh tế**<br>`student_budget` | - Giá bán (`cost`): **40.2%**<br>- CPU Single-Core (`benefit`): **24.5%**<br>- Dung lượng RAM (`fit`): **13.7%**<br>- Trọng lượng (`cost`): **13.7%**<br>- Ổ cứng SSD (`fit`): **7.9%** | $CR = 0.0074$<br>*(Đạt chuẩn < 0.10)* | Loại trừ máy có GPU rời nặng trên 1.85kg. Ưu tiên máy nhẹ, giá tiết kiệm, CPU đơn nhân mượt mà. |
| **2. Mỏng nhẹ & Di động**<br>`slim_mobility` | - Trọng lượng (`cost`): **42.5%**<br>- Giá bán (`cost`): **25.3%**<br>- CPU Multi-Core (`benefit`): **15.0%**<br>- Dung lượng RAM (`fit`): **9.9%**<br>- Ổ cứng SSD (`fit`): **7.2%** | $CR = 0.0164$<br>*(Đạt chuẩn < 0.10)* | **Trọng lượng $\le 1.45$ kg**. Ưu tiên di động tối đa cho giới văn phòng và doanh nhân. |
| **3. Kỹ thuật & Lập trình**<br>`technical_coding` | - CPU Multi-Core (`benefit`): **43.0%**<br>- Dung lượng RAM (`fit`): **26.0%**<br>- Giá bán (`cost`): **9.2%**<br>- Ổ cứng SSD (`fit`): **15.8%**<br>- Trọng lượng (`cost`): **6.1%** | $CR = 0.0152$<br>*(Đạt chuẩn < 0.10)* | **RAM tối thiểu 16 GB**. Ưu tiên hiệu năng đa nhân biên dịch mã nguồn, chạy máy ảo và container. |
| **4. Gaming & Đồ họa**<br>`gaming` | - GPU Time Spy (`benefit`): **41.7%**<br>- CPU Multi-Core (`benefit`): **26.3%**<br>- Giá bán (`cost`): **16.0%**<br>- Dung lượng RAM (`fit`): **9.7%**<br>- SSD (`fit`): **6.2%** | $CR = 0.0152$<br>*(Đạt chuẩn < 0.10)* | **Bắt buộc có GPU rời, Windows và màn hình $\ge 144$ Hz**. Tần số quét là ràng buộc khả thi, không chấm điểm trùng lặp. |

---

## 4. Hiệu Năng Mô Hình Học Máy Định Giá Thị Trường (Machine Learning)

Mô hình học máy hồi quy dự báo giá máy thị trường theo không gian logarit mục tiêu $\ln(\text{sale\_price\_vnd})$, thẩm định chéo bằng **Nested GroupKFold (5-Fold Outer, 3-Fold Inner)** chống rò rỉ dữ liệu cấu hình:

| Mô hình hồi quy | $R^2$ (VND gốc) | $R^2$ (Log Scale) | Sai số tuyệt đối trung bình (MAE) | Sai số phần trăm tuyệt đối (MAPE) |
| :--- | :---: | :---: | :---: | :---: |
| **Baseline (Mean Log-Price)** | -0.0417 | -0.0235 | 14,174,184 đ | 36.39% |
| **Linear Regression** | +0.8500 | +0.8313 | 5,378,828 đ | 14.34% |
| **Ridge Regression** | +0.8568 | +0.8398 | 5,324,052 đ | 14.25% |
| **K-Nearest Neighbors Regressor** | +0.7977 | +0.8144 | 5,822,125 đ | 14.56% |
| **Decision Tree Regressor** | +0.7861 | +0.7790 | 6,176,099 đ | 15.82% |
| **Random Forest Regressor** | +0.9023 | +0.8763 | 4,599,702 đ | 12.35% |
| **Gradient Boosting (Production)** | **+0.9034** | **+0.8776** | **4,544,510 đ** | **12.24%** |
| **LightGBM Regressor** | +0.8521 | +0.8674 | 4,877,961 đ | 12.48% |
| **XGBoost Regressor** | +0.9023 | +0.8807 | 4,357,567 đ | 11.93% |
| **MLP Regressor (ANN)** | +0.8406 | +0.8269 | 5,696,267 đ | 14.90% |

### Top 5 đặc trưng ảnh hưởng giá thị trường lớn nhất (SHAP Values):
1. **Độ sáng màn hình (`brightness_nits`)**: Điểm SHAP 0.0844 — phản ánh phân khúc màn hình cao cấp (OLED, HDR, >400 nits).
2. **Hiệu năng tính toán GPU (`gpu_benchmark_compute`)**: Điểm SHAP 0.0718 — dòng GPU RTX 40-series quyết định giá bán lớn.
3. **Dung lượng RAM (`ram_gb`)**: Điểm SHAP 0.0665 — các bản 16GB/32GB/64GB chênh lệch giá rõ rệt.
4. **Hiệu năng CPU đa nhân (`cpu_benchmark_multi`)**: Điểm SHAP 0.0631 — phân cấp Core i5/i7/i9 hoặc Ryzen 5/7/9.
5. **Dung lượng pin (`battery_capacity_wh`)**: Điểm SHAP 0.0526 — thể hiện phân khúc máy mỏng nhẹ cao cấp / workstation.
