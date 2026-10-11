# BÁO CÁO KIỂM THỬ KỊCH BẢN NỘI BỘ (INTERNAL SCENARIO TESTING REPORT)
## Giai Đoạn 6: Kiểm Thử Độc Lập 20 Hồ Sơ Nhu Cầu Người Dùng Thực Tế

**Ngày thực hiện:** 11/10/2026  
**Quy mô kho máy:** 220 laptop chuẩn hóa (210 CellphoneS + 10 FPT Shop)  
**Tính chất khoa học:** **Kiểm thử kịch bản nội bộ tự động (Automated Scenario Verification)**. Báo cáo này ghi nhận chính xác kết quả xuất từ thuật toán TOPSIS + AHP, tuyệt đối **không giả mạo số liệu khảo sát người dùng hay tỷ lệ chấp nhận (Acceptance Rate) chưa đo đạc thực tế**.

---

## 1. Phương Pháp & Tiêu Chí Kiểm Thử Kịch Bản

Hệ thống thiết lập 20 kịch bản bao quát 4 nhóm đối tượng người mua máy tính phổ biến tại Việt Nam:
1. **Nhóm Sinh viên & Kinh tế (S01–S05):** Ngân sách eo hẹp (13M–20M), cần CPU phản hồi mượt, RAM vừa đủ, trọng lượng nhẹ.
2. **Nhóm Kỹ thuật & Lập trình (S06–S10):** Cần CPU đa nhân khỏe để compile mã nguồn, RAM 16GB–32GB, cổng mạng LAN RJ45, khả năng nâng cấp.
3. **Nhóm Gaming & Đồ họa nặng (S11–S15):** Ép lọc bắt buộc GPU rời (RTX 3050/4050/5050), màn hình $\ge 144$ Hz, Windows.
4. **Nhóm Mỏng nhẹ & Siêu di động (S16–S20):** Lọc cứng trọng lượng $\le 1.45$ kg, sạc nhanh Type-C PD, màn hình độ sáng cao/OLED.

---

## 2. Bảng Tổng Hợp Kết Quả Gợi Ý Top 1 Cho 20 Kịch Bản

| Mã | Nhóm nhu cầu | Tiêu đề kịch bản & Yêu cầu | Ngân sách tối đa | Số máy hợp lệ | Máy gợi ý đứng đầu (Top 1) | Điểm TOPSIS |
| :---: | :--- | :--- | :---: | :---: | :--- | :---: |
| **S01** | Sinh viên & Kinh tế | Sinh viên năm nhất ngành kinh tế, ngân sách < 15 triệu | 15,000,000 đ | 3 | **Laptop Dell Inspiron 15 3520 JYM17 - Nhập khẩu chính hãng** | 0.8204 |
| **S02** | Sinh viên & Kinh tế | Sinh viên đại cương, ngân sách < 18 triệu | 18,000,000 đ | 9 | **Laptop Dell Inspiron 15 3520 JYM17 - Nhập khẩu chính hãng** | 0.8163 |
| **S03** | Sinh viên & Kinh tế | Sinh viên cần RAM tối thiểu 16GB làm đa nhiệm, ngân sách < 20 triệu | 20,000,000 đ | 8 | **Laptop MSI Modern 14 C12MO-660VN** | 0.7573 |
| **S04** | Sinh viên & Kinh tế | Sinh viên cần màn hình lớn 15.6 inch để đọc tài liệu, ngân sách < 18 triệu | 18,000,000 đ | 4 | **Laptop Dell Inspiron 15 3520 JYM17 - Nhập khẩu chính hãng** | 0.8264 |
| **S05** | Sinh viên & Kinh tế | Sinh viên ưu tiên máy ASUS, ngân sách < 19 triệu | 19,000,000 đ | 3 | **Laptop ASUS VivoBook 14 X1404VA-EB609W** | 1.0 |
| **S06** | Kỹ thuật & Lập trình | Sinh viên IT học Code Web/Backend, ngân sách < 22 triệu | 22,000,000 đ | 31 | **Laptop ASUS VivoBook 15 M1502NAQ-BQ031W** | 0.7736 |
| **S07** | Kỹ thuật & Lập trình | Lập trình viên chạy Docker/Máy ảo, ngân sách < 25 triệu | 25,000,000 đ | 54 | **Laptop ASUS VivoBook 15 M1502NAQ-BQ031W** | 0.768 |
| **S08** | Kỹ thuật & Lập trình | Kỹ sư phần mềm cần CPU Intel Core Ultra, ngân sách < 30 triệu | 30,000,000 đ | 12 | **Laptop ASUS Vivobook 16 X1607CA-MB399W** | 0.7337 |
| **S09** | Kỹ thuật & Lập trình | Lập trình viên cần RAM dồi dào/khả năng nâng cấp, ngân sách < 28 triệu | 28,000,000 đ | 51 | **Laptop ASUS VivoBook 15 M1502NAQ-BQ031W** | 0.7513 |
| **S10** | Kỹ thuật & Lập trình | Kỹ sư hệ thống cần cổng mạng LAN RJ45, ngân sách < 26 triệu | 26,000,000 đ | 12 | **Laptop MSI Cyborg 14 A13UDX-099VN** | 0.8109 |
| **S11** | Gaming & Đồ họa | Gamer eSports ngân sách nhập môn < 24 triệu | 24,000,000 đ | 2 | **Laptop MSI Gaming Thin 15 B13UC-3247VN** | 0.9539 |
| **S12** | Gaming & Đồ họa | Gamer chiến game AAA tầm trung, ngân sách < 27 triệu | 27,000,000 đ | 11 | **Laptop MSI Cyborg 14 A13UDX-099VN** | 0.7741 |
| **S13** | Gaming & Đồ họa | Gamer đồ họa nặng cần RTX 4050 / RTX 5050, ngân sách < 35 triệu | 35,000,000 đ | 10 | **Laptop Lenovo LOQ 15IRX9 83DV01H3VN** | 0.7768 |
| **S14** | Gaming & Đồ họa | Gamer ưa chuộng dòng ASUS TUF / ROG, ngân sách < 30 triệu | 30,000,000 đ | 7 | **Laptop ASUS TUF Gaming A15 FA506NCG-HN329W** | 0.7372 |
| **S15** | Gaming & Đồ họa | Gamer cao cấp cần màn hình chuẩn màu (100% sRGB/DCI-P3), ngân sách < 50 triệu | 50,000,000 đ | 28 | **Laptop Lenovo Legion 5 15IRX10 83LY00HQVN** | 0.7995 |
| **S16** | Mỏng nhẹ & Di động | Nhân viên kinh doanh thường xuyên di chuyển, ngân sách < 20 triệu | 20,000,000 đ | 10 | **Laptop MSI Modern 14 C12MO-660VN** | 0.6675 |
| **S17** | Mỏng nhẹ & Di động | Chuyên gia di động cần màn hình độ sáng cao (>= 300 nits), ngân sách < 23 triệu | 23,000,000 đ | 8 | **MacBook Neo 13 inch A18 Pro 2026 6CPU 5GPU 8GB 256GB | Chính hãng Apple Việt Nam** | 0.8024 |
| **S18** | Mỏng nhẹ & Di động | Doanh nhân cần sạc nhanh Type-C Power Delivery, ngân sách < 25 triệu | 25,000,000 đ | 17 | **Laptop MSI Modern 14 C12MO-660VN** | 0.6775 |
| **S19** | Mỏng nhẹ & Di động | Người làm nội dung cần ultrabook màn hình OLED, ngân sách < 32 triệu | 32,000,000 đ | 1 | **Laptop Asus Zenbook 14 UX3405CA-ST1713W Ultra 5 225H/AI/16GB/512GB/14 3K OLED/Win11** | 1.0 |
| **S20** | Mỏng nhẹ & Di động | Ultrabook cao cấp trọng lượng siêu nhẹ <= 1.25kg, ngân sách < 35 triệu | 35,000,000 đ | 16 | **MacBook Neo 13 inch A18 Pro 2026 6CPU 5GPU 8GB 256GB | Chính hãng Apple Việt Nam** | 0.6061 |

---

## 3. Phân Tích Tính Hợp Lý Của Kết Quả Gợi Ý

1. **Phân hóa theo phân khúc ngân sách:**
   - Ở mức ngân sách dưới 15–18 triệu (S01, S02), hệ thống chọn chính xác mẫu tối ưu giá/hiệu năng: *Laptop Dell Inspiron 15 3520 JYM17 - Nhập khẩu chính hãng*.
   - Khi có thêm ràng buộc RAM 16GB (S03), máy được đề xuất tự động chuyển sang dòng *Laptop MSI Modern 14 C12MO-660VN* cấu hình 16GB RAM.
2. **Tuân thủ đúng ràng buộc phần cứng:**
   - Kịch bản S04 (màn hình 15.6 inch) lọc chính xác các máy 15.6" (*Laptop Dell Inspiron 15 3520 JYM17 - Nhập khẩu chính hãng*).
   - Kịch bản S13 (Gaming card RTX 4050/5050) chọn chính xác *Laptop Lenovo LOQ 15IRX9 83DV01H3VN*.
   - Kịch bản S20 (Siêu mỏng nhẹ $\le 1.25$ kg) chọn chính xác *MacBook Neo 13 inch A18 Pro 2026 6CPU 5GPU 8GB 256GB | Chính hãng Apple Việt Nam*.

---

### Ghi chú hiệu chỉnh kịch bản

S13 sử dụng ngân sách 35 triệu VNĐ (thay cho 32 triệu trong bản phác thảo) và
S15 sử dụng 50 triệu VNĐ (thay cho 45 triệu) để tập ứng viên sau các ràng buộc
kỹ thuật vẫn có đủ phương án cho kiểm thử xếp hạng. Đây chỉ là hiệu chỉnh đầu
vào kiểm thử, không thay đổi thuật toán hay trọng số AHP-TOPSIS.

---

## 4. Tuyên Bố Liêm Chính Học Thuật (Academic Integrity Note)

* **Giới hạn thử nghiệm:** Đây là kết quả kiểm thử thuật toán nội bộ dựa trên dữ liệu sản phẩm thực tế của 2 nhà bán lẻ.
* **Không tuyên bố số liệu khảo sát:** Dự án không đưa vào các con số chưa đo đạc như "85% người dùng hài lòng" hay "giảm 85% thời gian". Các đánh giá về độ hài lòng người dùng thực tế sẽ được triển khai trong nghiên cứu thực địa mở rộng ở giai đoạn tiếp theo của đề tài.
