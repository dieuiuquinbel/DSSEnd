# 💻 LaptopDSS — Hệ hỗ trợ ra quyết định mua sắm laptop

Hệ hỗ trợ ra quyết định (DSS) quy mô nhỏ: lọc và xếp hạng laptop bằng **AHP + TOPSIS**, kiểm định độ bền bằng **OAT**, đồng thời dùng **hồi quy học máy** để định giá cấu hình và hỗ trợ thứ tự đề xuất.

> **Phân loại chương trình:** DSS / MCDM + học máy hồi quy trên snapshot **513 cấu hình** (505 CellphoneS + 8 FPT Shop pilot). **KHÔNG phải big data** — không luồng dữ liệu liên tục, không phân tán.

## Chương trình làm gì?

- Nhận yêu cầu, lọc laptop theo điều kiện bắt buộc và xếp hạng bằng AHP–TOPSIS.
- Có bốn hồ sơ: Sinh viên, Mỏng nhẹ, Kỹ thuật/Lập trình và Gaming.
- Phân tích câu tiếng Việt theo rule-based NLP; giải thích điều kiện nào đã áp dụng.
- Cho phép so sánh laptop, điều chỉnh trọng số, kiểm tra sensitivity/OAT và Monte Carlo.
- ML dự báo giá tham chiếu từ cấu hình. **TOPSIS thuần là mặc định**; người
  dùng có thể chủ động bật ML-assisted ranking (85% TOPSIS + 15% điểm ML OOF)
  để xem góc nhìn value-for-money. Điểm TOPSIS vẫn hiển thị riêng và ML không
  tự học sở thích người dùng.

Xem [PROGRAM.md](PROGRAM.md) để có mô tả đầy đủ về bài toán, thuật toán, ML,
công nghệ, giai đoạn thực hiện và các giới hạn cần trình bày trung thực.

---

## 1. Yêu cầu môi trường

| Thành phần | Phiên bản |
|---|---|
| Python | 3.10 trở lên |
| Node.js | 18 trở lên |

Trên Windows, **luôn thêm cờ `-X utf8`** khi chạy Python để tránh lỗi mã hoá tiếng Việt.

---

## 2. Cài đặt từ máy sạch

```powershell
# 1. Mở PowerShell tại thư mục dự án, tạo môi trường Python riêng
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# 2. Backend Python
pip install -r requirements.txt

# 3. Frontend JavaScript
cd frontend
npm install
cd ..
```

Nếu PowerShell chặn `Activate.ps1`, dùng trực tiếp `.\.venv\Scripts\python.exe`
thay cho `python` trong các lệnh dưới. Không cần Jupyter Server để chạy
notebook vì repository có runner bằng `nbformat`.

---

## 3. Khởi chạy (2 terminal riêng biệt)

### Terminal 1 — Backend API

```powershell
python -X utf8 -m uvicorn src.api:app --host 127.0.0.1 --port 8000
```

- API: `http://127.0.0.1:8000`
- Swagger UI: `http://127.0.0.1:8000/docs`

### Terminal 2 — Frontend

```powershell
cd frontend
npm run dev
```

- Giao diện: `http://127.0.0.1:5173`

> Vite đã cấu hình proxy `/api → http://localhost:8000` (`frontend/vite.config.js`), frontend gọi `/api/...` không cần CORS đặc biệt.

---

## 4. Kiểm thử & build

```powershell
python -X utf8 -m pytest tests/ -q   # số test lấy từ lần chạy hiện tại

cd frontend
npm run build
cd ..
```

Kết quả tham chiếu tại thời điểm cập nhật: **111 test pass**. Build tạo
`frontend/dist/`; không dùng `npm run build` ở thư mục gốc dự án.

Kiểm tra các artifact cần cho ML trước demo:

```powershell
Test-Path data/artifacts/price_model.joblib
Test-Path data/artifacts/price_model_metrics.json
Test-Path data/artifacts/price_model_oof.json
```

## 5. Kiểm chứng nhanh trước khi demo (5 phút)

Chạy theo thứ tự này trên máy nộp bài. Tất cả đều dùng dữ liệu và artifact đã
có sẵn trong repository, không cần crawl lại:

```powershell
# 1. Hồi quy: kiểm tra dữ liệu, DSS, API và ML artifact
python -X utf8 -m pytest tests/ -q

# 2. Run All notebook và lưu output để nộp
python -X utf8 -m src.execute_notebook notebooks/LaptopDSS_End_to_End_Audit.ipynb

# 3. Khởi động API rồi mở Swagger để kiểm tra endpoint
python -X utf8 -m uvicorn src.api:app --host 127.0.0.1 --port 8000
```

Ở terminal thứ hai chạy `cd frontend; npm run dev`, mở `http://127.0.0.1:5173`.
Kịch bản trình bày ngắn: chọn **Kỹ thuật & Lập trình** → đặt trần 25 triệu,
RAM 16 GB, SSD 512 GB → xem Top-3 **TOPSIS thuần** → chủ động bật **ML hỗ trợ
xếp hạng** để so sánh điểm TOPSIS, điểm ML và điểm đề xuất → mở **Thẩm định
giá hồi quy** để nhập cấu hình mới → chạy 300 mô phỏng trọng số. Kiểm định
OAT và Monte Carlo ở phiên bản hiện tại chỉ nói về TOPSIS thuần, không phải
bằng chứng cho lớp ML-assisted.

---

## 6. API endpoints

| Method | Endpoint | Mục đích |
|---|---|---|
| GET | `/api/health` | Trạng thái API. |
| GET | `/api/presets` | 4 hồ sơ nhu cầu, trọng số AHP và CR. |
| GET | `/api/laptops` | Toàn bộ danh mục laptop chuẩn hoá. |
| POST | `/api/parse-requirement` | Bóc tách yêu cầu tiếng Việt theo luật (offline). |
| POST | `/api/evaluate` | Lọc cứng + TOPSIS; tùy chọn `ml_assisted_ranking=true` để xếp theo 85% TOPSIS + 15% ML OOF. |
| POST | `/api/sensitivity` | Độ nhạy ngân sách và OAT trọng số (±10%, ±20%) cho **TOPSIS thuần**. |
| POST | `/api/robustness` | Monte Carlo Dirichlet quanh trọng số AHP/Direct Rating cho **TOPSIS thuần**; 25–1000 mô phỏng, seed tái lập. |
| GET | `/api/ml_valuation` | Chỉ số ML, SHAP, danh sách chênh lệch giá tham chiếu (OOF, giới hạn 15–40 triệu). |
| POST | `/api/predict_price` | Định giá một cấu hình nhập tay (kèm khoảng 95%). |

### Payload mẫu

Swagger UI tại `http://127.0.0.1:8000/docs` là tài liệu API đầy đủ và luôn
khớp code. Các payload tối thiểu thường dùng:

```json
POST /api/parse-requirement
{ "prompt": "laptop lập trình dưới 25 triệu, RAM 16GB, không Apple" }
```

```json
POST /api/evaluate
{
  "preset_key": "technical_coding",
  "min_budget_vnd": 0,
  "max_budget_vnd": 25000000,
  "min_ram_gb": 16,
  "min_storage_gb": 512,
  "excluded_brands": ["Apple"],
  "strict_benchmark": false
}
```

```json
POST /api/evaluate
{
  "preset_key": "technical_coding",
  "max_budget_vnd": 25000000,
  "min_ram_gb": 16,
  "ml_assisted_ranking": true,
  "ml_ranking_weight": 0.15
}
```

`ml_ranking_weight` chỉ nhận từ `0` đến `0.30`; giá trị `0` được xem là
TOPSIS thuần. API giữ đồng thời `topsis_rank`, `topsis_score`,
`ml_valuation_score` và `recommendation_score` để thứ hạng có thể kiểm tra.

```json
POST /api/sensitivity
{
  "preset_key": "student_budget",
  "max_budget_vnd": 25000000,
  "min_ram_gb": 16
}
```

```json
POST /api/predict_price
{
  "cpu_benchmark_multi": 12000,
  "cpu_benchmark_single": 2500,
  "ram_gb": 16,
  "storage_total_gb": 512,
  "brand": "Asus",
  "observed_price_vnd": 20000000
}
```

`/api/evaluate` trả `rankings`, `excluded`, `active_criteria`, `ahp_cr` và
`ml_status`. Khi artifact ML không khả dụng, `ml_status.available` là `false`;
đây không phải Value Gap bằng 0. `/api/predict_price` có thể trả `503` nếu file
pipeline ML chưa tồn tại.

---

## 7. Tìm kiếm theo yêu cầu tự nhiên (rule-based NLP)

Ô tìm kiếm nhận câu tiếng Việt và chuyển thành bộ lọc **minh bạch** trước khi chạy TOPSIS.

Ví dụ: `laptop lập trình dưới 25 triệu, RAM 16GB, không Apple`

Parser trả về entity kèm vị trí, từ chưa phân giải và cảnh báo; **không tự gán hồ sơ từ từ mơ hồ** ("ngon", "mượt"). Đây là **bộ phân tích theo quy tắc** (`src/nlp_parser.py`), không phải mô hình ngôn ngữ được huấn luyện.

---

## 8. Kết quả ML hiện tại

Nguồn chuẩn: `data/artifacts/price_model_metrics.json` (**không chép tay số**).

- Mô hình triển khai: **Gradient Boosting** (tham số và chỉ số lấy từ `price_model_metrics.json` sau mỗi lần chạy pipeline; không chép tay số vào mã nguồn).
- Tiêu chí chọn là $R^2$ trên Nested GroupKFold. XGBoost có MAE/MAPE thấp hơn trong lần chạy hiện tại, vì vậy kết quả không được diễn giải là Gradient Boosting vượt trội tuyệt đối.
- Benchmark bắt buộc được chạy lại trong notebook: Linear R² 0.8500, KNN 0.7977, Decision Tree 0.7861, Random Forest 0.9023, ANN 0.8406. Gradient Boosting triển khai đạt R² 0.9034, MAE 4.54 triệu; bảng đủ 10 model nằm trong `price_model_metrics.json` và notebook.
- Công thức Value Gap thống nhất: `(giá dự báo OOF − giá quan sát) / giá dự báo OOF × 100`.
- Khi artifact ML lỗi, API ghi `warning`, trả `ml_status.available = false`, UI hiện **"Không đủ dữ liệu thẩm định ML"** (không hiển thị 0%).
- Gradient Boosting học quan hệ phi tuyến qua tổng các cây hồi quy trên
  `log(price)`; không có công thức cộng giá linh kiện viết tay. Mã huấn luyện:
  `src/ml_price_prediction.py`; API suy luận: `src/api.py`.
- Lớp ML-assisted **không nằm trong ma trận TOPSIS**, nhưng vẫn có rủi ro
  đếm đôi ảnh hưởng của giá ở điểm đề xuất cuối. Vì vậy TOPSIS thuần là mặc
  định, ML chỉ là tùy chọn có cap 15%, và không được gọi là kết quả tối ưu hóa
  học thuật hay cam kết “món hời”.


---

## 9. Tái tạo notebook, phân tích và pipeline (nếu cần)

Các artifact đã tạo sẵn. Nếu cần chạy lại:

```powershell
python -X utf8 -m src.build_sqlite_db
python -X utf8 -m src.eda_analysis
python -X utf8 -m src.visualize_data
python -X utf8 -m src.ml_price_prediction
python -X utf8 -m src.experiment_external_validation
python -X utf8 -m src.experiment_d10_ml_comparison
python -X utf8 -m src.run_evaluation_scenarios
```

Chạy notebook đã có output (không cần mở trình duyệt Jupyter):

```powershell
python -X utf8 -m src.execute_notebook notebooks/LaptopDSS_End_to_End_Audit.ipynb
```

Lệnh `src.ml_price_prediction` huấn luyện lại và **ghi đè** model/metrics/OOF
hiện có; chỉ chạy khi chủ động tái tạo thí nghiệm. Sau khi chạy lại ML, chạy
lại EDA, visualization, D10, external validation và notebook để số liệu đồng
bộ.

`src.visualize_data` sinh các biểu đồ PNG tái lập tại
`data/reports/figures/`: phân phối giá, phân bổ thương hiệu, tương quan
giá–CPU, độ phủ dữ liệu và (khi có artifact) so sánh $R^2$ các mô hình.

### Thu thập và chuẩn hóa từ dữ liệu thô

Dữ liệu thô đã được lưu kèm để có thể kiểm tra nguồn. Luồng hiện tại gồm
`src/crawl_vietnam_catalog.py` (thu thập CellphoneS), dữ liệu FPT Shop trong
`data/raw/fpt_shop/`, rồi `src/legacy/standardize_cellphones.py` và
`src/integrate_expanded_catalog.py` để chuẩn hóa/ghép catalog trước khi tạo
SQLite và chạy EDA. Các crawler trong `src/legacy/` là lịch sử thu thập, không
phải một lệnh crawl duy nhất; không chạy crawler ngay trước lúc demo vì dữ
liệu nguồn và giá có thể thay đổi.

### Kiểm tra tính toàn vẹn trước khi commit/nộp

```powershell
git diff --cached --check
git show :src/dss_ranking.py | Select-String 'def analyze_monte_carlo_stability'
git show :requirements.txt | Select-String '^matplotlib'
git status --short
```

Hai dòng `git show` phải có kết quả nếu stage `src/api.py`/notebook: API import
Monte Carlo từ `dss_ranking.py` và notebook/visualization cần Matplotlib. Không
stage các file nháp cá nhân như `app_orig.jsx` hoặc `temp_diff.txt`.

---

## 10. Xử lý sự cố thường gặp

| Lỗi | Nguyên nhân | Cách xử lý |
|---|---|---|
| `ModuleNotFoundError: No module named 'lightgbm'` (xgboost/shap) | Thiếu thư viện | `pip install -r requirements.txt` |
| `UnicodeDecodeError` / chữ tiếng Việt vỡ | Thiếu cờ UTF-8 | Chạy `python -X utf8 ...` |
| `address already in use` (8000/5173) | Cổng bị chiếm | Đổi cổng hoặc tắt tiến trình cũ |
| Frontend `Failed to fetch` | Backend chưa chạy | Khởi động uvicorn, mở `:8000/docs` kiểm tra |
| `/api/ml_valuation` báo `available: false` | `price_model_metrics.json` thiếu/lỗi | Chạy `python -X utf8 -m src.ml_price_prediction` hoặc kiểm tra artifact |
| `/api/predict_price` trả 503 | `price_model.joblib` chưa có | Chạy lại pipeline ML (mục 8) |
| UI hiện "Không đủ dữ liệu thẩm định ML" | Đọc artifact ML lỗi | Kiểm tra `price_model_oof.json`, `price_model_metrics.json` |

---

## 11. Tài liệu liên quan

- **[STRUCTURE.md](STRUCTURE.md)** — phân loại, phương pháp, dữ liệu, module, các giai đoạn.
- **[PROGRAM.md](PROGRAM.md)** — tài liệu tổng quan theo bài toán, công nghệ, giai đoạn và ML.
- **[DECISIONS.md](DECISIONS.md)** — nhật ký 21 quyết định học thuật (D01–D21).
- **[Fix.md](Fix.md)** — nhật ký lỗi đã gặp và cách khắc phục.

**Giới hạn:** dữ liệu là snapshot tại một thời điểm; benchmark chip mới có thể là ước lượng kiến trúc (công tắc `strict_benchmark` theo D05); pin/NPU không phải tiêu chí TOPSIS lõi (D07/D15); ML-assisted ranking là lớp tùy chọn 15% dùng OOF, vẫn có rủi ro đếm đôi giá ở điểm cuối và không phải cam kết giá/thỏa mãn người dùng.
