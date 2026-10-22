# ĐÁNH GIÁ NGOÀI THEO NGUỒN VÀ CHỌN MÔ HÌNH ML

**Quy mô:** 513 cấu hình; nguồn: FPT Shop: 8, cellphones: 505.

## Kết luận chọn mô hình

**Gradient Boosting** là model triển khai vì dẫn đầu $R^2$ trong artifact Nested GroupKFold nội bộ. Kết quả dưới đây không cho phép gọi nó là tối ưu tuyệt đối nếu bootstrap chưa tách biệt nó khỏi model đối chứng.

## So sánh OOF hậu chọn (tham số đã khóa)

| Mô hình | MAE (VND) | MAPE (%) | R² |
|---|---:|---:|---:|
| Gradient Boosting | 4,386,949 | 11.89 | 0.9038 |
| XGBoost Regressor | 4,477,865 | 12.13 | 0.8943 |

Bootstrap cặp: ΔMAE(XGBoost Regressor − Gradient Boosting) = 90,251 VND, CI95% [-204,892; 379,760]. **Chưa đủ bằng chứng phân biệt Gradient Boosting và XGBoost Regressor**.

## Retailer holdout (quasi-external)

| Nguồn giữ lại làm test | Trạng thái | n | MAE (VND) | MAPE (%) |
|---|---|---:|---:|---:|
| FPT Shop | completed | 7 | 2018177.41 | 7.835 |
| cellphones | skipped | — | — | — |

## Calibration khoảng dự báo 95%

Coverage tổng thể: **94.74%** (mục tiêu danh nghĩa 95%). Kết quả này phải được đọc cùng cỡ mẫu từng phân khúc; nếu lệch đáng kể cần cân nhắc conformal prediction.

## Giới hạn

- Retailer holdout không thay thế tập ngoài độc lập hoặc temporal holdout.
- FPT Shop chỉ có 8 mẫu trước khi loại cấu hình trùng; đây là stress test, không là tiêu chí chọn mô hình.
- Bước tiếp theo là thu snapshot giá mới hoặc nguồn thứ ba và chỉ đánh giá pipeline đã khóa.
