# CHUONGTRINH.md

# Kế hoạch tổng thể triển khai đề tài DSS lựa chọn laptop cho sinh viên kết hợp Machine Learning

> **Tên đề tài dự kiến:** Hệ hỗ trợ quyết định lựa chọn laptop phù hợp cho sinh viên kết hợp học máy.
>
> **Mục đích tài liệu:** Đây là tài liệu điều phối dự án dành cho nhóm phát triển và AI Agent. Tài liệu quy định mục tiêu, phạm vi, kiến trúc, quy trình, thuật toán, tiêu chuẩn chất lượng, các đầu ra cần bàn giao và những quyết định còn để mở. Agent phải đọc tài liệu này cùng `Data.md` trước khi phân tích hoặc viết mã.

---

## 0. Quy tắc làm việc dành cho AI Agent

1. Đọc toàn bộ `Chuongtrinh.md` và `Data.md` trước khi thực hiện công việc.
2. Không tự ý quyết định các mục được đánh dấu `TBD`, `CHƯA CHỐT` hoặc `CẦN NGƯỜI DÙNG CHỌN`. Hãy trình bày lựa chọn, ưu/nhược điểm và đề nghị phương án, sau đó chờ người dùng xác nhận nếu quyết định đó ảnh hưởng đáng kể đến kiến trúc, nguồn dữ liệu, phạm vi hoặc kết quả nghiên cứu.
3. Không tự bịa dữ liệu laptop, giá bán, điểm benchmark, thời lượng pin, ngày phát hành, URL hoặc kết quả mô hình. Giá trị chưa xác minh phải được ghi là thiếu/chưa xác minh.
4. Không coi tên CPU/GPU, tên dòng laptop hay hậu tố linh kiện là bằng chứng đủ để suy ra một điểm hiệu năng chính xác.
5. Không cộng trực tiếp điểm từ các bài benchmark khác hệ điểm. Chọn một nguồn/bài kiểm tra chính cho mỗi loại linh kiện; chỉ dùng nguồn phụ để đối chiếu hoặc bổ sung khi có quy tắc rõ ràng.
6. Không lấy `Price` hoặc biến được tạo trực tiếp từ giá mục tiêu làm đầu vào dự đoán giá. Tránh rò rỉ dữ liệu giữa tập huấn luyện và kiểm thử.
7. Không coi “thêm ML” mặc nhiên làm hệ thống tốt hơn. Phải thực nghiệm phiên bản có ML và không có ML, báo cáo kết quả thực tế, bao gồm trường hợp không cải thiện.
8. Không gộp nhiều dataset chỉ nhằm tăng số dòng. Trước khi ghép, phải xác minh đơn vị, thời điểm, khu vực giá, danh tính sản phẩm, giấy phép và định nghĩa các trường.
9. Không cào dữ liệu bằng cách vượt cơ chế bảo vệ, đăng nhập trái phép, né CAPTCHA hoặc gây tải không hợp lý. Kiểm tra điều khoản sử dụng, `robots.txt` và quy định của từng nguồn; ưu tiên API/dataset được cho phép hoặc thu thập thủ công có kiểm soát.
10. Mọi bước dữ liệu và mô hình phải có thể lặp lại: mã nguồn, cấu hình, seed, phiên bản thư viện, ngày thu thập, log và mô tả cách chạy.
11. Giữ riêng dữ liệu thô, dữ liệu sạch, dữ liệu đã chuẩn hóa, dữ liệu benchmark và dữ liệu dùng cho mô hình. Không ghi đè dữ liệu thô.
12. Khi phát hiện yêu cầu mâu thuẫn, dữ liệu không đủ hoặc quyết định chưa chốt, ghi vấn đề vào `DECISIONS.md` hoặc báo người dùng thay vì tự giải quyết âm thầm.

---

## 1. Bài toán và mục tiêu dự án

### 1.1. Bài toán

Người mua laptop thường gặp khó khăn khi so sánh sản phẩm vì thông tin từ cửa hàng không đồng nhất; cùng tên phân khúc CPU/GPU nhưng hiệu năng thực tế có thể khác nhau; chất lượng màn hình, pin, trọng lượng, khả năng nâng cấp và giá bán có ảnh hưởng khác nhau tùy nhu cầu. Giá bán còn có thể thay đổi theo cửa hàng và thời điểm.

Đề tài xây dựng hệ hỗ trợ quyết định (Decision Support System, DSS) giúp sinh viên lọc, so sánh và xếp hạng laptop theo ngân sách và nhu cầu cá nhân. Hệ thống sử dụng dữ liệu sản phẩm được chuẩn hóa, tham khảo benchmark bên ngoài, dùng Machine Learning để ước lượng giá laptop theo cấu hình và kết hợp AHP + TOPSIS để hỗ trợ xếp hạng.

### 1.2. Mục tiêu tổng quát

Xây dựng một prototype có khả năng:

- Thu thập hoặc nhập dữ liệu laptop từ nguồn có thể kiểm chứng.
- Chuẩn hóa thông số, giá và danh tính cấu hình.
- Tạo điểm hiệu năng CPU/GPU dựa trên nguồn benchmark được ghi nhận.
- Huấn luyện và đánh giá các mô hình hồi quy dự đoán giá dựa trên thông số máy.
- Cho phép người dùng thiết lập ngân sách, nhu cầu và mức ưu tiên.
- Dùng AHP để xác định trọng số ưu tiên và TOPSIS để xếp hạng các phương án.
- Tùy chọn tích hợp chỉ số giá trị tương đối do ML hỗ trợ, đồng thời so sánh DSS có ML và không có ML.
- Giải thích vì sao một laptop được đề xuất, nêu rõ điểm mạnh, hạn chế và dữ liệu thiếu.

### 1.3. Mục tiêu cụ thể

1. Thiết kế schema dữ liệu và quy trình truy vết nguồn.
2. Xây dựng quy trình làm sạch và chuẩn hóa dữ liệu laptop.
3. Xử lý riêng những trường dễ gây sai: CPU/GPU, RAM, storage, màn hình, pin, giá và cấu hình trùng.
4. Xây dựng baseline dự đoán giá trước khi thử mô hình phức tạp.
5. So sánh mô hình bằng MAE, RMSE và R² trên tập kiểm thử.
6. Xây dựng AHP phân cấp để giảm gánh nặng so sánh cặp khi có nhiều tiêu chí.
7. Cài đặt TOPSIS có xử lý đúng tiêu chí benefit/cost và chuẩn hóa dữ liệu.
8. Kiểm thử các hồ sơ nhu cầu khác nhau, không giả định một laptop tốt nhất cho tất cả người dùng.
9. Đánh giá chất lượng dữ liệu, hiệu năng mô hình và mức hợp lý của kết quả DSS bằng các thí nghiệm có thể lặp lại.

### 1.4. Không nằm trong phạm vi bắt buộc

Những nội dung sau chỉ là phần mở rộng, không được làm chậm bản prototype chính:

- Dự báo giá laptop nhiều tháng/năm trong tương lai khi chưa có chuỗi lịch sử đủ dài.
- Đánh giá mọi tiêu chí vật lý như tiếng ồn, nhiệt độ bề mặt, độ bền, bàn phím, touchpad và chất lượng webcam cho tất cả máy.
- Tự động cào tất cả website trong mọi điều kiện.
- Xây dựng mô hình deep learning hoặc LLM nếu mô hình hồi quy bảng dữ liệu đã phù hợp.
- Khẳng định hệ thống tìm ra laptop “tốt nhất tuyệt đối”; kết quả chỉ là khuyến nghị theo dữ liệu, ràng buộc và trọng số được chọn.

---

## 2. Nguyên tắc thiết kế

### 2.1. Phân biệt ba vai trò

**Nguồn bán lẻ:** cung cấp giá tại thời điểm thu thập và thông tin cấu hình được công bố.

**Nguồn benchmark/đánh giá:** cung cấp điểm kiểm thử hoặc phép đo độc lập cho CPU, GPU, pin, màn hình, nhiệt độ... khi tìm được dữ liệu đúng mẫu linh kiện/thiết bị.

**DSS:** kết hợp các thuộc tính và ưu tiên của người dùng để lọc, chấm điểm, xếp hạng, giải thích.

Không được coi một nguồn có thể đảm nhiệm chính xác tất cả vai trò. Điểm benchmark là một phép đo theo phương pháp nhất định, không phải thước đo hoàn hảo cho mọi công việc.

### 2.2. Thuộc tính dữ liệu không đồng nghĩa với tiêu chí DSS

Dataset có thể chứa 20-40 cột mô tả nhưng không nên mặc định tất cả đều là tiêu chí AHP/TOPSIS độc lập. Một số cột chỉ dùng để làm sạch, đối chiếu, giải thích hoặc tạo điểm tổng hợp.

Ví dụ:

- `CPU_Name`, `CPU_Cores`, `CPU_Threads`, `CPU_Suffix` có thể hỗ trợ chuẩn hóa/đối chiếu; tiêu chí DSS chính có thể là `CPU_Performance_Score`.
- `ScreenResolution`, `PanelType`, `RefreshRate_Hz`, `Brightness_Nits` có thể cung cấp dữ liệu để xây dựng/hiển thị đặc điểm màn hình; không nhất thiết mỗi cột có trọng số độc lập.
- `Storage_GB` và `Storage_Type` là hai khía cạnh khác nhau và có thể trở thành hai tiêu chí nếu dữ liệu đầy đủ.

Mục tiêu là có đủ thông tin để phân biệt laptop nhưng tránh đếm cùng một yếu tố nhiều lần.

### 2.3. Số lượng tiêu chí

Mục tiêu thiết kế là xem xét **ít nhất 15 tiêu chí ứng viên**. Bộ tiêu chí chính thức chỉ được chốt sau khi khảo sát dataset, độ đầy đủ, tương quan và mục tiêu sử dụng.

AHP với 15 tiêu chí phẳng sẽ đòi hỏi nhiều phép so sánh cặp. Vì vậy, ưu tiên **AHP phân cấp**: so sánh nhóm tiêu chí trước rồi so sánh tiêu chí bên trong từng nhóm. Không ép dùng đủ 15 tiêu chí nếu dữ liệu không đủ tin cậy.

### 2.4. Dữ liệu thiếu

- Giá, cấu hình nhận diện và trường mục tiêu ML phải đáp ứng điều kiện chất lượng tối thiểu.
- Không gán `0` cho thông tin không biết, đặc biệt với điểm benchmark, pin hoặc GPU.
- Không coi thiếu dữ liệu là giá trị kém nhất, trừ khi đó là một quy tắc quyết định được xác nhận và có ý nghĩa rõ.
- Ghi lại nguồn và quy tắc điền/loại bỏ trường.
- Nếu một tiêu chí thiếu trên phần lớn sản phẩm, cân nhắc loại khỏi xếp hạng chính và giữ như thông tin tham khảo.

### 2.5. Giá có tính thời gian

Mỗi bản ghi giá phải có ngày thu thập và nhà bán lẻ. Không dùng giá hiện tại để khẳng định mức giảm giá trong quá khứ nếu chưa có lịch sử giá. Không tự suy luận xu hướng tăng/giảm thị trường từ vài ví dụ riêng lẻ.

---

## 3. Phạm vi người dùng và hồ sơ nhu cầu

Hệ thống ban đầu hướng tới sinh viên, nhưng không áp đặt rằng mọi sinh viên có cùng nhu cầu. Người dùng cần có thể nhập ngân sách và chọn các ưu tiên.

### 3.1. Hồ sơ mẫu dùng để kiểm thử

1. **Lập trình/IT:** CPU, RAM, SSD, khả năng chạy nhiều ứng dụng/VM.
2. **AI/đồ họa/kỹ thuật:** GPU, CPU, RAM, màn hình; cân nhắc yêu cầu phần mềm.
3. **Văn phòng/học tập và di chuyển:** giá, pin, trọng lượng, màn hình, độ ổn định.
4. **Gaming:** GPU, CPU, RAM, màn hình/tần số quét, tản nhiệt nếu có dữ liệu.
5. **Nhu cầu hỗn hợp:** người dùng tự đặt mức ưu tiên.

Đây chỉ là các preset ban đầu. Người dùng phải có khả năng chỉnh ưu tiên, vì hai người cùng nhóm nhu cầu vẫn có thể lựa chọn khác nhau.

### 3.2. Ngân sách là ràng buộc

Ngân sách tối đa nên được áp dụng như bộ lọc trước khi xếp hạng, không chỉ như một tiêu chí có trọng số. Có thể cho phép người dùng bật tùy chọn “hiển thị máy vượt ngân sách” nhưng phải gắn nhãn rõ.

### 3.3. Ràng buộc tối thiểu

Có thể hỗ trợ những bộ lọc tùy chọn như RAM tối thiểu, cần GPU rời, trọng lượng tối đa, hệ điều hành hoặc kích thước màn hình. Bộ lọc này giúp loại các phương án không đáp ứng yêu cầu bắt buộc trước khi chạy TOPSIS.

---

## 4. Kiến trúc tổng thể

Quy trình dữ liệu và ra quyết định:

```text
Nguồn bán lẻ + nguồn benchmark/đánh giá + dataset mở (nếu được phép)
                         ↓
               Thu thập dữ liệu thô
                         ↓
       Lưu nguồn, ngày thu thập và điều kiện sử dụng
                         ↓
        Chuẩn hóa danh tính sản phẩm/cấu hình
                         ↓
       Làm sạch, khử trùng lặp, kiểm tra chất lượng
                         ↓
        Bảng laptop sạch + bảng giá + bảng benchmark
                         ↓
             Phân tích dữ liệu/feature engineering
                         ↓
     ┌───────────────────┴────────────────────┐
     ↓                                        ↓
ML: dự đoán giá                    DSS: xây dựng tiêu chí
     ↓                                        ↓
Đánh giá MAE/RMSE/R²                 AHP: xác định trọng số
     ↓                                        ↓
Giá dự đoán / chỉ số tương đối       TOPSIS: xếp hạng phương án
     └───────────────────┬────────────────────┘
                         ↓
        Danh sách laptop + lý do + cảnh báo dữ liệu
                         ↓
              Thử nghiệm/đánh giá hệ thống
```

### 4.1. Các thành phần phần mềm dự kiến

- `data_ingestion/`: nhập hoặc thu thập nguồn dữ liệu được phép.
- `data_cleaning/`: chuẩn hóa, kiểm tra, khử trùng lặp.
- `benchmark_matching/`: đối chiếu CPU/GPU với nguồn benchmark.
- `eda/`: phân tích dữ liệu và báo cáo chất lượng.
- `ml/`: pipeline huấn luyện, so sánh, lưu mô hình và dự đoán giá.
- `dss/ahp.py`: AHP, ma trận so sánh cặp, trọng số và tỷ lệ nhất quán.
- `dss/topsis.py`: chuẩn hóa, tính điểm và xếp hạng TOPSIS.
- `dss/criteria.py`: định nghĩa tiêu chí, benefit/cost và quy tắc chuẩn hóa.
- `app/`: giao diện prototype nếu được chọn.
- `tests/`: kiểm thử đơn vị và kiểm thử tích hợp.
- `reports/`: báo cáo chất lượng dữ liệu, benchmark mô hình và kết quả DSS.

Đây là gợi ý cấu trúc, có thể thay đổi theo ngôn ngữ/framework đã được người dùng chọn. Không tạo sẵn toàn bộ thư mục/mã phức tạp trước khi xác nhận kiến trúc triển khai.

### 4.2. Công nghệ dự kiến

Phương án khởi đầu phù hợp prototype:

- Python.
- pandas, NumPy.
- scikit-learn cho tiền xử lý và các mô hình hồi quy.
- matplotlib cho biểu đồ; thư viện bổ sung chỉ khi thật cần thiết.
- Streamlit hoặc Flask cho giao diện: **TBD, người dùng chọn sau**.
- CSV/Parquet cho giai đoạn thử nghiệm; SQLite hoặc cơ sở dữ liệu khác chỉ khi cần quản lý nhiều bảng/lịch sử giá.

Không dùng thư viện không cần thiết chỉ để làm dự án có vẻ phức tạp.

---

## 5. Danh sách tiêu chí DSS ứng viên

Bộ tiêu chí dưới đây là **danh sách ứng viên cần đánh giá**, không phải quyết định rằng tất cả phải được đưa vào TOPSIS. Mục tiêu là có ít nhất 15 tiêu chí hợp lý nếu dữ liệu cho phép.

| Mã | Tiêu chí ứng viên | Hướng | Dữ liệu/nguồn | Ghi chú |
|---|---|---|---|---|
| C01 | Giá bán hiện tại | Cost | Website bán lẻ | Có thể đồng thời là ràng buộc ngân sách |
| C02 | Hiệu năng CPU | Benefit | Benchmark chuẩn hóa | Ưu tiên một điểm CPU chính nhất quán |
| C03 | Hiệu năng GPU | Benefit | Benchmark chuẩn hóa | Đánh dấu tích hợp/rời; cần đúng GPU laptop |
| C04 | Dung lượng RAM | Benefit có ngưỡng | Cấu hình sản phẩm | Lợi ích có thể giảm sau ngưỡng nhu cầu |
| C05 | Khả năng nâng cấp RAM | Benefit | Trang hãng/bài đánh giá | Chỉ dùng nếu có dữ liệu xác minh |
| C06 | Dung lượng lưu trữ | Benefit có ngưỡng | Cấu hình sản phẩm | GB/TB chuẩn hóa |
| C07 | Công nghệ lưu trữ | Benefit | Cấu hình sản phẩm | HDD/SATA SSD/NVMe SSD; không quy đổi tùy tiện |
| C08 | Chất lượng màn hình tổng hợp | Benefit | Thông số/bài đánh giá | Có thể kết hợp độ phân giải, tấm nền, màu và độ sáng |
| C09 | Kích thước màn hình phù hợp | Tùy nhu cầu | Cấu hình sản phẩm | Không phải cứ lớn hơn là tốt hơn |
| C10 | Tần số quét | Benefit có điều kiện | Thông số sản phẩm | Quan trọng hơn với gaming/chuyển động |
| C11 | Thời lượng pin thực tế | Benefit | Bài đánh giá theo phương pháp rõ | Chỉ so sánh phép thử tương thích |
| C12 | Trọng lượng | Cost | Cấu hình/trang hãng | Có thể có ngưỡng phù hợp theo người dùng |
| C13 | Tính di động/sạc | Benefit theo nhu cầu | Trọng lượng, pin, sạc USB-C nếu có | Tránh đồng thời đếm lại pin và trọng lượng nếu điểm tổng hợp gồm chúng |
| C14 | Kết nối/cổng giao tiếp | Benefit theo nhu cầu | Thông số chính thức | Chỉ tách tiêu chí nếu có dữ liệu đủ và ý nghĩa rõ |
| C15 | Hệ điều hành/tương thích phần mềm | Fit/constraint | Thông số hãng, yêu cầu người dùng | Không coi một OS tốt cho mọi người |
| C16 | Khả năng sửa chữa/nâng cấp tổng thể | Benefit | Trang hãng/bài đánh giá | Có thể khó thu thập đồng nhất; ưu tiên mở rộng |
| C17 | Bảo hành/hỗ trợ | Benefit | Nhà bán lẻ/nhà sản xuất | Phân biệt bảo hành hãng và ưu đãi cửa hàng |
| C18 | Giá trị tương đối so với cấu hình (ML) | Benefit | Giá dự đoán và giá thực tế | Chỉ tích hợp sau khi đánh giá được mô hình |

### 5.1. Quy tắc chốt tiêu chí chính thức

Với mỗi tiêu chí, đánh giá:

1. Có liên quan trực tiếp đến việc chọn laptop không?
2. Có dữ liệu đủ, đáng tin và nhất quán không?
3. Có phân biệt được các phương án không?
4. Có trùng lặp mạnh với tiêu chí khác không?
5. Có dễ hiểu và giải thích cho sinh viên không?
6. Hướng benefit/cost/fit đã được định nghĩa rõ chưa?

Không đưa C13 nếu nó chỉ tính lại C11 và C12 mà không có định nghĩa độc lập. Không đưa C08 cùng lúc với toàn bộ thành phần màn hình như các tiêu chí có trọng số lớn mà không đánh giá trùng lặp. C18 chỉ được bật ở phiên bản DSS có ML.

### 5.2. Tiêu chí dạng ngưỡng hoặc mức phù hợp

Một số tiêu chí không tăng vô hạn theo hướng tốt hơn. Ví dụ, sinh viên văn phòng có thể không cần màn hình 18 inch; dung lượng RAM 64 GB không nhất thiết đáng giá hơn 32 GB nếu nhu cầu chỉ là văn phòng.

Đối với tiêu chí này, cần có hàm “mức phù hợp với nhu cầu” hoặc giới hạn/ngưỡng do người dùng chọn. Không áp dụng tuyến tính “càng nhiều càng tốt” cho mọi thuộc tính.

### 5.3. AHP phân cấp

Cấu trúc nhóm gợi ý:

- Kinh tế: giá, giá trị tương đối.
- Hiệu năng: CPU, GPU.
- Bộ nhớ: RAM, nâng cấp RAM, lưu trữ, công nghệ lưu trữ.
- Hiển thị: chất lượng màn hình, kích thước, tần số quét.
- Di động: pin, trọng lượng, sạc.
- Tiện ích/độ bền hỗ trợ: cổng kết nối, OS/tương thích, sửa chữa/nâng cấp, bảo hành.

Các nhóm trên chỉ là phương án khởi đầu. Nhóm phải quyết định tiêu chí nào thật sự có trong dữ liệu. AHP cần lưu ma trận so sánh cặp, trọng số và Consistency Ratio (CR). Dùng quy tắc CR mục tiêu dưới 0,10 làm hướng dẫn thông dụng; nếu không đạt thì yêu cầu người dùng xem lại đánh giá, không âm thầm bỏ qua.

---

## 6. Quy trình Machine Learning

### 6.1. Bài toán ML chính

Xây dựng bài toán hồi quy dự đoán giá bán của laptop từ thông số và đặc điểm sản phẩm.

- **Biến mục tiêu `y`:** giá bán đã chuẩn hóa theo chính sách thống nhất.
- **Đặc trưng `X`:** CPU benchmark, GPU benchmark, RAM, loại/dung lượng storage, màn hình, trọng lượng, thương hiệu, loại máy, hệ điều hành và những trường đủ dữ liệu.
- Không dùng giá mục tiêu, chiết khấu được tính trực tiếp từ giá mục tiêu hoặc biến hậu nghiệm làm đặc trưng đầu vào.

Nếu không đủ benchmark, lập baseline sử dụng thông số cấu hình đã làm sạch rồi bổ sung benchmark trong lần thử tiếp theo. Phải so sánh xem benchmark có cải thiện kết quả thực tế hay không.

### 6.2. Các mô hình ứng viên

Bắt đầu từ mô hình đơn giản, thêm độ phức tạp khi có lý do:

1. DummyRegressor (baseline theo giá trung bình/trung vị).
2. Linear Regression hoặc Ridge.
3. Decision Tree Regressor.
4. Random Forest Regressor.
5. Extra Trees Regressor.
6. HistGradientBoostingRegressor hoặc Gradient Boosting Regressor.
7. Mô hình boosting bổ sung chỉ khi môi trường và giấy phép thư viện phù hợp: **TBD**.

Không bắt buộc huấn luyện tất cả nếu cỡ dữ liệu hoặc tài nguyên không phù hợp. Không chọn mô hình chỉ vì nghe tên phổ biến.

### 6.3. Tiền xử lý ML

- Chia đặc trưng số và phân loại.
- Giá trị thiếu: imputation được thực hiện bên trong pipeline để tránh rò rỉ từ tập kiểm thử.
- Biến phân loại: dùng OneHotEncoder hoặc phương pháp đã được giải thích.
- Đặc trưng số: kiểm tra phân phối và scale khi mô hình yêu cầu.
- Chuẩn hóa đơn vị và xử lý ngoại lệ theo quy tắc được ghi nhận.
- Đóng gói preprocessing và estimator trong cùng pipeline để dự đoán nhất quán.

### 6.4. Chia dữ liệu và chống rò rỉ

Mặc định ban đầu có thể dùng 80% train và 20% test, nhưng phải điều chỉnh theo quy mô dữ liệu.

- Dùng random seed cố định để có kết quả lặp lại.
- Không fit preprocessing trên toàn bộ dữ liệu trước khi chia train/test.
- Nếu có nhiều giá của cùng một cấu hình, phải tránh để các bản ghi của cùng máy xuất hiện ở cả train và test theo cách gây rò rỉ. Cân nhắc chia nhóm theo model/configuration.
- Nếu có lịch sử giá theo thời gian và mục tiêu là dự báo về sau, dùng chia theo thời gian, không xáo trộn ngẫu nhiên.
- Nếu dataset quá nhỏ, dùng cross-validation trên tập huấn luyện và chỉ đánh giá cuối cùng một lần trên test.

### 6.5. Chỉ số đánh giá

- **MAE:** sai số tuyệt đối trung bình; dễ diễn giải bằng đơn vị tiền.
- **RMSE:** nhạy hơn với các sai số lớn.
- **R²:** mức độ giải thích biến thiên trong dữ liệu đánh giá; có thể âm và không phải accuracy.

Không báo cáo “accuracy 90%” cho bài toán hồi quy. Không đặt mục tiêu R² cụ thể như một kết quả bắt buộc. Chỉ báo cáo giá trị thực nghiệm, quy mô dữ liệu, cách chia dữ liệu và giới hạn.

### 6.6. Chọn mô hình

- So sánh mô hình trên cùng phân chia dữ liệu và cùng cách tiền xử lý hợp lệ.
- Chọn mô hình dựa trên MAE/RMSE và mục tiêu ứng dụng; xem xét R² như thông tin bổ sung.
- Phân tích sai số theo phân khúc giá, thương hiệu hoặc loại laptop nếu đủ dữ liệu.
- Lưu pipeline, phiên bản thư viện, tham số, seed, ngày huấn luyện và metrics.
- Không giả định mô hình phức tạp chắc chắn tốt hơn baseline.

### 6.7. Chỉ số giá trị tương đối do ML hỗ trợ

Ý tưởng: đối chiếu giá mô hình ước lượng từ cấu hình với giá quan sát. Giá thực tế thấp hơn mức mô hình ước lượng có thể là một tín hiệu “giá trị tương đối tốt”, nhưng không chứng minh chắc chắn laptop đáng mua hơn.

Công thức thử nghiệm ban đầu:

`value_gap = (predicted_price - observed_price) / predicted_price`

Các điều kiện bắt buộc:

- `predicted_price` phải dương và được tạo bởi mô hình được đánh giá trên dữ liệu hợp lệ.
- Xác định rõ `observed_price` là giá nào: giá niêm yết, giá sale hay mức giá đại diện đã chốt.
- Chuẩn hóa `value_gap` thành thang điểm dễ dùng cho TOPSIS nếu cần; công thức chuẩn hóa là **TBD**.
- Xem xét giới hạn ngoại lệ để các dự đoán cực sai không tạo điểm quá lớn.
- Không dùng `observed_price` trực tiếp như một đặc trưng dự đoán giá.
- Vì giá bán đã là tiêu chí C01, C18 có thể đếm lại một phần tác động giá. Phải chạy thử nghiệm có/không C18 và phân tích tương quan/tính nhạy của thứ hạng trước khi quyết định trọng số.
- Nếu mô hình không đủ chất lượng hoặc chỉ số thiếu ổn định, không tích hợp C18 vào DSS chính; giữ làm thử nghiệm nghiên cứu.

---

## 7. Quy trình DSS: lọc, AHP, TOPSIS, giải thích

### 7.1. Chuỗi xử lý quyết định

1. Người dùng nhập ngân sách, nhu cầu và điều kiện tối thiểu.
2. Hệ thống lọc laptop thỏa ràng buộc bắt buộc.
3. Hệ thống kiểm tra dữ liệu thiếu và loại phương án không thể so sánh theo chính sách đã chọn.
4. Chuyển các thuộc tính về biểu diễn số hoặc mức phù hợp có định nghĩa.
5. Xây dựng trọng số AHP theo hồ sơ nhu cầu hoặc câu trả lời của người dùng.
6. Kiểm tra Consistency Ratio của AHP.
7. Chạy TOPSIS với tiêu chí đã chốt và hướng benefit/cost.
8. Trả Top N laptop kèm giá, cấu hình chính, điểm theo tiêu chí, lý do xếp hạng và cảnh báo dữ liệu.
9. Nếu bật ML, chạy phiên bản có C18 để so sánh với phiên bản không ML.

### 7.2. TOPSIS

Triển khai TOPSIS theo quy trình tiêu chuẩn:

1. Tạo ma trận quyết định từ các laptop ứng viên và tiêu chí chính thức.
2. Chuẩn hóa ma trận bằng phương pháp đã lựa chọn và mô tả rõ.
3. Nhân giá trị chuẩn hóa với trọng số tiêu chí.
4. Xác định nghiệm lý tưởng dương và âm theo hướng benefit/cost.
5. Tính khoảng cách đến hai nghiệm lý tưởng.
6. Tính hệ số gần với nghiệm lý tưởng và xếp hạng.

Cần kiểm tra các trường hợp cạnh biên: một phương án, tiêu chí có giá trị giống nhau, dữ liệu bằng 0, tiêu chí thiếu hoặc tất cả phương án bị lọc hết.

### 7.3. Xử lý dữ liệu thiếu trong DSS

Chọn một chính sách công khai, có thể là:

- Không dùng tiêu chí có tỷ lệ thiếu vượt ngưỡng đã chọn.
- Không đưa phương án thiếu dữ liệu của một tiêu chí bắt buộc vào bảng xếp hạng.
- Cho phép chạy xếp hạng trên tập tiêu chí con có dữ liệu nhưng phải thông báo rằng kết quả không hoàn toàn so sánh được.

**Chính sách cụ thể và ngưỡng tỷ lệ thiếu: TBD.** Không thay dữ liệu thiếu bằng 0 và tiếp tục như thể đó là giá trị thật.

### 7.4. Giải thích kết quả

Mỗi kết quả nên hiển thị:

- Tên/mã cấu hình, nhà bán lẻ, giá và thời điểm giá được thu thập.
- Các thông số chính.
- Điểm/tác động theo nhóm tiêu chí.
- Lý do máy được xếp hạng cao hoặc thấp theo trọng số đã chọn.
- Thông tin chưa xác minh hoặc bị thiếu.
- Cảnh báo nếu giá là khuyến mãi ngắn hạn hoặc benchmark không có đúng cấu hình máy.

Không tự tạo lời giải thích nhân quả mà mô hình không hỗ trợ.

---

## 8. Thiết kế thí nghiệm

### 8.1. Thí nghiệm ML

- Baseline dự đoán giá.
- So sánh các mô hình ứng viên.
- So sánh đầu vào không có benchmark với đầu vào có benchmark nếu đủ dữ liệu.
- Báo cáo MAE, RMSE, R² trên cùng test set.
- Phân tích sai số lớn và phân khúc có hiệu quả kém.

### 8.2. Thí nghiệm DSS

Tối thiểu kiểm thử các hồ sơ nhu cầu: lập trình, AI/đồ họa, văn phòng/di động, gaming.

Kiểm tra:

- Ngân sách khác nhau có làm thay đổi danh sách phù hợp không?
- Thay đổi trọng số CPU/GPU/pin có ảnh hưởng thứ hạng hợp lý không?
- Bộ lọc ràng buộc có hoạt động đúng không?
- Một laptop thiếu dữ liệu pin có được xử lý đúng chính sách không?
- Cùng một cấu hình nhưng giá ở hai cửa hàng khác nhau được xử lý thế nào?

### 8.3. So sánh DSS không ML và có ML

- **Phiên bản A:** giá và các tiêu chí kỹ thuật; không dùng chỉ số giá trị ML.
- **Phiên bản B:** cùng bộ dữ liệu và tiêu chí, có thêm chỉ số giá trị tương đối ML nếu mô hình đủ chất lượng.

Báo cáo các thay đổi Top 5, laptop lên/xuống hạng, độ ổn định dưới thay đổi trọng số và các trường hợp cần giải thích. Không khẳng định B tốt hơn chỉ vì thứ hạng thay đổi. Nếu có thể, tổ chức đánh giá thủ công bởi người có kiến thức về laptop hoặc kiểm tra theo kịch bản; nêu rõ đây không phải ground truth tuyệt đối.

### 8.4. Đánh giá độ nhạy

Thử thay đổi trọng số tiêu chí ở một phạm vi nhỏ và ghi nhận mức thay đổi thứ hạng. Nếu thứ hạng đảo liên tục với thay đổi rất nhỏ, cần báo cáo độ nhạy thay vì trình bày kết quả như thể hoàn toàn ổn định.

---

## 9. Ứng dụng/giao diện prototype

**Framework giao diện: TBD.** Các lựa chọn ban đầu:

- Streamlit: triển khai nhanh dashboard Python, phù hợp prototype học thuật.
- Flask: linh hoạt hơn nếu muốn cấu trúc web tách frontend/backend.
- Không cần làm giao diện phức tạp trước khi pipeline dữ liệu và DSS hoạt động chính xác.

### 9.1. Màn hình đề xuất

1. **Màn hình yêu cầu:** ngân sách, mục đích, ưu tiên, bộ lọc tối thiểu.
2. **Danh sách đề xuất:** Top N laptop, giá và điểm tổng.
3. **Chi tiết sản phẩm:** cấu hình, benchmark, pin/màn hình nếu có và nguồn dữ liệu.
4. **So sánh laptop:** chọn 2-4 máy để xem khác biệt.
5. **Giải thích xếp hạng:** trọng số và điểm từng tiêu chí.
6. **Thông tin dữ liệu:** ngày cập nhật, tỷ lệ thiếu, cảnh báo dữ liệu.
7. **Trang đánh giá mô hình** dành cho báo cáo/nhóm phát triển: metrics, so sánh mô hình và phiên bản DSS.

### 9.2. Hành vi khi không đủ phương án

Nếu không có laptop thỏa ngân sách/ràng buộc, hệ thống phải thông báo rõ và cho phép người dùng nới ngân sách hoặc điều chỉnh tiêu chí. Không âm thầm bỏ ràng buộc.

---

## 10. Các giai đoạn triển khai và điều kiện hoàn thành

### Giai đoạn 0: Chốt quyết định nền tảng

Nhiệm vụ:

- Đọc tài liệu này và `Data.md`.
- Tạo `DECISIONS.md` liệt kê toàn bộ mục `TBD`.
- Chọn nguồn dữ liệu thử nghiệm, ngôn ngữ/framework và phạm vi thu thập.

Đầu ra:

- Bảng quyết định đã chốt/chưa chốt.
- Không bắt đầu cào quy mô lớn trước khi kiểm tra mẫu.

**Hoàn thành khi:** người dùng đã xác nhận các lựa chọn ảnh hưởng đến nguồn dữ liệu, phương pháp giá và benchmark.

### Giai đoạn 1: Proof of concept dữ liệu

Nhiệm vụ:

- Thu thập mẫu nhỏ có kiểm soát (đề xuất 30-100 listing ban đầu).
- Kiểm tra độ đầy đủ và độ ổn định của các trường.
- Phân biệt sản phẩm/cấu hình khác nhau.
- Thử ghép một tập CPU/GPU benchmark mẫu.

Đầu ra:

- File dữ liệu thô mẫu.
- Báo cáo trường thiếu, lỗi parsing, bản ghi trùng và tỷ lệ ghép benchmark thành công.
- Đề xuất bộ trường khả thi.

**Hoàn thành khi:** chứng minh được pipeline có thể chuẩn hóa dữ liệu thật và liệt kê rõ trường nào thu thập được/không được.

### Giai đoạn 2: Thu thập và làm sạch dataset

Nhiệm vụ:

- Mở rộng nguồn đã được xác nhận.
- Lưu URL, thời điểm, nhà bán lẻ, giá niêm yết/giá bán.
- Chuẩn hóa thông số và ghép benchmark đúng mã linh kiện.
- Khử trùng lặp và lập báo cáo chất lượng.

Mục tiêu dữ liệu sơ bộ: **500-1.500 cấu hình laptop đã chuẩn hóa nếu khả thi**, nhưng đây là mục tiêu kế hoạch chứ không phải điều kiện bắt buộc. Chất lượng, độ bao phủ phân khúc và độ xác minh quan trọng hơn số dòng. Có thể giảm phạm vi nếu nguồn hợp lệ không cho phép mở rộng.

**Hoàn thành khi:** schema và quy tắc được áp dụng nhất quán; có báo cáo dữ liệu thiếu, nguồn và bản ghi bị loại.

### Giai đoạn 3: EDA và chốt tiêu chí

Nhiệm vụ:

- Thống kê phân phối giá và thuộc tính.
- Kiểm tra dữ liệu ngoại lệ, sự trùng lặp và quan hệ giữa thuộc tính.
- Đánh giá khả năng sử dụng các tiêu chí ứng viên.
- Chốt ít nhất 15 tiêu chí chỉ khi dữ liệu hỗ trợ; nếu không, giải thích lý do chọn ít hơn hoặc tổ chức theo nhóm.

Đầu ra: báo cáo EDA, bảng tiêu chí cuối cùng, định nghĩa benefit/cost/fit và quy tắc chuẩn hóa.

**Hoàn thành khi:** mọi tiêu chí DSS có định nghĩa, nguồn, cách chuyển thành điểm và quy tắc xử lý thiếu.

### Giai đoạn 4: Pipeline ML

Nhiệm vụ:

- Tạo baseline.
- Huấn luyện mô hình hồi quy ứng viên.
- So sánh MAE/RMSE/R².
- Chọn mô hình và lưu pipeline.
- Tính chỉ số giá trị tương đối nếu mô hình đủ chất lượng.

**Hoàn thành khi:** có kết quả tái lập và không có rò rỉ dữ liệu rõ ràng.

### Giai đoạn 5: AHP + TOPSIS

Nhiệm vụ:

- Xây dựng nhóm tiêu chí phân cấp.
- Tạo trọng số preset ban đầu và/hoặc quy trình thu thập đánh giá từ người dùng.
- Tính CR.
- Cài TOPSIS và viết kiểm thử đơn vị.
- Tạo kết quả giải thích được.

**Hoàn thành khi:** kiểm thử được các trường hợp bình thường, biên và dữ liệu thiếu.

### Giai đoạn 6: Tích hợp giao diện

Nhiệm vụ:

- Kết nối yêu cầu người dùng, bộ lọc, AHP, TOPSIS và ML.
- Hiển thị Top N cùng thông tin nguồn.
- Cho phép so sánh máy và xem giải thích.

**Hoàn thành khi:** một người dùng thử có thể nhập yêu cầu và nhận kết quả mà không chạy mã thủ công.

### Giai đoạn 7: Đánh giá, báo cáo và đóng gói

Nhiệm vụ:

- Chạy thí nghiệm ML/DSS.
- So sánh phiên bản có/không có chỉ số ML.
- Thực hiện đánh giá độ nhạy.
- Viết hạn chế dữ liệu, giới hạn mô hình và đề xuất mở rộng.
- Cung cấp hướng dẫn cài đặt/chạy lại.

**Hoàn thành khi:** có kết quả thực nghiệm, code, dữ liệu xử lý theo quyền sử dụng, README và tài liệu báo cáo.

---

## 11. Tiêu chuẩn nghiệm thu

### 11.1. Dữ liệu

- Trường giá có tiền tệ, loại giá, nhà bán lẻ và thời điểm.
- Mỗi bản ghi có ID ổn định trong dự án và trường nguồn.
- Không ghép cấu hình khác nhau chỉ dựa trên tên model gần giống.
- Giá trị thiếu được ghi nhận và xử lý theo quy tắc.
- Benchmark có nguồn, tên bài test, điểm và ngày lấy dữ liệu.
- Không có dữ liệu bịa hoặc điểm benchmark không truy vết được.

### 11.2. ML

- Có baseline và ít nhất một mô hình học máy so sánh.
- Có train/test hoặc cross-validation phù hợp.
- Báo cáo MAE, RMSE, R².
- Có thể tái tạo pipeline bằng cấu hình lưu lại.
- Không tuyên bố accuracy cho hồi quy.

### 11.3. DSS

- Ngân sách và điều kiện cứng được xử lý đúng.
- AHP có trọng số và kiểm tra nhất quán.
- TOPSIS xử lý đúng benefit/cost.
- Kết quả đổi theo nhu cầu khác nhau khi dữ liệu và trọng số yêu cầu điều đó.
- Có thông tin giải thích và cảnh báo dữ liệu thiếu.
- Có so sánh phiên bản không ML và có ML nếu C18 được bật.

### 11.4. Mã nguồn

- Có README hướng dẫn cài đặt và chạy.
- Có file requirements/environment.
- Có kiểm thử các phần chuẩn hóa, AHP, TOPSIS và pipeline dữ liệu.
- Không hard-code đường dẫn tuyệt đối trên máy của một cá nhân.
- Không chứa khóa API hoặc thông tin bí mật.

---

## 12. Rủi ro và cách giảm thiểu

| Rủi ro | Ảnh hưởng | Cách xử lý |
|---|---|---|
| Website đổi cấu trúc/chặn truy cập | Thu thập hỏng | Dùng adapter theo nguồn, kiểm tra định kỳ, giữ dữ liệu đã thu thập hợp lệ; tuân thủ điều khoản |
| Cấu hình trùng tên nhưng khác phiên bản | Ghép sai giá/benchmark | Dùng model/config ID, CPU/RAM/SSD/GPU/màn hình và mã sản phẩm nếu có |
| Thiếu pin/màn hình/tản nhiệt | Không thể xếp hạng đồng đều | Thử mẫu, loại/giữ tiêu chí theo quy tắc; không bịa dữ liệu |
| Benchmark khác phương pháp | So sánh sai | Chọn một benchmark chính nhất quán cho CPU/GPU; không cộng điểm khác thang đo |
| Giá khuyến mãi ngắn hạn | Sai lệch mục tiêu ML | Lưu loại giá và thời điểm; chọn định nghĩa target rõ ràng |
| Rò rỉ dữ liệu | Metrics quá lạc quan | Pipeline, split theo nhóm hoặc thời gian khi phù hợp |
| Đếm đôi các tiêu chí | Xếp hạng thiên lệch | AHP phân cấp, xem xét tương quan, không đưa điểm tổng hợp và mọi thành phần cùng lúc nếu không có lý do |
| ML không cải thiện DSS | Phần ML thiếu giá trị thực tế | Báo cáo trung thực; có thể giữ ML ở vai trò phân tích giá hoặc đề xuất lại biến đóng góp |
| AHP quá nặng với nhiều tiêu chí | Khó nhập trọng số | AHP phân cấp, preset nhu cầu và cho phép chỉnh sửa |
| Dữ liệu ít hoặc thiên về gaming/cao cấp | Kém đại diện cho sinh viên | Lập kế hoạch lấy mẫu theo phân khúc; ghi rõ phạm vi dữ liệu |

---

## 13. Các quyết định còn mở (không tự ý chốt)

Agent phải tạo/duy trì một bảng trong `DECISIONS.md` theo các mục sau.

| Mã | Quyết định | Lựa chọn ban đầu | Đề xuất có điều kiện |
|---|---|---|---|
| D01 | Nguồn bán lẻ chính | Xgear, FPT Shop, Thế Giới Di Động, CellphoneS, LaptopAZ hoặc nguồn khác | Chọn sau thử nghiệm thu thập và kiểm tra điều khoản |
| D02 | Có dùng dataset mở làm seed/baseline không | Kaggle Laptop Price hoặc dataset khác; chỉ dataset bán lẻ; kết hợp có kiểm soát | Không merge thẳng với giá Việt Nam; dùng làm tham khảo hoặc benchmark riêng |
| D03 | Quy mô dataset | 500-1.500 cấu hình; nhỏ hơn nếu bị giới hạn | Chốt sau proof of concept |
| D04 | Giá mục tiêu ML | Giá sale; giá niêm yết; median nhiều cửa hàng; một mức giá chuẩn | Lưu mọi loại giá có thể, chọn một target rõ ràng |
| D05 | Benchmark CPU chính | Geekbench 6 Multi-Core (kèm Single-Core) | Đã chốt chính thức (hỗ trợ cross-platform x86, ARM, Apple Silicon) |
| D06 | Benchmark GPU chính | 3DMark Time Spy Graphics (kèm Notebookcheck TGP) | Đã chốt chính thức cho laptop Windows dGPU (chuẩn DirectX 12) |
| D07 | Có sử dụng điểm pin thực tế không | Có; không; chỉ nhóm mẫu có đủ coverage | Ưu tiên nếu phép thử có phương pháp tương thích |
| D08 | Bộ tiêu chí DSS cuối cùng | 15-18 tiêu chí ứng viên | Chốt dựa trên EDA/coverage và tránh đếm đôi |
| D09 | AHP nhập trọng số | Ma trận cặp đầy đủ; AHP phân cấp; preset có thể chỉnh | Ưu tiên phân cấp |
| D10 | Công thức `Value for Money` | Chỉ số chênh lệch giá dự đoán/quan sát; không dùng; công thức khác | Chỉ bật sau khi kiểm định mô hình và phân tích trùng với tiêu chí giá |
| D11 | Giao diện | Streamlit; Flask; CLI/dashboard trước | Streamlit nếu mục tiêu là prototype nhanh |
| D12 | Lưu dữ liệu | CSV/Parquet; SQLite; DB khác | CSV/Parquet ban đầu, nâng cấp khi cần lịch sử/quan hệ |
| D13 | Lịch sử giá | Một lần chụp; thu thập định kỳ; nguồn lịch sử được phép | Bắt đầu ghi snapshot ngay từ ngày thu thập đầu tiên |
| D14 | Chính sách dữ liệu thiếu | Loại tiêu chí; loại sản phẩm; xếp hạng theo tập con | Chốt trước khi TOPSIS |
| D15 | Dữ liệu CPU/GPU AI/NPU | Tiêu chí riêng; lưu thuộc tính nhưng chỉ filter; bỏ ở phiên bản đầu | Thu thập nếu độ phủ đủ, không ép thành tiêu chí |

---

## 14. Yêu cầu đầu ra cuối cùng

Khi hoàn thành prototype, dự án nên có tối thiểu:

1. `README.md`: cài đặt, cấu hình và cách chạy.
2. `Chuongtrinh.md` và `Data.md`: tài liệu kế hoạch/quy tắc dữ liệu.
3. `DECISIONS.md`: các lựa chọn đã chốt và lý do.
4. Dữ liệu thô được phép lưu và dữ liệu đã chuẩn hóa, cùng data dictionary.
5. Mã nguồn pipeline thu thập/nhập, làm sạch, benchmark matching, ML, AHP/TOPSIS.
6. Báo cáo chất lượng dữ liệu.
7. Bảng so sánh mô hình và metrics.
8. Kết quả kiểm thử DSS theo hồ sơ nhu cầu.
9. So sánh DSS có ML và không ML nếu C18 được sử dụng.
10. Hướng dẫn nêu rõ hạn chế, phạm vi và những dữ liệu không thể xác minh.

**Nguyên tắc kết thúc:** Một quyết định minh bạch và có thể truy vết tốt hơn một hệ thống có nhiều thông số nhưng nguồn gốc mơ hồ. Ưu tiên chất lượng dữ liệu và khả năng lặp lại trước số lượng tính năng.
