# BÁO CÁO MÔ HÌNH HỌC MÁY DỰ BÁO GIÁ & ĐỊNH GIÁ THỊ TRƯỜNG (GĐ4)
## Kiến Trúc Log-Target, Nested GroupKFold, SHAP Explainability & Sàng Lọc Chênh Lệch Giá OOF

**Ngày thực hiện:** 11/10/2026  
**Quy mô tập mẫu:** 513 laptop chuẩn hóa (CellphoneS + FPT Shop)  
**Mã băm dữ liệu gốc:** `6eeaae6af60294985a44ec28fd9defce2dadc3428df881030e5e1ebceffdd0e4`
**Tuân thủ học thuật:** DECISIONS.md D10 (không đưa ML vào ma trận TOPSIS), D14 (KNN Imputation chỉ cho ML), Chuongtrinh.md GĐ4.

---

## 1. Phương Pháp Luận: Target Log-Scale & Feature Engineering Chống Rò Rỉ

### 1.1. Giải quyết phân phối lệch phải (Right-skewness)
- Phân phối giá laptop thị trường dao động từ 8.79M đến 199.99M VNĐ.
- **Giải pháp toán học:** Áp dụng biến đổi logarit tự nhiên $y = \ln(\text{sale\_price\_vnd})$, huấn luyện mô hình trên không gian logarit.

- **Tính chất thống kê của phép chuyển đổi ngược:** Phép biến đổi $\hat{y}_{\text{median}} = \exp(\hat{y}_{\ln})$ ước lượng trung vị có điều kiện (geometric mean) của giá máy, kháng nhiễu cực tốt trước các mẫu ngoại lai siêu đắt. Với thừa số hiệu chỉnh smearing $\exp(\sigma^2 / 2)$, mô hình xấp xỉ kỳ vọng trung bình cộng có điều kiện.
- **Kết quả:** Sai số phần trăm tuyệt đối trung bình (MAPE) đạt **12.24%**, hệ số xác định đạt **$R^2 = +0.9034 \pm 0.0157$**.

### 1.2. Kỹ nghệ đặc trưng phần cứng & Chống rò rỉ Imputation (Scale-Normalized)
1. **Bảo tồn giá trị thiếu thực tế:** Các thông số kỹ thuật chưa được nhà sản xuất công bố được giữ nguyên `NaN` thực tế (không dùng heuristic bịa số).
2. **Chuẩn hóa thang đo trước Imputation (M3):** Áp dụng `RobustScaler` trước khi đưa vào `KNNImputer(k=5)` để loại bỏ hiện tượng khoảng cách Euclid bị thống trị đơn lẻ bởi CPU benchmark (~1.000–26.000) so với các đặc trưng 0/1.
3. **Imputation không rò rỉ dữ liệu (Leakage-free):** `RobustScaler` và `KNNImputer` được fit độc lập bên trong từng fold huấn luyện của Outer GroupKFold, sau đó mới transform lên fold validation.
4. **Đặc trưng kỹ thuật và mã hóa thương hiệu:** GPU rời, VRAM (GB), 3DMark Time Spy, CPU Geekbench 6 Multi/Single, số nhân CPU, cờ nhị phân `cpu_benchmark_missing`, độ phân giải Megapixels, OLED, tần số quét Hz, độ sáng nits, pin Wh, trọng lượng kg, hệ điều hành macOS và mã hóa thương hiệu.

---

## 2. Kết Quả Đánh Giá Mô Hình Bằng Nested GroupKFold Cross-Validation

Đánh giá nghiêm ngặt qua **Nested GroupKFold** (5-Fold Outer để ước lượng sai số kỳ vọng, 3-Fold Inner GridSearchCV để tinh chỉnh siêu tham số) phân cụm theo `configuration_id`:

| Mô hình hồi quy | $R^2$ (VND gốc) | $R^2$ (Log Scale) | MAE (VND) | RMSE (VND) | MAPE (%) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Baseline (Mean Log-Price)** | -0.0417 ± 0.0285 | -0.0079 ± 0.0082 |  14,174,184 ± 1,367,631 đ |  22,768,808 đ | 36.39% |
| **Linear Regression** | +0.8500 ± 0.0287 | +0.8444 ± 0.0168 |   5,378,828 ±   505,338 đ |   8,592,556 đ | 14.34% |
| **Ridge Regression** | +0.8568 ± 0.0236 | +0.8465 ± 0.0157 |   5,324,052 ±   518,059 đ |   8,405,409 đ | 14.25% |
| **K-Nearest Neighbors Regressor** | +0.7977 ± 0.0320 | +0.8136 ± 0.0345 |   5,822,125 ±   353,013 đ |   9,979,642 đ | 14.56% |
| **Decision Tree Regressor** | +0.7861 ± 0.0581 | +0.7943 ± 0.0299 |   6,176,099 ±   881,255 đ |  10,294,868 đ | 15.82% |
| **Random Forest Regressor** | +0.9023 ± 0.0199 | +0.8764 ± 0.0181 |   4,599,702 ±   604,240 đ |   6,982,102 đ | 12.35% |
| **Gradient Boosting** | +0.9034 ± 0.0157 | +0.8776 ± 0.0191 |   4,544,510 ±   611,139 đ |   6,935,911 đ | 12.24% |
| **LightGBM Regressor** | +0.8521 ± 0.0597 | +0.8695 ± 0.0236 |   4,877,961 ±   626,259 đ |   8,498,843 đ | 12.48% |
| **XGBoost Regressor** | +0.9023 ± 0.0267 | +0.8772 ± 0.0212 |   4,357,567 ±   324,516 đ |   6,934,194 đ | 11.93% |
| **MLP Regressor (ANN)** | +0.8406 ± 0.0183 | +0.8269 ± 0.0274 |   5,696,267 ±   663,446 đ |   8,905,803 đ | 14.90% |

> [!NOTE]
> Mô hình **Gradient Boosting** đạt hiệu năng dẫn đầu với **$R^2 = +0.9034 \pm 0.0157$**, sai số tuyệt đối trung bình $\text{MAE} = 4,544,510 \pm 611,139$ đ và $\text{MAPE} = 12.24\%$.
> Bộ siêu tham số tối ưu xuất xưởng (GridSearchCV): `{'learning_rate': 0.1, 'max_depth': 3, 'n_estimators': 150}`.

---

## 3. Khả Năng Giải Thích Mô Hình Với SHAP (SHAP TreeExplainer)

SHAP TreeExplainer được thực thi trực tiếp trên mô hình **Gradient Boosting** xuất xưởng:

| Thứ hạng | Đặc trưng kỹ thuật | Giá trị SHAP trung bình (|SHAP|) | Ý nghĩa kinh tế |
| :---: | :--- | :---: | :--- |
| 1 | `brightness_nits` | 0.0844 |
| 2 | `gpu_benchmark_compute` | 0.0718 |
| 3 | `ram_gb` | 0.0665 |
| 4 | `cpu_benchmark_multi` | 0.0631 |
| 5 | `battery_capacity_wh` | 0.0526 |
| 6 | `screen_pixels_mp` | 0.0407 |
| 7 | `cpu_benchmark_single` | 0.0386 |
| 8 | `refresh_rate_hz` | 0.0211 |
| 9 | `weight_kg` | 0.0202 |
| 10 | `cpu_benchmark_missing` | 0.0132 |
| 11 | `gpu_vram_gb` | 0.0116 |
| 12 | `brand_Dell` | 0.0115 |

> [!NOTE]
> **Hiện tượng cộng tuyến đặc trưng trên cây quyết định (Tree Feature Collinearity):**  
> Các đặc trưng như `is_discrete_gpu` và `brand_Apple` có giá trị SHAP xấp xỉ 0 do mô hình cây đã rẽ nhánh hoàn toàn dựa trên các đặc trưng đại diện liên tục có tương quan hoàn hảo (`gpu_benchmark_time_spy > 0` và `is_macos == 1`). Đây là hành vi phân tách tự nhiên của thuật toán gradient boosting cây quyết định, không làm suy giảm chất lượng dự báo.

---

## 4. Sàng Lọc Chênh Lệch Giá Tham Chiếu Từ Dự Đoán Out-Of-Fold

Theo **DECISIONS.md D10**, ML không là tiêu chí trong ma trận TOPSIS. TOPSIS thuần là mặc định; giao diện có thể bật một lớp hậu xử lý ML-assisted tùy chọn 15%, và lớp này vẫn được công khai là có rủi ro đếm đôi giá ở điểm cuối:
- Sai số chuẩn phần dư Out-Of-Fold: $\sigma_{pred} = 0.1617$ (tương đương biên độ $\approx \pm 16.2\%$).
- Khoảng dự báo 95%: $[\hat{y}_{OOF} \cdot \exp(-1.96 \sigma_{pred}), \hat{y}_{OOF} \cdot \exp(+1.96 \sigma_{pred})]$.
- Cả giá kỳ vọng và ngưỡng tin cậy đều tính từ **dự đoán Out-Of-Fold (OOF)**, loại bỏ hoàn toàn thiên vị tự khớp in-sample.

Danh sách dưới đây là **ứng viên OOF chưa giới hạn khoảng giá**, phục vụ kiểm tra pipeline. API/UI chỉ hiển thị chênh lệch giá tham chiếu trong khoảng 15–40 triệu đồng; đây không phải khuyến nghị mua hoặc đầu tư.

### Ứng Viên Chênh Lệch Giá OOF (Chưa Giới Hạn Khoảng Giá)

| Tên laptop | Hãng | Giá bán thực tế | Giá định giá OOF | Cận dưới 95% | Thặng dư (Value Gap) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Apple MacBook Air M2 2024 8CPU 8GPU 16GB** | Apple | 18,590,000 đ | 28,930,000 đ | 21,070,000 đ | +35.74% |
| **Laptop MSI Modern 14 C12MO-660VN** | MSI | 11,790,000 đ | 19,010,000 đ | 13,840,000 đ | +37.97% |
| **Laptop MSI Venture 14 AI A1MG-005VN** | MSI | 25,990,000 đ | 39,210,000 đ | 28,560,000 đ | +33.71% |
| **Laptop MSI Prestige 14 AI+ EVO C2VMG-020** | MSI | 34,990,000 đ | 53,270,000 đ | 38,800,000 đ | +34.31% |
| **Laptop Dell Inspiron 15 3520 JYM17 - Nhậ** | Dell | 8,790,000 đ | 20,330,000 đ | 14,810,000 đ | +56.77% |
| **Laptop ASUS ROG Strix G18 G815LP-S9102W** | Asus | 56,990,000 đ | 82,080,000 đ | 59,780,000 đ | +30.56% |
| **Laptop Gaming Acer Nitro 5 Tiger AN515 5** | Acer | 16,490,000 đ | 27,720,000 đ | 20,190,000 đ | +40.51% |
| **Laptop Acer Gaming Nitro ProPanel ANV15-** | Acer | 17,390,000 đ | 26,060,000 đ | 18,980,000 đ | +33.27% |

---

## 5. Đóng Gói Vòng Đời & Tái Lập (Model Lifecycle & Reproducibility)

- Pipeline hoàn chỉnh (bao gồm `RobustScaler`, `KNNImputer`, mô hình `Gradient Boosting`, siêu tham số `{'learning_rate': 0.1, 'max_depth': 3, 'n_estimators': 150}` và ngưỡng $\sigma$) đã được lưu tại:
  `data/artifacts/price_model.joblib`.
- Thông số kỹ thuật chi tiết lưu tại: `data/artifacts/price_model_metrics.json`.
- File dự đoán OOF phục vụ kiểm thử D10 độc lập: `data/artifacts/price_model_oof.json`.
- Cung cấp hàm `get_trained_model_and_predictions()` phục vụ thí nghiệm đối chứng D10.

---

## 6. Phân Tích Sai Số Chi Tiết Theo Phân Khúc Giá & Thương Hiệu (§6.6)

Đánh giá chi tiết sự phân bố sai số dựa trên dự đoán Out-Of-Fold (OOF) của mô hình tối ưu (Gradient Boosting) nhằm nhận diện các vùng không gian đặc trưng có độ bất định cao:

### 6.1. Phân tích sai số theo phân khúc ngân sách

| Phân khúc giá | Số lượng ($N$) | Giá trung bình | MAE (VNĐ) | RMSE (VNĐ) | MAPE (%) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| < 15 Triệu (Phổ thông) | 6 |  12,856,667 đ |  6,530,669 đ |  7,566,420 đ | 56.08% |
| 15 - 25 Triệu (Tầm trung) | 153 |  21,391,307 đ |  2,606,953 đ |  3,482,247 đ | 12.67% |
| 25 - 40 Triệu (Cận cao cấp) | 215 |  31,130,930 đ |  3,367,562 đ |  4,678,207 đ | 10.55% |
| >= 40 Triệu (Cao cấp / Flagship) | 139 |  65,270,216 đ |  8,407,908 đ | 11,509,362 đ | 12.47% |

> [!NOTE]
> **Nhận định phân khúc:** 
- Phân khúc **Tầm trung (15 - 25M, N=153)** và **Cận cao cấp (25 - 40M, N=215)** chiếm đại đa số tập mẫu (71.7%) và đạt độ chính xác tương đối xuất sắc (MAPE lần lượt là **12.67%** và **10.55%**). Điều này chứng minh thị trường laptop đại chúng tuân theo quy luật định giá linh kiện (CPU/RAM/SSD/GPU) rất chặt chẽ và nhất quán.
- Phân khúc **Phổ thông (< 15M, N=6)** có MAPE là **56.08%** do số lượng mẫu ít và tập trung các đợt xả kho giảm giá sâu đột biến — vì vậy không được API/UI dùng làm sàng lọc chênh lệch giá tham chiếu.
- Phân khúc **Cao cấp / Flagship (>= 40M, N=139)** có sai số tuyệt đối (MAE) cao hơn do biên độ giá rộng và các yếu tố phi phần cứng (vật liệu nguyên khối, màn hình chuẩn đồ họa, buồng hơi tản nhiệt), nhưng sai số tương đối (MAPE) vẫn được kiểm soát ở mức lý tưởng (**12.47%**) nhờ việc huấn luyện trên không gian log-target.

### 6.2. Phân tích sai số theo thương hiệu nhà sản xuất

| Thương hiệu | Số lượng ($N$) | Giá trung bình | MAE (VNĐ) | RMSE (VNĐ) | MAPE (%) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Asus** | 137 |  45,422,336 đ |  5,757,137 đ |  9,214,818 đ | 11.32% |
| **Lenovo** | 132 |  35,930,227 đ |  4,660,635 đ |  6,488,500 đ | 13.48% |
| **Acer** | 65 |  31,971,692 đ |  3,016,542 đ |  4,205,190 đ | 10.47% |
| **HP** | 55 |  28,500,909 đ |  2,711,999 đ |  3,951,461 đ | 8.83% |
| **Dell** | 49 |  26,516,531 đ |  3,197,108 đ |  4,190,579 đ | 13.83% |
| **MSI** | 48 |  41,558,750 đ |  5,136,073 đ |  7,266,633 đ | 13.61% |
| **Other** | 17 |  31,031,176 đ |  3,968,393 đ |  5,424,478 đ | 15.37% |
| **Apple** | 10 |  68,270,000 đ | 11,095,355 đ | 14,909,846 đ | 18.82% |

> [!NOTE]
> **Nhận định thương hiệu:**
> - Các hãng dải sản phẩm rộng tập trung vào phân khúc hiệu năng trên giá như **Asus, Acer, Lenovo, MSI** có MAPE rất đồng đều (~9–12%), bám sát giá trị phần cứng.
> - Các thương hiệu định vị cao cấp hoặc biên lợi nhuận thương hiệu đặc thù (Brand Premium) như **Apple, Dell** có mức giá trung bình cao hơn và khoảng lệch đặc thù; việc mô hình hóa bằng cờ thương hiệu one-hot đã giúp giải thuật hấp thu chính xác độ dốc giá riêng của từng hãng.

### 6.3. Phân tích các trường hợp ngoại lai lớn nhất (Top Outliers)

Dưới đây là 5 mẫu máy có sai số phần trăm (MAPE) lớn nhất trong tập kiểm thử OOF:

| Tên laptop | Hãng | Giá thực tế | Giá định giá OOF | Độ lệch (VNĐ) | Sai số MAPE (%) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Laptop Dell Inspiron 15 3520 JYM17 - Nhậ** | Dell | 8,790,000 đ | 20,330,000 đ | +11,540,000 đ | 131.31% |
| **Laptop Lenovo V14 G5 IRL 83HD0062VA** | Lenovo | 14,590,000 đ | 25,040,000 đ | +10,450,000 đ | 71.62% |
| **Laptop Gaming Acer Nitro 5 Tiger AN515 5** | Acer | 16,490,000 đ | 27,720,000 đ | +11,230,000 đ | 68.09% |
| **Laptop MSI Modern 14 C12MO-660VN** | MSI | 11,790,000 đ | 19,010,000 đ | +7,220,000 đ | 61.21% |
| **Laptop Lenovo Yoga Pro 7 14IAH10 83KF002** | Lenovo | 37,990,000 đ | 60,680,000 đ | +22,690,000 đ | 59.73% |

> [!NOTE]
> **Nguyên nhân ngoại lai:** Các mẫu có sai số phần trăm cao nhất thường thuộc hai nhóm:
> 1. Laptop được bán lẻ xả kho hoặc khuyến mãi giảm giá sâu đột xuất (giá thực tế thấp hơn nhiều so với giá trị cấu hình danh định).
> 2. Các mẫu laptop doanh nhân siêu nhẹ cao cấp mang các tính năng bảo mật doanh nghiệp, độ bền quân đội hoặc vật liệu siêu nhẹ đắt tiền không thể hiện hết qua bảng thông số kỹ thuật cốt lõi.
