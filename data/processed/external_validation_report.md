# ĐÁNH GIÁ NGOÀI THEO NGUỒN VÀ CHỌN MÔ HÌNH ML

**Quy mô:** 220 cấu hình; nguồn: FPT Shop: 10, cellphones: 210.

## Kết luận chọn mô hình

Gradient Boosting được giữ làm mô hình triển khai **tạm thời** vì dẫn đầu artifact Nested GroupKFold nội bộ. Kết quả dưới đây không cho phép gọi nó là tối ưu tuyệt đối nếu bootstrap chưa tách biệt nó khỏi XGBoost.

## So sánh OOF hậu chọn (tham số đã khóa)

| Mô hình | MAE (VND) | MAPE (%) | R² |
|---|---:|---:|---:|
| Gradient Boosting | 4,241,232 | 11.29 | 0.9083 |
| XGBoost | 4,368,690 | 11.74 | 0.9068 |

Bootstrap cặp: ΔMAE(XGBoost − Gradient Boosting) = 129,507 VND, CI95% [-162,401; 423,251]. **Chưa đủ bằng chứng phân biệt Gradient Boosting và XGBoost**.

## Retailer holdout (quasi-external)

| Nguồn giữ lại làm test | Trạng thái | n | MAE (VND) | MAPE (%) |
|---|---|---:|---:|---:|
| FPT Shop | completed | 10 | 1435080.69 | 5.846 |
| cellphones | skipped | — | — | — |

## Calibration khoảng dự báo 95%

Coverage tổng thể: **95.0%** (mục tiêu danh nghĩa 95%). Kết quả này phải được đọc cùng cỡ mẫu từng phân khúc; nếu lệch đáng kể cần cân nhắc conformal prediction.

## Giới hạn

- Retailer holdout không thay thế tập ngoài độc lập hoặc temporal holdout.
- FPT Shop chỉ có 10 mẫu; đây là stress test, không là tiêu chí chọn mô hình.
- Bước tiếp theo là thu snapshot giá mới hoặc nguồn thứ ba và chỉ đánh giá pipeline đã khóa.
