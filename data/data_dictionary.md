# Data dictionary — laptop pilot

Mỗi laptop được lưu theo hai lớp:

- `raw`: giữ nguyên tên trường và giá trị hiển thị trên trang bán hàng.
- `processed`: các giá trị đã được chuyển về số hoặc nhãn thống nhất để lọc, ML và DSS.

Ba tệp làm việc hiện có:

- `data/raw/fpt_shop/*.json`: bản ghi nguồn của từng máy. Khóa trong `specifications` giữ nguyên nhãn FPT Shop.
- `data/processed/fpt_shop_pilot_full.csv`: bảng rộng để kiểm tra dữ liệu. Mỗi nhãn thông số xuất hiện trong bất kỳ máy nào sẽ là một cột riêng; máy không được hãng công bố trường đó để trống.
- `data/processed/fpt_shop_pilot.csv`: bảng chuẩn hóa, chỉ dùng cho lọc, tính điểm và mô hình sau này.
- `data/processed/fpt_shop_completeness_audit.csv`: bảng kiểm trường lõi và trường phụ của từng máy; dùng để biết máy nào phải bổ sung nguồn.
- `data/processed/fpt_shop_criteria_readiness.csv`: quyết định tái lập được cho từng tiêu chí (coverage, hướng cost/benefit/fit và trạng thái score/filter/display/blocked).

## Nhận diện và giá

`source`, `source_product_id`, `product_name_raw`, `brand`, `model_name`, `sku_or_part_number`, `source_url`, `collected_at`, `currency`, `listed_price_vnd`, `sale_price_vnd`, `special_price_vnd`, `promotion_notes`, `warranty_months`.

## CPU và GPU

`cpu_vendor`, `cpu_name_raw`, `cpu_name_normalized`, `cpu_cores`, `cpu_threads`, `cpu_base_ghz`, `cpu_boost_ghz`, `gpu_vendor`, `gpu_name_raw`, `gpu_name_normalized`, `gpu_type`, `gpu_vram_gb`, `gpu_tgp_w`.

## RAM và lưu trữ

`ram_gb`, `ram_type`, `ram_speed_mts`, `ram_slots`, `ram_slots_used`, `ram_slots_free`, `max_ram_gb`, `ram_upgradeable`, `storage_total_gb`, `storage_primary_type`, `storage_secondary_gb`, `storage_slots`, `storage_upgradeable`.

## Màn hình

`screen_size_inch`, `screen_resolution_raw`, `screen_width_px`, `screen_height_px`, `panel_type`, `refresh_rate_hz`, `brightness_nits`, `color_gamut_raw`, `anti_glare`, `touchscreen`.

## Pin, thiết kế và hệ điều hành

`battery_capacity_wh`, `battery_cells`, `charger_w`, `fast_charge_raw`, `weight_kg`, `thickness_mm`, `dimensions_raw`, `color_raw`, `material_raw`, `os_name`.

## Kết nối và phần cứng khác

`usb_a_count`, `usb_c_count`, `thunderbolt_or_usb4`, `usb_c_power_delivery`, `usb_c_displayport`, `hdmi_present`, `hdmi_version`, `lan_present`, `audio_jack_present`, `wifi_raw`, `bluetooth_raw`, `webcam_raw`, `keyboard_raw`, `speaker_raw`, `microphone_raw`, `security_raw`.

## Quy tắc

- Trường nào nguồn không ghi: để trống, không đoán.
- Dữ liệu hiển thị nhưng chưa thể chuẩn hóa chắc chắn: giữ nguyên trong JSON nguồn và trong cột tương ứng của `fpt_shop_pilot_full.csv`.
- Giá khuyến mãi có điều kiện: lưu vào `special_price_vnd` cùng `promotion_notes`, không thay thế `sale_price_vnd`.
- Chỉ tiêu chí có coverage từ 80% trở lên mới có thể được xem xét để chấm điểm. Đạt coverage không tự động có nghĩa là được cộng điểm: trường dạng sở thích, ràng buộc hoặc dữ liệu khác thang vẫn là filter/hiển thị.
- Bảng `fpt_shop_completeness_audit.csv` chỉ xác nhận đủ **trường lõi cho DSS**, không chứng minh đã cào đủ mọi dòng thông số của trang. Độ đầy đủ từng dòng phải được đối chiếu với popup "Thông số kỹ thuật".
