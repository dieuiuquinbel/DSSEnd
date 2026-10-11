# Cấu trúc chương trình LaptopDSS

## Phân loại

LaptopDSS là **DSS/MCDM quy mô nhỏ** cho lựa chọn laptop. Dữ liệu hiện tại gồm 220 cấu hình trong một snapshot. Đây không phải hệ big data, không có dòng dữ liệu liên tục và không đưa ML vào điểm TOPSIS.

## Phương pháp áp dụng

| Thành phần | Vai trò |
|---|---|
| AHP | Tính trọng số theo hồ sơ nhu cầu và kiểm `CR < 0.10`. |
| TOPSIS | Xếp hạng phương án đã qua ràng buộc cứng. |
| OAT | Thay đổi từng trọng số/ngân sách để kiểm tra độ bền Top 1. |
| Gradient Boosting + Nested GroupKFold | Dự báo OOF để thẩm định giá; độc lập với TOPSIS theo D10. |
| Rule-based NLP | Bóc tách yêu cầu tiếng Việt offline, có entity/offset/cảnh báo; không phải mô hình ngôn ngữ huấn luyện. |

## Module

| Nhóm | Module | Trách nhiệm |
|---|---|---|
| Core | `src/dss_ranking.py` | AHP, TOPSIS, Fit RAM/SSD, OAT. |
| Core | `src/ml_price_prediction.py` | ML, OOF, SHAP, artifact metrics. |
| Core | `src/api.py` | FastAPI và ghép lọc/xếp hạng/thẩm định. |
| Core | `src/nlp_parser.py` | Parser yêu cầu tiếng Việt theo luật. |
| Pipeline | `src/build_sqlite_db.py`, `eda_analysis.py`, `experiment_d10_ml_comparison.py`, `experiment_external_validation.py`, `run_evaluation_scenarios.py` | CSDL, EDA, đối chứng D10, đánh giá theo nguồn/chọn mô hình, kịch bản đánh giá. |
| Legacy | `src/legacy/` | Crawler, pilot, script một lần và prototype Streamlit. |
| UI | `frontend/src/App.jsx` | React UI, feedback parser, bốn tab phân tích. |

## Giai đoạn đã thực hiện

1. Thu thập/pilot, chuẩn hóa thuộc tính và định danh cấu hình.
2. EDA, kiểm coverage và lựa chọn tiêu chí theo D14.
3. AHP + TOPSIS cùng bốn hồ sơ nhu cầu.
4. ML định giá bằng OOF, SHAP và khoảng dự báo 95%.
5. Đối chứng D10 để giữ ML ngoài điểm DSS.
6. Kịch bản kiểm thử, độ nhạy ngân sách/trọng số và giao diện React.

## Luồng chạy

`catalog chuẩn hóa → bộ lọc cứng → AHP/TOPSIS → xếp hạng`.

Song song: `catalog chuẩn hóa → pipeline ML OOF → thẩm định giá`. Hai nhánh chỉ gặp nhau ở giao diện; ML không thay đổi điểm TOPSIS.
