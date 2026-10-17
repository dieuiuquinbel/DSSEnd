# DECISIONS.md

# Nhật ký quyết định dự án DSS lựa chọn laptop

> Trạng thái tại thời điểm tạo: các quyết định dưới đây được chốt từ định hướng hiện tại. Những mục phụ thuộc vào kết quả khảo sát nguồn vẫn phải được xác nhận bằng dữ liệu thực tế trước khi thu thập quy mô lớn.

---

## 1. Quyết định đã chốt

| Mã | Quyết định | Trạng thái | Lý do / quy tắc áp dụng |
|---|---|---|---|
| D01 / DATA-01 | Pilot trên FPT Shop và CellPhones; sau pilot chọn tối đa một nguồn bán lẻ chính cho dataset V1. | Chờ khảo sát nguồn | Hai nguồn có độ phủ phân khúc sinh viên. Chỉ thu thập tự động khi điều khoản sử dụng, `robots.txt` và phương thức truy cập cho phép; nếu không, dùng nhập thủ công hoặc nguồn hợp lệ khác. |
| D02 / DATA-02 | Kaggle Laptop Price chỉ dùng thử pipeline hoặc làm baseline riêng. | Đã chốt | Không trộn trực tiếp với dữ liệu giá Việt Nam vì khác thị trường, tiền tệ, thời điểm và định nghĩa giá. |
| D03 / DATA-04 | Mục tiêu V1 là 300–500 cấu hình laptop đã chuẩn hóa. | Đã chốt có điều kiện | Có thể mở rộng sau khi pilot chứng minh được chất lượng dữ liệu, coverage và tính hợp lệ khi thu thập. Không chạy theo số dòng bằng cách nhân listing hoặc snapshot giá. |
| D04 / DATA-05 | Target ML là `sale_price` công khai, không phụ thuộc voucher, thành viên hay trả góp. | Đã chốt | Lưu đồng thời `listed_price`, `sale_price` và giá đặc biệt khi có; không trộn các loại giá. Mỗi target phải có retailer, URL và thời điểm quan sát. |
| D05 / DATA-06 | Benchmark CPU chính là Geekbench 6 Multi-Core (lưu kèm Single-Core). | Đã chốt | Dùng Geekbench 6 để so sánh năng lực CPU đa nền tảng (x86, ARM Snapdragon, Apple Silicon). Toàn bộ CPU dùng đúng phiên bản Geekbench 6 (không trộn GB5/GB7). Lấy median/trung bình từ Geekbench Browser, lưu link nguồn, số mẫu, match_level. Phần cứng chưa bán thương mại để trống điểm, tuyệt đối không bịa số. |
| D06 / DATA-07 | Benchmark GPU gaming chính là 3DMark Time Spy Graphics. | Đã chốt | Chỉ áp dụng để so sánh các laptop Windows có GPU rời (dGPU) với nhau; tuyệt đối không đưa GPU onboard, Apple GPU hay Adreno vào chung cột Time Spy. Khớp đúng mẫu laptop/TGP nếu có (exact_laptop_or_tgp), hoặc mức TGP gần nhất (approximate). |
| D07 / DATA-08 | Không dùng thời lượng pin thực tế làm tiêu chí TOPSIS lõi ở V1. | Đã chốt | Vẫn lưu/thể hiện số liệu pin đáng tin nếu có, nhưng không xếp hạng bằng dữ liệu review thiếu hoặc không tương thích phương pháp thử. |
| D08 | Không ép đủ 15–18 tiêu chí; V1 dùng 8–12 tiêu chí có coverage tốt. | Đã chốt | Chất lượng, ý nghĩa và tính so sánh quan trọng hơn số lượng tiêu chí. Chỉ thêm tiêu chí sau EDA và kiểm tra trùng lặp. |
| D09 | Dùng AHP phân cấp với preset theo hồ sơ nhu cầu; cho phép điều chỉnh trọng số nhóm. | Đã chốt | Tránh ma trận so sánh cặp quá lớn. Lưu trọng số và Consistency Ratio; nếu CR không đạt hướng dẫn dưới 0,10 thì yêu cầu đánh giá lại. |
| D10 | Không đưa C18 `Value for Money` do ML vào DSS V1. | Đã chốt | Chỉ chạy như thí nghiệm đối chiếu có/không C18 sau khi mô hình ML đạt chất lượng phù hợp; không để giá bị đếm đôi. |
| D11 | Giao diện: Streamlit (Prototype) → FastAPI + React 18 (Production). | Đã chốt | Phù hợp Python và prototype ban đầu; nâng cấp kiến trúc decoupled FastAPI + React 18 SPA cho sản phẩm chính thức nhằm đáp ứng tính toán thời gian thực và so sánh đa phương án. |
| D12 | SQLite là nơi lưu dữ liệu nghiệp vụ; CSV/Parquet dùng để xuất dữ liệu và phân tích. | Đã chốt | Quan hệ giữa cấu hình, listing và quan sát giá theo thời gian phù hợp SQLite hơn một CSV đơn lẻ. |
| D13 / DATA-11 | Lưu lịch sử giá từ ngày thu thập đầu tiên, với chu kỳ hai tuần. | Đã chốt có điều kiện | Chỉ duy trì nếu nguồn và nguồn lực cho phép. Cần tối thiểu 8–12 tuần dữ liệu trước khi kết luận về biến động giá. |
| D14 / DATA-12 | Tiêu chí chỉ được đưa vào TOPSIS khi coverage từ 80% trở lên; máy thiếu trường lõi bị loại khỏi lần xếp hạng tương ứng. | Đã chốt | Không thay dữ liệu thiếu bằng 0. Trường lõi phụ thuộc hồ sơ người dùng nhưng luôn gồm giá, RAM, lưu trữ và trọng lượng; CPU/GPU là lõi khi hồ sơ cần hiệu năng tương ứng. |
| D15 | Lưu NPU/AI capability nếu xuất hiện, nhưng chỉ để mô tả hoặc lọc ở V1. | Đã chốt | Độ phủ và cách đánh giá NPU chưa đồng nhất; không dùng làm tiêu chí có trọng số. |
| DATA-03 | Pilot ưu tiên nhập thủ công hoặc API/export chính thức; scraper chỉ được dùng khi được phép. | Đã chốt | Không vượt CAPTCHA, đăng nhập, anti-bot hoặc giới hạn truy cập. |
| DATA-09 / DATA-13 | Không tạo `display_score` ở V1. | Đã chốt | Chỉ giữ các thuộc tính màn hình riêng như kích thước, độ phân giải, panel và Hz; không gán điểm cảm tính cho OLED/độ phân giải/tần số quét. |
| DATA-10 | Không thu thập nhiệt độ/độ ồn trong V1. | Đã chốt | Dữ liệu review không đồng nhất. Có thể thêm dưới dạng ghi chú ở phiên bản mở rộng, không dùng để xếp hạng V1. |
| DATA-14 | Cổng kết nối và bảo hành là thông tin hiển thị/bộ lọc trước; chưa là tiêu chí TOPSIS lõi. | Đã chốt | Chỉ đưa vào xếp hạng nếu EDA cho thấy coverage và định nghĩa đủ nhất quán. |
| DATA-15 | Lưu từng listing riêng; khi cần giá đại diện của cùng cấu hình trong cùng đợt quan sát, dùng median `sale_price` công khai. | Đã chốt | Không dùng giá thấp nhất vì dễ bị khuyến mãi bất thường. Trong giao diện, nhóm theo cấu hình và hiển thị các báo giá theo nhà bán lẻ. |

---

## 2. Tiêu chí DSS V1

### 2.1. Tiêu chí ứng viên lõi

Các tiêu chí sau chỉ được dùng khi đạt ngưỡng coverage đã chốt và dữ liệu có thể so sánh:

| Mã | Tiêu chí | Hướng | Cách dùng V1 |
|---|---|---|---|
| C01 | Giá bán hiện tại | Cost | Đồng thời là ràng buộc ngân sách. |
| C02 | Hiệu năng CPU | Benefit | Geekbench 6 Multi-Core đã ghép đúng chip; lưu kèm Single-Core. |
| C03 | Hiệu năng GPU | Benefit | 3DMark Time Spy Graphics; chỉ áp dụng cho Windows laptop có GPU rời (dGPU), kèm mức TGP. |
| C04 | Dung lượng RAM | Fit | Điểm theo ngưỡng nhu cầu, không tăng tuyến tính vô hạn. |
| C06 | Dung lượng lưu trữ | Fit | Điểm theo ngưỡng nhu cầu. |
| C07 | Công nghệ lưu trữ | Benefit/Fit | Mã hóa theo quy tắc giải thích được; không đoán NVMe nếu nguồn chỉ nói SSD. |
| C09 | Kích thước màn hình | Fit | Phù hợp nhu cầu, không mặc định lớn hơn là tốt hơn. |
| C10 | Tần số quét | Benefit có điều kiện | Trọng số cao hơn cho gaming/đồ họa; thấp hoặc bằng 0 ở profile văn phòng. |
| C12 | Trọng lượng | Cost | Dùng trực tiếp theo kg chuẩn hóa. |
| C15 | Hệ điều hành/tương thích phần mềm | Constraint/Fit | Ưu tiên làm ràng buộc trước TOPSIS khi người dùng có yêu cầu cụ thể. |

### 2.2. Tiêu chí loại khỏi phạm vi V1

| Mã | Tiêu chí | Quyết định |
|---|---|---|
| C05 | Khả năng nâng cấp RAM | Thu thập và hiển thị; chỉ đưa vào TOPSIS sau khi kiểm tra coverage. |
| C11 | Thời lượng pin thực tế | Không là tiêu chí lõi V1; chỉ hiển thị khi có nguồn đáng tin. |
| C13 | Tính di động/sạc tổng hợp | Loại vì có nguy cơ đếm lại trọng lượng và pin. |
| C16 | Khả năng sửa chữa/nâng cấp tổng thể | Loại theo yêu cầu người dùng. |
| C18 | Giá trị tương đối ML | Không dùng trong DSS V1; chỉ làm thí nghiệm sau này. |

`C08` (chất lượng màn hình tổng hợp), `C14` (cổng) và `C17` (bảo hành) ở trạng thái thông tin hiển thị/bộ lọc; chỉ xét nâng cấp thành tiêu chí sau EDA.

---

## 3. Chính sách dữ liệu và kiểm thử bắt buộc

1. Giữ tách biệt `product_family_id`, `configuration_id`, `listing_id` và `price_observation_id`.
2. Không coi nhiều listing hoặc nhiều snapshot giá của một cấu hình là nhiều laptop độc lập khi huấn luyện ML.
3. Chia train/test ML theo `configuration_id`; toàn bộ tiền xử lý phải fit trên tập train.
4. Không dùng benchmark có trạng thái `uncertain` làm dữ liệu chính thức.
5. Dataset phải có báo cáo: coverage từng trường, lỗi parse, bản ghi trùng, phân phối giá và tỷ lệ benchmark matching.
6. Trước khi triển khai scraper quy mô lớn phải có `source_audit.md`, `raw_sample`, `parsed_sample`, `field_coverage` và `data_quality_report`.
7. Mọi lần xếp hạng phải hiển thị nguồn giá, thời điểm thu thập, dữ liệu thiếu và các cảnh báo benchmark.

---

## 4. Điều kiện chuyển sang giai đoạn thu thập chính thức

Chỉ mở rộng sau pilot khi thỏa cả các điều kiện sau:

- Nguồn được xác minh phương thức thu thập hợp lệ.
- Schema lưu được giá, nguồn, thời điểm và định danh cấu hình.
- Parser cho các trường lõi đạt độ ổn định chấp nhận được và có báo cáo lỗi.
- Có quy tắc xác định cấu hình trùng/khác cấu hình.
- Tỷ lệ ghép benchmark `exact` đủ để CPU/GPU có thể trở thành tiêu chí của profile cần hiệu năng.
- Các tiêu chí TOPSIS cuối cùng đạt ngưỡng coverage 80% đã chốt.

## 5. Mục cần xác nhận bằng khảo sát thực tế

Các mục này không còn là lựa chọn thiết kế mở, nhưng cần bằng chứng từ pilot trước khi thực thi ở quy mô lớn:

1. Nguồn nào trong FPT Shop và CellphoneS được phép và phù hợp làm nguồn chính.
2. Quy mô thực tế đạt được trong giới hạn quyền truy cập và thời gian.
3. Độ phủ thực tế của benchmark CPU/GPU và các trường màn hình/cổng/bảo hành.
4. Khả năng duy trì snapshot giá hai tuần một lần.

---

## 6. Phân tích chi tiết cho từng nhóm quyết định

Phần này ghi lại lý do chọn phương án, những lựa chọn không chọn ở V1, hệ quả triển khai và điều kiện đánh giá lại. Mục đích là để các quyết định trong bảng phía trên có thể giải trình được trong báo cáo đề tài.

### 6.1. Nguồn dữ liệu và phạm vi thu thập

#### D01 / DATA-01 — Nguồn bán lẻ

**Quyết định:** khảo sát FPT Shop và CellphoneS trên mẫu nhỏ; sau pilot, chỉ chọn tối đa một nguồn chính cho dataset V1.

**Các phương án đã cân nhắc:**

- Chọn một nguồn ngay từ đầu: đơn giản, nhưng có rủi ro nguồn đó thiếu phân khúc, thiếu trường dữ liệu, hoặc thay đổi cấu trúc.
- Dùng hai nguồn trong toàn bộ V1: phủ thị trường tốt hơn, nhưng tăng mạnh công việc chuẩn hóa tên sản phẩm, nhận diện cấu hình trùng và xử lý khác biệt chính sách giá.
- Dùng ba nguồn trở lên: không phù hợp trước khi chứng minh pipeline; số nguồn tăng không đồng nghĩa số cấu hình hợp lệ tăng tương ứng.

**Lý do dùng hai nguồn cho pilot:** chỉ dữ liệu thử mới cho biết được tỷ lệ có các trường RAM, SSD, màn hình, trọng lượng; mức nhất quán giá; số SKU; lỗi parse; tỷ lệ ghép CPU/GPU; và chi phí khử trùng. Sau đó dùng một nguồn chính giúp target ML và ma trận DSS nhất quán hơn.

**Điều kiện chấp nhận nguồn:** phải có cách thu thập hợp lệ; URL chi tiết còn truy cập được; giá công khai; trường lõi đủ coverage; khả năng nhận diện SKU/cấu hình; tỷ lệ lỗi parsing có thể kiểm soát. Không giữ nguồn chỉ để làm dataset lớn hơn.

**Hệ quả:** các giá từ nguồn phụ chỉ là dữ liệu đối chiếu hoặc bổ sung sau này; không mặc định trộn vào target ML của nguồn chính.

#### D02 / DATA-02 — Dataset Kaggle

**Quyết định:** Kaggle Laptop Price chỉ dùng thử ETL, EDA hoặc baseline tách biệt; không merge với dataset giá Việt Nam.

**Lý do:** khác biệt năm thu thập, quốc gia, tiền tệ, định nghĩa giá và cách ghi cấu hình khiến việc quy đổi EUR sang VND không thể biến nó thành giá thị trường Việt Nam hiện tại. Merge trực tiếp sẽ khiến mô hình học chênh lệch thị trường thay vì học giá trị cấu hình.

**Cách dùng được chấp nhận:** thử parser RAM/storage/CPU, kiểm tra pipeline preprocessing, hoặc báo cáo baseline riêng. Báo cáo phải nói rõ Kaggle không phải tập huấn luyện chính cho thị trường mục tiêu.

#### DATA-03 và D03 / DATA-04 — Phương thức và quy mô thu thập

**Quyết định:** pilot 60–100 listing bằng nhập thủ công, API/export chính thức hoặc tự động hóa được phép; V1 hướng đến 300–500 cấu hình đã chuẩn hóa.

**Vì sao không bắt buộc 1.500 dòng:** listing và snapshot giá không phải lúc nào cũng là laptop độc lập. Đếm mỗi listing/lần quan sát là một mẫu ML tạo rò rỉ, thiên lệch về mẫu đăng nhiều và metrics lạc quan giả tạo.

**Ý nghĩa của mục tiêu 300–500:** chỉ được xem là đủ nếu phủ được nhiều phân khúc giá, hãng và loại máy; thông tin lõi ít thiếu; và các cấu hình được nhận diện đúng. Nếu không đạt điều kiện này, cần giảm phạm vi và nêu giới hạn thay vì suy diễn dữ liệu.

### 6.2. Giá và lịch sử giá

#### D04 / DATA-05 — Giá mục tiêu cho ML

**Quyết định:** dùng `sale_price` công khai, không điều kiện làm target ML V1.

**Các phương án không chọn:**

- `listed_price`: phù hợp nếu nghiên cứu giá niêm yết, nhưng thường không phải giá người mua phổ thông trả.
- Giá thấp nhất trên tất cả cửa hàng: dễ bị méo bởi voucher, điều kiện thành viên, quà tặng quy đổi hoặc lỗi hiển thị.
- Trộn giá niêm yết, sale, sinh viên và trả góp: tạo biến mục tiêu không có một ý nghĩa nhất quán.

**Quy tắc lưu:** vẫn giữ `listed_price`, `sale_price`, `special_price`; chỉ `sale_price` không điều kiện đi vào ML/DSS. Mỗi record phải có retailer, URL, tiền tệ, thời điểm, trạng thái parse và ghi chú khuyến mãi.

**Khi một cấu hình có nhiều cửa hàng:** lưu mỗi listing riêng. Khi cần giá đại diện để so sánh cấu hình, dùng median các `sale_price` hợp lệ ở cùng đợt quan sát. Khi gợi ý nơi mua, hiển thị từng báo giá thay vì che khác biệt này.

#### D13 / DATA-11 — Lịch sử giá

**Quyết định:** lưu snapshot hai tuần/lần từ ngày thu thập đầu tiên, nếu hợp lệ và đủ nguồn lực.

**Lý do:** hàng tuần có thể quá nặng cho prototype, còn hàng tháng dễ bỏ qua thay đổi nhanh. Hai tuần tạo được chuỗi quan sát vừa đủ mà không tạo kỳ vọng sai về khả năng dự báo giá.

**Giới hạn:** dưới 8–12 tuần chỉ là tập snapshot, chưa được gọi là xu hướng thị trường hay dùng để suy luận dự báo chuỗi thời gian. Snapshot mới thêm dòng; không được ghi đè lịch sử.

### 6.3. Benchmark và thông số kỹ thuật

#### D05 / DATA-06 — Benchmark CPU

**Quyết định:** Geekbench 6 Multi-Core là benchmark CPU chính (lưu kèm Single-Core).

**Lý do:** Geekbench 6 là chuẩn benchmark đo lường năng lực tính toán chéo kiến trúc (x86 của Intel/AMD, ARM của Apple Silicon M-series và Qualcomm Snapdragon X) một cách khách quan nhất hiện nay. Điểm được lấy theo median/trung bình các mẫu laptop trên Geekbench Browser công khai, gắn kèm link tra cứu, số mẫu test (`sample_count`) và mức độ khớp (`match_level`). Bắt buộc dùng thống nhất Geekbench 6, không trộn điểm Geekbench 5 hay 7 vào cùng cột.

**Quy tắc liêm chính dữ liệu:** Đối với phần cứng chưa phát hành thương mại hoặc sản phẩm đặt trước chưa có mẫu đo thực tế (ví dụ: MacBook M5, chip A18 Pro trên MacBook Neo), điểm số bắt buộc để trống (`null`), gán `match_level = unreleased_hardware`, tuyệt đối không suy đoán hay bịa điểm.

#### D06 / DATA-07 — Benchmark GPU

**Quyết định:** 3DMark Time Spy Graphics là benchmark GPU gaming chính cho các laptop Windows có GPU rời (dGPU).

**Lý do:** 3DMark Time Spy là bài test đồ họa DirectX 12 chuẩn mực được công nhận rộng rãi cho GPU laptop Windows. Chỉ so sánh các máy Windows có GPU rời với nhau.

**Quy tắc phân loại và chống trộn lẫn:** 
- Tuyệt đối không đưa GPU onboard (Intel Arc, Intel UHD/Graphics), Apple GPU hay Qualcomm Adreno vào chung cột 3DMark Time Spy vì khác biệt API và mục đích sử dụng.
- Khi người dùng cần máy Gaming Windows, hệ thống sẽ lọc bỏ máy macOS và Snapdragon ARM ra trước vì tính tương thích game/hệ điều hành.
- Khớp đúng mẫu laptop và mức TGP thực tế (`exact_laptop_or_tgp`) hoặc theo TGP gần nhất (`approximate`) kèm ghi chú công suất TGP, vì cùng tên GPU (như RTX 4050/3050) nhưng TGP khác nhau (45W vs 75W vs 105W) sẽ cho hiệu năng chênh lệch lớn.

#### DATA-08, DATA-09, DATA-10 — Pin, màn hình, nhiệt độ và độ ồn

**Quyết định:** không dùng pin thực tế, `display_score`, nhiệt độ hay độ ồn làm tiêu chí TOPSIS lõi V1.

**Lý do:** pin/nhiệt/ồn phụ thuộc phương pháp review. Màn hình không thể cộng OLED, độ phân giải, nits, gamut và Hz thành một điểm nếu chưa có coverage hoặc công thức được phê duyệt. Đưa vào sớm tạo kết quả nhiều tiêu chí nhưng không công bằng.

**Cách bảo toàn thông tin:** vẫn lưu và hiển thị pin Wh, panel, độ phân giải, Hz, độ sáng/màu nếu nguồn có; dùng làm mô tả/bộ lọc. Chỉ xem xét thêm vào DSS sau EDA.

### 6.4. DSS, AHP và TOPSIS

#### D08 — Số tiêu chí và bộ tiêu chí V1

**Quyết định:** V1 dùng 8–12 tiêu chí thay vì bắt buộc 15–18.

**Lý do:** TOPSIS không tốt hơn chỉ vì nhiều cột. Một tiêu chí phải liên quan trực tiếp, có dữ liệu đáng tin, phân biệt phương án, không trùng lặp mạnh và có hướng benefit/cost/fit rõ. Mục tiêu “15 tiêu chí” là tham khảo, không phải lý do chấp nhận dữ liệu thiếu.

**Bộ khởi đầu:** C01, C02, C03, C04, C06, C07, C09, C10, C12, C15. C03/C10 tùy profile; C15 ưu tiên làm ràng buộc trước TOPSIS khi người dùng yêu cầu hệ điều hành cụ thể.

**Không dùng ở V1:** C16 loại theo yêu cầu; C13 bỏ để tránh đếm lại pin/trọng lượng; C18 làm thí nghiệm; C11 chỉ hiển thị; C08/C14/C17 đợi EDA. C05 được thu thập và hiển thị, chỉ đưa vào TOPSIS sau khi kiểm tra coverage.

#### D09 — AHP phân cấp và preset nhu cầu

**Quyết định:** AHP theo nhóm, có preset lập trình, AI/đồ họa, văn phòng/di động và gaming.

**Lý do:** AHP phẳng với 15 tiêu chí cần 105 so sánh cặp; 18 tiêu chí cần 153. Đây là gánh nặng và dễ thiếu nhất quán. Phân cấp theo kinh tế, hiệu năng, bộ nhớ, hiển thị, di động và tiện ích giảm số so sánh, dễ diễn giải.

**Quy tắc:** lưu ma trận, trọng số và CR. Nếu CR vượt 0,10, không âm thầm tiếp tục; điều chỉnh preset hoặc yêu cầu xem lại ưu tiên. Người dùng chỉ cần điều chỉnh trọng số nhóm.

#### D10 — Value for Money từ ML

**Quyết định:** không dùng C18 trong DSS V1.

**Lý do:** `value_gap` phụ thuộc giá quan sát và giá dự đoán. Khi C01 đã là giá, C18 có thể đếm lại tác động giá. Mô hình lệch theo phân khúc cũng có thể đẩy sai thứ hạng.

**Cách nghiên cứu sau này:** chạy phiên bản A không có C18 và B có C18 sau khi ML được kiểm tra hợp lệ; báo cáo thay đổi Top N, tương quan thứ hạng và độ nhạy. Nếu B không ổn định, C18 chỉ nằm trong phần thảo luận.

#### D14 — Dữ liệu thiếu

**Quyết định:** tiêu chí chỉ vào TOPSIS khi coverage ≥80%; máy thiếu trường lõi không được xếp hạng trong lượt đó.

**Lý do:** thiếu VRAM, TGP, pin hoặc panel không đồng nghĩa giá trị trung bình/0. Imputation tùy tiện tạo ưu thế hay phạt giả. TOPSIS nhạy với ma trận đầu vào, nên chính sách thiếu dữ liệu phải rõ và nhất quán.

**Cách thể hiện:** nếu máy bị loại, hệ thống nêu trường thiếu. Nếu tiêu chí bị loại do coverage dưới 80%, phải thông báo tiêu chí không được dùng trong lượt xếp hạng.

### 6.5. Công nghệ, lưu trữ và giao diện

#### D11 — Kiến trúc Giao diện & Dịch vụ: Streamlit (Prototype) → FastAPI + React 18 (Production)

**Quyết định:** 
- Giai đoạn 1 (Khảo nghiệm & Demo nội bộ): Sử dụng Streamlit để kiểm thử nhanh luồng DSS (nhập yêu cầu → lọc → TOPSIS → giải thích biểu đồ).
- Giai đoạn 2 (Sản phẩm chính thức & Nghiệm thu): Tách biệt hoàn toàn Kiến trúc Backend API (FastAPI) và Frontend SPA (React 18 + Vite + Tailwind CSS / Lucide Icons).

**Lý do nâng cấp từ Streamlit sang FastAPI + React 18:**
1. **Trải nghiệm người dùng phản hồi thời gian thực (Real-time reactivity):** Hệ thống cần thanh trượt tùy biến trọng số (Direct Rating Override) với tính năng chuẩn hóa tổng 100% tức thì và tính toán lại thứ hạng TOPSIS/Sensitivity Analysis không bị giật lag hay reload lại toàn bộ trang (vấn đề cố hữu của cơ chế Streamlit rerun).
2. **So sánh đa phương án (Side-by-side comparison):** Giao diện React cho phép người dùng chọn tối đa 3 máy để đối chiếu ma trận thông số kỹ thuật đa chiều kèm highlight trực quan phương án dẫn đầu ở từng chỉ số.
3. **Phân tách trách nhiệm (Separation of Concerns):** Backend FastAPI (`src/api.py`) đóng vai trò dịch vụ tính toán toán học độc lập (AHP, TOPSIS, Sensitivity Analysis), chuẩn hóa dữ liệu đầu vào thông qua Pydantic schema validation và phục vụ cho mọi client (web, mobile, script kiểm thử tự động). Streamlit vẫn được lưu giữ trong `src/app.py` làm công cụ kiểm thử bổ trợ.

#### D12 — SQLite, CSV và Parquet

**Quyết định:** SQLite lưu dữ liệu nghiệp vụ; CSV/Parquet để xuất, EDA và ML.

**Lý do:** một cấu hình có nhiều listing, một listing có nhiều lần quan sát giá. SQLite giữ khóa và truy vấn lịch sử tốt hơn một CSV lớn. Parquet tiện cho pandas; CSV dễ kiểm tra thủ công. Không cần PostgreSQL/MySQL ở V1 vì tăng cấu hình nhưng không giải quyết bài toán nghiên cứu cốt lõi.

#### D15 — NPU/AI capability

**Quyết định:** lưu nếu có, không đưa vào xếp hạng V1.

**Lý do:** tên NPU, TOPS và workload chưa thống nhất giữa hãng; độ phủ chưa đủ. Đây chỉ là mô tả hoặc filter khi người dùng có yêu cầu AI on-device rõ ràng.

### 6.6. Phạm vi C05 và C16

#### C05 — Khả năng nâng cấp RAM

**Trạng thái:** khôi phục theo yêu cầu người dùng: thu thập, chuẩn hóa và hiển thị trong chi tiết máy; chưa mặc định là tiêu chí TOPSIS.

**Hệ quả cụ thể:** thu thập `ram_upgradeable`, `ram_slots`, `ram_slots_used`, `ram_slots_free` và `max_ram_gb` khi FPT/CellphoneS hiển thị. Các trường này được chuẩn hóa và đưa vào trang chi tiết/so sánh. Chỉ tạo trọng số AHP và cột TOPSIS nếu mẫu pilot cho thấy thông tin có ở ít nhất 80% cấu hình và có ý nghĩa với hồ sơ người dùng.

#### C16 — Khả năng sửa chữa/nâng cấp tổng thể

**Trạng thái:** loại khỏi phạm vi dự án.

**Hệ quả cụ thể:** không cần thu thập teardown, điểm sửa chữa, số khe mở rộng hoặc review chuyên sâu. Không dùng C16 làm bộ lọc, tiêu chí hay kết luận đánh giá. Việc loại bỏ này giảm rủi ro dữ liệu thiếu và đánh giá chủ quan giữa các hãng/mẫu máy.

### 6.7. Kết quả pilot FPT Shop (10 mẫu) — 10/10/2026

#### D16 — Bộ dữ liệu nào đã đủ để dùng ngay

**Kết quả kiểm tra:** cả 10/10 máy có đủ các trường lõi: giá bán, tên CPU, RAM, ổ lưu trữ, kích thước/độ phân giải màn hình, trọng lượng, hệ điều hành và bảo hành. Vì vậy không có máy nào bị loại khỏi pilot chỉ vì thiếu dữ liệu lõi. Đây không phải xác nhận rằng mọi dòng trong popup thông số đã được cào đủ; việc đối chiếu theo từng popup là một kiểm tra riêng.

**Được chấm điểm trong DSS V1:** giá bán (cost), RAM (benefit), dung lượng lưu trữ (benefit), trọng lượng (cost), bảo hành (benefit). Độ sáng đạt đúng ngưỡng 80%; chỉ được thêm vào preset "ưu tiên màn hình", không bắt buộc trong mọi kết quả.

**Dùng để lọc chứ không chấm điểm:** kích thước màn hình và hệ điều hành là sở thích/ràng buộc, không có hướng tốt-xấu chung. Khả năng nâng cấp RAM cũng chỉ là bộ lọc/nhãn: `max_ram_gb` có nhiều dữ liệu, nhưng số khe RAM trống mới đạt 50%, nên không đủ công bằng để cho điểm.

**Chỉ hiển thị:** tần số quét (70%), pin Wh (không đại diện thời lượng dùng thực tế), màu màn hình (dù đủ trường nhưng cách ghi %NTSC, sRGB, DCI-P3 không cùng thang), cổng kết nối và Wi-Fi/Bluetooth. Người dùng vẫn xem/lọc theo các thông tin này.

**Đã được chuẩn hóa hiệu năng:** hiệu năng CPU/GPU đã được ánh xạ minh bạch qua `benchmarks.csv` (Geekbench 6 Multi-Core/Single-Core và 3DMark Time Spy Graphics) và xuất vào `fpt_shop_pilot_standardized.csv`. Các máy Windows có GPU rời đạt đủ điều kiện chấm điểm Gaming (`is_gaming_eligible = true`), các máy văn phòng/Mac/Snapdragon được lọc hoặc tắt trọng số GPU tương ứng. Không có điểm số nào bị suy đoán bừa bãi.

**Nguồn kiểm chứng:** `data/catalog/benchmarks.csv`, `data/archive/legacy/fpt_shop_pilot_standardized.csv`, `data/archive/legacy/fpt_shop_completeness_audit.csv` và `data/archive/legacy/fpt_shop_criteria_readiness.csv`. Quyết định này phải được cập nhật lại khi thêm CellphoneS hoặc thêm mẫu mới; ngưỡng vẫn là coverage >= 80%.

#### D17 — Kiến trúc Two-Stage DSS & 4 Hồ sơ phân khúc Trung thực (Honest Presets)
* **Quyết định:** Rút gọn và chuẩn hóa từ phân loại ban đầu xuống **4 hồ sơ nhu cầu trung thực**, loại bỏ hoàn toàn các tuyên bố tiếp thị sai lệch:
  1. `student_budget` (Sinh viên & Kinh tế): Ưu tiên Tối ưu ngân sách, CPU đơn nhân mượt mà, RAM, Trọng lượng và SSD.
  2. `slim_mobility` (Mỏng nhẹ & Di động): Lọc cứng trọng lượng $\le 1.45$ kg; ưu tiên Trọng lượng siêu nhẹ > Giá bán > CPU > RAM > SSD.
  3. `technical_coding` (Kỹ thuật & Lập trình): Ngân sách là ràng buộc tối đa; trong các máy hợp lệ ưu tiên CPU đa nhân (Geekbench 6 Multi-Core) để compile mã nguồn > RAM dồi dào > SSD > Giá bán > Trọng lượng. Ma trận AHP giữ giá là tiêu chí cost phụ (khoảng 9,2%) để tránh máy rẻ nhất lấn át CPU/RAM khi người dùng đã đặt trần ngân sách.
  4. `gaming` (Gaming & Đồ họa nặng): Lọc cứng GPU rời NVIDIA/AMD, hệ điều hành Windows, màn hình $\ge 144$ Hz; ưu tiên Điểm GPU đồ họa (3DMark Time Spy) > CPU đa nhân > Giá bán > RAM > SSD.
* **Lý do loại bỏ profile AI Creator và Doanh nhân (Business) cũ:**
  - *Profile AI Creator*: Bị bãi bỏ theo **D15** vì NPU TOPS giữa các hãng (Intel NPU, AMD Ryzen AI, Apple Neural Engine, Qualcomm Hexagon) chưa cùng phương pháp đo lường chuẩn hóa và độ phủ công bố còn thấp.
  - *Profile Doanh nhân*: Bị bãi bỏ theo **D07/D16** vì dung lượng pin Wh không tương đương với thời lượng sử dụng thực tế (không thể chấm điểm benefit), và chất liệu vỏ nhôm/kim loại chỉ là thuộc tính lọc mô tả.
* **Toán học AHP:** Cả 4 ma trận $5 \times 5$ đều đạt tỷ số nhất quán $CR \le 0.0164 \ll 0.10$ (vượt xa chuẩn học thuật Saaty).

#### D18 — Bỏ `warranty_months`, thay bằng `storage_total_gb` trong Sinh viên - Văn phòng
* **Quyết định:** Loại bỏ tiêu chí thời gian bảo hành khỏi ma trận chấm điểm Sinh viên/Văn phòng, thay bằng dung lượng ổ cứng (fit) và nâng trọng số Giá bán lên ~40%.
* **Lý do:** Thời hạn bảo hành tại thị trường bán lẻ hầu như chỉ có 12 hoặc 24 tháng, ít tạo sự phân hóa giá trị sử dụng. Sinh viên ưu tiên tối đa việc dùng số tiền thấp nhất để đạt cấu hình CPU, RAM, SSD mượt mà nhất (P/P).

#### D19 — Xóa bỏ toàn bộ giá trị dự đoán mặc định trên giao diện (Zero Fabricated Specs)
* **Quyết định:** Mọi thông số kỹ thuật (cổng kết nối, Wi-Fi, Bluetooth, vật liệu, độ dày, pin, sạc, tần số quét) nếu nguồn bán lẻ chưa công bố hoặc thiếu dữ liệu phải hiển thị chính xác "Chưa công bố", tuyệt đối không dùng giá trị fallback phỏng đoán.

### 6.9. Tối ưu hóa tiêu chí học thuật & Bộ lọc tiện ích (110 Laptop) — 11/10/2026

#### D20 — Chuyển đổi CPU Đa nhân sang Đơn nhân cho Profile Sinh viên & Kinh tế
* **Quyết định:** Profile `student_budget` chuyển sang dùng `cpu_benchmark_single_core` (Geekbench 6 Single-Core) thay cho `cpu_benchmark_multi_core`. Các profile `technical_coding` và `gaming` tiếp tục giữ `cpu_benchmark_multi_core`.
* **Cơ sở khoa học:**
  1. **Đặc thù khối lượng công việc:** Sinh viên văn phòng chủ yếu xử lý Word, Excel, duyệt web, PDF và ứng dụng họp trực tuyến — các tác vụ này phụ thuộc chủ yếu vào IPC và xung nhịp đơn nhân (độ trễ phản hồi), không chạy render đa luồng nặng.
  2. **Tránh đếm trùng (Multicollinearity / Double-counting):** Điểm đơn nhân và đa nhân của cùng một thế hệ chip có hệ số tương quan rất cao ($\rho \sim 0.9$). Việc đưa cả hai vào cùng ma trận sẽ vi phạm D08 (thổi phồng trọng số CPU gấp đôi một cách phi lý). Thay thế thay vì bổ sung song song là giải pháp triệt để.

#### D21 — Tiêu chí phụ đóng vai trò Bộ lọc tiện ích (Secondary Utility Filters) thay vì chấm điểm cơ học
* **Quyết định:**
  - `battery_capacity_wh`: Tiếp tục ở trạng thái hiển thị chi tiết (D07/D16). Dung lượng Wh không đồng nghĩa với thời lượng thực tế (máy gaming 90Wh hết pin nhanh hơn ultrabook 50Wh); áp dụng quy tắc "Wh càng lớn càng tốt" vào TOPSIS là sai phương pháp luận.
  - `brightness_nits`, `lan_present` (RJ45), `ram_slots` (khe nâng cấp), `type_c_charging` (sạc USB-C), `thunderbolt_present`: Triển khai thành nhóm **Bộ lọc tiện ích bổ sung (Secondary Filters)** trên giao diện.
* **Lý do:** Giữ ma trận AHP cốt lõi ở quy mô $5 \times 5$ chuẩn Miller ($7 \pm 2$), bảo toàn tỷ số nhất quán $CR < 0.02$, đồng thời trao quyền cho người mua tự lọc theo nhu cầu kết nối thực tế mà không làm méo mó hàm khoảng cách TOPSIS.

