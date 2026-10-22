# Cấu trúc chương trình LaptopDSS

Tài liệu tổng hợp: phân loại hệ thống, phương pháp, dữ liệu, kiến trúc module và các giai đoạn đã thực hiện.

---

## 1. Phân loại chương trình

LaptopDSS là **DSS / MCDM (Multi-Criteria Decision Making) + học máy hồi quy** quy mô nhỏ, phục vụ lựa chọn laptop cho sinh viên/người dùng phổ thông.

- Dữ liệu: **513 cấu hình laptop** trong một **snapshot** (505 CellphoneS + 8 FPT Shop pilot).
- **KHÔNG phải big data**: không xử lý phân tán, không Hadoop/Spark, không luồng dữ liệu liên tục.
- ML tạo điểm định giá OOF. TOPSIS luôn được tính riêng; chế độ tùy chọn
  `ml_assisted_ranking` xếp theo 85% TOPSIS + 15% điểm định giá ML.

---

## 2. Phương pháp áp dụng

| Thành phần | Vai trò |
|---|---|
| AHP | Tính trọng số tiêu chí theo từng hồ sơ nhu cầu; kiểm `CR < 0.10`. |
| TOPSIS | Xếp hạng phương án sau khi qua ràng buộc cứng (chuẩn hoá vector + khoảng cách Euclid đến A+/A-). |
| OAT | Thay đổi từng trọng số/ngân sách để kiểm tra độ bền của Top 1. |
| Monte Carlo | Sinh 25–1000 vector trọng số Dirichlet quanh AHP/Direct Rating; đo tần suất Top-1. |
| Gradient Boosting + benchmark Linear/KNN/Decision Tree/Random Forest/XGBoost/ANN, Nested GroupKFold | Dự báo giá OOF; tạo điểm định giá tùy chọn trong đề xuất cuối, giữ TOPSIS hiển thị riêng. |
| Rule-based NLP | Bóc tách yêu cầu tiếng Việt offline (regex + từ điển), có entity/offset/cảnh báo; không phải mô hình ngôn ngữ huấn luyện. |

---

## 3. Dữ liệu & nguồn

### 3.1. Nguồn bán lẻ

| Nguồn | Số lượng | Ghi chú |
|---|---|---|
| CellphoneS | 505 | `https://cellphones.com.vn/laptop.html` (Làm giàu thông số 9 nhóm trực tiếp từ Nuxt state) |
| FPT Shop | 8 | `https://fptshop.com.vn/may-tinh-xach-tay` (mẫu khảo sát pilot D01 thương mại) |

Tổng: **513 cấu hình laptop** (snapshot chuẩn hóa tại `data/catalog/laptops.csv`).

#### Thống kê độ phủ thực tế từ 505 máy CellphoneS:
- **Panel (tấm nền):** 481/505 (**95.25%**)
- **Kích thước màn hình (`screen_size_inch`):** 504/505 (**99.80%**)
- **Webcam (`webcam_raw`):** 503/505 (**99.60%**)
- **Bluetooth (`bluetooth_raw`):** 501/505 (**99.21%**)
- **Thời gian bảo hành (`warranty_months`):** 500/505 (**99.01%**, 5 máy không công bố thời hạn bảo hành nên để `NULL` chuẩn xác theo D14)
- **Tần số quét (`refresh_rate_hz`):** 424/505 (**83.96%**)
- **Số khe RAM (`ram_slots`):** 396/505 (**78.42%**)
- **RAM / Storage / Wi-Fi / Kích thước hiển thị:** 100% đầy đủ.

### 3.2. Nguồn benchmark (đã chốt theo D05/D06 & D14)

- **CPU:** Geekbench 6 Multi-Core (lưu kèm Single-Core). Không dùng PassMark vì không công bằng chéo nền tảng (x86/ARM/Apple Silicon).
- **GPU Gaming:** 3DMark Time Spy Graphics, áp dụng laptop **Windows dGPU**, đối chiếu theo TGP.
- **GPU Compute:** Geekbench 6 OpenCL (iGPU Intel UHD/Iris/Arc, AMD Radeon, Qualcomm Adreno, RTX) & Geekbench 6 Metal (Apple Silicon M1–M4).

### 3.3. Kho dữ liệu & phiên bản

- Catalog chuẩn duy nhất: `data/catalog/laptops.csv` (513 dòng).
- Benchmark đối chiếu: `data/catalog/benchmarks.csv` (209 cặp component-benchmark).
- SQLite: `data/artifacts/laptop_dss.db` — 4 bảng chuẩn BCNF: `configurations` (511), `retail_listings` (513), `price_observations` (513), `component_benchmarks` (209).
- Snapshot có **hash SHA-256** để khoá phiên bản; chính sách thiếu dữ liệu lưu `NULL` thực tế (không bịa 0/`false`).


---

## 4. Kiến trúc module

| Nhóm | Module | Trách nhiệm |
|---|---|---|
| Core | `src/dss_ranking.py` | AHP, TOPSIS, Fit RAM/SSD, OAT. |
| Core | `src/ml_price_prediction.py` | ML, OOF, SHAP, RobustScaler+KNN, artifact metrics. |
| Core | `src/api.py` | FastAPI, ghép lọc/xếp hạng/thẩm định ML. |
| Core | `src/nlp_parser.py` | Parser yêu cầu tiếng Việt theo luật. |
| Pipeline | `src/build_sqlite_db.py` | Định danh SKU + khử trùng lặp + NULL policy. |
| Pipeline | `src/eda_analysis.py` | EDA sinh report động (513 máy). |
| Pipeline | `src/experiment_d10_ml_comparison.py` | Thí nghiệm đối chứng D10 (có/không có C18). |
| Pipeline | `src/experiment_external_validation.py` | Bootstrap so sánh mô hình + retailer holdout + calibration. |
| Pipeline | `src/run_evaluation_scenarios.py` | Kiểm thử 20 kịch bản nội bộ (GĐ6). |
| Legacy | `src/legacy/` | Crawler, pilot, script một lần và prototype Streamlit. |
| UI | `frontend/src/App.jsx` | React UI, feedback parser, tab phân tích. |

---

## 5. Các giai đoạn đã thực hiện

Theo đặc tả gốc (Giai đoạn 0–7):

| Giai đoạn | Nội dung | Trạng thái |
|---|---|---|
| GĐ0 | Chốt quyết định nền tảng (D01–D21) | ✅ `DECISIONS.md` |
| GĐ1 | Proof of concept dữ liệu | ✅ |
| GĐ2 | Thu thập & làm sạch dataset | ✅ 513 máy (505 CellphoneS + 8 FPT Shop) |
| GĐ3 | EDA & chốt tiêu chí (coverage ≥ 80%, D14) | ✅ `eda_report_220_laptops.md` (đồng bộ 513 máy) |
| GĐ4 | Pipeline ML (nested CV, OOF, SHAP) | ✅ `ml_price_prediction_report.md` |
| GĐ5 | AHP + TOPSIS (4 hồ sơ nhu cầu) | ✅ |
| GĐ6 | Tích hợp giao diện (React + FastAPI + NLP) | ✅ |
| GĐ7 | Đánh giá, báo cáo & đóng gói (test, build, docs) | ✅ |

---

## 6. Luồng chạy

```
catalog chuẩn hoá → bộ lọc cứng → AHP/TOPSIS → xếp hạng → giải thích
                                        ↕ (chỉ gặp ở giao diện)
catalog chuẩn hoá → pipeline ML OOF → thẩm định giá / chênh lệch giá tham chiếu
```

Hai thành phần vẫn tách bạch về thuật toán: TOPSIS tính mức phù hợp nhu cầu;
ML định giá. Chế độ tùy chọn ghép hai điểm ở hậu xử lý với tỷ lệ 85%/15%.
