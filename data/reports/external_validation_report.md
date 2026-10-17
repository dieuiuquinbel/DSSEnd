# ĐÁNH GIÁ NGOÀI THEO NGUỒN VÀ CHỌN MÔ HÌNH ML

**Quy mô:** 513 cấu hình; nguồn: FPT Shop: 8, cellphones: 505.

## Kết luận chọn mô hình

Gradient Boosting được giữ làm mô hình triển khai **tạm thời** vì dẫn đầu artifact Nested GroupKFold nội bộ. Kết quả dưới đây không cho phép gọi nó là tối ưu tuyệt đối nếu bootstrap chưa tách biệt nó khỏi XGBoost.

## So sánh OOF hậu chọn (tham số đã khóa)

| Mô hình | MAE (VND) | MAPE (%) | R² |
|---|---:|---:|---:|
| Gradient Boosting | 4,619,963 | 12.27 | 0.8893 |
| XGBoost | 4,602,894 | 12.17 | 0.8825 |

Bootstrap cặp: ΔMAE(XGBoost − Gradient Boosting) = -21,233 VND, CI95% [-196,918; 170,728]. **Chưa đủ bằng chứng phân biệt Gradient Boosting và XGBoost**.

## Retailer holdout (quasi-external)

| Nguồn giữ lại làm test | Trạng thái | n | MAE (VND) | MAPE (%) |
|---|---|---:|---:|---:|
| FPT Shop | completed | 8 | 2391106.38 | 9.045 |
| cellphones | skipped | — | — | — |

## Calibration khoảng dự báo 95%

Coverage tổng thể: **94.54%** (mục tiêu danh nghĩa 95%). Kết quả này phải được đọc cùng cỡ mẫu từng phân khúc; nếu lệch đáng kể cần cân nhắc conformal prediction.

## Giới hạn

- Retailer holdout không thay thế tập ngoài độc lập hoặc temporal holdout.
- FPT Shop chỉ có 10 mẫu; đây là stress test, không là tiêu chí chọn mô hình.
- Bước tiếp theo là thu snapshot giá mới hoặc nguồn thứ ba và chỉ đánh giá pipeline đã khóa.
