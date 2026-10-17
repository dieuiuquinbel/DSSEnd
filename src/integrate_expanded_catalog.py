"""Pipeline chuẩn hóa và hợp nhất catalog laptop mở rộng cho LaptopDSS.

Đầu vào:
- data/raw/cellphones_enriched_raw.json (Dữ liệu cào làm giàu trực tiếp từ Nuxt state CellphoneS)
- data/archive/legacy/fpt_shop_pilot_standardized.csv (Dữ liệu pilot FPT Shop chuẩn mực)
- data/catalog/benchmarks.csv (Geekbench 6 CPU, 3DMark Time Spy GPU & Geekbench 6 OpenCL/Metal GPU Compute)

Đầu ra:
- data/catalog/laptops.csv (Catalog thống nhất)
- data/artifacts/laptop_dss.db (Cơ sở dữ liệu SQLite BCNF)
"""

import csv
import json
import re
import sys
import hashlib
import sqlite3
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any

ROOT = Path(__file__).resolve().parents[1]
sys.stdout.reconfigure(encoding='utf-8')

EXISTING_CSV = ROOT / "data" / "catalog" / "laptops.csv"
ENRICHED_RAW_JSON = ROOT / "data" / "raw" / "cellphones_enriched_raw.json"
FPT_LEGACY_CSV = ROOT / "data" / "archive" / "legacy" / "fpt_shop_pilot_standardized.csv"
BENCHMARKS_CSV = ROOT / "data" / "catalog" / "benchmarks.csv"
DB_FILE = ROOT / "data" / "artifacts" / "laptop_dss.db"

# Import direct standardization functions
sys.path.insert(0, str(ROOT / "src" / "legacy"))
from standardize_cellphones import (
    normalize_cpu,
    normalize_gpu,
    parse_ram,
    parse_storage,
    parse_cpu_cores_threads,
    parse_battery_wh,
    parse_battery_cells,
    parse_brightness_nits,
    parse_ports,
    parse_ram_slots,
    parse_screen_inch,
    parse_resolution,
    parse_panel_type,
    parse_refresh_rate,
    parse_weight,
    parse_os,
    parse_storage_type,
    parse_charger_w,
    parse_color_gamut,
    parse_cpu_ghz,
    load_benchmarks,
)


def determine_gaming_eligibility(os_name: str, gpu_type: str, hz: Optional[int]) -> str:
    """Xác định khả năng gaming: GPU rời, Windows OS và màn hình >= 144Hz."""
    return 'true' if (gpu_type == 'discrete' and os_name == 'Windows' and (hz or 0) >= 144) else 'false'


def parse_strict_rich_ports(ports_str: str, pin_str: str = "") -> dict:
    """Trích xuất cổng giao tiếp theo nguyên tắc Strict NULL: chỉ 'true' khi có bằng chứng rõ ràng."""
    combined = ((ports_str or '') + ' ' + (pin_str or '')).strip()
    if not combined:
        return {
            'lan_present': '',
            'audio_jack_present': '',
            'hdmi_version': '',
            'thunderbolt_present': '',
            'sd_card_slot_present': '',
            'type_c_charging': '',
        }
    
    lan = 'true' if re.search(r'\b(?:lan|rj45|rj-45|ethernet)\b', combined, re.I) else ''
    audio = 'true' if re.search(r'3\.5|tai nghe|headset|audio', combined, re.I) else ''
    thunderbolt = 'true' if re.search(r'thunderbolt|usb4', combined, re.I) else ''
    sd_card = 'true' if re.search(r'\b(?:sd|micro\s*sd|card\s*reader|khe\s*thẻ)\b', combined, re.I) else ''
    type_c_charge = 'true' if re.search(r'(?:sạc|power\s*delivery|pd).*(?:type-?c|usb-?c)|(?:type-?c|usb-?c).*(?:sạc|power\s*delivery|pd)', combined, re.I) else ''
    
    m_h = re.search(r'hdmi\s*([12]\.\d[a-z]?)', combined, re.I)
    hdmi_ver = m_h.group(1) if m_h else ''
    
    return {
        'lan_present': lan,
        'audio_jack_present': audio,
        'hdmi_version': hdmi_ver,
        'thunderbolt_present': thunderbolt,
        'sd_card_slot_present': sd_card,
        'type_c_charging': type_c_charge,
    }


def parse_strict_warranty(warranty_text: Optional[str]) -> str:
    """Trích xuất số tháng bảo hành từ văn bản gốc. Không bao giờ đoán mò hoặc gán default 24."""
    if not warranty_text:
        return ''
    m = re.search(r'Bảo hành\s*(\d+)\s*(tháng|năm)', warranty_text, re.I)
    if m:
        num = int(m.group(1))
        unit = m.group(2).lower()
        return str(num * 12 if unit == 'năm' else num)
    return ''


def standardize_cellphones_item(raw_item: Dict[str, Any], benchmarks: dict) -> Dict[str, Any]:
    """Chuẩn hóa một bản ghi laptop CellphoneS từ Nuxt state với nguyên tắc Strict NULL."""
    specs = raw_item.get('specs_raw', {})
    name = raw_item.get('product_name_raw', '')
    url = raw_item.get('source_url', '')
    pid = raw_item.get('source_product_id', '')

    # 1. CPU & GPU
    raw_cpu = specs.get('Loại CPU', '')
    cpu_norm = normalize_cpu(raw_cpu)
    cores, threads = parse_cpu_cores_threads(raw_cpu)
    base_ghz, boost_ghz = parse_cpu_ghz(raw_cpu)

    raw_gpu = specs.get('Loại card đồ họa', '')
    gpu_norm, gpu_type, vram = normalize_gpu(raw_gpu, raw_cpu, name)

    # 2. RAM & Storage
    ram_gb = parse_ram(specs.get('Dung lượng RAM', ''))
    storage_gb = parse_storage(specs.get('Ổ cứng', ''))
    slots, free_slots, max_ram = parse_ram_slots(specs.get('Số khe ram', '') or specs.get('Dung lượng RAM', ''), ram_gb)
    storage_tech = parse_storage_type(specs.get('Ổ cứng', '')) or ''
    ram_type = specs.get('Loại RAM', '')

    # 3. Screen
    screen_inch = parse_screen_inch(specs.get('Kích thước màn hình', ''))
    screen_w, screen_h = parse_resolution(specs.get('Độ phân giải màn hình', ''))
    panel = parse_panel_type(specs.get('Chất liệu tấm nền', '') or specs.get('Công nghệ màn hình', ''))
    hz = parse_refresh_rate(specs.get('Tần số quét', '') or specs.get('Công nghệ màn hình', ''))
    nits = parse_brightness_nits(specs.get('Độ sáng', '') or specs.get('Công nghệ màn hình', ''))
    color_gamut = parse_color_gamut(specs.get('Công nghệ màn hình', ''))

    # 4. Mobility & Battery
    battery_wh = parse_battery_wh(specs.get('Pin', ''))
    battery_cells = parse_battery_cells(specs.get('Pin', ''))
    charger_w = parse_charger_w(specs.get('Pin', ''))
    weight_val = parse_weight(specs.get('Trọng lượng', ''))

    # 5. OS
    os_name = parse_os(specs.get('Hệ điều hành khi ra mắt') or specs.get('Hệ điều hành') or '')

    # 6. Benchmark Matching
    # CPU Multi-core & Single-core
    cpu_bench_key = ("CPU", cpu_norm, "Geekbench 6 Multi-Core")
    cpu_bench = benchmarks.get(cpu_bench_key, {})
    cpu_m_score = cpu_bench.get('score')
    cpu_match = cpu_bench.get('match_level', '')
    cpu_url = cpu_bench.get('source_url', '')

    cpu_sc_key = ("CPU", cpu_norm, "Geekbench 6 Single-Core")
    cpu_sc_bench = benchmarks.get(cpu_sc_key, {})
    cpu_s_score = cpu_sc_bench.get('score')

    # GPU Gaming (3DMark Time Spy)
    gpu_score = None
    gpu_match = ''
    gpu_url = ''
    if gpu_type == 'discrete':
        gpu_bench_key = ("GPU", gpu_norm, "3DMark Time Spy Graphics")
        gpu_bench = benchmarks.get(gpu_bench_key, {})
        gpu_score = gpu_bench.get('score')
        gpu_match = gpu_bench.get('match_level', '')
        gpu_url = gpu_bench.get('source_url', '')

    # GPU Compute (Geekbench 6 Metal / OpenCL)
    gpu_compute_score = None
    compute_api = 'Geekbench 6 Metal' if 'Apple' in gpu_norm else 'Geekbench 6 OpenCL'
    compute_key = ("GPU", gpu_norm, compute_api)
    if compute_key in benchmarks and benchmarks[compute_key].get('score'):
        gpu_compute_score = benchmarks[compute_key].get('score')
    elif ("GPU", "Integrated Graphics", compute_api) in benchmarks:
        gpu_compute_score = benchmarks[("GPU", "Integrated Graphics", compute_api)].get('score')

    # 7. Ports & Connectivity
    ports_str = specs.get('Cổng giao tiếp', '')
    pin_str = specs.get('Pin', '')
    usb_a, usb_c, hdmi_present = parse_ports(ports_str)
    rich = parse_strict_rich_ports(ports_str, pin_str)

    gaming_eligible = determine_gaming_eligibility(os_name, gpu_type, hz)
    img_path = raw_item.get('image_url_remote') or f"/images/{pid}.png"

    sale_p = raw_item.get('sale_price_vnd')
    listed_p = raw_item.get('listed_price_vnd')  # Strict NULL: Không fallback sang sale_p nếu không công bố

    # Strict VRAM: Chỉ gán VRAM khi có GPU rời và vram > 0, tuyệt đối không gán '0' cho integrated
    vram_str = str(vram) if (gpu_type == 'discrete' and vram is not None and vram > 0) else ''

    # Strict warranty: Trích xuất từ văn bản bảo hành thực tế
    w_str = parse_strict_warranty(raw_item.get('warranty_raw'))

    return {
        'source': 'cellphones',
        'source_product_id': pid,
        'product_name_raw': name,
        'source_url': url,
        'collected_at': raw_item.get('crawled_at', '2026-10-17T00:00:00'),
        'currency': 'VND',
        'listed_price_vnd': str(int(listed_p)) if listed_p else '',
        'sale_price_vnd': str(int(sale_p)) if sale_p else '',
        'special_price_vnd': '',
        'cpu_name_normalized': cpu_norm,
        'cpu_cores': str(cores) if cores else '',
        'cpu_threads': str(threads) if threads else '',
        'cpu_base_ghz': str(base_ghz) if base_ghz else '',
        'cpu_boost_ghz': str(boost_ghz) if boost_ghz else '',
        'gpu_name_normalized': gpu_norm,
        'gpu_type': gpu_type,
        'gpu_vram_gb': vram_str,
        'ram_gb': str(ram_gb) if ram_gb else '',
        'ram_type': ram_type,
        'ram_slots': str(slots) if slots is not None else '',
        'ram_slots_free': str(free_slots) if free_slots is not None else '',
        'max_ram_gb': str(max_ram) if max_ram is not None else '',
        'storage_total_gb': str(storage_gb) if storage_gb else '',
        'storage_primary_type': storage_tech,
        'screen_size_inch': str(screen_inch) if screen_inch else '',
        'screen_width_px': str(screen_w) if screen_w else '',
        'screen_height_px': str(screen_h) if screen_h else '',
        'panel_type': panel if panel else '',
        'refresh_rate_hz': str(hz) if hz else '',
        'brightness_nits': str(nits) if nits else '',
        'color_gamut_raw': color_gamut,
        'battery_capacity_wh': str(battery_wh) if battery_wh else '',
        'battery_cells': str(battery_cells) if battery_cells else '',
        'charger_w': str(charger_w) if charger_w else '',
        'weight_kg': str(weight_val) if weight_val else '',
        'thickness_mm': '',
        'dimensions_raw': specs.get('Kích thước', ''),
        'material_raw': specs.get('Chất liệu', '') or specs.get('Chất liệu vỏ trên', ''),
        'color_raw': '',
        'usb_a_count': str(usb_a) if usb_a > 0 else ('0' if ports_str else ''),
        'usb_c_count': str(usb_c) if usb_c > 0 else ('0' if ports_str else ''),
        'hdmi_present': hdmi_present if ports_str else '',
        'hdmi_version': rich.get('hdmi_version', ''),
        'lan_present': rich.get('lan_present', ''),
        'audio_jack_present': rich.get('audio_jack_present', ''),
        'wifi_raw': specs.get('Wi-Fi', ''),
        'bluetooth_raw': specs.get('Bluetooth', ''),
        'webcam_raw': specs.get('Webcam', ''),
        'os_name': os_name,
        'warranty_months': w_str,
        'cpu_benchmark_multi_core': str(cpu_m_score) if cpu_m_score else '',
        'cpu_benchmark_single_core': str(cpu_s_score) if cpu_s_score else '',
        'cpu_benchmark_source_url': cpu_url if cpu_url else '',
        'cpu_benchmark_match_level': cpu_match if cpu_match else '',
        'gpu_benchmark_time_spy': str(gpu_score) if gpu_score else '',
        'gpu_benchmark_source_url': gpu_url if gpu_url else '',
        'gpu_benchmark_match_level': gpu_match if gpu_match else '',
        'gpu_benchmark_compute': str(gpu_compute_score) if gpu_compute_score else '',
        'gpu_benchmark_compute_api': compute_api.replace('Geekbench 6 ', '') if gpu_compute_score else '',
        'is_gaming_eligible': gaming_eligible,
        'image_url': img_path,
        'npu_tops': specs.get('Chip AI', ''),
        'thunderbolt_present': rich.get('thunderbolt_present', ''),
        'sd_card_slot_present': rich.get('sd_card_slot_present', ''),
        'type_c_charging': rich.get('type_c_charging', ''),
    }


def integrate_catalog():
    print("=== BẮT ĐẦU CHUẨN HÓA VÀ HỢP NHẤT CATALOG LAPTOP DSS ===", flush=True)

    # 1. Tải benchmarks
    benchmarks = load_benchmarks()
    print(f"1. Đã tải benchmark index: {len(benchmarks)} cặp component-benchmark.", flush=True)

    # 2. Đọc và chuẩn hóa dữ liệu cào giàu thông số từ Nuxt state CellphoneS
    with open(ENRICHED_RAW_JSON, 'r', encoding='utf-8') as f:
        cellphones_raw_items = json.load(f)
    print(f"2. Đã tải dữ liệu cào Nuxt CellphoneS: {len(cellphones_raw_items)} laptop.", flush=True)

    cps_rows = []
    seen_ids = set()
    seen_urls = set()
    for item in cellphones_raw_items:
        pid = item.get('source_product_id', '')
        url = item.get('source_url', '')
        if pid in seen_ids or url in seen_urls:
            continue
        std = standardize_cellphones_item(item, benchmarks)
        if std.get('sale_price_vnd'):
            cps_rows.append(std)
            seen_ids.add(pid)
            seen_urls.add(url)

    print(f"3. Chuẩn hóa thành công {len(cps_rows)} laptop CellphoneS chính hãng.", flush=True)

    # 3. Đọc dữ liệu pilot FPT Shop (loại trừ các bản ghi M5/A18 chưa phát hành)
    fpt_rows = []
    if FPT_LEGACY_CSV.exists():
        with open(FPT_LEGACY_CSV, 'r', encoding='utf-8') as f:
            for r in csv.DictReader(f):
                c_norm = r.get('cpu_name_normalized', '').lower()
                name_l = r.get('product_name_raw', '').lower()
                if 'm5' in c_norm or 'a18' in c_norm or 'm5' in name_l or 'a18' in name_l:
                    continue
                # Map compute benchmark
                gpu_norm = r.get('gpu_name_normalized', '')
                compute_api = 'Geekbench 6 Metal' if 'Apple' in gpu_norm else 'Geekbench 6 OpenCL'
                k_comp = ("GPU", gpu_norm, compute_api)
                if k_comp in benchmarks and benchmarks[k_comp].get('score'):
                    r['gpu_benchmark_compute'] = str(benchmarks[k_comp].get('score'))
                    r['gpu_benchmark_compute_api'] = compute_api.replace('Geekbench 6 ', '')
                else:
                    r['gpu_benchmark_compute'] = ''
                    r['gpu_benchmark_compute_api'] = ''
                fpt_rows.append(r)

    print(f"4. Giữ lại {len(fpt_rows)} laptop FPT Shop pilot đã phát hành thương mại.", flush=True)

    # 4. Hợp nhất catalog
    unified_catalog = cps_rows + fpt_rows
    print(f"5. Tổng catalog hợp nhất toàn diện: {len(unified_catalog)} laptop.", flush=True)

    # 5. Lưu CSV
    if unified_catalog:
        fieldnames = list(unified_catalog[0].keys())
        for row in unified_catalog:
            for k in row.keys():
                if k not in fieldnames:
                    fieldnames.append(k)

        with open(EXISTING_CSV, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(unified_catalog)
        print(f"6. Đã lưu catalog chuẩn hóa vào {EXISTING_CSV.relative_to(ROOT)}", flush=True)

    # 6. Thống kê phân khúc
    prices = [float(r['sale_price_vnd']) for r in unified_catalog if r.get('sale_price_vnd')]
    u15 = sum(1 for p in prices if p < 15_000_000)
    b15_25 = sum(1 for p in prices if 15_000_000 <= p <= 25_000_000)
    b25_40 = sum(1 for p in prices if 25_000_000 < p <= 40_000_000)
    above40 = sum(1 for p in prices if p > 40_000_000)

    print("\n--- THỐNG KÊ CATALOG HỢP NHẤT ---", flush=True)
    print(f"  • Tổng số laptop: {len(unified_catalog)} (CellphoneS: {len(cps_rows)}, FPT Shop: {len(fpt_rows)})", flush=True)
    print(f"  • Phân khúc dưới 15 triệu: {u15} máy (Giá thấp nhất: {min(prices):,.0f} đ)", flush=True)
    print(f"  • Phân khúc 15 - 25 triệu: {b15_25} máy", flush=True)
    print(f"  • Phân khúc 25 - 40 triệu: {b25_40} máy", flush=True)
    print(f"  • Phân khúc trên 40 triệu: {above40} máy (Giá cao nhất: {max(prices):,.0f} đ)", flush=True)

    # 7. Cập nhật SQLite Database
    sys.path.insert(0, str(ROOT / "src"))
    from build_sqlite_db import init_and_populate_db
    print("\n7. Đang cập nhật cơ sở dữ liệu SQLite laptop_dss.db theo chuẩn BCNF...", flush=True)
    init_and_populate_db()
    print("Đã cập nhật SQLite DB laptop_dss.db thành công!", flush=True)


if __name__ == '__main__':
    integrate_catalog()
