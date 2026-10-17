# 💻 LaptopDSS — Hệ hỗ trợ ra quyết định mua sắm laptop

Hệ hỗ trợ ra quyết định (DSS) quy mô nhỏ: xếp hạng cấu hình laptop bằng **AHP + TOPSIS**, kiểm định độ bền bằng **OAT**, và dùng **hồi quy học máy** làm lớp *thẩm định giá độc lập* (không đưa vào điểm TOPSIS theo D10).

> **Phân loại chương trình:** DSS / MCDM + học máy hồi quy trên snapshot **513 cấu hình** (505 CellphoneS + 8 FPT Shop pilot). **KHÔNG phải big data** — không luồng dữ liệu liên tục, không phân tán.

---

## 1. Yêu cầu môi trường

| Thành phần | Phiên bản |
|---|---|
| Python | 3.10 trở lên |
| Node.js | 18 trở lên |

Trên Windows, **luôn thêm cờ `-X utf8`** khi chạy Python để tránh lỗi mã hoá tiếng Việt.

---

## 2. Cài đặt

```powershell
# Backend
pip install -r requirements.txt

# Frontend
cd frontend
npm install
```

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
```

---

## 5. API endpoints

| Method | Endpoint | Mục đích |
|---|---|---|
| GET | `/api/health` | Trạng thái API. |
| GET | `/api/presets` | 4 hồ sơ nhu cầu, trọng số AHP và CR. |
| GET | `/api/laptops` | Toàn bộ danh mục laptop chuẩn hoá. |
| POST | `/api/parse-requirement` | Bóc tách yêu cầu tiếng Việt theo luật (offline). |
| POST | `/api/evaluate` | Lọc cứng + xếp hạng TOPSIS + thẩm định ML; hỗ trợ `min_ram_gb`, `min_storage_gb`. |
| POST | `/api/sensitivity` | Độ nhạy ngân sách và OAT trọng số (±10%, ±20%). |
| GET | `/api/ml_valuation` | Chỉ số ML, SHAP, danh sách "Kèo Thơm" (OOF). |
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

## 6. Tìm kiếm theo yêu cầu tự nhiên (rule-based NLP)

Ô tìm kiếm nhận câu tiếng Việt và chuyển thành bộ lọc **minh bạch** trước khi chạy TOPSIS.

Ví dụ: `laptop lập trình dưới 25 triệu, RAM 16GB, không Apple`

Parser trả về entity kèm vị trí, từ chưa phân giải và cảnh báo; **không tự gán hồ sơ từ từ mơ hồ** ("ngon", "mượt"). Đây là **bộ phân tích theo quy tắc** (`src/nlp_parser.py`), không phải mô hình ngôn ngữ được huấn luyện.

---

## 7. Kết quả ML hiện tại

Nguồn chuẩn: `data/artifacts/price_model_metrics.json` (**không chép tay số**).

- Mô hình triển khai: **Gradient Boosting Regressor**, `R² = 0.8823 ± 0.0171`, `MAE ≈ 4.60 triệu`, `MAPE = 12.16%` (Nested GroupKFold 5-fold outer, 3-fold inner, 513 laptop chuẩn hóa, 26 đặc trưng phần cứng bao gồm GPU Compute).
- So sánh đa mô hình: Gradient Boosting ($R^2 = 0.8823$) và XGBoost ($R^2 = 0.8811$) dẫn đầu, vượt trội so với Random Forest ($0.8732$) và Ridge ($0.8301$).
- Công thức Value Gap thống nhất: `(giá dự báo OOF − giá quan sát) / giá dự báo OOF × 100`.
- Khi artifact ML lỗi, API ghi `warning`, trả `ml_status.available = false`, UI hiện **"Không đủ dữ liệu thẩm định ML"** (không hiển thị 0%).


---

## 8. Tái tạo dữ liệu & pipeline (nếu cần)

Các artifact đã tạo sẵn. Nếu cần chạy lại:

```powershell
python -X utf8 -m src.build_sqlite_db
python -X utf8 -m src.eda_analysis
python -X utf8 -m src.ml_price_prediction
python -X utf8 -m src.experiment_external_validation
python -X utf8 -m src.experiment_d10_ml_comparison
python -X utf8 -m src.run_evaluation_scenarios
```

---

## 9. Xử lý sự cố thường gặp

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

## 10. Tài liệu liên quan

- **[STRUCTURE.md](STRUCTURE.md)** — phân loại, phương pháp, dữ liệu, module, các giai đoạn.
- **[DECISIONS.md](DECISIONS.md)** — nhật ký 21 quyết định học thuật (D01–D21).
- **[Fix.md](Fix.md)** — nhật ký lỗi đã gặp và cách khắc phục.

**Giới hạn:** dữ liệu là snapshot tại một thời điểm; benchmark chip mới có thể là ước lượng kiến trúc (công tắc `strict_benchmark` theo D05); pin/NPU không phải tiêu chí TOPSIS lõi (D07/D15); ML chỉ là thẩm định tham khảo độc lập (D10).
