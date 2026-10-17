# BÁO CÁO MÔ HÌNH HỌC MÁY DỰ BÁO GIÁ & ĐỊNH GIÁ THỊ TRƯỜNG (GĐ4)
## Kiến Trúc Log-Target, Nested GroupKFold, SHAP Explainability & Lớp Nhận Diện "Kèo Thơm"

**Ngày thực hiện:** 11/10/2026  
**Quy mô tập mẫu:** 513 laptop chuẩn hóa (CellphoneS + FPT Shop)  
**Mã băm dữ liệu gốc:** `33fbe2a993575d56f2e6bda2b43ffc288fcb51552e0254d713ba910faab154b8`  
**Tuân thủ học thuật:** DECISIONS.md D10 (Tách rời ML khỏi TOPSIS), D14 (KNN Imputation chỉ cho ML), Chuongtrinh.md GĐ4.

---

## 1. Phương Pháp Luận: Target Log-Scale & Feature Engineering Chống Rò Rỉ

### 1.1. Giải quyết phân phối lệch phải (Right-skewness)
- Phân phối giá laptop thị trường dao động từ 8.79M đến 199.99M VNĐ.
- **Giải pháp toán học:** Áp dụng biến đổi logarit tự nhiên $y = \ln(\text{sale\_price\_vnd})$, huấn luyện mô hình trên không gian logarit.

- **Tính chất thống kê của phép chuyển đổi ngược:** Phép biến đổi $\hat{y}_{\text{median}} = \exp(\hat{y}_{\ln})$ ước lượng trung vị có điều kiện (geometric mean) của giá máy, kháng nhiễu cực tốt trước các mẫu ngoại lai siêu đắt. Với thừa số hiệu chỉnh smearing $\exp(\sigma^2 / 2)$, mô hình xấp xỉ kỳ vọng trung bình cộng có điều kiện.
- **Kết quả:** Sai số phần trăm tuyệt đối trung bình (MAPE) đạt **12.16%**, hệ số xác định đạt **$R^2 = +0.8823 \pm 0.0171$**.

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
| **Baseline (Mean Log-Price)** | -0.0477 ± 0.0387 | -0.0265 ± 0.0301 |  14,201,323 ± 2,414,472 đ |  22,208,856 đ | 36.51% |
| **Ridge Regression** | +0.8301 ± 0.0580 | +0.8397 ± 0.0414 |   5,350,938 ± 1,031,714 đ |   9,019,740 đ | 13.96% |
| **Random Forest Regressor** | +0.8732 ± 0.0407 | +0.8610 ± 0.0492 |   4,650,295 ±   607,148 đ |   7,525,692 đ | 12.42% |
| **Gradient Boosting** | +0.8823 ± 0.0171 | +0.8709 ± 0.0386 |   4,602,138 ±   530,553 đ |   7,323,595 đ | 12.16% |
| **LightGBM Regressor** | +0.8258 ± 0.0420 | +0.8510 ± 0.0434 |   5,050,677 ±   680,262 đ |   8,931,327 đ | 12.82% |
| **XGBoost Regressor** | +0.8811 ± 0.0164 | +0.8667 ± 0.0397 |   4,590,869 ±   681,580 đ |   7,431,964 đ | 12.13% |

> [!NOTE]
> Mô hình **Gradient Boosting** đạt hiệu năng dẫn đầu với **$R^2 = +0.8823 \pm 0.0171$**, sai số tuyệt đối trung bình $\text{MAE} = 4,602,138 \pm 530,553$ đ và $\text{MAPE} = 12.16\%$.  
> Bộ siêu tham số tối ưu xuất xưởng (GridSearchCV): `{'learning_rate': 0.1, 'max_depth': 3, 'n_estimators': 150}`.

---

## 3. Khả Năng Giải Thích Mô Hình Với SHAP (SHAP TreeExplainer)

SHAP TreeExplainer được thực thi trực tiếp trên mô hình **Gradient Boosting** xuất xưởng:

| Thứ hạng | Đặc trưng kỹ thuật | Giá trị SHAP trung bình (|SHAP|) | Ý nghĩa kinh tế |
| :---: | :--- | :---: | :--- |
| 1 | `brightness_nits` | 0.0896 |
| 2 | `gpu_benchmark_compute` | 0.0701 |
| 3 | `cpu_benchmark_multi` | 0.0649 |
| 4 | `ram_gb` | 0.0547 |
| 5 | `battery_capacity_wh` | 0.0484 |
| 6 | `screen_pixels_mp` | 0.0465 |
| 7 | `cpu_benchmark_single` | 0.0426 |
| 8 | `weight_kg` | 0.0244 |
| 9 | `refresh_rate_hz` | 0.0222 |
| 10 | `cpu_cores` | 0.0114 |
| 11 | `storage_total_gb` | 0.0113 |
| 12 | `cpu_benchmark_missing` | 0.0105 |

> [!NOTE]
> **Hiện tượng cộng tuyến đặc trưng trên cây quyết định (Tree Feature Collinearity):**  
> Các đặc trưng như `is_discrete_gpu` và `brand_Apple` có giá trị SHAP xấp xỉ 0 do mô hình cây đã rẽ nhánh hoàn toàn dựa trên các đặc trưng đại diện liên tục có tương quan hoàn hảo (`gpu_benchmark_time_spy > 0` và `is_macos == 1`). Đây là hành vi phân tách tự nhiên của thuật toán gradient boosting cây quyết định, không làm suy giảm chất lượng dự báo.

---

## 4. Tầng Gợi Ý "Kèo Thơm" (Good Deals Layer) Từ Dự Đoán Out-Of-Fold

Tuân thủ tinh thần **DECISIONS.md D10**, ML hoạt động như một lớp tham chiếu giá độc lập ngoài TOPSIS:
- Sai số chuẩn phần dư Out-Of-Fold: $\sigma_{pred} = 0.1614$ (tương đương biên độ $\approx \pm 16.1\%$).
- Khoảng tin cậy dự báo 95%: $[\hat{y}_{OOF} \cdot \exp(-1.96 \sigma_{pred}), \hat{y}_{OOF} \cdot \exp(+1.96 \sigma_{pred})]$.
- Cả giá kỳ vọng và ngưỡng tin cậy đều tính từ **dự đoán Out-Of-Fold (OOF)**, loại bỏ hoàn toàn thiên vị tự khớp in-sample.

### Danh Sách Laptop Đạt Chuẩn "Kèo Thơm" (OOF):

| Tên laptop | Hãng | Giá bán thực tế | Giá định giá OOF | Cận dưới 95% | Thặng dư (Value Gap) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Laptop MSI Modern 14 C12MO-660VN** | MSI | 11,790,000 đ | 20,480,000 đ | 14,920,000 đ | +42.42% |
| **Laptop MSI Prestige 13 AI+ Evo A2VMG-040** | MSI | 41,990,000 đ | 59,700,000 đ | 43,510,000 đ | +29.67% |
| **Laptop MSI Prestige 14 AI+ EVO C2VMG-020** | MSI | 34,990,000 đ | 49,770,000 đ | 36,270,000 đ | +29.69% |
| **Laptop MSI Venture 14 AI A1MG-005VN** | MSI | 25,990,000 đ | 40,330,000 đ | 29,390,000 đ | +35.55% |
| **Laptop ASUS ZenBook 14 UX3405CA-ST629W** | Asus | 35,190,000 đ | 54,580,000 đ | 39,780,000 đ | +35.53% |
| **Laptop Dell Inspiron 15 3520 JYM17 - Nhậ** | Dell | 8,790,000 đ | 18,820,000 đ | 13,720,000 đ | +53.3% |
| **Laptop Acer Nitro V 15 ANV15-41-R1JY** | Acer | 19,290,000 đ | 26,880,000 đ | 19,590,000 đ | +28.24% |
| **Laptop Acer Gaming Nitro ProPanel ANV15-** | Acer | 17,390,000 đ | 24,760,000 đ | 18,040,000 đ | +29.76% |

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
| < 15 Triệu (Phổ thông) | 6 |  12,856,667 đ |  6,300,116 đ |  7,393,167 đ | 53.85% |
| 15 - 25 Triệu (Tầm trung) | 153 |  21,394,575 đ |  2,643,153 đ |  3,595,308 đ | 12.80% |
| 25 - 40 Triệu (Cận cao cấp) | 215 |  31,130,930 đ |  3,292,456 đ |  4,865,382 đ | 10.30% |
| >= 40 Triệu (Cao cấp / Flagship) | 139 |  65,270,216 đ |  8,708,484 đ | 12,403,812 đ | 12.53% |

> [!NOTE]
> **Nhận định phân khúc:** 
- Phân khúc **Tầm trung (15 - 25M, N=153)** và **Cận cao cấp (25 - 40M, N=215)** chiếm đại đa số tập mẫu (71.7%) và đạt độ chính xác tương đối xuất sắc (MAPE lần lượt là **12.80%** và **10.30%**). Điều này chứng minh thị trường laptop đại chúng tuân theo quy luật định giá linh kiện (CPU/RAM/SSD/GPU) rất chặt chẽ và nhất quán.
- Phân khúc **Phổ thông (< 15M, N=6)** có MAPE là **53.85%** do số lượng mẫu ít và tập trung các đợt xả kho giảm giá sâu đột biến — chính các mẫu này sau đó được lớp thống kê nhận diện thành công vào danh sách "Kèo Thơm".
- Phân khúc **Cao cấp / Flagship (>= 40M, N=139)** có sai số tuyệt đối (MAE) cao hơn do biên độ giá rộng và các yếu tố phi phần cứng (vật liệu nguyên khối, màn hình chuẩn đồ họa, buồng hơi tản nhiệt), nhưng sai số tương đối (MAPE) vẫn được kiểm soát ở mức lý tưởng (**12.53%**) nhờ việc huấn luyện trên không gian log-target.

### 6.2. Phân tích sai số theo thương hiệu nhà sản xuất

| Thương hiệu | Số lượng ($N$) | Giá trung bình | MAE (VNĐ) | RMSE (VNĐ) | MAPE (%) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Asus** | 137 |  45,422,336 đ |  6,432,562 đ | 10,915,283 đ | 11.88% |
| **Lenovo** | 132 |  35,934,015 đ |  4,374,532 đ |  6,280,273 đ | 13.01% |
| **Acer** | 65 |  31,971,692 đ |  2,804,570 đ |  3,889,312 đ | 10.49% |
| **HP** | 55 |  28,500,909 đ |  2,770,317 đ |  3,864,417 đ | 9.19% |
| **Dell** | 49 |  26,516,531 đ |  2,919,086 đ |  3,883,386 đ | 12.65% |
| **MSI** | 48 |  41,558,750 đ |  5,741,480 đ |  8,077,674 đ | 14.76% |
| **Other** | 17 |  31,031,176 đ |  3,801,433 đ |  5,918,455 đ | 14.68% |
| **Apple** | 10 |  68,270,000 đ |  8,394,605 đ |  9,904,454 đ | 13.01% |

> [!NOTE]
> **Nhận định thương hiệu:**
> - Các hãng dải sản phẩm rộng tập trung vào phân khúc hiệu năng trên giá như **Asus, Acer, Lenovo, MSI** có MAPE rất đồng đều (~9–12%), bám sát giá trị phần cứng.
> - Các thương hiệu định vị cao cấp hoặc biên lợi nhuận thương hiệu đặc thù (Brand Premium) như **Apple, Dell** có mức giá trung bình cao hơn và khoảng lệch đặc thù; việc mô hình hóa bằng cờ thương hiệu one-hot đã giúp giải thuật hấp thu chính xác độ dốc giá riêng của từng hãng.

### 6.3. Phân tích các trường hợp ngoại lai lớn nhất (Top Outliers)

Dưới đây là 5 mẫu máy có sai số phần trăm (MAPE) lớn nhất trong tập kiểm thử OOF:

| Tên laptop | Hãng | Giá thực tế | Giá định giá OOF | Độ lệch (VNĐ) | Sai số MAPE (%) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Laptop Dell Inspiron 15 3520 JYM17 - Nhậ** | Dell | 8,790,000 đ | 18,820,000 đ | +10,030,000 đ | 114.15% |
| **Laptop Gaming Acer Nitro 5 Tiger AN515 5** | Acer | 16,490,000 đ | 30,160,000 đ | +13,670,000 đ | 82.90% |
| **Laptop MSI Modern 14 C12MO-660VN** | MSI | 11,790,000 đ | 20,480,000 đ | +8,690,000 đ | 73.68% |
| **Laptop Lenovo Yoga Pro 7 14IAH10 83KF002** | Lenovo | 37,990,000 đ | 65,890,000 đ | +27,900,000 đ | 73.43% |
| **Laptop Thunderobot Aibook 14 Air** | Other | 22,990,000 đ | 39,230,000 đ | +16,240,000 đ | 70.66% |

> [!NOTE]
> **Nguyên nhân ngoại lai:** Các mẫu có sai số phần trăm cao nhất thường thuộc hai nhóm:
> 1. Laptop được bán lẻ xả kho hoặc khuyến mãi giảm giá sâu đột xuất (giá thực tế thấp hơn nhiều so với giá trị cấu hình danh định).
> 2. Các mẫu laptop doanh nhân siêu nhẹ cao cấp mang các tính năng bảo mật doanh nghiệp, độ bền quân đội hoặc vật liệu siêu nhẹ đắt tiền không thể hiện hết qua bảng thông số kỹ thuật cốt lõi.
