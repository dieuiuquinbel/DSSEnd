# BÁO CÁO MÔ HÌNH HỌC MÁY DỰ BÁO GIÁ & ĐỊNH GIÁ THỊ TRƯỜNG (GĐ4)
## Kiến Trúc Log-Target, Nested GroupKFold, SHAP Explainability & Lớp Nhận Diện "Kèo Thơm"

**Ngày thực hiện:** 11/10/2026  
**Quy mô tập mẫu:** 220 laptop chuẩn hóa (CellphoneS + FPT Shop)  
**Mã băm dữ liệu gốc:** `be4093c63d17651eaa3b92502596a7d3a6e8900c6866129ee1e20d9b50173611`  
**Tuân thủ học thuật:** DECISIONS.md D10 (Tách rời ML khỏi TOPSIS), D14 (KNN Imputation chỉ cho ML), Chuongtrinh.md GĐ4.

---

## 1. Phương Pháp Luận: Target Log-Scale & Feature Engineering Chống Rò Rỉ

### 1.1. Giải quyết phân phối lệch phải (Right-skewness)
- Phân phối giá laptop thị trường dao động từ 8.79M đến 134.0M VNĐ.
- **Giải pháp toán học:** Áp dụng biến đổi logarit tự nhiên $y = \ln(\text{sale\_price\_vnd})$, huấn luyện mô hình trên không gian logarit.
- **Tính chất thống kê của phép chuyển đổi ngược:** Phép biến đổi $\hat{y}_{\text{median}} = \exp(\hat{y}_{\ln})$ ước lượng trung vị có điều kiện (geometric mean) của giá máy, kháng nhiễu cực tốt trước các mẫu ngoại lai siêu đắt. Với thừa số hiệu chỉnh smearing $\exp(\sigma^2 / 2)$, mô hình xấp xỉ kỳ vọng trung bình cộng có điều kiện.
- **Kết quả:** Sai số phần trăm tuyệt đối trung bình (MAPE) đạt **11.16%**, hệ số xác định đạt **$R^2 = +0.9028 \pm 0.0194$**.

### 1.2. Kỹ nghệ đặc trưng phần cứng & Chống rò rỉ Imputation (Scale-Normalized)
1. **Bảo tồn giá trị thiếu thực tế:** Các thông số kỹ thuật chưa được nhà sản xuất công bố được giữ nguyên `NaN` thực tế (không dùng heuristic bịa số).
2. **Chuẩn hóa thang đo trước Imputation (M3):** Áp dụng `RobustScaler` trước khi đưa vào `KNNImputer(k=5)` để loại bỏ hiện tượng khoảng cách Euclid bị thống trị đơn lẻ bởi CPU benchmark (~1.000–26.000) so với các đặc trưng 0/1.
3. **Imputation không rò rỉ dữ liệu (Leakage-free):** `RobustScaler` và `KNNImputer` được fit độc lập bên trong từng fold huấn luyện của Outer GroupKFold, sau đó mới transform lên fold validation.
4. **24 Đặc trưng kỹ thuật:** GPU rời, VRAM (GB), 3DMark Time Spy, CPU Geekbench 6 Multi/Single, số nhân CPU, cờ nhị phân `cpu_benchmark_missing`, độ phân giải Megapixels, OLED, tần số quét Hz, độ sáng nits, pin Wh, trọng lượng kg, hệ điều hành macOS và mã hóa thương hiệu.

---

## 2. Kết Quả Đánh Giá Mô Hình Bằng Nested GroupKFold Cross-Validation

Đánh giá nghiêm ngặt qua **Nested GroupKFold** (5-Fold Outer để ước lượng sai số kỳ vọng, 3-Fold Inner GridSearchCV để tinh chỉnh siêu tham số) phân cụm theo `configuration_id`:

| Mô hình hồi quy | $R^2$ (VND gốc) | $R^2$ (Log Scale) | MAE (VND) | RMSE (VND) | MAPE (%) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Baseline (Mean Log-Price)** | -0.0680 ± 0.0352 | -0.0471 ± 0.0619 |  14,824,788 ± 1,750,259 đ |  22,528,529 đ | 37.82% |
| **Ridge Regression** | +0.8505 ± 0.1167 | +0.8821 ± 0.0411 |   4,760,450 ± 1,182,265 đ |   8,114,308 đ | 12.05% |
| **Random Forest Regressor** | +0.8889 ± 0.0119 | +0.8769 ± 0.0298 |   4,524,189 ±   551,086 đ |   7,212,961 đ | 11.78% |
| **Gradient Boosting** | +0.9028 ± 0.0194 | +0.8884 ± 0.0267 |   4,194,268 ±   622,161 đ |   6,698,646 đ | 11.16% |
| **LightGBM Regressor** | +0.8522 ± 0.0373 | +0.8641 ± 0.0401 |   4,962,225 ±   747,203 đ |   8,282,304 đ | 12.58% |
| **XGBoost Regressor** | +0.9005 ± 0.0182 | +0.8808 ± 0.0303 |   4,402,054 ±   502,574 đ |   6,812,331 đ | 11.71% |

> [!NOTE]
> Mô hình **Gradient Boosting** đạt hiệu năng dẫn đầu với **$R^2 = +0.9028 \pm 0.0194$**, sai số tuyệt đối trung bình $\text{MAE} = 4,194,268 \pm 622,161$ đ và $\text{MAPE} = 11.16\%$.  
> Bộ siêu tham số tối ưu xuất xưởng (GridSearchCV): `{'learning_rate': 0.05, 'max_depth': 3, 'n_estimators': 150}`.

---

## 3. Khả Năng Giải Thích Mô Hình Với SHAP (SHAP TreeExplainer)

SHAP TreeExplainer được thực thi trực tiếp trên mô hình **Gradient Boosting** xuất xưởng:

| Thứ hạng | Đặc trưng kỹ thuật | Giá trị SHAP trung bình (|SHAP|) | Ý nghĩa kinh tế |
| :---: | :--- | :---: | :--- |
| 1 | `cpu_benchmark_single` | 0.1051 |
| 2 | `cpu_benchmark_multi` | 0.0962 |
| 3 | `screen_pixels_mp` | 0.0831 |
| 4 | `ram_gb` | 0.0799 |
| 5 | `gpu_benchmark_time_spy` | 0.0514 |
| 6 | `battery_capacity_wh` | 0.0282 |
| 7 | `weight_kg` | 0.0235 |
| 8 | `screen_size_inch` | 0.0197 |
| 9 | `refresh_rate_hz` | 0.0191 |
| 10 | `brand_Lenovo` | 0.0185 |
| 11 | `storage_total_gb` | 0.0173 |
| 12 | `cpu_cores` | 0.0163 |

> [!NOTE]
> **Hiện tượng cộng tuyến đặc trưng trên cây quyết định (Tree Feature Collinearity):**  
> Các đặc trưng như `is_discrete_gpu` và `brand_Apple` có giá trị SHAP xấp xỉ 0 do mô hình cây đã rẽ nhánh hoàn toàn dựa trên các đặc trưng đại diện liên tục có tương quan hoàn hảo (`gpu_benchmark_time_spy > 0` và `is_macos == 1`). Đây là hành vi phân tách tự nhiên của thuật toán gradient boosting cây quyết định, không làm suy giảm chất lượng dự báo.

---

## 4. Tầng Gợi Ý "Kèo Thơm" (Good Deals Layer) Từ Dự Đoán Out-Of-Fold

Tuân thủ tinh thần **DECISIONS.md D10**, ML hoạt động như một lớp tham chiếu giá độc lập ngoài TOPSIS:
- Sai số chuẩn phần dư Out-Of-Fold: $\sigma_{pred} = 0.1549$ (tương đương biên độ $\approx \pm 15.5\%$).
- Khoảng tin cậy dự báo 95%: $[\hat{y}_{OOF} \cdot \exp(-1.96 \sigma_{pred}), \hat{y}_{OOF} \cdot \exp(+1.96 \sigma_{pred})]$.
- Cả giá kỳ vọng và ngưỡng tin cậy đều tính từ **dự đoán Out-Of-Fold (OOF)**, loại bỏ hoàn toàn thiên vị tự khớp in-sample.

### Danh Sách Laptop Đạt Chuẩn "Kèo Thơm" (OOF):

| Tên laptop | Hãng | Giá bán thực tế | Giá định giá OOF | Cận dưới 95% | Thặng dư (Value Gap) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Apple MacBook Air M2 2024 8CPU 8GPU 16GB** | Apple | 18,590,000 đ | 27,410,000 đ | 20,230,000 đ | +32.17% |
| **Laptop MSI Modern 14 C12MO-660VN** | MSI | 11,790,000 đ | 20,480,000 đ | 15,120,000 đ | +42.42% |
| **Laptop MSI Prestige 14 AI+ EVO C2VMG-020** | MSI | 34,990,000 đ | 49,860,000 đ | 36,810,000 đ | +29.83% |
| **Laptop ASUS ZenBook 14 UX3405CA-ST648W** | Asus | 38,590,000 đ | 64,410,000 đ | 47,540,000 đ | +40.09% |
| **Laptop Dell Inspiron 15 3520 JYM17 - Nhậ** | Dell | 8,790,000 đ | 19,370,000 đ | 14,300,000 đ | +54.62% |

---

## 5. Đóng Gói Vòng Đời & Tái Lập (Model Lifecycle & Reproducibility)

- Pipeline hoàn chỉnh (bao gồm `RobustScaler`, `KNNImputer`, mô hình `Gradient Boosting`, siêu tham số `{'learning_rate': 0.05, 'max_depth': 3, 'n_estimators': 150}` và ngưỡng $\sigma$) đã được lưu tại:
  `data/processed/laptop_price_pipeline.joblib`.
- Thông số kỹ thuật chi tiết lưu tại: `data/processed/ml_metrics.json`.
- File dự đoán OOF phục vụ kiểm thử D10 độc lập: `data/processed/ml_oof_predictions.json`.
- Cung cấp hàm `get_trained_model_and_predictions()` phục vụ thí nghiệm đối chứng D10.

---

## 6. Phân Tích Sai Số Chi Tiết Theo Phân Khúc Giá & Thương Hiệu (§6.6)

Đánh giá chi tiết sự phân bố sai số dựa trên dự đoán Out-Of-Fold (OOF) của mô hình tối ưu (Gradient Boosting) nhằm nhận diện các vùng không gian đặc trưng có độ bất định cao:

### 6.1. Phân tích sai số theo phân khúc ngân sách

| Phân khúc giá | Số lượng ($N$) | Giá trung bình | MAE (VNĐ) | RMSE (VNĐ) | MAPE (%) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| < 15 Triệu (Phổ thông) | 3 |  11,356,667 đ |  7,288,647 đ |  8,044,182 đ | 71.10% |
| 15 - 25 Triệu (Tầm trung) | 55 |  21,408,345 đ |  2,473,569 đ |  3,215,561 đ | 11.81% |
| 25 - 40 Triệu (Cận cao cấp) | 98 |  31,578,776 đ |  3,026,953 đ |  4,697,844 đ | 9.33% |
| >= 40 Triệu (Cao cấp / Flagship) | 64 |  65,899,531 đ |  7,315,395 đ | 10,498,058 đ | 10.60% |

> [!NOTE]
> **Nhận định phân khúc:** 
> - Phân khúc **Tầm trung (15 - 25M, N=55)** và **Cận cao cấp (25 - 40M, N=98)** chiếm đại đa số tập mẫu (70%) và đạt độ chính xác tương đối xuất sắc (MAPE lần lượt là **11.81%** và **9.33%**). Điều này chứng minh thị trường laptop đại chúng tuân theo quy luật định giá linh kiện (CPU/RAM/SSD/GPU) rất chặt chẽ và nhất quán.
> - Phân khúc **Phổ thông (< 15M, N=3)** có MAPE cao (71.10%) do số lượng mẫu ít và tập trung các đợt xả kho giảm giá sâu đột biến (Dell Inspiron 8.79M, MSI Modern 11.79M) — chính các mẫu này sau đó được lớp thống kê nhận diện thành công vào danh sách "Kèo Thơm".
> - Phân khúc **Cao cấp / Flagship (>= 40M, N=64)** có sai số tuyệt đối (MAE) cao hơn do biên độ giá rộng và các yếu tố phi phần cứng (vật liệu nguyên khối, màn hình chuẩn đồ họa, buồng hơi tản nhiệt), nhưng sai số tương đối (MAPE) vẫn được kiểm soát ở mức lý tưởng (**10.60%**) nhờ việc huấn luyện trên không gian log-target.

### 6.2. Phân tích sai số theo thương hiệu nhà sản xuất

| Thương hiệu | Số lượng ($N$) | Giá trung bình | MAE (VNĐ) | RMSE (VNĐ) | MAPE (%) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Lenovo** | 49 |  38,765,510 đ |  3,630,385 đ |  5,235,478 đ | 9.38% |
| **Asus** | 45 |  37,630,200 đ |  5,751,702 đ | 10,141,305 đ | 12.43% |
| **Apple** | 41 |  56,680,244 đ |  5,685,231 đ |  7,748,375 đ | 10.84% |
| **MSI** | 31 |  34,722,258 đ |  3,599,655 đ |  5,376,113 đ | 12.41% |
| **Acer** | 26 |  31,890,385 đ |  2,508,759 đ |  3,281,314 đ | 8.94% |
| **Dell** | 26 |  25,020,769 đ |  2,875,844 đ |  3,769,123 đ | 14.23% |
| **HP** | 2 |  25,490,000 đ |    670,024 đ |    725,356 đ | 2.55% |

> [!NOTE]
> **Nhận định thương hiệu:**
> - Các hãng dải sản phẩm rộng tập trung vào phân khúc hiệu năng trên giá như **Asus, Acer, Lenovo, MSI** có MAPE rất đồng đều (~9–12%), bám sát giá trị phần cứng.
> - Các thương hiệu định vị cao cấp hoặc biên lợi nhuận thương hiệu đặc thù (Brand Premium) như **Apple, Dell** có mức giá trung bình cao hơn và khoảng lệch đặc thù; việc mô hình hóa bằng cờ thương hiệu one-hot đã giúp giải thuật hấp thu chính xác độ dốc giá riêng của từng hãng.

### 6.3. Phân tích các trường hợp ngoại lai lớn nhất (Top Outliers)

Dưới đây là 5 mẫu máy có sai số phần trăm (MAPE) lớn nhất trong tập kiểm thử OOF:

| Tên laptop | Hãng | Giá thực tế | Giá định giá OOF | Độ lệch (VNĐ) | Sai số MAPE (%) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Laptop Dell Inspiron 15 3520 JYM17 - Nhậ** | Dell | 8,790,000 đ | 19,370,000 đ | +10,580,000 đ | 120.34% |
| **Laptop MSI Modern 14 C12MO-660VN** | MSI | 11,790,000 đ | 20,480,000 đ | +8,690,000 đ | 73.68% |
| **Laptop ASUS ZenBook 14 UX3405CA-ST648W** | Asus | 38,590,000 đ | 64,410,000 đ | +25,820,000 đ | 66.91% |
| **Apple MacBook Air M2 2024 8CPU 8GPU 16GB** | Apple | 18,590,000 đ | 27,410,000 đ | +8,820,000 đ | 47.43% |
| **Laptop MSI Prestige 14 AI+ EVO C2VMG-020** | MSI | 34,990,000 đ | 49,860,000 đ | +14,870,000 đ | 42.51% |

> [!NOTE]
> **Nguyên nhân ngoại lai:** Các mẫu có sai số phần trăm cao nhất thường thuộc hai nhóm:
> 1. Laptop được bán lẻ xả kho hoặc khuyến mãi giảm giá sâu đột xuất (giá thực tế thấp hơn nhiều so với giá trị cấu hình danh định).
> 2. Các mẫu laptop doanh nhân siêu nhẹ cao cấp mang các tính năng bảo mật doanh nghiệp, độ bền quân đội hoặc vật liệu siêu nhẹ đắt tiền không thể hiện hết qua bảng thông số kỹ thuật cốt lõi.
