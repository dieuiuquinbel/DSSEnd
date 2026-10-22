# LaptopDSS — Tổng quan chương trình

## 1. Bài toán hướng đến

LaptopDSS là hệ hỗ trợ ra quyết định chọn laptop từ catalog có sẵn. Người dùng
đưa ra nhu cầu và ràng buộc, ví dụ: *lập trình dưới 25 triệu, RAM tối thiểu
16 GB, không Apple*. Hệ thống lọc các máy không phù hợp, xếp hạng các máy còn
lại và giải thích kết quả.

Hệ thống có hai nhánh có thể kết hợp ở bước đề xuất cuối:

```text
Yêu cầu người dùng → lọc cứng → AHP + TOPSIS → điểm phù hợp nhu cầu
Catalog + giá thực tế → ML hồi quy OOF → điểm định giá / khoảng dự báo
                                      ↓
                         Điểm đề xuất tùy chọn: 85% TOPSIS + 15% ML
```

ML không đi vào ma trận TOPSIS và điểm TOPSIS luôn được giữ nguyên để giải
thích. **TOPSIS thuần là mặc định**. Khi người dùng chủ động bật
**ML-assisted ranking**, hệ thống dùng điểm giá trị OOF làm lớp hậu xử lý có
giới hạn 15%; model đã train có ảnh hưởng thật đến thứ tự đề xuất nhưng đây là
góc nhìn value-for-money tùy chọn, không phải kết quả TOPSIS thuần.

## 2. Dữ liệu

- 513 cấu hình laptop trong một snapshot: 505 CellphoneS và 8 FPT Shop.
- Catalog chuẩn: `data/catalog/laptops.csv`.
- Có giá, CPU/GPU benchmark, RAM, SSD, màn hình, pin, trọng lượng, hệ điều
  hành, bảo hành và các thông tin phụ trợ khác.
- Dữ liệu thiếu được giữ `NULL`; không tự thay bằng 0 hay thông số giả.
- Catalog không phải dữ liệu thời gian thực và không có lịch sử giá.

## 3. Những chức năng người dùng dùng được

### 3.1. Chọn theo bốn hồ sơ nhu cầu

| Hồ sơ | Điều hệ thống ưu tiên | Ràng buộc chính |
|---|---|---|
| Sinh viên & Kinh tế | Giá, CPU đơn nhân, RAM, trọng lượng, SSD | Tránh dGPU nặng trên 1.85 kg |
| Mỏng nhẹ & Di động | Trọng lượng, giá, CPU, RAM, SSD | Trọng lượng không quá 1.45 kg |
| Kỹ thuật & Lập trình | CPU đa nhân, RAM, SSD, giá, trọng lượng | RAM tối thiểu 16 GB |
| Gaming & Đồ họa | GPU, CPU đa nhân, giá, RAM, SSD | dGPU + Windows + màn hình từ 144 Hz |

### 3.2. Lọc và tìm kiếm

- Lọc ngân sách, hãng, hệ điều hành, RAM/SSD tối thiểu, cân nặng, màn hình,
  GPU và các tiêu chí có dữ liệu.
- Nhập câu tiếng Việt cơ bản: ngân sách, RAM/SSD, hãng loại trừ, tần số quét
  và nhu cầu. Parser là **rule-based NLP**: regex + từ điển, có cảnh báo nếu
  yêu cầu mơ hồ hoặc xung đột.
- Các điều kiện như `RAM 16 GB` được hiểu là **từ 16 GB trở lên**, không phải
  bằng đúng 16 GB.
- Có so sánh tối đa ba laptop và hiển thị lý do máy bị loại / được xếp hạng.
- Có công tắc **ML hỗ trợ xếp hạng** và hiển thị riêng điểm TOPSIS, điểm ML,
  điểm đề xuất cuối để người dùng kiểm tra được lý do đổi thứ hạng.
- Có form giao diện để nhập cấu hình mới và chạy model định giá trực tiếp,
  không cần dùng Swagger.

### 3.3. Kiểm tra độ bền của quyết định

- OAT sensitivity: thay đổi từng trọng số hoặc ngân sách để xem Top-1 đổi ra
  sao. Phạm vi hiện tại: TOPSIS thuần.
- Monte Carlo: sinh 25–1000 bộ trọng số Dirichlet quanh AHP hoặc Direct
  Rating, rồi tính tần suất Top-1 xuất hiện. Seed có thể tái lập. Phạm vi hiện
  tại: TOPSIS thuần, không suy diễn sang ML-assisted.

## 4. Thuật toán DSS

### 4.1. Lọc cứng

Ràng buộc bắt buộc được áp dụng trước xếp hạng. Ví dụ Gaming không để máy
không có dGPU, không chạy Windows hoặc dưới 144 Hz lọt vào danh sách.

### 4.2. AHP

AHP xác định trọng số tiêu chí cho từng hồ sơ nhu cầu từ ma trận so sánh cặp.
Mỗi preset kiểm tra Consistency Ratio; chỉ chấp nhận khi `CR < 0.10`.

### 4.3. TOPSIS

TOPSIS chuẩn hóa ma trận tiêu chí, xác định phương án lý tưởng tốt/xấu rồi
xếp hạng bằng khoảng cách Euclid. Kết quả là **điểm TOPSIS**, không phải phần
trăm chắc chắn người dùng sẽ hài lòng.

Các tiêu chí chỉ được đưa vào TOPSIS khi đủ độ phủ dữ liệu; CPU/GPU là tiêu
chí lõi chỉ trong các hồ sơ thực sự cần hiệu năng đó.

## 5. Machine Learning định giá

### 5.1. Bài toán ML

ML giải bài toán hồi quy: dự báo **log giá bán** từ thông số laptop, sau đó
quy đổi về VND. Đầu vào gồm CPU/GPU benchmark, VRAM, RAM, SSD, độ phân giải,
OLED, Hz, độ sáng, pin, cân nặng, OS và hãng.

Mô hình không dùng bảng cộng giá thủ công như “OLED cộng 2 triệu”. Nó học từ
513 giá bán quan sát được. Model triển khai là `GradientBoostingRegressor`:

\[
\widehat{\log(price)} = b + \eta\sum_{m=1}^{M} T_m(x),\qquad
\widehat{price}=\exp(\widehat{\log(price)})
\]

Trong đó mỗi (T_m) là một cây hồi quy học các ngưỡng và tương tác giữa các
feature. Model hiện dùng 150 cây, learning rate 0.1 và depth tối đa 3.

### 5.2. Quy trình huấn luyện và đánh giá

- Benchmark: Linear Regression, Ridge, KNN, Decision Tree, Random Forest,
  Gradient Boosting, LightGBM, XGBoost và ANN/MLP.
- Validation: Nested GroupKFold, outer 5 folds và inner 3 folds; nhóm theo
  cấu hình để giảm rò rỉ giữa máy gần giống nhau.
- Tiền xử lý: RobustScaler và KNNImputer chỉ fit trong train fold.
- Dự báo OOF dùng cho đánh giá chênh lệch giá, không dùng dự đoán trên chính
  mẫu đã train.

Kết quả hiện tại được lưu tại `data/artifacts/price_model_metrics.json`, báo
cáo đầy đủ tại `data/reports/ml_price_prediction_report.md`, và hiển thị trong
notebook `notebooks/LaptopDSS_End_to_End_Audit.ipynb`.

| Mô hình | R² | MAE | MAPE |
|---|---:|---:|---:|
| Linear Regression | 0.8500 | 5.38 triệu | 14.34% |
| KNN Regressor | 0.7977 | 5.82 triệu | 14.56% |
| Decision Tree | 0.7861 | 6.18 triệu | 15.82% |
| Random Forest | 0.9023 | 4.60 triệu | 12.35% |
| Gradient Boosting | **0.9034** | 4.54 triệu | 12.24% |
| XGBoost | 0.9023 | **4.36 triệu** | **11.93%** |
| ANN / MLP | 0.8406 | 5.70 triệu | 14.90% |

Gradient Boosting được chọn vì R² Nested GroupKFold cao nhất trong artifact
hiện hành, kiến trúc gọn và feature importance có thể giải thích bằng SHAP.
XGBoost có MAE/MAPE tốt hơn ở lần chạy này; vì chênh lệch R² rất nhỏ, không
được diễn giải rằng Gradient Boosting vượt trội tuyệt đối. Tham số model triển
khai: `n_estimators=150`, `max_depth=3`, `learning_rate=0.1`.

### 5.3. Kết quả ML được dùng như thế nào

`/api/predict_price` nhận cấu hình nhập tay, tạo đúng feature vector đã lưu
trong artifact ML, dự báo giá và trả khoảng dự báo 95%.

`/api/evaluate` có chế độ `ml_assisted_ranking`. Khi bật, mỗi laptop có:

\[
S_{final}=0.85S_{TOPSIS}+0.15S_{ML}
\]

`S_ML` được tạo từ chênh lệch giữa giá quan sát và dự báo OOF, chặn trong
0–1. Máy ngoài cửa sổ giá 15–40 triệu nhận điểm trung tính 0.5 để không được
hưởng lợi từ vùng ít được hỗ trợ. UI hiện rõ `topsis_score`, `ml_valuation_score`
và `recommendation_score`; tắt công tắc (mặc định) thì hệ thống quay về
TOPSIS thuần. `ml_ranking_weight=0` cũng được coi là TOPSIS thuần.

### 5.4. Chính sách dùng ML trong quyết định

| Chế độ | Khi nào dùng | Điều được phép kết luận | Không được kết luận |
|---|---|---|---|
| TOPSIS thuần (mặc định) | Gợi ý/bảo vệ chính | Phù hợp tương đối với hồ sơ và ràng buộc | Giá “hợp lý” hay mức hài lòng tuyệt đối |
| ML-assisted 15% (tùy chọn) | So sánh thêm value-for-money | Thứ tự có xét tín hiệu OOF minh bạch | ML đã tối ưu trọng số 15%, hoặc hết rủi ro đếm đôi giá |
| `/api/predict_price` | Nhập cấu hình mới | Giá tham chiếu và khoảng dự báo của model | Giá thị trường chắc chắn hay dự báo xu hướng thời gian |

Thí nghiệm D10 chứng minh không được đưa C18 vào **ma trận** TOPSIS. Lớp
ML-assisted nằm ngoài ma trận nhưng vẫn có thể đếm đôi ảnh hưởng của giá trong
điểm cuối; cap 15% là quyết định thiết kế để trình bày minh bạch, không phải
kết quả tối ưu hóa. Vì vậy các kiểm định OAT/Monte Carlo chỉ áp dụng TOPSIS
thuần và giao diện/API đều ghi rõ phạm vi này.

`/api/ml_valuation` vẫn hiển thị tín hiệu **chênh lệch giá tham chiếu** khi
giá quan sát thấp hơn cận dưới OOF trong khoảng 15–40 triệu. Đây không phải
cam kết “món hời”; model có thể overpredict ở một số phân khúc, đặc biệt máy
giá thấp.

ANN có mặt để so sánh. Một số fold chạm giới hạn tối ưu, nên ANN không phải
model triển khai.

## 6. Công nghệ sử dụng

| Lớp | Công nghệ | Vai trò |
|---|---|---|
| Ngôn ngữ | Python 3.10+ | Pipeline dữ liệu, DSS, ML, API và test |
| Xử lý dữ liệu | Pandas, NumPy, SciPy | Chuẩn hóa, phân tích và tính toán |
| ML | scikit-learn, LightGBM, XGBoost, SHAP, joblib | Benchmark, giải thích feature và lưu model |
| API | FastAPI, Pydantic, Uvicorn | REST API, validation input, Swagger |
| Frontend | React 19, Vite, Tailwind CSS, Lucide React | Giao diện web và trực quan hóa kết quả |
| Database | SQLite | Catalog đã chuẩn hóa, listing và benchmark |
| Kiểm thử | pytest | Regression test dữ liệu, ranking, NLP, API và ML |
| Notebook | Jupyter/nbformat + Matplotlib | Notebook tái lập benchmark và biểu đồ |

## 7. Các giai đoạn đã thực hiện

| Giai đoạn | Kết quả |
|---|---|
| GĐ0 — Thiết kế | Chốt D01–D21: phạm vi, dữ liệu, tiêu chí, chính sách thiếu dữ liệu |
| GĐ1 — Proof of concept | Kiểm tra luồng thu thập, chuẩn hóa và đề xuất laptop |
| GĐ2 — Dataset | Chuẩn hóa 513 cấu hình, benchmark CPU/GPU và SQLite |
| GĐ3 — EDA | Phân tích phân phối, coverage, tương quan; `src.visualize_data` sinh 5 PNG tái lập |
| GĐ4 — ML | Benchmark các model, Nested GroupKFold, OOF, SHAP và artifact dự báo giá |
| GĐ5 — DSS | AHP, TOPSIS, presets, lọc cứng, OAT và Monte Carlo |
| GĐ6 — Tích hợp | FastAPI, React, parser tiếng Việt, so sánh, định giá cấu hình mới và ML-assisted ranking tùy chọn (mặc định tắt) |
| GĐ7 — Kiểm chứng | Notebook executed, 20 kịch bản nội bộ, holdout FPT nhỏ, 110 regression tests, production build và kiểm tra staged snapshot |

## 8. Kiến trúc và file quan trọng

| File | Nội dung |
|---|---|
| `src/dss_ranking.py` | AHP, TOPSIS, hard filter, OAT và Monte Carlo |
| `src/nlp_parser.py` | Rule-based NLP tiếng Việt |
| `src/ml_price_prediction.py` | Feature engineering, benchmark, train, OOF, SHAP, export artifact |
| `src/visualize_data.py` | Sinh biểu đồ EDA/so sánh model Matplotlib vào `data/reports/figures/` |
| `src/api.py` | FastAPI endpoints, validation và gọi model dự báo |
| `frontend/src/App.jsx` | Giao diện React |
| `data/catalog/laptops.csv` | Catalog chuẩn 513 laptop |
| `data/artifacts/price_model.joblib` | Model ML đã huấn luyện |
| `notebooks/LaptopDSS_End_to_End_Audit.ipynb` | Notebook tái lập và kết quả benchmark |

## 9. Giới hạn hiện tại

- Chỉ có snapshot giá, không có chuỗi giá theo thời gian nên không tuyên bố
  temporal validation hay dự báo xu hướng giá.
- FPT Shop chỉ có 8 mẫu trong catalog; external holdout thực tế còn 7 sau loại
  cấu hình trùng, nên chỉ là stress test nhỏ.
- NLP là rule-based, không hiểu bảo đảm mọi câu tiếng Việt tự do, sai chính tả
  hay mô tả chủ quan.
- Một số trường chưa đủ coverage để làm tiêu chí lõi: LAN, Type-C charging,
  độ sáng, color gamut, khe RAM; `thickness_mm` gần như không có dữ liệu.
- Khoảng 22.8% CPU benchmark là approximate; `strict_benchmark=true` loại
  các mẫu đó khi cần nghiêm ngặt.
- Chênh lệch giá tham chiếu không phải lời khuyên mua hay bảo đảm giá thị
  trường; nó là kết quả thống kê của model trên catalog hiện có.
- ML-assisted có cap 15% nhưng vẫn có rủi ro đếm đôi giá ở điểm đề xuất cuối;
  không dùng để thay thế TOPSIS thuần hoặc làm bằng chứng từ OAT/Monte Carlo.

## 10. Hướng đi hiện tại

Mục tiêu trước khi nộp không phải mở rộng thêm model hay crawler, mà là giữ
chuỗi bằng chứng tái lập và nhất quán: catalog → EDA/5 biểu đồ → benchmark ML
→ artifact/OOF → notebook → API/UI → test/build. Nếu huấn luyện lại model,
phải tái sinh tất cả report phụ thuộc và chạy lại notebook/test; không trộn số
liệu của artifact mới với report cũ. Sau khi đồ án ổn định mới cân nhắc dữ liệu
giá theo thời gian, nhiều retailer và kiểm định ML-assisted riêng.

## 11. Cách mô tả ngắn khi bảo vệ

> LaptopDSS là DSS lai giữa MCDM và ML hồi quy. AHP xác định trọng số theo
> hồ sơ, TOPSIS tạo điểm phù hợp sau lọc cứng. ML Gradient Boosting học giá
> tham chiếu từ thông số máy. TOPSIS thuần là mặc định. Khi người dùng bật chế
> độ hỗ trợ ML, điểm đề xuất là 85% TOPSIS và 15% điểm định giá OOF, còn từng
> thành phần vẫn hiển thị riêng và có cảnh báo rủi ro đếm đôi giá.
> Hệ thống không tuyên bố AI tự học sở thích người dùng vì chưa có dữ liệu
> click, rating hay mua hàng.
