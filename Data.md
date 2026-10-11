# Data.md

# Đặc tả dataset và kế hoạch thu thập dữ liệu laptop

> **Vai trò tài liệu:** Quy định cần thu thập dữ liệu gì, từ nguồn nào, theo cách nào, cách lưu dữ liệu thô và dữ liệu sạch, chuẩn hóa tên CPU/GPU, đối chiếu benchmark, quản lý giá theo thời gian, xử lý dữ liệu thiếu và các quyết định còn mở. Dùng kèm `Chuongtrinh.md`.
>
> **Lưu ý:** Nguồn được liệt kê là ứng viên, chưa phải quyết định cuối cùng. Cần kiểm tra điều khoản sử dụng, `robots.txt`, khả năng truy cập và tính đầy đủ bằng một đợt thử nghiệm nhỏ trước khi cào quy mô lớn.

---

## 1. Nguyên tắc dữ liệu

1. Mỗi thông tin cần có nguồn và thời điểm thu thập.
2. Giữ bản dữ liệu thô nguyên vẹn; làm sạch trên bản sao hoặc qua pipeline có thể chạy lại.
3. Không tự bịa thông số, giá, điểm benchmark, thời lượng pin hoặc ngày ra mắt.
4. Không ghép sản phẩm chỉ dựa vào tên gần giống. Một model laptop có thể có nhiều cấu hình CPU/RAM/SSD/GPU/màn hình.
5. Không ghép trực tiếp nhiều dataset chỉ để tăng số dòng. Khác biệt tiền tệ, khu vực, năm, định nghĩa trường và phiên bản sản phẩm có thể tạo ra dữ liệu sai lệch.
6. Lưu các loại giá riêng: giá niêm yết, giá bán/giá sau giảm, giá đặc biệt nếu có, ngày thu thập và nhà bán lẻ.
7. Không xem thiếu dữ liệu là 0. Mỗi kiểu thiếu cần mã hóa nhất quán và được mô tả.
8. CPU/GPU benchmark phải có tên phép thử và nguồn. Không cộng thẳng điểm từ thang đo khác nhau.
9. Ưu tiên một benchmark chính cho CPU và một benchmark chính cho GPU để giữ quy trình dễ quản lý. Benchmark khác chỉ là dữ liệu phụ/đối chiếu nếu cần.
10. Tuân thủ điều khoản sử dụng, quy tắc truy cập tự động, `robots.txt` và các giới hạn kỹ thuật của nguồn. Không vượt CAPTCHA, tường đăng nhập, cơ chế chống bot hoặc giới hạn truy cập.

---

## 2. Kế hoạch nguồn dữ liệu

### 2.1. Nguồn bán lẻ tại Việt Nam (chưa chốt)

Những trang sau là ứng viên cần khảo sát. Chúng có thể thay đổi đường dẫn/cấu trúc, vì vậy cần kiểm tra lại khi triển khai.

| Mã | Nguồn ứng viên | URL tham khảo | Vai trò | Điểm cần xác minh |
|---|---|---|---|---|
| S01 | Xgear | https://xgear.net/collections/laptop | Laptop gaming/cao cấp, cấu hình và giá | Khả năng thu thập hợp lệ, độ đầy đủ thông tin, sản phẩm trùng phiên bản |
| S02 | FPT Shop | https://fptshop.com.vn/may-tinh-xach-tay | Laptop văn phòng, học tập và nhiều phân khúc | Cấu trúc trang, quy tắc truy cập, chính sách giá/khuyến mãi |
| S03 | Thế Giới Di Động | https://www.thegioididong.com/laptop | Bộ lọc và dữ liệu sản phẩm phổ biến | Phân biệt giá bán/giá niêm yết, biến thể cấu hình |
| S04 | CellphoneS | https://cellphones.com.vn/laptop.html | Cấu hình và giá nhiều phân khúc | Cách thể hiện giá và ưu đãi, điều kiện truy cập |
| S05 | LaptopAZ | https://laptopaz.vn/ | Laptop theo cấu hình, giá và thông tin kỹ thuật | Trang danh mục/chi tiết, trường nào thực sự có sẵn |
| S06 | Nguồn bán lẻ khác | Người dùng quyết định sau | Bổ sung độ phủ nếu cần | Chỉ thêm sau khi xác minh giá trị tăng thêm và quyền sử dụng |

**Chưa chốt:** chọn một nguồn chính hay nhiều nguồn. Đề xuất thử nghiệm 1-2 nguồn trước. Chỉ thêm nguồn khi có thể chuẩn hóa dữ liệu và tạo độ phủ tốt hơn rõ ràng.

### 2.2. Nguồn benchmark CPU (Đã chốt chính thức theo D05)

* **Nguồn chính thức:** **Geekbench 6 Browser** (`https://browser.geekbench.com/`)
* **Chỉ số:** Geekbench 6 Multi-Core (lưu kèm Geekbench 6 Single-Core).
* **Lý do lựa chọn:** Geekbench 6 là bộ kiểm chuẩn duy nhất hỗ trợ so sánh hiệu năng kiến trúc CPU chéo nền tảng (cross-platform parity) công bằng giữa x86 (Intel Core/Core Ultra, AMD Ryzen), ARM (Qualcomm Snapdragon X Elite/Plus) và Apple Silicon (M-series, A-series). Không sử dụng PassMark CPU Mark vì PassMark không hỗ trợ native công bằng trên macOS/Apple Silicon.

### 2.3. Nguồn benchmark GPU (Đã chốt chính thức theo D06)

* **Nguồn chính thức:** **3DMark Time Spy Graphics** (`https://www.3dmark.com/`) kết hợp đối chiếu TGP thực tế từ **Notebookcheck** (`https://www.notebookcheck.net/`).
* **Phạm vi áp dụng:** Chỉ áp dụng cho các laptop Windows trang bị card đồ họa rời (discrete GPU). Tuyệt đối không đưa card tích hợp (iGPU) hay Apple GPU vào chung thang đo 3DMark Time Spy.
* **Lý do lựa chọn:** 3DMark Time Spy là bài test chuẩn công nghiệp đồ họa DirectX 12, phản ánh chân thực năng lực render và chiến game của GPU rời theo từng mức công suất TGP. Loại bỏ PassMark G3D Mark vì không phân biệt được mức TGP thực tế của laptop.

### 2.4. Nguồn đánh giá laptop, pin, màn hình và nhiệt độ

| Mã | Nguồn | URL | Vai trò | Giới hạn |
|---|---|---|---|---|
| R01 | Notebookcheck | https://www.notebookcheck.net/ | Bài review laptop, CPU/GPU, pin, màn hình, nhiệt độ, độ ồn tùy mẫu | Các phép thử chỉ so sánh trực tiếp khi phương pháp/điều kiện tương thích |
| R02 | Website chính thức hãng laptop | Ví dụ: website ASUS, Lenovo, HP, Dell, Acer, Apple, MSI... | Thông số công bố, dung lượng pin, loại màn hình, kích thước, cổng | Thời lượng pin quảng cáo không tương đương thời lượng đo thực tế |
| R03 | Trang đánh giá khác | Người dùng quyết định sau | Bổ sung kết quả kiểm thử | Chỉ thêm nếu nguồn và phép thử đủ rõ ràng |

### 2.5. Dataset mở (tùy chọn, chưa chốt)

Một dataset có thể dùng để tham khảo schema, thử pipeline hoặc làm baseline riêng:

- Kaggle Laptop Price của Muhammet Varlı: https://www.kaggle.com/datasets/muhammetvarl/laptop-price
- Dataset này mô tả các trường truyền thống như Company, Product, TypeName, Inches, ScreenResolution, Cpu, Ram, Memory, GPU, OpSys, Weight và Price_euros.

Điểm cần lưu ý:

- Dataset này không tự động đại diện cho thị trường Việt Nam hiện tại.
- Tiền tệ, thời điểm dữ liệu, mức giá và nguồn sản phẩm khác với các website bán lẻ tại Việt Nam.
- Cần kiểm tra giấy phép/điều khoản của dataset trước khi dùng.
- **Không merge trực tiếp giá euro với giá VNĐ và coi là một phân phối giá thống nhất.**
- Có thể dùng dataset mở làm bài thử pipeline hoặc bộ đối chiếu riêng; quyết định cuối cùng do người dùng chọn.

---

## 3. Chiến lược thu thập: làm thử trước, mở rộng sau

### Giai đoạn A: khảo sát nguồn

1. Mở trang danh mục và trang chi tiết của một số laptop thuộc phân khúc văn phòng, gaming, mỏng nhẹ/cao cấp.
2. Ghi danh sách trường có thật, không dựa vào dự đoán về trang.
3. Kiểm tra điều khoản sử dụng, `robots.txt`, cấu trúc truy cập và giới hạn yêu cầu.
4. Đánh giá có thể thu thập hợp lệ bằng cách nào: thủ công, xuất dữ liệu, API được cấp phép hoặc cào tốc độ thấp nếu được cho phép.
5. Tạo báo cáo nguồn có trường, coverage, tỷ lệ lỗi, độ phức tạp và quyết định tiếp tục/dừng.

### Giai đoạn B: thu thập mẫu nhỏ

Mục tiêu sơ bộ: 30-100 listing/mẫu bản ghi từ 1-2 nguồn đã được chọn. Đây là tập thử quy trình, không phải dataset nghiên cứu cuối.

Mẫu phải có độ đa dạng theo:

- Phân khúc giá.
- Laptop văn phòng/mỏng nhẹ.
- Laptop gaming/GPU rời.
- Máy cao cấp, bao gồm thiết bị dùng nền tảng CPU khác biệt nếu có.
- Các cấu hình RAM/SSD/màn hình khác nhau.

Sau khi thử, tính tỷ lệ có dữ liệu cho từng trường; chỉ mở rộng khi schema phù hợp.

### Giai đoạn C: thu thập chính thức

Quy mô mục tiêu tham khảo: 500-1.500 cấu hình laptop đã chuẩn hóa nếu khả thi. Không coi đây là ngưỡng khoa học bắt buộc. Nếu nguồn hợp lệ chỉ cho phép ít hơn, hãy giảm phạm vi, ghi rõ giới hạn và tối ưu chất lượng.

Không chỉ thu thập nhiều listing của cùng một dòng máy. Cần cân bằng các phân khúc và tránh để một hãng hoặc loại laptop áp đảo không chủ đích.

### Giai đoạn D: thu thập định kỳ giá (tùy chọn)

Nếu muốn phân tích biến động giá:

- Mỗi lần thu thập lưu timestamp mới, không ghi đè giá cũ.
- Lưu giá niêm yết và giá bán/giá khuyến mãi riêng.
- Lưu nhà bán lẻ và URL listing.
- Ghi trạng thái hết hàng nếu quan sát được; không tự suy ra giá bằng 0.
- Chu kỳ thu thập: **TBD**; lựa chọn có thể là hàng tuần, hai tuần hoặc tháng tùy khả năng và quy định nguồn.
- Không gọi đây là dự báo thị trường nếu chỉ có một vài snapshot.

---

## 4. Định nghĩa bản ghi và danh tính sản phẩm

Cần tách ít nhất ba khái niệm:

1. **Laptop model/family:** tên dòng máy tổng thể.
2. **Laptop configuration/SKU:** một cấu hình cụ thể của dòng máy, gồm CPU, GPU, RAM, SSD, màn hình và các thuộc tính khác có ảnh hưởng.
3. **Retail listing/price observation:** một trang bán hàng hoặc một lần quan sát giá của cấu hình đó.

Một cấu hình có thể có nhiều listing từ nhiều nhà bán lẻ và nhiều giá theo thời gian. Không được coi tất cả listing này là laptop khác nhau độc lập khi huấn luyện ML.

### 4.1. Khóa và ID đề xuất

- `product_family_id`: nhận diện dòng/model ở cấp tổng quát.
- `configuration_id`: nhận diện tổ hợp thông số cụ thể.
- `listing_id`: nhận diện listing tại nhà bán lẻ.
- `price_observation_id`: nhận diện một lần thu thập giá.
- `benchmark_observation_id`: nhận diện một kết quả benchmark.

Nếu chưa đủ thông tin để biết hai listing có cùng cấu hình hay không, giữ riêng và gắn `identity_status = uncertain`, không tự động gộp.

---

## 5. Schema đề xuất: dữ liệu sản phẩm

Các tên trường tiếng Anh được khuyến nghị để code dễ sử dụng; có thể đổi tên nếu nhất quán toàn dự án.

### 5.1. Nhận diện và nguồn

| Trường | Kiểu | Bắt buộc? | Mô tả |
|---|---|---|---|
| `configuration_id` | string | Có | ID nội bộ cho cấu hình chuẩn hóa |
| `product_family_id` | string | Nên có | ID dòng/model tổng quát |
| `brand` | string | Có | Thương hiệu |
| `model_name_raw` | string | Có | Tên sản phẩm gốc trên nguồn |
| `model_name_normalized` | string | Nên có | Tên chuẩn hóa |
| `sku_or_part_number` | string | Nếu có | Mã sản phẩm/part number |
| `retailer` | string | Với listing | Tên nhà bán lẻ |
| `source_url` | string | Có | URL nguồn |
| `source_type` | enum | Có | retailer, manufacturer, benchmark, review, public_dataset... |
| `collected_at` | datetime | Có | Ngày giờ thu thập |
| `identity_status` | enum | Có | verified, probable, uncertain |
| `source_notes` | string | Không | Ghi chú về nguồn/độ tin cậy |

### 5.2. CPU

| Trường | Kiểu | Mô tả |
|---|---|---|
| `cpu_name_raw` | string | Tên CPU nguyên gốc |
| `cpu_name_normalized` | string | Tên chuẩn hóa để đối chiếu |
| `cpu_vendor` | string | Intel, AMD, Apple, Qualcomm... nếu phù hợp |
| `cpu_family` | string | Dòng CPU được nhận diện; không thay thế tên đầy đủ |
| `cpu_generation_or_series` | string | Thế hệ/series nếu xác minh được |
| `cpu_suffix` | string | Hậu tố dòng CPU nếu có, ví dụ U/H/HX/HS; không suy ra điểm trực tiếp |
| `cpu_cores` | numeric | Số nhân nếu nguồn xác nhận |
| `cpu_threads` | numeric | Số luồng nếu nguồn xác nhận |
| `cpu_benchmark_name` | string | Tên bài benchmark chính được dùng |
| `cpu_benchmark_score` | numeric | Điểm benchmark đã xác minh |
| `cpu_benchmark_source` | string | Nguồn điểm |
| `cpu_benchmark_url` | string | URL trực tiếp đến kết quả hoặc trang tham chiếu |
| `cpu_benchmark_collected_at` | datetime | Ngày thu thập điểm |

**Quy tắc:** Core i5/i7, Ryzen 5/7 hoặc hậu tố U/H/HX không đủ để gán hiệu năng. Dùng tên CPU đầy đủ để tìm điểm benchmark, sau đó kiểm tra đúng chip laptop. Nếu không tìm được, giữ điểm thiếu và ghi trạng thái ghép.

### 5.3. GPU

| Trường | Kiểu | Mô tả |
|---|---|---|
| `gpu_name_raw` | string | Tên GPU nguyên gốc |
| `gpu_name_normalized` | string | Tên GPU đã chuẩn hóa |
| `gpu_type` | enum | integrated, discrete, unknown |
| `gpu_vram_gb` | numeric | VRAM riêng nếu có |
| `gpu_tgp_w` | numeric | Mức công suất/TGP nếu nguồn xác minh đúng cấu hình |
| `gpu_benchmark_name` | string | Bài benchmark GPU chính |
| `gpu_benchmark_score` | numeric | Điểm benchmark từ bài đã chọn |
| `gpu_benchmark_source` | string | Nguồn |
| `gpu_benchmark_url` | string | URL nguồn |
| `gpu_benchmark_collected_at` | datetime | Ngày thu thập |
| `gpu_match_status` | enum | exact, likely, unavailable, uncertain |

**Quy tắc đơn giản hóa:** chỉ chọn một điểm benchmark GPU chính cho phiên bản đầu. Không cần tạo một cột/tiêu chí DSS cho từng benchmark. Điểm bổ sung có thể lưu ở bảng phụ nếu thật sự hữu ích.

### 5.4. RAM và lưu trữ

| Trường | Kiểu | Mô tả |
|---|---|---|
| `ram_gb` | numeric | Tổng dung lượng RAM theo GB |
| `ram_type` | string | DDR4, DDR5, LPDDR5X... nếu xác minh được |
| `ram_speed_mts` | numeric | Tốc độ truyền nếu có và đơn vị thống nhất |
| `ram_upgradeable` | boolean/unknown | Có thể nâng cấp hay không nếu biết |
| `ram_slots` | numeric/unknown | Số khe nếu biết |
| `storage_total_gb` | numeric | Tổng dung lượng lưu trữ chuẩn hóa sang GB |
| `storage_primary_type` | enum/string | HDD, SATA_SSD, NVME_SSD, eMMC, other, unknown |
| `storage_secondary_gb` | numeric/nullable | Dung lượng ổ thứ hai nếu có |
| `storage_upgradeable` | boolean/unknown | Có thể nâng cấp hay không nếu biết |
| `storage_slots` | numeric/unknown | Số khe nếu có nguồn |
| `storage_speed_read_mbs` | numeric/nullable | Tốc độ đọc nếu có benchmark phù hợp |
| `storage_speed_write_mbs` | numeric/nullable | Tốc độ ghi nếu có benchmark phù hợp |

Nếu nguồn chỉ ghi `512GB SSD`, có thể chuẩn hóa thành `storage_total_gb=512`, `storage_primary_type=SSD_UNKNOWN_INTERFACE` hoặc một nhãn SSD tổng quát. Không tự gán NVMe nếu nguồn không xác nhận.

Nếu có cả SSD và HDD/ổ thứ hai, cần lưu riêng các thành phần. Không ép dung lượng ghép thành một con số mà mất thông tin loại ổ.

### 5.5. Màn hình

| Trường | Kiểu | Mô tả |
|---|---|---|
| `screen_size_inch` | numeric | Kích thước màn hình |
| `screen_resolution_raw` | string | Chuỗi độ phân giải gốc |
| `screen_width_px` | numeric | Số pixel ngang nếu suy ra chắc chắn từ chuỗi rõ ràng |
| `screen_height_px` | numeric | Số pixel dọc nếu suy ra chắc chắn |
| `screen_resolution_class` | enum/string | HD, FHD, WUXGA, 2.5K, 3K, 4K... theo quy tắc thống nhất |
| `panel_type` | enum/string | IPS, OLED, Mini-LED, TN, other, unknown |
| `refresh_rate_hz` | numeric | Tần số quét nếu có |
| `brightness_nits` | numeric/nullable | Độ sáng, phải ghi rõ là hãng công bố hay đo thực tế |
| `color_gamut_raw` | string/nullable | Độ phủ màu và không gian màu nếu có |
| `touchscreen` | boolean/unknown | Cảm ứng nếu có |
| `display_measurement_source` | string/nullable | Nguồn phép đo thực tế nếu có |

Không suy ra `panel_type=OLED` chỉ từ dòng sản phẩm. Không giả định mọi màn hình cùng độ phân giải có chất lượng như nhau. Nếu không có độ phủ màu/độ sáng, vẫn có thể dùng các trường cơ bản và ghi thiếu trường nâng cao.

### 5.6. Pin, thiết kế và các thuộc tính khác

| Trường | Kiểu | Mô tả |
|---|---|---|
| `battery_capacity_wh` | numeric/nullable | Dung lượng pin Wh |
| `battery_runtime_hours` | numeric/nullable | Thời lượng từ một bài test có phương pháp rõ |
| `battery_test_type` | string/nullable | Web browsing, video playback, workload... |
| `battery_test_conditions` | string/nullable | Mô tả ngắn điều kiện thử nếu có |
| `battery_source_url` | string/nullable | Nguồn của phép đo |
| `weight_kg` | numeric | Trọng lượng máy, xác định có tính adapter hay không nếu nguồn ghi rõ |
| `thickness_mm` | numeric/nullable | Độ dày nếu cần |
| `os_name` | string/nullable | Hệ điều hành |
| `usb_a_count` | integer/nullable | Số cổng USB-A nếu cần |
| `usb_c_count` | integer/nullable | Số cổng USB-C nếu cần |
| `thunderbolt_or_usb4` | boolean/unknown | Cổng hỗ trợ nếu xác minh được |
| `hdmi_present` | boolean/unknown | Có HDMI hay không |
| `lan_present` | boolean/unknown | Có LAN hay không |
| `warranty_months` | numeric/nullable | Thời hạn bảo hành, cần phân biệt hãng/cửa hàng |
| `launch_date_or_year` | date/year/nullable | Ngày/năm ra mắt nếu có nguồn xác minh |
| `cooling_review_notes` | string/nullable | Ghi chú về tản nhiệt nếu có review |
| `noise_db` | numeric/nullable | Độ ồn nếu đo thực tế và điều kiện rõ |
| `surface_temperature_c` | numeric/nullable | Nhiệt độ bề mặt nếu review có phép đo rõ |

Không bắt buộc phải có toàn bộ trường này trong bản đầu. Chọn trường theo coverage thực tế; các trường pin và thông số màn hình cần tách nguồn công bố với kết quả thử nghiệm.

---

## 6. Schema giá và lịch sử giá

Không để giá là một cột duy nhất mà không có ngữ cảnh.

| Trường | Kiểu | Mô tả |
|---|---|---|
| `price_observation_id` | string | ID bản ghi giá |
| `configuration_id` | string | Khóa cấu hình laptop |
| `retailer` | string | Nhà bán lẻ |
| `source_url` | string | URL listing |
| `observed_at` | datetime | Thời điểm thu thập |
| `currency` | string | VND, EUR... |
| `listed_price` | numeric/nullable | Giá niêm yết trước giảm nếu thấy |
| `sale_price` | numeric/nullable | Giá bán hiện tại/sau giảm theo định nghĩa nhất quán |
| `special_price` | numeric/nullable | Giá sinh viên/thành viên/điều kiện đặc biệt nếu có |
| `stock_status` | enum/unknown | in_stock, out_of_stock, unknown |
| `promotion_notes` | string/nullable | Điều kiện quà tặng/voucher/trả góp nếu cần |
| `price_parse_status` | enum | parsed, manual_verified, uncertain, failed |

### 6.1. Chọn biến mục tiêu ML

**Chưa chốt, người dùng phải chọn sau proof of concept.** Lựa chọn:

- A. `sale_price` tại thời điểm thu thập.
- B. Giá đại diện của một cấu hình ở cùng thời điểm, ví dụ trung vị giá bán đã quan sát từ các listing hợp lệ.
- C. Giá niêm yết nếu nghiên cứu giá niêm yết, không phải giá trả thực tế.

Đề xuất có điều kiện: lưu cả `listed_price` và `sale_price` khi có thể; chọn một định nghĩa làm target duy nhất và ghi rõ trong báo cáo. Không trộn giá đặc biệt chỉ áp dụng trong điều kiện riêng với giá bán phổ thông nếu chưa có quy tắc.

### 6.2. Giá lịch sử

Nếu cào/thu thập định kỳ, thêm một dòng cho mỗi lần quan sát. Không ghi đè giá cũ. Chỉ kết luận biến động theo thời gian khi có nhiều thời điểm đủ tin cậy.

Không sử dụng trường giá tương lai làm đầu vào để dự đoán giá tại thời điểm trước đó. Nếu thử dự báo chuỗi thời gian, phải chia train/test theo thời gian.

---

## 7. Chuẩn hóa các trường quan trọng

### 7.1. RAM

Ví dụ dữ liệu gốc có thể là `16GB`, `16 GB RAM`, `32GB DDR5`, `16GB LPDDR5X`.

- Trích xuất dung lượng thành `ram_gb`.
- Loại RAM lưu riêng thành `ram_type`.
- Không suy diễn loại RAM nếu không có căn cứ.
- Kiểm tra giá trị bất thường và lưu chuỗi gốc để rà soát.

### 7.2. Storage

Có thể gặp `512GB SSD`, `1TB SSD`, `512GB SSD + 1TB HDD`, `256GB NVMe` hoặc cách ghi khác.

- Chuẩn hóa dung lượng về GB theo một quy tắc thống nhất.
- Lưu loại ổ riêng.
- Tách ổ chính/ổ phụ nếu thông tin đủ.
- Không xem 512GB SSD và 512GB HDD là tương đương.
- Không tự gán NVMe nếu chỉ có chữ SSD.
- Nếu không biết giao thức SSD, dùng nhãn chưa xác định thay vì đoán.

### 7.3. CPU

- Giữ `cpu_name_raw`.
- Tạo `cpu_name_normalized` để khớp đúng tên ở nguồn benchmark.
- Hậu tố U/H/HX/HS là thông tin mô tả; không thay thế benchmark.
- Ghi benchmark score và nguồn vào trường riêng.
- Kiểm tra nhầm lẫn giữa CPU laptop và CPU desktop cùng họ tên gần nhau.

### 7.4. GPU

- Phân biệt GPU tích hợp và GPU rời khi có căn cứ.
- Lưu VRAM/TGP chỉ khi xác minh đúng biến thể.
- Điểm benchmark GPU phải từ một bài kiểm tra chính đã chọn và có tên nguồn.
- Không cộng điểm nhiều benchmark khác thang đo.
- Không lấy điểm của GPU desktop để đại diện GPU laptop khi không phải cùng cấu hình/định nghĩa.

### 7.5. Màn hình

- Chuẩn hóa kích thước về inch.
- Lưu chuỗi độ phân giải gốc và trường số pixel khi trích xuất được chính xác.
- Chuẩn hóa panel thành các nhãn thống nhất như IPS, OLED, Mini-LED, TN, unknown.
- Lưu tần số quét Hz.
- Ghi rõ độ sáng/màu là thông số công bố hay phép đo thực tế.
- Tính `display_score` chỉ khi đã có quy tắc được phê duyệt; không tạo điểm cảm tính không giải thích được.

### 7.6. Battery

- Dung lượng Wh và thời lượng giờ là hai trường khác nhau.
- Ghi phép thử và điều kiện nếu dùng thời lượng thực tế.
- Không suy ra thời lượng pin chính xác chỉ từ dòng CPU/GPU hoặc dung lượng pin.
- Không gán mặc định “gaming 2 giờ”, “văn phòng 8 giờ”, “Mac 15 giờ” cho mọi máy.
- Nếu không có số liệu đáng tin, để thiếu và ghi trạng thái.

### 7.7. Giá

- Chuẩn hóa tiền tệ về một đơn vị khi so sánh trong thị trường Việt Nam, thường là VND.
- Giữ giá gốc và trường giá chuẩn hóa nếu cần chuyển tiền tệ.
- Ghi thời điểm thu thập và loại giá.
- Xử lý dấu phân cách nghìn, chữ `đ`, voucher và giá khuyến mãi thận trọng.
- Không tự tính một giá “sau voucher” nếu điều kiện áp dụng không rõ.

### 7.8. Trọng lượng

- Chuẩn hóa về kg.
- Nếu nguồn ghi trọng lượng máy và adapter riêng, lưu riêng nếu có.
- Không trộn trọng lượng bao gồm adapter với trọng lượng máy mà không ghi chú.

---

## 8. Đối chiếu benchmark CPU/GPU

### 8.1. Quy trình ghép

1. Đọc tên CPU/GPU từ nguồn bán lẻ và giữ chuỗi gốc.
2. Chuẩn hóa khoảng trắng, dấu câu và tên thương mại mà không xóa thông tin quan trọng.
3. Tìm đúng mã linh kiện ở nguồn benchmark được chọn.
4. Xác minh đó là biến thể laptop khi khác với desktop.
5. Ghi tên benchmark, score, URL và ngày thu thập.
6. Gắn `match_status`: `exact`, `likely`, `uncertain`, `unavailable`.
7. Tạo danh sách bản ghi `likely/uncertain` để kiểm tra thủ công.
8. Không gán điểm khi không tìm được đối chiếu chắc chắn.

### 8.2. Quy tắc điểm benchmark (Đã chốt theo D05 & D06)

- **Benchmark CPU chính:** Geekbench 6 Multi-Core (lưu kèm Geekbench 6 Single-Core). Geekbench 6 là bài test duy nhất đo lường công bằng kiến trúc CPU chéo nền tảng giữa x86, ARM Snapdragon X và Apple Silicon. Không sử dụng PassMark CPU Mark vì PassMark không hỗ trợ native công bằng trên macOS/Apple Silicon.
- **Benchmark GPU chính:** 3DMark Time Spy Graphics (DirectX 12). Chỉ áp dụng cho laptop Windows có GPU rời (dGPU), ghi nhận theo mức TGP công bố. Loại bỏ PassMark G3D Mark vì không phân biệt được mức TGP thực tế của GPU laptop.
- Nếu dùng cả điểm đơn nhân và đa nhân từ Geekbench 6, giữ chúng riêng: Profile Sinh viên/Văn phòng dùng Single-Core; Profile Kỹ thuật/Gaming dùng Multi-Core (D20). Tuyệt đối không đưa cả hai vào cùng ma trận để tránh đếm trùng CPU (D08).
- Không cộng gộp điểm CPU và GPU thành một “điểm hiệu năng tổng” cảm tính nếu chưa kiểm chứng phép chuẩn hóa.
- Mọi phép biến đổi trong dataset phải công bố rõ ràng trong báo cáo. Không gán trọng số cảm tính từ trước.

### 8.3. Nếu không tìm được điểm benchmark

- Giữ `benchmark_score = null`.
- Giữ thông số nhận dạng linh kiện nếu nguồn sản phẩm có.
- Tùy chính sách, có thể loại trường benchmark khỏi lần phân tích, loại sản phẩm khỏi một phép so sánh đòi hỏi benchmark hoặc sử dụng một bộ tiêu chí thay thế cho toàn bộ phương án.
- Không trộn điểm đã benchmark và ước tính cảm tính trong cùng một cột như thể chúng cùng chất lượng.

---

## 9. Tạo điểm tổng hợp màn hình và tiêu chí nâng cao

Một số trường như độ phân giải, panel type, tần số quét, độ sáng và màu không nhất thiết phải thành năm tiêu chí DSS riêng.

Có thể tạo `display_score` khi đã định nghĩa quy tắc rõ ràng:

- Cách A: dùng một benchmark/chỉ số đánh giá màn hình từ bài review có phương pháp tương thích, nếu đủ coverage.
- Cách B: dùng một hàm tổng hợp minh bạch từ thông số sẵn có, với trọng số/ngưỡng do người dùng hoặc nhóm phê duyệt.
- Cách C: không tạo điểm tổng hợp, giữ các thuộc tính riêng để người dùng lọc, rồi chọn các tiêu chí DSS cuối cùng sau EDA.

**Chưa chốt:** phương pháp sẽ chọn sau khi khảo sát độ đầy đủ. Không tạo `display_score` bằng cách cộng điểm tùy tiện cho OLED, 2.5K hoặc Hz.

Tương tự, tính di động có thể là nhóm diễn giải hoặc preset nhu cầu, nhưng không nên đưa điểm tổng hợp của nó vào TOPSIS cùng lúc với pin và trọng lượng nếu điểm đó chỉ tính lại hai yếu tố này.

---

## 10. Cào/thu thập dữ liệu: yêu cầu kỹ thuật và giới hạn

### 10.1. Trước khi viết scraper

Với từng nguồn, Agent phải ghi nhận:

- URL danh mục mẫu và URL trang chi tiết mẫu.
- Quy tắc sử dụng/robots/giới hạn truy cập đã kiểm tra.
- Phương pháp thu thập được phép: thủ công, export/API chính thức hoặc tự động hóa có kiểm soát.
- Trường lấy được ở danh mục và trường phải lấy từ trang chi tiết.
- Tần suất cập nhật cần thiết.
- Tỷ lệ lỗi sau thử nghiệm.

Nếu không thể xác minh việc cào tự động có được phép hay không, không triển khai scraper quy mô lớn. Có thể dùng mẫu nhập thủ công, dữ liệu công khai có điều khoản phù hợp hoặc nguồn khác.

### 10.2. Cách xây dựng scraper nếu được phép

- Tách adapter riêng cho từng website, không viết một scraper chung dựa trên giả định HTML giống nhau.
- Lấy URL từ danh sách trang danh mục và phân trang hợp lệ.
- Truy cập chi tiết sản phẩm với tốc độ thấp, có delay, retry có giới hạn và backoff.
- Đặt timeout và ghi log lỗi.
- Không bypass CAPTCHA, không né đăng nhập hoặc cơ chế chống bot.
- Không tải ảnh nếu đề tài không cần xử lý ảnh.
- Lưu raw HTML/JSON chỉ khi điều khoản cho phép và có nhu cầu kiểm chứng; nếu không thì lưu dữ liệu trích xuất cùng URL/timestamp.
- Nhận biết thay đổi cấu trúc. Nếu tỷ lệ parse fail tăng mạnh, dừng và báo lỗi thay vì ghi CSV sai âm thầm.
- Có thể lưu cache để không liên tục tải lại cùng trang.

### 10.3. Tránh tạo dữ liệu trùng

- Tạo fingerprint từ nguồn, URL, mã SKU và trường cấu hình.
- Một `configuration_id` có thể liên kết với nhiều `listing_id`.
- Một `listing_id` có nhiều `price_observation_id` qua thời gian.
- Không gộp hai SKU nếu CPU/RAM/SSD/GPU/màn hình khác nhau.
- Không coi cùng cấu hình tại nhiều cửa hàng là các cấu hình laptop khác nhau khi phân tích số lượng thiết bị.

---

## 11. Chất lượng dữ liệu và báo cáo kiểm tra

Sau mỗi đợt thu thập, tạo báo cáo tự động gồm:

1. Tổng listing thô.
2. Tổng cấu hình đã nhận diện.
3. Số và tỷ lệ trùng lặp.
4. Số bản ghi bị loại cùng lý do.
5. Tỷ lệ thiếu từng trường.
6. Tỷ lệ parse giá thành công.
7. Tỷ lệ nhận diện CPU/GPU thành công.
8. Tỷ lệ ghép benchmark exact/likely/uncertain/unavailable.
9. Phân phối giá và số lượng theo thương hiệu/loại máy/phân khúc.
10. Những giá trị bất thường cần rà soát.
11. Số nguồn và thời điểm dữ liệu.

Không nên chỉ báo cáo tổng số dòng. Chất lượng và coverage phải được xem xét cùng số lượng.

### 11.1. Kiểm tra ngoại lệ

Ví dụ các kiểm tra cần có:

- Giá âm hoặc bằng 0.
- RAM/SSD/trọng lượng không hợp lý.
- Đơn vị inch/kg/GB parse sai.
- CPU hoặc GPU trống nhưng trường benchmark lại có điểm.
- Điểm benchmark bị ghép với tên linh kiện khác.
- Giá sale lớn hơn giá niêm yết (không tự sửa nếu chưa hiểu trường hợp).
- Các bản ghi cùng cấu hình nhưng có giá chênh quá lớn trong cùng thời điểm.

Ngoại lệ không phải lúc nào cũng là lỗi. Gắn cờ để kiểm tra, không tự động xóa tất cả.

---

## 12. Dữ liệu phục vụ ML

### 12.1. Target

`target_price` là giá được chọn theo quyết định D04 trong `Chuongtrinh.md`. Phải định nghĩa rõ một đơn vị tiền, một thời điểm/định nghĩa và chính sách với nhiều nhà bán lẻ.

### 12.2. Đặc trưng đầu vào có thể sử dụng

- CPU benchmark hoặc thông tin CPU đã chuẩn hóa.
- GPU benchmark, loại GPU và VRAM nếu có.
- RAM dung lượng/loại.
- Lưu trữ dung lượng/công nghệ.
- Màn hình.
- Trọng lượng.
- Pin nếu đủ coverage.
- Thương hiệu, dòng sản phẩm, loại máy, OS.
- Thuộc tính khác đã được kiểm tra và có ý nghĩa.

### 12.3. Trường không được dùng gây rò rỉ

- `target_price` và biến được tính trực tiếp từ target.
- `value_for_money` khi nó được tính từ target price.
- Trường có chứa giá bán dưới một tên khác.
- Mã sản phẩm hoặc URL chỉ đóng vai trò nhận diện mẫu giá và làm mô hình ghi nhớ, trừ khi có lý do nghiên cứu đặc biệt.

Nếu dữ liệu có nhiều snapshot giá, cần quyết định là dự đoán giá cùng thời điểm hay dự đoán giá tương lai. Hai bài toán khác nhau và cách chia tập cũng khác nhau.

### 12.4. Chia tập dữ liệu

- Tách train/test trước khi fit preprocessing.
- Dùng pipeline để fit imputation/encoding/scale chỉ trên train.
- Nếu nhiều bản ghi cùng cấu hình, cân nhắc GroupShuffleSplit hoặc cách chia nhóm tương đương.
- Nếu dự báo tương lai, dùng time-based split.
- Báo cáo quy mô và cách chia thực tế; không chỉ nêu mỗi tỷ lệ 80/20 mà bỏ qua vấn đề trùng cấu hình.

---

## 13. Dữ liệu phục vụ DSS và bảng tiêu chí

Những tiêu chí dưới đây là ứng viên. Trường nào dùng trong TOPSIS chính thức phải được đánh dấu khi nhóm chốt tiêu chí.

| Tiêu chí DSS ứng viên | Trường cần dùng | Hướng dự kiến | Điều kiện/cảnh báo |
|---|---|---|---|
| Giá bán | `sale_price` hoặc target price đã định nghĩa | Cost | Đồng thời có thể dùng làm bộ lọc ngân sách |
| Hiệu năng CPU | `cpu_benchmark_score` | Benefit | Chỉ khi cùng benchmark/đúng định nghĩa |
| Hiệu năng GPU | `gpu_benchmark_score` | Benefit | Một benchmark chính, đúng GPU laptop |
| Dung lượng RAM | `ram_gb` | Benefit có ngưỡng | Không tăng tuyến tính vô hạn |
| Nâng cấp RAM | `ram_upgradeable`, `ram_slots` | Benefit | Thiếu dữ liệu phải có chính sách |
| Dung lượng storage | `storage_total_gb` | Benefit có ngưỡng | Lưu thêm ổ phụ nếu có |
| Công nghệ storage | `storage_primary_type` | Benefit | Cần mã hóa thứ tự hoặc mức phù hợp có giải thích |
| Chất lượng màn hình | Các trường màn hình hoặc `display_score` đã định nghĩa | Benefit | Không gán điểm cảm tính |
| Kích thước màn hình | `screen_size_inch` | Fit theo nhu cầu | Lớn hơn không luôn tốt hơn |
| Tần số quét | `refresh_rate_hz` | Benefit có điều kiện | Tùy nhu cầu |
| Thời lượng pin thực tế | `battery_runtime_hours` | Benefit | Cần phương pháp thử tương thích |
| Trọng lượng | `weight_kg` | Cost | Có thể định nghĩa vùng phù hợp |
| Cổng kết nối | Các trường cổng | Fit/benefit | Chỉ dùng nếu dữ liệu nhất quán |
| Tương thích OS/phần mềm | `os_name` và yêu cầu người dùng | Fit/constraint | Tùy ứng dụng mục tiêu |
| Nâng cấp/sửa chữa | Trường nâng cấp/review | Benefit | Có thể là phần mở rộng |
| Bảo hành | `warranty_months`/điều kiện bảo hành | Benefit | Phân biệt hãng/cửa hàng |
| Value for Money ML | Dự đoán giá + giá quan sát | Benefit | Chỉ bật sau đánh giá model; nguy cơ đếm lại giá |

Bộ chính thức cần khoảng 15 tiêu chí nếu dữ liệu cho phép, nhưng phải xem xét trùng lặp, coverage và chi phí AHP. Các thuộc tính ít có dữ liệu có thể hiển thị như mô tả hoặc dùng làm bộ lọc thay vì tạo trọng số TOPSIS.

---

## 14. Quy tắc tạo Value for Money từ ML

### 14.1. Dữ liệu cần có

- Giá mục tiêu/giá quan sát được đã thống nhất.
- Giá dự đoán từ mô hình ML được huấn luyện hợp lệ.
- ID cấu hình và ngày/phiên bản mô hình.

### 14.2. Công thức thử nghiệm

`value_gap = (predicted_price - observed_price) / predicted_price`

Chỉ số này dương khi giá quan sát thấp hơn giá mô hình dự đoán. Trước khi đưa vào TOPSIS, cần quyết định cách chuyển thành điểm, ví dụ chuẩn hóa, giới hạn ngoại lệ hoặc ánh xạ sang thang điểm dễ giải thích. Công thức cuối cùng là **TBD**.

### 14.3. Cảnh báo

- Đây là tín hiệu giá trị tương đối theo mô hình, không phải chất lượng tuyệt đối.
- Sai số dự đoán lớn có thể làm value_gap sai.
- Vì giá thực tế còn là tiêu chí cost, bổ sung value_gap có thể đếm lại yếu tố giá.
- Cần so sánh ranking có/không value_gap và kiểm tra độ nhạy trọng số.
- Nếu kết quả không ổn định hoặc mô hình yếu, không dùng value_gap trong DSS chính.

---

## 15. Quy tắc lưu trữ và quản lý phiên bản

Cấu trúc thư mục gợi ý:

```text
data/
  raw/
    retailer_a/
    retailer_b/
    benchmarks/
    reviews/
  interim/
  processed/
  external_reference/
  reports/
```

- `raw/`: dữ liệu nguyên gốc hoặc trích xuất không biến đổi, chỉ lưu theo quyền sử dụng.
- `interim/`: dữ liệu đã parse nhưng chưa qua mọi quy tắc làm sạch.
- `processed/`: dataset chuẩn hóa dùng cho EDA/ML/DSS.
- `external_reference/`: bảng đối chiếu linh kiện/benchmark có nguồn.
- `reports/`: báo cáo chất lượng và thống kê.

Không đưa dữ liệu cá nhân hoặc thông tin bí mật vào dataset. Không lưu API key, cookie phiên đăng nhập hay credential trong repo.

Mỗi bản phát hành dataset cần lưu:

- `dataset_version`.
- Ngày tạo.
- Danh sách nguồn.
- Số record.
- Quy tắc làm sạch.
- Hash/tên file đầu vào nếu cần truy vết.
- Các thay đổi so với phiên bản trước.

---

## 16. Quyết định dữ liệu còn mở

Các mục này phải được giữ ở trạng thái `OPEN` cho đến khi người dùng chọn hoặc đã có kết quả khảo sát thuyết phục.

| Mã | Câu hỏi | Các lựa chọn cần cân nhắc | Cách quyết định |
|---|---|---|---|
| DATA-01 | Nguồn bán lẻ chính là gì? | Xgear; FPT Shop; Thế Giới Di Động; CellphoneS; LaptopAZ; kết hợp 2-3 nguồn | Chạy proof of concept, kiểm tra quyền truy cập, coverage và effort |
| DATA-02 | Có dùng Kaggle dataset không? | Không; dùng để phát triển pipeline; dùng làm benchmark riêng; merge có kiểm soát | Kiểm tra giấy phép, tiền tệ, thời điểm và định nghĩa trường |
| DATA-03 | Thu thập thủ công hay tự động? | Thủ công; API/export hợp lệ; scraper có kiểm soát; kết hợp | Dựa trên điều khoản sử dụng và khả năng kỹ thuật |
| DATA-04 | Quy mô cuối? | 300-500; 500-1.500; khác | Dựa vào độ bao phủ và khả năng thu thập hợp lệ |
| DATA-05 | Mục tiêu giá ML? | Sale price; listed price; giá đại diện nhiều retailer | Chọn một định nghĩa và ghi rõ trong báo cáo |
| DATA-06 | Benchmark CPU chính? | Đã chốt: Geekbench 6 Multi-Core (kèm Single-Core) | D05: So sánh chéo nền tảng x86, ARM Snapdragon và Apple Silicon công bằng |
| DATA-07 | Benchmark GPU chính? | Đã chốt: 3DMark Time Spy Graphics | D06: Chuẩn đồ họa DirectX 12 cho laptop Windows dGPU theo TGP |
| DATA-08 | Pin có là tiêu chí chính? | Có với trường thực tế; chỉ dùng pin Wh; không đưa vào TOPSIS bản đầu | Kiểm tra coverage và khả năng so sánh phép thử |
| DATA-09 | Thông số màn hình sâu đến đâu? | Kích thước/độ phân giải/panel; thêm Hz; thêm sáng/màu/đo thực tế | Tỷ lệ trường có dữ liệu và mục tiêu người dùng |
| DATA-10 | Có thu thập nhiệt độ/độ ồn? | Không; chỉ review mẫu; tiêu chí mở rộng | Chỉ chọn nếu có phương pháp đo tương thích |
| DATA-11 | Chu kỳ lịch sử giá? | Không; tuần; hai tuần; tháng | Dựa vào effort/điều khoản/giá trị nghiên cứu |
| DATA-12 | Chính sách thiếu dữ liệu DSS? | Bỏ tiêu chí; loại máy; tiêu chí con theo dữ liệu | Chốt trước khi xếp hạng |
| DATA-13 | Chuẩn hóa display score? | Không tổng hợp; rule minh bạch; chỉ số từ review có coverage | Không tạo trọng số cảm tính |
| DATA-14 | Chọn các trường nâng cấp/bảo hành/cổng? | Tiêu chí chính; bộ lọc; thông tin hiển thị | Chỉ thành tiêu chí nếu ý nghĩa và độ phủ đủ |
| DATA-15 | Gộp listing nhiều nhà bán lẻ thế nào? | Lưu từng listing; lấy median/giá thấp nhất/giá đại diện | Lưu toàn bộ quan sát rồi chọn quy tắc cho từng phân tích |

---

## 17. Đầu ra AI Agent phải tạo sau giai đoạn khảo sát dữ liệu

Trước khi cào quy mô lớn, Agent cần tạo:

1. `source_audit.md`: nguồn, URL, điều khoản/truy cập đã kiểm tra, trường có thể lấy, hạn chế và quyết định tiếp tục/dừng.
2. `field_coverage.csv`: một dòng cho mỗi trường; tỷ lệ có dữ liệu trên mẫu thử.
3. `raw_sample.csv` hoặc định dạng phù hợp, chỉ sử dụng dữ liệu thu thập hợp lệ.
4. `parsed_sample.csv`: dữ liệu đã parse nhưng chưa gộp/khử trùng triệt để.
5. `data_quality_report.md`: lỗi parse, trường thiếu, nghi trùng và vấn đề cần người dùng quyết định.
6. `benchmark_match_sample.csv`: CPU/GPU gốc, tên chuẩn hóa, kết quả đối chiếu, nguồn, score và trạng thái match.
7. `DECISIONS.md`: cập nhật các mục DATA-01 đến DATA-15 thành OPEN/DECIDED và ghi lý do.

Không chuyển sang cào hàng loạt khi mẫu thử cho thấy trường cốt lõi bị thiếu quá nhiều, nhận diện cấu hình không đáng tin hoặc cách truy cập chưa được xác minh.

---

## 18. Liên kết tham khảo chính

### Nguồn bán lẻ ứng viên

- Xgear: https://xgear.net/collections/laptop
- FPT Shop: https://fptshop.com.vn/may-tinh-xach-tay
- Thế Giới Di Động: https://www.thegioididong.com/laptop
- CellphoneS: https://cellphones.com.vn/laptop.html
- LaptopAZ: https://laptopaz.vn/

### Benchmark và đánh giá

- PassMark CPU: https://www.cpubenchmark.net/ (Tham khảo ban đầu; không dùng trong engine V1, đã chuyển sang Geekbench 6 theo D05)
- PassMark GPU: https://www.videocardbenchmark.net/ (Tham khảo ban đầu; không dùng trong engine V1, đã chuyển sang 3DMark Time Spy theo D06)
- Geekbench Browser (Benchmark CPU chính thức): https://browser.geekbench.com/
- 3DMark Time Spy (Benchmark GPU chính thức): https://www.3dmark.com/
- Notebookcheck: https://www.notebookcheck.net/
- TechPowerUp GPU Database: https://www.techpowerup.com/gpu-specs/

### Dataset mở tham khảo

- Kaggle Laptop Price: https://www.kaggle.com/datasets/muhammetvarl/laptop-price

**Các URL chỉ là điểm bắt đầu.** Khi triển khai, cần kiểm tra đường dẫn hoạt động, nội dung hiện tại, điều khoản, độ phủ và sự phù hợp với phạm vi dự án.
