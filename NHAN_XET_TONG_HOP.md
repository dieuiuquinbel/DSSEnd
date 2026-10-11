# BÁO CÁO ĐÁNH GIÁ TỔNG HỢP CUỐI CÙNG
## Dự án LaptopDSS — Hệ thống hỗ trợ ra quyết định mua sắm laptop kết hợp học máy

> **Bản chất tài liệu:** Đây là bản hợp nhất của 2 lượt rà soát trước (bản "GĐ1→GĐ7" và bản "P0/P1") cộng với kết quả đối chiếu trực tiếp code + artefact tại thời điểm viết bản này. Các phát hiện được đánh dấu nguồn gốc: `[R1]` = rà soát lần 1, `[R2]` = rà soát lần 2, `[ĐC]` = đối chiếu trực tiếp mới.

---

## 0. GHI CHÚ QUAN TRỌNG TRƯỚC KHI ĐỌC (ĐC)

Trước khi đi vào từng hạng mục, cần ghi nhận **một vấn đề nền tảng ảnh hưởng đến toàn bộ bằng chứng số liệu**:

> **Dataset đã mở rộng từ 110 → 220 máy nhưng hệ thống tài liệu chưa đồng bộ theo kịp.**

Bằng chứng trực tiếp:
- `data/processed/dataset_snapshot_v1.json` → `total_laptops: 110` (100 CellphoneS + 10 FPT Shop).
- `data/processed/dataset_snapshot_v2.json` → `total_laptops: 220` (210 CellphoneS + 10 FPT Shop), snapshot `2.0.0-phase6-expanded-220`.
- Báo cáo EDA hiện tại (`eda_report_110_laptops.md`) chạy trên **220 mẫu** (bảng giá ghi "Số lượng mẫu 220", phân bổ hãng cộng lại = 220), nhưng **tiêu đề vẫn ghi "110 Laptops"**.
- `phase6_validation_report.md` và `README.md` vẫn ghi "110 Laptops (100 CellphoneS + 10 FPT Shop)".

Hệ quả: **nhiều con số cụ thể trong hai bản nhận xét cũ đã lệch so với artefact hiện hành.** Đây không phải lỗi của người nhận xét, mà là triệu chứng của việc "số liệu được hard-code vào tài liệu thay vì sinh tự động từ artefact" — đúng là lỗi mà bản `[R2] P1` đã cảnh báo. Chi tiết xem mục IV.

---

## I. BẢNG TỔNG KẾT ĐÁNH GIÁ (Hợp nhất 2 bản)

| Hạng mục | Trạng thái | Mức độ | Hành động bắt buộc |
| :--- | :--- | :--- | :--- |
| **GĐ1 — Dọn nợ kỹ thuật** | ✅ Đạt, chất lượng cao | Không cần sửa | Không |
| **GĐ3 — EDA** | 🟠 Đủ dùng, nhưng số liệu nội bộ mâu thuẫn | P1 | Sửa để mọi số sinh từ artefact |
| **GĐ4 — ML** | 🔴 Lỗi phương pháp nghiêm trọng | **P0 ×2 + P1** | Làm lại D10 + CV + 3 đầu ra §6.6 |
| **GĐ6 — Validation** | 🔴 Bằng chứng không thể tái lập | **P0/P1** | Đổi tên thành internal test HOẶC khảo sát thật |
| **GĐ7 — Đóng gói** | 🟠 Ổn, nhưng kéo theo lỗi D10 | P1 | Đồng bộ sau khi sửa D10 |
| **Tài liệu (DECISIONS/Data/README)** | 🟠 Lệch hiện trạng | P1 | Đồng bộ Streamlit→React, PassMark, số liệu ML |

**Tóm tắt một câu:** *Thuật toán (AHP + TOPSIS + OAT + 4 preset + D14 coverage guard) là ổn và có nền tảng tốt; phần đang bị hổng là **tính trung thực và khả năng tái lập của bằng chứng thực nghiệm** (D10, GĐ6) và **sự nhất quán số liệu giữa các artefact** (EDA, README, phase6).*

---

## II. GĐ1 — DỌN NỢ KỸ THUẬT ✅ ĐẠT

Kết luận: **đồng ý với cả [R1] và [R2], không cần sửa thêm.**

Các điểm đã kiểm chứng đúng:
1. **D05/D06 về benchmark:** DECISIONS.md ghi rõ dùng Geekbench 6 (Multi-Core + Single-Core) và 3DMark Time Spy, lý do loại PassMark được thuyết minh đầy đủ. Khớp với code (`dss_ranking.py`, `benchmark_matching.py`). Mâu thuẫn PassMark/Geekbench đã triệt tiêu ở cấp quyết định.
2. **Dedup hash thêm brand+sku:** khử trùng lặp không còn dựa thuần spec hash; nhận diện 106/110 SKU (96.4%) tại thời điểm snapshot v1. Hết nguy cơ gộp nhầm cấu hình cùng thông số nhưng khác thương hiệu.
3. **NULL policy:** SQLite trả `NULL` cho trường thiếu (VRAM, LAN, warranty...) thay vì gán 0/`false`/24 — đúng nguyên tắc "không suy đoán".
4. **Frontend sạch chuỗi marketing:** UI không còn nhồi nhét từ khoá quảng cáo vào giải thích.

> ⚠️ Lưu ý nhỏ cho tương lai: con số "106/110 SKU" thuộc snapshot v1 (110 máy). Sau khi mở rộng lên 220 máy (snapshot v2), cần **chạy lại bộ định danh SKU và cập nhật tỷ lệ** — hiện chưa thấy con số tương ứng cho 220 máy trong tài liệu.

---

## III. GĐ3 — EDA 🟠 ĐỦ DÙNG NHƯNG CÓ LỖI SỐ LIỆU NỘI BỘ

### 3.1. Điểm mạnh (đồng ý [R1])
- **Pearson single-core vs multi-core** là bằng chứng định lượng tốt cho D20 (tránh đa cộng tuyến khi đưa cả hai vào AHP).
- **`criteria_readiness` đã đúng:** OLED (19.1%) và NPU (28.2%) dưới ngưỡng 80% → được chuyển sang vai trò **filter/mô tả, không scoring**. Đúng tinh thần D14.
- Outlier detection và phân bổ theo hãng/phân khúc là nên bổ sung nhưng **không bắt buộc**.

### 3.2. Lỗi nghiêm trọng cần sửa (P1 — [R2], xác nhận lại bằng [ĐC])
Báo cáo EDA hiện **mâu thuẫn ngay trong cùng một tệp**:

| Vị trí | Giá trị ghi |
| :--- | :--- |
| Bảng thống kê (bảng §1, dòng "Giá bán") | 220 mẫu, min **8.79M**, max **133.99M**, median **30.99M**, IQR **18.125M** |
| Đoạn diễn giải (chú thích `[!NOTE]`) | median **24.99M**, IQR **11M**, "dao động 19.99M–30.99M", "từ 13.49M đến 115M" |

→ **Bốn cặp số mâu thuẫn nhau hoàn toàn** (median 30.99 ≠ 24.99; IQR 18.125 ≠ 11; khoảng 19.99–30.99 ≠ 13.49–115). Hơn nữa:
- Tiêu đề tệp ghi "**110** Laptops" nhưng bảng chạy trên **220** mẫu (phân bổ hãng cộng = 220; OS 180+40 = 220).
- Hệ số Pearson single/multi trong báo cáo là **ρ = 0.8954**, trong khi `README.md` ghi **0.8872**, còn bản [R2] dẫn lại "0.8642". **Ba con số khác nhau cho cùng một đại lượng.**

**Nguyên nhân gốc:** đoạn diễn giải bị hard-code bằng tay, không sinh ra từ biến thống kê thực. Đây chính là điểm hội đồng dễ bắt lỗi nhất.

**Yêu cầu sửa:** viết lại `eda_analysis.py` để **mọi số trong câu diễn giải được nội suy trực tiếp từ biến** (median, IQR, min, max, Pearson) rồi render vào report — không được gõ tay. Đồng thời thống nhất tiêu đề (110 hay 220) với snapshot hiện hành.

---

## IV. GĐ4 — MACHINE LEARNING 🔴 LỖI PHƯƠNG PHÁP

Đây là phần yếu nhất, cần sửa **trước khi bảo vệ**. Hợp nhất đầy đủ các phát hiện:

### 4.1. P0 — Thí nghiệm D10 không hề dùng ML (lỗi bản chất)
**Xác nhận bằng [ĐC] trên `src/experiment_d10_ml_comparison.py`:**
- Dòng 18 import `train_and_evaluate` từ `ml_price_prediction`, nhưng **không bao giờ gọi**.
- Dòng 30: "Version B" chỉ là `custom_weights_b = [0.25, 0.25, 0.20, 0.15, 0.15]` — **đổi trọng số AHP của 5 tiêu chí hiện có**, không thêm tiêu chí mới.
- Không có `predicted_price`, không có `value_gap = (predicted − observed)/predicted`, **không có tiêu chí C18** trong ma trận TOPSIS.

→ Kết luận trong `d10_ml_experiment_report.md` rằng "Spearman ρ = 0.9092 chứng minh hiện tượng phạt kép do ML" là **vượt quá bằng chứng**. Thí nghiệm thực chất chỉ chứng minh "đổi trọng số thì thứ hạng xê dịch" — điều hiển nhiên, không phải "có vs không có ML".

> Lưu ý: chính `DECISIONS.md` D10 (dòng 220) đã quy định đúng cách làm: *"chạy phiên bản A không có C18 và B có C18 sau khi ML được kiểm tra hợp lệ; báo cáo thay đổi Top N, tương quan thứ hạng và độ nhạy."* Code hiện tại chưa thực hiện đúng chính quyết định của mình.

**Cách sửa tối thiểu:**
1. Version B phải gọi mô hình ML thật → sinh `predicted_price` cho từng máy → tính `value_gap = (predicted_price − sale_price) / predicted_price`.
2. Thêm `value_gap` làm **criterion thứ 6 (C18)** vào ma trận TOPSIS.
3. Tái chuẩn hoá 5 trọng số gốc còn lại sao cho tổng vẫn = 1, rồi so sánh A (5 tiêu chí) vs B (6 tiêu chí) trên **cùng** các máy.

Hoặc, nếu không làm nổi thí nghiệm ML thật, **bỏ toàn bộ claim "ML" khỏi thí nghiệm** và đổi tên thành "phân tích độ nhạy trọng số" — không được giữ mác "ML comparison".

### 4.2. P0 — Không có Cross-Validation, R² không đáng tin
**Xác nhận bằng [ĐC] trên `ml_price_prediction.py`:**
- Chỉ chia **1 lần** 80/20 theo `configuration_id` (manual group-aware split), seed cố định 42.
- Không dùng `GroupKFold`. `Chuongtrinh.md` §6.4 yêu cầu dùng cross-validation khi dataset nhỏ — **đang vi phạm**.

**Sửa:** dùng `GroupKFold(n_splits=5)` theo `configuration_id`, báo **R² trung bình ± std** (và MAE/MAPE tương ứng), không báo một con số đơn lẻ.

### 4.3. P1 — Số liệu R² bị "thổi phồng" và đã bị lệch khỏi artefact hiện hành
Đây là phát hiện quan trọng nhất của [ĐC]:

| Mô hình | `ml_metrics.json` HIỆN TẠI | `README.md` đang ghi | Bản [R2] dẫn lại |
| :--- | :--- | :--- | :--- |
| Random Forest | R² **0.6239**, MAE 6.29M, MAPE **20.15%** | R² **0.8523**, MAE 5.9M | R² 0.8523, MAE 5.92M, MAPE 15.08% |
| Gradient Boosting | R² 0.7561, MAE 5.42M, MAPE 16.72% | — | MAE 5.58M |
| **Mô hình tốt nhất theo R²** | **Ridge (0.8043)** | (gọi Random Forest là tốt) | (gọi Random Forest là tốt) |

**Ba vấn đề cùng lúc:**
1. Con số "R² 0.8523 / MAPE 15.08%" **không còn tồn tại** trong bất kỳ artefact hiện hành nào → `README.md` đang quảng bá số liệu cũ (stale).
2. Mô hình tốt nhất hiện là **Ridge (R² 0.8043)**, không phải Random Forest → nhận định "Random Forest vượt trội" trong README là sai hai lần (sai mô hình + sai số).
3. Sau khi mở rộng 110 → 220 máy, R² của Random Forest **tụt mạnh từ 0.85 → 0.62**, còn MAPE tăng lên ~20% → đây là minh chứng sống cho đúng cảnh báo "single split → metric dao động mạnh" của [R2].

**Yêu cầu:**
- Đồng bộ README/report với `ml_metrics.json` thực tế.
- Hạ giọng kết luận: không nói "năng lực giải thích mạnh mẽ / chính xác". Với MAPE ~16–20% trên máy ~30–38M, sai số ~5.4–6.3 triệu là **tầm trung**. Nên viết "giải thích được phần lớn biến thiên giá (R² ~0.8) nhưng sai số tuyệt đối còn lớn, chỉ phù hợp làm tham chiếu sơ bộ".
- Không gọi đây là "Fair Value / định giá tham chiếu chính xác".

### 4.4. P1 — Thiếu 3 đầu ra bắt buộc của §6.6
Xác nhận **chưa có**:
1. **Feature importance** — chưa biết đặc trưng nào đẩy giá (GPU? brand? CPU?).
2. **Phân tích sai số theo phân khúc/brand** — chưa biết máy nào sai nhiều nhất.
3. **Hyperparameter tuning** — `max_depth=8`, `n_estimators=100` đang hard-code, chưa GridSearch (dù chỉ "nhẹ").

### 4.5. Nhỏ — Chiến lược imputation cần được nêu rõ là chiến lược ML
Xác nhận trong `load_dataset()`:
- `gpu_time_spy` thiếu → gán **0.0** (mất tín hiệu hiệu năng đồ hoạ của Apple M-series / Radeon 680M — máy iGPU bị coi như "không có GPU").
- CPU thiếu → `NaN` → **median impute** (bịa benchmark cho 2 máy Mac chưa phát hành).
- RAM thiếu → 16, SSD thiếu → 512, cân nặng thiếu → 1.8, refresh thiếu → 60.

Các giá trị mặc định này không "sai" nếu là **chiến lược imputation được khai báo rõ**, nhưng hiện đang mâu thuẫn với nguyên tắc "không bịa dữ liệu" (D14) được tuyên bố ở chỗ khác. **Phải ghi rõ trong report:** đây là imputation của ML, các máy bị impute được đánh dấu, và không dùng cho mục đích xếp hạng TOPSIS.

### 4.6. Nhỏ — Model chưa được lưu / chưa tích hợp
- Không có bước `joblib.dump`/`pickle` lưu model.
- Không có prediction per-laptop, API/UI chưa gọi model.
- Câu trong `ml_price_prediction_report.md` (dòng 42) rằng UI "hiển thị mức giá tham chiếu" là **chưa đúng**.

**Yêu cầu:** mô tả chính xác là *"thử nghiệm hồi quy giá tham chiếu, chưa tích hợp vào luồng gợi ý người dùng"*.

---

## V. GĐ6 — VALIDATION 🔴 BẰNG CHỨNG KHÔNG THỂ TÁI LẬP

### 5.1. Vấn đề cốt lõi (P0 — [R2], xác nhận [ĐC])
`src/run_evaluation_scenarios.py` **chỉ chạy 20 kịch bản do code định nghĩa sẵn** rồi xuất Top 3. Nó **không có**:
- người đánh giá / nhãn "lựa chọn đúng của chuyên gia";
- phiếu khảo sát;
- dữ liệu thời gian thao tác;
- bất kỳ công thức nào tính acceptance rate.

Do đó các con số trong `phase6_validation_report.md`:
- "Top-1 Acceptance 85% (17/20)",
- "Top-3 Acceptance 100% (20/20)",
- "Giảm thời gian quyết định > 85%",
- "Độ ổn định thứ hạng OAT 82.5% / ngân sách 90%",

…**không thể tái lập từ code hay dataset.** Đây là những con số "đẹp" nhưng không có nguồn gốc đo đạc — rủi ro liêm chính học thuật cao nhất, ngang với lỗi D10.

### 5.2. Lỗi filter trong kịch bản (P0 — [R2], xác nhận [ĐC])
Một số kịch bản mô tả yêu cầu nhưng code **không áp filter tương ứng**:
| Kịch bản | Yêu cầu mô tả | Filter thực tế trong code |
| :--- | :--- | :--- |
| S04 | màn hình 15.6" | ❌ không filter kích thước |
| S13 | RTX 4050/5050 | ❌ không filter GPU |
| S15 | chuẩn màu 100% sRGB/DCI-P3 | ❌ không filter gamut |
| S20 | ≤ 1.2 kg | ❌ preset chỉ ép ≤ 1.45 kg |

→ Top-1 "trùng khớp chuyên gia" của các kịch bản này hiện không có cơ sở, vì đầu vào đã không đúng yêu cầu.

### 5.3. Hướng xử lý (2 lựa chọn, chọn 1)
- **Phương án A (đề xuất, nhanh):** đổi tên GĐ6 thành **"kiểm thử kịch bản nội bộ (internal scenario test)"**, xoá toàn bộ các tỷ lệ acceptance/time-reduction/OAT% không đo được, chỉ giữ "20 kịch bản chạy thành công + Top 3".
- **Phương án B (đầy đủ):** tổ chức khảo sát người dùng/chuyên gia thật, lưu câu trả lời thô + công thức tính metric, rồi mới được ghi các con số acceptance.

---

## VI. GĐ7 — ĐÓNG GÓI 🟠 ỔN NHƯNG KÉO THEO LỖI D10

Đồng ý với [R1]:
- `requirements.txt`, `README.md`, **19/19 test pass**: ✅.
- Frontend build thành công; lint chỉ còn warning (import dư) không chặn build: ✅.

Nhưng `d10_ml_experiment_report.md` là artefact dựa trên thí nghiệm sai phương pháp (mục IV.1) → **kết luận "phạt kép do ML" chưa được chứng minh thật.** Phải tái sinh sau khi sửa D10.

---

## VII. TÀI LIỆU CẦN ĐỒNG BỘ (P1)

1. **`DECISIONS.md` D11 (dòng 232–236):** vẫn ghi "dùng **Streamlit** cho prototype", trong khi hệ thống thực là **React + FastAPI**. → sửa.
2. **`Data.md` (dòng 673–674):** vẫn liệt kê URL **PassMark** mà không ghi chú. Vì D05/D06 đã quyết định loại PassMark, cần gắn nhãn *"nguồn tham khảo không sử dụng"* để không mâu thuẫn.
3. **`README.md`:**
   - Dòng 22: Pearson ρ ghi **0.8872** → phải khớp artefact EDA (hiện 0.8954).
   - Dòng 25: "Random Forest R² = 0.8523, MAE 5.9M" → **stale**, phải khớp `ml_metrics.json` (Ridge 0.8043 là tốt nhất; RF 0.6239).
   - Dòng 24, 39: "110 laptop" → phải khớp snapshot v2 (220).
   - Mô tả ML nên ghi rõ "chưa tích hợp vào luồng gợi ý".
4. **`phase6_validation_report.md`:** tiêu đề/dữ liệu "110 Laptops" → đồng bộ 220; xoá/cải chính các metric không đo được.

---

## VIII. ĐIỂM ĐÃ SỬA ĐÚNG (ghi nhận tích cực)

Tổng hợp và xác nhận bằng [ĐC]:
- `dss_ranking.py` (dòng 238–253) đã có **validation `custom_weights`** đầy đủ: kiểm tra độ dài, số hữu hạn, không âm, tổng > 0, chuẩn hoá tổng = 1 → đúng như mô tả.
- SQLite có helper chuyển trường thiếu thành `NULL` (không còn 0/`false` giả).
- SKU parser tồn tại, nhận diện 106/110 SKU (tại snapshot v1).
- 4 profile khớp engine: Sinh viên, Mỏng nhẹ, Coding, Gaming.
- Hard filter Gaming 144 Hz đã có.
- Benchmark và snapshot artefacts đã version/hash (SHA-256).
- 19/19 test pass là đúng; frontend build thành công.

---

## IX. THỨ TỰ SỬA ƯU TIÊN (Hợp nhất P0 → P1 → optional)

| Ưu tiên | Việc | Bản chất |
| :---: | :--- | :--- |
| **1 (P0)** | Viết lại thí nghiệm D10 cho đúng: ML thật → `value_gap` → C18 → so sánh A/B, HOẶC bỏ claim ML khỏi thí nghiệm | Sai bản chất, không thể vào báo cáo |
| **2 (P0)** | Thay single-split bằng `GroupKFold` 5-fold → báo R² ± std | Vi phạm §6.4 |
| **3 (P0/P1)** | Đổi GĐ6 thành internal scenario test HOẶC khảo sát thật; xoá metric không đo được | Liêm chính bằng chứng |
| **4 (P1)** | Sửa EDA/report GĐ6 để **mọi số sinh tự động từ artefact**, không hard-code | Đồng nhất số liệu |
| **5 (P1)** | Thêm feature importance + phân tích sai số theo phân khúc + GridSearch nhẹ | §6.6 bắt buộc |
| **6 (P1)** | Hạ giọng kết luận ML (bỏ "chính xác/mạnh mẽ"), ghi rõ imputation, ghi "chưa tích hợp UI" | Trung thực |
| **7 (P1)** | Đồng bộ README/DECISIONS/Data/phase6 với hiện trạng (React, bỏ PassMark, số liệu 220 máy) | Nhất quán tài liệu |
| **8 (optional)** | Outlier detection + phân bổ theo hãng/phân khúc trong EDA; lưu model + prediction per-laptop | Nâng cấp |

---

## X. NHẬN XÉT CHI TIẾT CUỐI CÙNG

**Đánh giá tổng thể:** Dự án có **nền tảng phương pháp vững chắc và đáng bảo vệ ở phần lõi**. Chuỗi AHP → TOPSIS với 4 preset trung thực, cơ chế D14 coverage-guard (tự loại tiêu chí dưới 80%), quyết định D10 (không đưa C18 vào V1 để tránh đếm đôi giá), và khâu dọn nợ kỹ thuật (NULL policy, dedup theo SKU, validation trọng số, version/hash snapshot) đều được làm **cẩn thận và đúng tinh thần học thuật**.

**Điểm yếu tập trung ở "bằng chứng thực nghiệm", không phải ở "thuật toán":**
1. **D10** là một thí nghiệm mang tên "ML comparison" nhưng thực chất chỉ đổi trọng số — đây là lỗi sai bản chất, kết luận đang vượt quá bằng chứng.
2. **GĐ6** công bố các tỷ lệ acceptance/time-reduction không thể tái lập từ code — cùng mức nghiêm trọng với D10 về mặt liêm chính.
3. **EDA/README/phase6** chứa số liệu hard-code đã lệch khỏi artefact, và bị khuếch đại thêm bởi việc dataset mở rộng 110 → 220 máy mà tài liệu không theo kịp.

**Kết luận hành động:** Không cần làm lại hệ thống. Cần **cứu tính trung thực và khả năng tái lập của bằng chứng**. Nếu hoàn thành 5 việc ưu tiên (sửa D10 → CV cho ML → đổi tên GĐ6 → sinh số tự động cho EDA → đồng bộ tài liệu), dự án đủ chặt để bảo vệ. **Ưu tiên tuyệt đối là mục 1 (D10) và mục 3 (GĐ6)**, vì đây là hai chỗ mà một hội đồng có chuyên môn về phương pháp sẽ bắt lỗi ngay lập tức và có thể làm mất uy tín toàn bộ phần còn lại vốn đang rất ổn.
