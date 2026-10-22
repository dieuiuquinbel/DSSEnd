# LaptopDSS — sơ đồ file, quy trình xây dựng và cách kiểm thử

Tài liệu này mô tả **trạng thái hiện tại** của dự án. Cây bên dưới chỉ liệt kê
file nguồn, dữ liệu, báo cáo và cấu hình có ý nghĩa; bỏ qua `.git/`,
`frontend/node_modules/` và `frontend/dist/` vì đó là metadata, thư viện đã
cài và kết quả build có thể tạo lại.

## Notebook Jupyter hiện tại

Notebook chính nằm tại:

`notebooks/LaptopDSS_End_to_End_Audit.ipynb`

Đây là notebook audit end-to-end: lưu lại đầu ra của quá trình kiểm chứng
catalog, DSS, ML và các kết quả phục vụ báo cáo. Có thể chạy lại không cần
Jupyter Server bằng:

```powershell
python -X utf8 -m src.execute_notebook notebooks/LaptopDSS_End_to_End_Audit.ipynb
```

Lệnh này thực thi notebook rồi lưu output trở lại chính file `.ipynb`.

## Sơ đồ cây dự án

```text
D:\Dự Án DSS 1
├── README.md                         # Hướng dẫn cài đặt, chạy và API
├── PROGRAM.md                        # Mô tả bài toán, thuật toán, giới hạn
├── STRUCTURE.md                      # Kiến trúc và cấu trúc dữ liệu tổng quan
├── DECISIONS.md                      # 21 quyết định học thuật/thiết kế (D01–D21)
├── Fix.md                            # Nhật ký lỗi và cách khắc phục
├── PROJECT_FILE_GUIDE.md             # Tài liệu này
├── requirements.txt                  # Thư viện Python cần cài
├── .gitignore                        # Các file không đưa vào Git
│
├── src/                              # Mã Python vận hành/pipeline
│   ├── api.py                        # FastAPI: API cho giao diện và Swagger
│   ├── dss_ranking.py                # AHP, TOPSIS, lọc cứng, OAT, Monte Carlo
│   ├── nlp_parser.py                 # Đọc yêu cầu tiếng Việt theo rule-based
│   ├── ml_price_prediction.py        # Train/đánh giá/export model dự báo giá
│   ├── build_sqlite_db.py             # Tạo SQLite từ catalog chuẩn
│   ├── eda_analysis.py                # Thống kê khám phá dữ liệu và báo cáo EDA
│   ├── visualize_data.py              # Sinh 5 biểu đồ EDA/so sánh model
│   ├── execute_notebook.py            # Runner chạy notebook bằng nbformat
│   ├── run_evaluation_scenarios.py    # Chạy 20 kịch bản đánh giá nội bộ
│   ├── experiment_d10_ml_comparison.py# Thí nghiệm ML có/không vào TOPSIS
│   ├── experiment_external_validation.py # Bootstrap/holdout/calibration ML
│   ├── integrate_expanded_catalog.py  # Chuẩn hoá và ghép catalog CellphoneS
│   ├── crawl_vietnam_catalog.py       # Crawler catalog CellphoneS (không chạy demo)
│   ├── enrich_catalog_from_nuxt.js    # Lấy thông số từ Nuxt payload
│   ├── decode_nuxt_specs.py           # Hỗ trợ giải mã thông số Nuxt
│   ├── inspect_cellphones_full_specs.py # Kiểm tra cấu trúc full specs nguồn
│   ├── laptop_images.py               # Chọn ảnh laptop/fallback cho dữ liệu
│   ├── audit_criteria_readiness.py    # Audit độ sẵn sàng tiêu chí DSS
│   ├── report_criteria_readiness.py   # Xuất báo cáo độ sẵn sàng tiêu chí
│   ├── report_field_coverage.py       # Báo cáo mức độ đầy đủ các trường dữ liệu
│   └── legacy/                        # Công cụ lịch sử, không phải luồng chạy chính
│       ├── app.py                     # Giao diện Streamlit prototype cũ
│       ├── crawl_cellphones.py         # Crawler CellphoneS phiên bản cũ
│       ├── standardize_cellphones.py   # Chuẩn hoá dữ liệu CellphoneS bản cũ
│       ├── build_pilot.py              # Chuẩn hoá pilot FPT Shop
│       ├── benchmark_matching.py       # Ghép CPU/GPU với bảng benchmark
│       ├── merge_catalogs.py           # Ghép các catalog lịch sử
│       ├── audit_pilot_completeness.py # Kiểm tra độ đủ dữ liệu FPT pilot
│       ├── enrich_refresh_rates.py     # Bổ sung refresh rate từ dữ liệu cũ
│       ├── fetch_full_specs.py         # Tải thông số chi tiết bản cũ
│       ├── download_fpt_images.py      # Tải ảnh FPT cho pipeline cũ
│       ├── harvest_all_brands.py       # Thu thập URL thương hiệu (cũ)
│       ├── generate_laptop_svgs.py     # Sinh ảnh SVG minh hoạ (cũ)
│       └── test_*.py                   # Script kiểm tra crawler cũ, không phải pytest chính
│
├── frontend/                         # Giao diện React/Vite đang dùng
│   ├── package.json                   # Scripts và dependencies JavaScript
│   ├── vite.config.js                 # Vite + proxy /api tới backend :8000
│   ├── index.html                     # Điểm mount HTML
│   ├── src/main.jsx                   # Khởi tạo React
│   ├── src/App.jsx                    # Toàn bộ UI và lời gọi API chính
│   ├── src/App.css, src/index.css     # Style giao diện
│   ├── src/assets/                    # Ảnh/logo dùng trong source
│   ├── public/images/                 # Ảnh laptop phục vụ trực tiếp cho web
│   ├── node_modules/                  # Thư viện npm đã cài, có thể cài lại
│   └── dist/                          # Bản build, có thể tạo lại bằng npm run build
│
├── data/                             # Dữ liệu, model và báo cáo
│   ├── catalog/laptops.csv            # Catalog chuẩn 513 laptop — dữ liệu runtime chính
│   ├── catalog/benchmarks.csv         # Điểm benchmark CPU/GPU
│   ├── artifacts/laptop_dss.db        # SQLite được tạo từ catalog
│   ├── artifacts/price_model.joblib   # Model Gradient Boosting đã train
│   ├── artifacts/price_model_metrics.json # Chỉ số/thiết lập ML
│   ├── artifacts/price_model_oof.json # Dự báo out-of-fold dùng thẩm định giá
│   ├── raw/                           # Dữ liệu thô đã thu thập để truy xuất nguồn
│   ├── archive/legacy/                # Snapshot/pilot cũ, giữ cho audit
│   ├── reports/                       # Báo cáo EDA, ML, validation, kịch bản
│   ├── reports/figures/               # PNG do visualize_data.py tạo
│   ├── images/laptop_fallback.png     # Ảnh thay thế khi thiếu ảnh sản phẩm
│   ├── data_dictionary.md             # Từ điển cột dữ liệu
│   └── README.md                      # Ghi chú riêng cho dữ liệu
│
├── notebooks/
│   └── LaptopDSS_End_to_End_Audit.ipynb # Notebook Jupyter chính
│
└── tests/                            # Bộ pytest regression chính
    ├── test_api_filters.py            # Validation input/API/filter/ML-assisted
    ├── test_dss_ranking.py            # AHP, TOPSIS, filter, OAT, Monte Carlo
    ├── test_nlp_parser.py             # Parser tiếng Việt và phủ định/ràng buộc
    ├── test_ml_pipeline.py            # Artifact ML, metrics, dự báo, OOF
    ├── test_ml_enrichment.py          # Xử lý khi OOF/ML artifact không sẵn sàng
    ├── test_data_invariants.py        # Kích thước catalog, NULL, SQLite, tính hợp lệ
    ├── test_data_layout.py            # Runtime dùng đúng catalog/artifact chuẩn
    ├── test_benchmarks.py             # Schema và quy tắc benchmark CPU/GPU
    ├── test_build_pilot.py            # Chuẩn hoá/đủ trường FPT pilot
    └── test_external_validation.py    # Bootstrap và schema báo cáo ML validation
```

## Folder test có tác dụng gì?

`tests/` là bộ **pytest chính**. Các test không tạo chức năng mới; chúng phát
hiện việc sửa code hoặc dữ liệu làm hỏng chức năng đã đúng trước đó. Chạy toàn
bộ bằng:

```powershell
python -X utf8 -m pytest tests/ -q
```

Ví dụ, test đảm bảo không biến dữ liệu thiếu thành `0`, không cho máy gaming
thiếu GPU/Windows/144 Hz lọt qua, kiểm tra trọng số AHP nhất quán, và bảo đảm
ML-assisted vẫn giữ điểm TOPSIS hiển thị riêng. Đây là lý do nên chạy test sau
mỗi thay đổi đáng kể.

Các file `src/legacy/test_*.py` là script kiểm tra phục vụ quá trình crawl cũ;
chúng không thuộc bộ test chạy chính `tests/` và không cần chạy khi demo app.

## Chức năng của các nhóm file quan trọng

| Nhóm | Chịu trách nhiệm | Khi nào dùng |
|---|---|---|
| `frontend/` | Hiển thị form, kết quả xếp hạng, biểu đồ và so sánh | Khi người dùng mở web `:5173` |
| `src/api.py` | Nhận yêu cầu web, validate dữ liệu, gọi DSS/ML và trả JSON | Khi frontend hoặc Swagger gọi `/api/*` |
| `src/dss_ranking.py` | Lọc bắt buộc và xếp hạng phù hợp | Mỗi lần đánh giá laptop |
| `src/nlp_parser.py` | Trích ngân sách, RAM, SSD, hãng loại trừ từ câu tiếng Việt | Khi dùng ô tìm kiếm tự nhiên |
| `src/ml_price_prediction.py` | Huấn luyện lại và đánh giá ML | Chỉ chạy khi chủ động tái tạo thí nghiệm |
| `data/catalog/` + `data/artifacts/` | Input dữ liệu chuẩn và model có sẵn | Backend đọc khi chạy app |
| `tests/` | Chống hồi quy sau khi sửa code/dữ liệu | Trước demo, nộp bài hoặc commit |
| `notebooks/` | Bằng chứng phân tích có thể chạy lại | Audit/báo cáo/bảo vệ |
| `src/legacy/` | Lịch sử thu thập/Streamlit prototype | Chỉ dùng khi cần truy cứu hoặc tái tạo pipeline cũ |

## Chương trình đã được xây dựng qua những bước nào?

```text
1. Xác định bài toán và quyết định thiết kế (D01–D21)
   ↓
2. Thu thập dữ liệu thô CellphoneS + FPT Shop pilot
   ↓
3. Chuẩn hoá cấu hình, ghép benchmark CPU/GPU, xử lý thiếu dữ liệu bằng NULL
   ↓
4. Ghép thành catalog chuẩn 513 laptop và tạo SQLite
   ↓
5. EDA: kiểm tra phân phối giá, hãng, độ phủ dữ liệu, tương quan
   ↓
6. Xây DSS: hồ sơ nhu cầu → AHP → lọc cứng → TOPSIS
   ↓
7. Thêm kiểm tra độ bền: OAT sensitivity + Monte Carlo
   ↓
8. Xây ML hồi quy: feature engineering → Nested GroupKFold → OOF → model/artifact
   ↓
9. Thí nghiệm D10 và external validation để giới hạn vai trò ML
   ↓
10. Tích hợp FastAPI + React, parser tiếng Việt, so sánh và định giá cấu hình
   ↓
11. Viết pytest, chạy notebook audit, build frontend và đóng gói demo
```

## Luồng dữ liệu khi chạy app hiện tại

```text
Người dùng trên React
  → `frontend/src/App.jsx`
  → API `/api/evaluate` trong `src/api.py`
  → đọc `data/catalog/laptops.csv`
  → lọc cứng + `src/dss_ranking.py` (AHP/TOPSIS)
  → trả Top-N, điểm và lời giải thích về React

Nếu người dùng bật ML hoặc nhập cấu hình để định giá:
  → `src/api.py`
  → `data/artifacts/price_model.joblib` + metrics/OOF
  → dự báo giá hoặc cộng tối đa 15% điểm ML vào đề xuất tùy chọn
```

## Lưu ý khi đọc hoặc dọn dự án

- Không xóa `data/catalog/laptops.csv` hoặc ba file trong `data/artifacts/` nếu
  vẫn muốn chạy đầy đủ DSS + ML.
- Không chạy crawler hay `src.ml_price_prediction` ngay trước demo: crawler có
  thể thay đổi dữ liệu; pipeline ML sẽ ghi đè artifact/báo cáo hiện có.
- `frontend/node_modules/`, `frontend/dist/`, `.pytest_cache/` là phần tạo lại
  được; các file trong `src/legacy/` là lịch sử nhưng nên chỉ xóa sau khi đã
  quyết định không cần tái tạo nguồn dữ liệu hoặc Streamlit prototype.
