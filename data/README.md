# Dữ liệu chạy của LaptopDSS

Chỉ các thư mục sau phục vụ chương trình:

- `catalog/laptops.csv`: catalog chuẩn, duy nhất, 513 cấu hình laptop (505 CellphoneS + 8 FPT Shop pilot). API, DSS và ML đều đọc file này.
- `catalog/benchmarks.csv`: bảng đối chiếu CPU/GPU (209 cặp chỉ số, gồm Geekbench 6 CPU, 3DMark Time Spy GPU & Geekbench 6 OpenCL/Metal GPU Compute) để tái tạo catalog và SQLite.

- `artifacts/`: SQLite cùng mô hình dự đoán giá, chỉ số và dự đoán OOF đã huấn luyện.
- `images/`: ảnh sản phẩm phục vụ giao diện.
- `raw/`: dữ liệu nguồn thô để truy vết.

`reports/` chỉ là báo cáo tái tạo được. `archive/legacy/` là kết quả pilot/cũ, không được API, DSS hoặc mô hình chạy hiện tại sử dụng.
