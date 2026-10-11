# 🔧 Nhật ký lỗi & bài học kinh nghiệm (Fix.md)

Tài liệu ghi lại các lỗi đã gặp trong quá trình phát triển LaptopDSS, nguyên nhân gốc, cách sửa và bài học rút ra — để tái lập và tránh lặp lại.

---

## 1. Lỗi phương pháp ML (quan trọng nhất)

### 1.1. Value Gap dùng hai mẫu số khác nhau
- **Triệu chứng:** UI hiển thị `+120.4%`, báo cáo ML ghi `+54.62%` cho cùng một máy (Dell Inspiron 8.79M / dự báo 19.37M).
- **Nguyên nhân:** `/api/evaluate` dùng `(pred − obs) / obs`, còn pipeline/report/D10 dùng `(pred − obs) / pred`.
- **Cách sửa:** Thống nhất về mẫu số **dự báo**: `gap = (pred − obs) / pred × 100`.
- **Bài học:** Một chỉ số phải có **một định nghĩa duy nhất** dùng chung ở mọi nơi.

### 1.2. Rò rỉ dữ liệu khi imputation (data leakage)
- **Triệu chứng:** Điểm CV bị thổi phồng, không tổng quát hoá thật.
- **Nguyên nhân:** `KNNImputer.fit_transform` trên **toàn bộ dataset** trước khi chia fold.
- **Cách sửa:** Fit `RobustScaler` + `KNNImputer` **chỉ trong fold train**, rồi `transform` lên fold validation.
- **Bài học:** Mọi biến đổi học từ dữ liệu (imputer, scaler, encoder) phải nằm **trong** vòng CV.

### 1.3. KNNImputer bị áp đảo thang đo
- **Triệu chứng:** Imputation chỉ phụ thuộc benchmark CPU, bỏ qua đặc trưng 0/1.
- **Nguyên nhân:** Khoảng cách Euclid nhạy thang đo; `cpu_benchmark_multi` (~1.000–26.000) lấn át `is_macos`/`is_oled` (0/1).
- **Cách sửa:** Thêm `RobustScaler(unit_variance=True)` **trước** `KNNImputer`.
- **Bài học:** Luôn chuẩn hoá thang đo trước các thuật toán dựa trên khoảng cách.

### 1.4. Gọi là "Nested CV" nhưng thực tế chưa lồng
- **Triệu chứng:** Docstring/report ghi "Nested GroupKFold" nhưng code chỉ có 1 tầng GroupKFold, hyperparameter hardcode.
- **Cách sửa:** Dựng thật: **outer 5-fold GroupKFold** (đánh giá) + **inner 3-fold GridSearchCV** (tune).
- **Bài học:** Tên phương pháp phải khớp đúng cách chia dữ liệu; không "nói quá" trong báo cáo.

### 1.5. Thí nghiệm D10 không hề dùng ML
- **Triệu chứng:** "Version B" chỉ đổi trọng số AHP, không có `predicted_price`/`value_gap`/C18.
- **Nguyên nhân:** Import `train_and_evaluate` nhưng không gọi; chỉ đổi `custom_weights`.
- **Cách sửa:** Version B phải thật sự dự đoán giá → tính `value_gap` → thêm C18 vào TOPSIS.
- **Bài học:** Thí nghiệm "đối chứng" phải khác nhau đúng **một biến** cần đo, không phải thứ khác.

### 1.6. Model xuất xưởng ≠ model tốt nhất; SHAP chạy sai model
- **Triệu chứng:** CV chọn Gradient Boosting, nhưng lưu và SHAP lại dùng Random Forest hardcode.
- **Cách sửa:** Lưu + SHAP đúng `best_model_name`; sau CV chạy 1 lượt GridSearchCV trên full data để khoá `best_params`.
- **Bài học:** Model được báo cáo, model được lưu và model được giải thích phải là **một**.

### 1.7. "Kèo thơm" dùng dự đoán in-sample (tự khớp)
- **Triệu chứng:** Cờ good-deal tính trên dự đoán của model fit trên chính dữ liệu đó.
- **Cách sửa:** Dùng **dự đoán Out-Of-Fold (OOF)** cho cả điểm dự báo lẫn σ; lưu OOF ra `ml_oof_predictions.json`.
- **Bài học:** Mọi đánh giá "thật" phải dùng dự đoán ngoài mẫu huấn luyện.

### 1.8. Bịa dữ liệu bằng heuristic
- **Triệu chứng:** CPU thiếu → đoán số nhân theo tên (i7→12, i5→8...); VRAM/refresh/pin gán mặc định.
- **Cách sửa:** Giữ `NaN` thật, để KNN impute; thêm cờ `cpu_benchmark_missing`.
- **Bài học:** Không được "bịa" dữ liệu để lấp chỗ trống (đúng tinh thần D14).

### 1.9. Back-transformation "không thiên lệch" sai khái niệm
- **Triệu chứng:** Ghi `exp(ŷ)` là "không thiên lệch".
- **Cách sửa:** Làm rõ `exp(ŷ)` là ước lượng **trung vị** (geometric mean); muốn trung bình cộng cần smearing `exp(σ²/2)`.
- **Bài học:** Dùng đúng thuật ngữ thống kê; không gán nhãn "không thiên lệch" tuỳ tiện.

---

## 2. Lỗi dữ liệu & nhất quán

### 2.1. EDA có số liệu mâu thuẫn ngay trong cùng báo cáo
- **Triệu chứng:** Bảng ghi median 30.99M / IQR 18.125M, nhưng câu diễn giải ghi 24.99M / 11M; tiêu đề "110" nhưng bảng 220 mẫu.
- **Nguyên nhân:** Câu diễn giải hardcode bằng tay, không nối với biến thống kê.
- **Cách sửa:** Sinh report **100% động** từ biến thống kê; chỉ giữ đúng 1 file (xoá file tên "110").
- **Bài học:** Mọi con số trong report phải sinh từ biến, không gõ tay.

### 2.2. Dataset mở rộng 110 → 220 nhưng tài liệu không theo kịp
- **Triệu chứng:** `phase6`/README/EDA tiêu đề còn ghi "110", snapshot đã là 220.
- **Cách sửa:** Đồng bộ mọi tài liệu với `dataset_snapshot_v2.json` (220 máy); dùng hash SHA-256 để khoá phiên bản.
- **Bài học:** Dữ liệu thay đổi phải kéo theo cập nhật tất cả artefact + tài liệu.

### 2.3. Mâu thuẫn công nghệ (Streamlit vs React) và nguồn benchmark (PassMark)
- **Triệu chứng:** `DECISIONS.md` D11 ghi Streamlit trong khi hệ thống là React+FastAPI; `Data.md` liệt kê PassMark.
- **Cách sửa:** D11 ghi "Streamlit (Prototype) → FastAPI + React 18 (Production)"; PassMark gắn nhãn "tham khảo, không dùng trong engine".
- **Bài học:** Tài liệu quyết định phải khớp hiện trạng code thật.

---

## 3. Lỗi nghiệp vụ & kiểm thử

### 3.1. GĐ6 công bố số liệu không thể tái lập
- **Triệu chứng:** "Top-1 acceptance 85%", "giảm thời gian 85%" không có nguồn đo đạc.
- **Nguyên nhân:** `run_evaluation_scenarios.py` chỉ chạy 20 kịch bản, không có khảo sát/người đánh giá.
- **Cách sửa:** Đổi thành **"Kiểm thử kịch bản nội bộ"**, xoá số giả, thêm Tuyên bố liêm chính học thuật.
- **Bài học:** Không công bố số liệu khảo sát nếu chưa thực sự đo đạc.

### 3.2. Kịch bản mô tả yêu cầu nhưng không filter tương ứng
- **Triệu chứng:** S04 (15.6") không filter màn; S13 (RTX 4050/5050) không filter GPU; S15 (gamut) không filter; S20 (≤1.2kg) chỉ dùng preset 1.45kg.
- **Cách sửa:** Thêm filter thật: `screen_size`, `gpu_series`, `require_wide_gamut`, `max_weight_kg`.
- **Bài học:** Mô tả kịch bản phải khớp 1-1 với bộ lọc code thực thi.

### 3.3. "RAM 16GB" bị hiểu là "đúng bằng 16GB"
- **Triệu chứng:** Lọc `ram_gb == 16` loại mất máy 32GB/64GB.
- **Cách sửa:** Thêm `min_ram_gb`/`min_storage_gb` (ngưỡng tối thiểu) xuyên suốt parser → API → engine → sensitivity → GĐ6.
- **Bài học:** Phân biệt **lọc bằng tuyệt đối** với **ngưỡng tối thiểu**.

### 3.4. Lỗi đọc artifact ML bị nuốt im lặng
- **Triệu chứng:** `except Exception: pass` khiến lỗi tải OOF/metrics thành "Value Gap 0%".
- **Cách sửa:** Ghi `logging.warning` có ngữ cảnh file lỗi, trả `ml_status.available = false`; UI hiện "Không đủ dữ liệu thẩm định ML".
- **Bài học:** Không bao giờ biến lỗi dữ liệu thành số liệu hợp lệ.

---

## 4. Checklist tái lập (khi chạy lại pipeline)

Mỗi lần chạy lại, đối chiếu 3 nguồn phải **cùng phiên bản**:
1. **Mã nguồn** (code hiện tại).
2. **Artifact** (`ml_metrics.json`, `ml_oof_predictions.json`, `dataset_snapshot_*.json`, hash SHA-256).
3. **Báo cáo** (`ml_price_prediction_report.md`, `phase6_validation_report.md`, `d10_ml_experiment_report.md`).

Cụ thể kiểm tra:
- [ ] Value Gap mọi nơi dùng mẫu số **dự báo**.
- [ ] Imputer/scaler fit **trong fold** (không rò rỉ).
- [ ] Best model = model lưu = model SHAP.
- [ ] "Kèo thơm" dùng OOF, không in-sample.
- [ ] Không còn số liệu "chấp nhận 85%" kiểu giả mạo.
- [ ] Filter kịch bản khớp mô tả (màn hình/GPU/gamut/cân nặng).
- [ ] `min_ram_gb`/`min_storage_gb` hoạt động (không phải "bằng").
- [ ] Số ML trong README khớp `ml_metrics.json` (không chép tay).
