# THÍ NGHIỆM ĐỐI CHỨNG: DSS CÓ VS. KHÔNG CÓ ML (DECISIONS.MD D10)
## Đánh Giá Tác Động Của Tiêu Chí Định Giá ML Value-for-Money (C18) Vào Hàm Khoảng Cách TOPSIS

**Ngày thực hiện:** 11/10/2026  
**Phương pháp luận:** Thực thi nghiêm ngặt theo DECISIONS.md D10 (Thí nghiệm phiên bản A không có C18 vs. Phiên bản B có C18).  
**Số lượng ứng viên đánh giá:** 132 laptop (Phân khúc Sinh viên & Kinh tế, ngân sách $\le 25$ triệu).

---

## 1. Thiết Kế Thí Nghiệm Đối Chứng Chuẩn Mực

* **Phiên bản A (Chuẩn D10 - Thuần AHP/TOPSIS):**
  - Sử dụng **5 tiêu chí gốc** của profile `student_budget`: Giá bán (Cost) 40.2%, CPU Single-Core (Benefit) 24.5%, RAM (Fit) 13.7%, Trọng lượng (Cost) 13.7%, SSD (Fit) 7.9%.
  - Tổng trọng số: 100%. Không có bất kỳ thành phần phỏng đoán ML nào.
* **Phiên bản B (Thí nghiệm - Tích hợp C18 ML Value Gap):**
  - Sử dụng mô hình Machine Learning hồi quy **Gradient Boosting** đã triển khai trong artifact GĐ4 để dự báo giá thị trường `predicted_price` cho từng máy.
  - Tính chỉ số chênh lệch giá tham chiếu: $\text{Value Gap} = \frac{\text{Giá dự đoán} - \text{Giá niêm yết}}{\text{Giá dự đoán}}$. Giá trị dương chỉ cho biết giá quan sát thấp hơn giá tham chiếu OOF, không phải khuyến nghị mua.
  - Bổ sung $\text{Value Gap}$ làm **tiêu chí thứ 6 ($C18$, hướng Benefit)** vào TOPSIS với trọng số $15\%$, co cụm 5 tiêu chí gốc theo tỷ lệ còn lại $85\%$.

---

## 2. Kết Quả Xếp Hạng Top 5 So Sánh Thực Nghiệm

| Thứ hạng | Phiên bản A (Chuẩn D10: Thuần AHP-TOPSIS) | Phiên bản B (Thí nghiệm: Bổ sung ML C18) | Thay đổi vị trí |
| :---: | :--- | :--- | :---: |
| **Top 1** | **Laptop Dell Inspiron 15 3520 JYM17 - Nhập khẩu chính hãng** (8790000 đ) | **Laptop Dell Inspiron 15 3520 JYM17 - Nhập khẩu chính hãng** (8790000 đ) | Giữ nguyên |
| **Top 2** | **Laptop MSI Modern 14 C12MO-660VN** (11790000 đ) | **Laptop Lenovo V14 G5 IRL 83HD0062VA** (14590000 đ) | Đổi ngôi (Top 3) |
| **Top 3** | **Laptop Acer Aspire Lite Gen 2 AL14-52M-32KV** (13490000 đ) | **Laptop MSI Modern 14 C12MO-660VN** (11790000 đ) | Đổi ngôi (Top 40) |
| **Top 4** | **Laptop Lenovo V14 G5 IRL 83HD0062VA** (14590000 đ) | **Apple MacBook Air M2 2024 8CPU 8GPU 16GB 256GB I Chính hãng Apple Việt Nam** (18590000 đ) | Đổi ngôi (Top 2) |
| **Top 5** | **Laptop ASUS ExpertBook P1 P1503CVAY-S73484W** (15290000 đ) | **Laptop Lenovo IdeaPad Slim 5 14Q8X9 83HL005AVN** (19990000 đ) | Đổi ngôi (Top 35) |

---

## 3. Phân Tích Định Lượng & Bằng Chứng Học Thuật

* **Hệ số tương quan hạng Spearman:** **$\rho = 0.6940$** ($p$-value $= 2.8199e-20$).
* **Biến động thứ hạng trung bình (Mean Rank Shift):** **21.64 bậc** (Dịch chuyển tối đa lên tới **97 bậc**).

### 4. Kết luận khoa học và phạm vi DECISIONS.md D10

1. **Minh chứng về hiện tượng Đếm đôi (Double Counting Bias):**
   - Tiêu chí Giá bán ($C01$) vốn dĩ đã là tiêu chí chi phí cốt lõi chiếm tới hơn 40% trọng số trong profile sinh viên.
   - Khi đưa thêm $\text{Value Gap}$ từ ML vào ma trận TOPSIS, giá bán tiếp tục đóng vai trò mẫu số trong công thức chênh lệch giá, dẫn đến việc các dòng máy siêu rẻ bị "thổi phồng" điểm số hai lần liên tiếp.
   - Ngược lại, các dòng máy mỏng nhẹ hoàn thiện cao cấp (vỏ kim loại, màn hình sắc nét) có chi phí sản xuất cao hơn cấu hình linh kiện thuần túy sẽ bị phạt điểm hai lần một cách bất công.
2. **Quyết định triển khai:**
   - Kết quả thực nghiệm giữ nguyên quyết định D10: **không tích hợp C18 vào ma trận TOPSIS V1**. TOPSIS thuần là chế độ mặc định và là đối tượng của OAT/Monte Carlo.
   - Chương trình có thêm lớp **ML-assisted tùy chọn** ngoài ma trận: $S_{final}=0.85S_{TOPSIS}+0.15S_{ML}$, dùng dự đoán OOF, chỉ áp dụng trong cửa sổ 15–40 triệu và giữ điểm trung tính ngoài cửa sổ.
   - Lớp tùy chọn này vẫn có rủi ro đếm đôi giá ở điểm đề xuất cuối; 15% là cap thiết kế minh bạch, không phải trọng số được tối ưu. Vì vậy không được diễn giải là kết quả TOPSIS thuần, không dùng để khẳng định một máy là “món hời”, và người dùng có thể tắt nó.
