"""Pipeline chuẩn hóa dữ liệu laptop CellphoneS thô.

Parses data/raw/cellphones_laptops_raw.json into standard DSS schema:
- Extracts normalized CPU model, GPU model, RAM GB, Storage GB, Screen Inch, Hz, Panel, Weight.
- Adheres to DECISIONS.md D14 and coverage rules.
- Matches against data/processed/benchmarks.csv.
"""

import json
import re
import csv
from typing import Optional, Tuple
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RAW_JSON = ROOT / "data" / "raw" / "cellphones_laptops_raw.json"
BENCHMARKS_CSV = ROOT / "data" / "processed" / "benchmarks.csv"
OUT_CSV = ROOT / "data" / "processed" / "cellphones_standardized.csv"


def normalize_cpu(raw_cpu: str) -> str:
    if not raw_cpu:
        return "Unknown CPU"
    raw = raw_cpu.strip()
    
    # Intel Core Ultra (including Arrow Lake, Lunar Lake, Meteor Lake)
    m = re.search(r'Intel\s+Core\s+Ultra\s+(\d)\s+(\d{3}[A-Z]*)', raw, re.I)
    if m:
        return f"Intel Core Ultra {m.group(1)} {m.group(2)}"
        
    # Intel Core (Series 1 / 2) like Core 5 120U, Core 7 150U, Core 5 210H, Core 5 320, Core 3 100U
    m = re.search(r'Intel\s+Core\s*(\d)[- ]*(\d{3}[A-Z]*)', raw, re.I)
    if m:
        return f"Intel Core {m.group(1)} {m.group(2)}"

    # Intel Core i3/i5/i7/i9 Gen 11-14
    m = re.search(r'Intel\s+Core\s+(i[3579])[- ]+(\d{4,5}[A-Z]*)', raw, re.I)
    if m:
        return f"Intel Core {m.group(1)} {m.group(2)}"

    # Intel Processor / N-series
    m = re.search(r'Intel\s+(Processor|N\d{3}|Core\s+i[3579])', raw, re.I)
    if m:
        return f"Intel {m.group(1)}"

    # AMD Ryzen AI Strix Point / Strix Halo
    m = re.search(r'AMD\s+Ryzen\s+AI\s+(?:MAX\+?\s*)?(\d)\s+([A-Z0-9]+)', raw, re.I)
    if m:
        return f"AMD Ryzen AI {m.group(1)} {m.group(2)}"
    if 'MAX+ 395' in raw or 'Max+ 395' in raw:
        return "AMD Ryzen AI Max+ 395"

    # Specific fix: ASUS truncated Ryzen 5 40 -> Ryzen 5 7520U
    if 'Ryzen 5 40' in raw or 'ryzen 5 40' in raw.lower():
        return "AMD Ryzen 5 7520U"

    # AMD Ryzen 3/5/7/9 (e.g. Ryzen 7 155, Ryzen 7 8845HS, Ryzen 5 7530U, Ryzen 5 7535HS)
    m = re.search(r'AMD\s+Ryzen\s+([3579])\s+(\d{3,4}[A-Z]*)', raw, re.I)
    if m:
        return f"AMD Ryzen {m.group(1)} {m.group(2)}"

    # Qualcomm Snapdragon
    if 'snapdragon' in raw.lower():
        m = re.search(r'X1[- ](\d{2})[- ](\d{3})', raw, re.I)
        if m:
            return f"Qualcomm Snapdragon X Series X1-{m.group(1)}"
        return "Qualcomm Snapdragon X Plus"

    # Apple Silicon
    m = re.search(r'Apple\s+(M[1-5](?:\s+(?:Pro|Max))?)', raw, re.I)
    if m:
        return f"Apple {m.group(1)}"

    # Fallback to first 25 chars
    return raw[:30].strip()


def normalize_gpu(raw_gpu: str) -> tuple[str, str, int]:
    """Returns (gpu_name_normalized, gpu_type: 'discrete'|'integrated', vram_gb)."""
    if not raw_gpu:
        return "Integrated Graphics", "integrated", 0
    raw = raw_gpu.strip()
    
    # Trích xuất VRAM thực tế từ chuỗi raw (ví dụ: "8 GB GDDR7", "16GB GDDR7", "6GB GDDR6", "4GB GDDR6")
    vram = 0
    m_vram = re.search(r'(\d+)\s*(?:GB|G)\b', raw, re.I)
    if m_vram:
        vram = int(m_vram.group(1))

    # RTX 50-series
    m = re.search(r'RTX\s*(50[56789]0(?:\s*Ti)?)', raw, re.I)
    if m:
        name = f"NVIDIA GeForce RTX {m.group(1)}"
        if vram == 0:
            vram = 16 if '5080' in name else (12 if '5070 Ti' in name else 8)
        return name, "discrete", vram

    # RTX 40-series
    m = re.search(r'RTX\s*(40[56789]0(?:\s*Ti)?)', raw, re.I)
    if m:
        name = f"NVIDIA GeForce RTX {m.group(1)}"
        if vram == 0:
            vram = 6 if '4050' in name else 8
        return name, "discrete", vram

    # RTX 30-series
    m = re.search(r'RTX\s*(30[56789]0(?:\s*Ti)?)', raw, re.I)
    if m:
        name = f"NVIDIA GeForce RTX {m.group(1)}"
        if vram == 0:
            vram = 6 if '6GB' in raw or '6 GB' in raw else 4
        return name, "discrete", vram

    # MX-series
    if 'mx570' in raw.lower() or 'geforce mx' in raw.lower():
        return "NVIDIA GeForce MX570A", "discrete", 2

    # Intel Arc
    if 'arc' in raw.lower():
        return "Intel Arc Graphics", "integrated", 0

    # Intel Iris / UHD / Graphics
    if 'iris' in raw.lower():
        return "Intel Iris Xe Graphics", "integrated", 0
    if 'intel' in raw.lower():
        return "Intel Graphics", "integrated", 0

    # AMD Radeon 680M / 780M / Graphics
    if '780m' in raw.lower():
        return "AMD Radeon 780M", "integrated", 0
    if '680m' in raw.lower():
        return "AMD Radeon 680M", "integrated", 0
    if 'radeon' in raw.lower():
        return "AMD Radeon Graphics", "integrated", 0

    if 'adreno' in raw.lower():
        return "Qualcomm Adreno GPU", "integrated", 0

    return "Integrated Graphics", "integrated", 0


def parse_ram(raw_ram: str) -> int:
    m = re.search(r'(\d+)\s*GB', raw_ram or '', re.I)
    return int(m.group(1)) if m else 8


def parse_storage(raw_storage: str) -> int:
    """Extract actual initial storage capacity, ignoring upgrade maximums strictly.
    
    Handles both parenthesized '(Nâng cấp tối đa 2TB)' and dash-separated '- Nâng cấp tối đa 1TB'.
    """
    if not raw_storage:
        return 512
        
    cleaned = raw_storage.strip()
    # 1. Cắt bỏ toàn bộ chuỗi từ chữ "nâng cấp" hoặc "tối đa" trở đi
    cleaned = re.split(r'[-–(]\s*(?:nâng cấp|tối đa|dư|slot)', cleaned, flags=re.I)[0].strip()
    # 2. Xóa bỏ bất kỳ cặp ngoặc đơn còn lại nào
    cleaned = re.sub(r'\(.*?\)', '', cleaned).strip()
    
    # 3. Lấy số và đơn vị xuất hiện ĐẦU TIÊN
    m_first = re.search(r'(\d+)\s*(GB|TB)', cleaned, re.I)
    if m_first:
        val = int(m_first.group(1))
        unit = m_first.group(2).upper()
        return val * 1024 if unit == 'TB' else val
        
    # Fallback dự phòng
    m_any = re.search(r'(\d+)\s*(GB|TB)', raw_storage, re.I)
    if m_any:
        val = int(m_any.group(1))
        unit = m_any.group(2).upper()
        return val * 1024 if unit == 'TB' else val
        
    return 512


def parse_cpu_cores_threads(raw_cpu: str) -> tuple[Optional[int], Optional[int]]:
    """Extract CPU physical cores and threads."""
    if not raw_cpu:
        return None, None
    cores, threads = None, None
    
    # Patterns: "14 nhân 14 luồng", "8 lõi / 12 luồng", "10C/12T", "6C (2P + 4LPE) / 6T"
    m_ct = re.search(r'(\d+)\s*(?:nhân|lõi|C)\b.*?(\d+)\s*(?:luồng|T)\b', raw_cpu, re.I)
    if m_ct:
        return int(m_ct.group(1)), int(m_ct.group(2))
        
    m_c = re.search(r'(\d+)\s*(?:nhân|lõi)\b', raw_cpu, re.I)
    if m_c:
        cores = int(m_c.group(1))
        
    m_t = re.search(r'(\d+)\s*luồng\b', raw_cpu, re.I)
    if m_t:
        threads = int(m_t.group(1))
        
    return cores, (threads if threads else cores)


def parse_battery_wh(raw_battery: str) -> Optional[float]:
    """Extract battery capacity in Watt-hours."""
    if not raw_battery:
        return None
    m = re.search(r'(\d+(?:\.\d+)?)\s*(?:Wh|WHrs)', raw_battery, re.I)
    return float(m.group(1)) if m else None


def parse_brightness_nits(raw_screen_tech: str) -> Optional[int]:
    """Extract display peak brightness in nits."""
    if not raw_screen_tech:
        return None
    m = re.search(r'(\d{3,4})\s*nits?', raw_screen_tech, re.I)
    return int(m.group(1)) if m else None


def parse_ports(raw_ports: str) -> tuple[int, int, str]:
    """Extract (usb_a_count, usb_c_count, hdmi_present)."""
    if not raw_ports:
        return 0, 0, "false"
    
    # USB-A
    usb_a = 0
    for m in re.finditer(r'(\d+)\s*(?:x|\*|-)\s*USB(?:\s*Type)?[- ]A', raw_ports, re.I):
        usb_a += int(m.group(1))
    if usb_a == 0 and re.search(r'USB(?:\s*Type)?[- ]A', raw_ports, re.I):
        usb_a = 1
        
    # USB-C
    usb_c = 0
    for m in re.finditer(r'(\d+)\s*(?:x|\*|-)\s*USB(?:\s*Type)?[- ]C', raw_ports, re.I):
        usb_c += int(m.group(1))
    if usb_c == 0 and re.search(r'USB(?:\s*Type)?[- ]C|Thunderbolt', raw_ports, re.I):
        usb_c = 1
        
    # HDMI
    hdmi = "true" if re.search(r'HDMI', raw_ports, re.I) else "false"
    return usb_a, usb_c, hdmi


def parse_ram_slots(raw_ram_slots: str, ram_gb: int) -> tuple[Optional[int], Optional[int], Optional[int]]:
    """Extract (ram_slots, ram_slots_free, max_ram_gb) honestly without fabricated defaults."""
    if not raw_ram_slots:
        return None, None, None
    raw = raw_ram_slots.strip()
    slots, free_slots, max_ram = None, None, None
    
    # 1. Total slots
    if re.search(r'onboard\s+không\s+nâng\s+cấp|^onboard$|không\s+nâng\s+cấp', raw, re.I):
        slots = 0
        free_slots = 0
    elif '1 ram onboard + 1 khe' in raw.lower() or '1 khe onboard + 1 khe' in raw.lower():
        slots = 2
    else:
        m_s = re.search(r'(\d+)\s*khe', raw, re.I)
        if m_s:
            slots = int(m_s.group(1))
            
    # 2. Free slots
    if 'khe trống' in raw.lower():
        free_slots = 1
    elif slots == 2:
        if re.search(r'1\s*[xX*]\s*\d+\s*GB', raw) and not re.search(r'1\s*[xX*].*?\+\s*1\s*[xX*]', raw):
            free_slots = 1  # 1 populated -> 1 free!
        elif re.search(r'2\s*[xX*]\s*\d+\s*GB', raw) or re.search(r'1\s*[xX*].*?\+\s*1\s*[xX*]', raw) or '8gb+16gb' in raw.lower():
            free_slots = 0  # Both populated
        else:
            free_slots = None  # Genuinely unknown -> None, NEVER fabricate 0!
    elif slots == 1:
        free_slots = 0
    elif slots == 0:
        free_slots = 0
        
    # 3. Max RAM
    m_max = re.search(r'tối\s*đa\s*(\d+)\s*GB', raw, re.I)
    if m_max:
        max_ram = int(m_max.group(1))
    elif slots == 0:
        max_ram = ram_gb
        
    return slots, free_slots, max_ram


def parse_screen_inch(raw_screen: str) -> Optional[float]:
    if not raw_screen:
        return None
    m = re.search(r'(\d{1,2}(?:\.\d)?)\s*(?:inch|"|”)', raw_screen, re.I)
    return float(m.group(1)) if m else None


def parse_resolution(raw_res: str) -> tuple[Optional[int], Optional[int]]:
    if not raw_res:
        return None, None
    m = re.search(r'(\d{3,4})\s*[xX×]\s*(\d{3,4})', raw_res)
    if m:
        return int(m.group(1)), int(m.group(2))
    if 'fhd' in raw_res.lower() or '1080' in raw_res:
        return 1920, 1080
    if 'wuxga' in raw_res.lower():
        return 1920, 1200
    if '2k' in raw_res.lower():
        return 2560, 1440
    return None, None


def parse_panel_type(raw_tech: str) -> Optional[str]:
    if not raw_tech:
        return None
    raw = raw_tech.upper()
    if 'OLED' in raw:
        return "OLED"
    if 'IPS' in raw:
        return "IPS"
    if 'VA' in raw:
        return "VA"
    if 'TN' in raw:
        return "TN"
    return None


def parse_weight(raw_weight: str) -> Optional[float]:
    if not raw_weight:
        return None
    m = re.search(r'(\d{1,2}(?:\.\d{1,2})?)', str(raw_weight).replace(',', '.'))
    return float(m.group(1)) if m else None


def parse_refresh_rate(raw_tech: str) -> Optional[int]:
    if not raw_tech:
        return None
    m = re.search(r'(\d{2,3})\s*Hz', raw_tech, re.I)
    return int(m.group(1)) if m else None


def parse_os(raw_os: str) -> str:
    if not raw_os:
        return "Windows"
    raw = raw_os.lower()
    if "mac" in raw or "macos" in raw:
        return "macOS"
    if "linux" in raw or "ubuntu" in raw:
        return "Linux"
    if "dos" in raw or "no os" in raw:
        return "No OS"
    return "Windows"


def parse_storage_type(raw_storage: str) -> str:
    """Extract storage technology (NVMe PCIe SSD vs SATA SSD)."""
    if not raw_storage:
        return ""
    if 'nvme' in raw_storage.lower():
        return "SSD M.2 NVMe PCIe"
    if 'pcie' in raw_storage.lower():
        return "SSD PCIe"
    if 'ssd' in raw_storage.lower():
        return "SSD"
    return ""


def parse_charger_w(raw_battery: str) -> Optional[int]:
    """Extract charger power in Watts from Pin string (e.g., '65W Round Tip', '100W Type-C')."""
    if not raw_battery:
        return None
    m = re.search(r'(\d{2,3})\s*W\b', raw_battery, re.I)
    return int(m.group(1)) if m else None


def parse_color_gamut(raw_screen: str) -> str:
    """Extract color gamut coverage (e.g., '100% sRGB', '45% NTSC', '100% DCI-P3')."""
    if not raw_screen:
        return ""
    matches = re.findall(r'(\d{2,3}%\s*(?:sRGB|NTSC|DCI-P3|Adobe\s*RGB))', raw_screen, re.I)
    return ", ".join(matches) if matches else ""


def parse_cpu_ghz(raw_cpu: str) -> tuple[Optional[float], Optional[float]]:
    """Extract (cpu_base_ghz, cpu_boost_ghz)."""
    base_ghz, boost_ghz = None, None
    if not raw_cpu:
        return base_ghz, boost_ghz
        
    m_mhz = re.search(r'cơ bản[:\s]*(\d+)\s*MHz', raw_cpu, re.I)
    if m_mhz:
        base_ghz = round(float(m_mhz.group(1)) / 1000.0, 2)
        
    m_turbo = re.search(r'(?:turbo|tối đa)[:\s]*(\d+(?:\.\d+)?)\s*GHz', raw_cpu, re.I)
    if m_turbo:
        boost_ghz = float(m_turbo.group(1))
        
    m_range = re.search(r'(\d+(?:\.\d+)?)\s*(?:GHz)?\s*[-–]\s*(\d+(?:\.\d+)?)\s*GHz', raw_cpu, re.I)
    if m_range:
        b1, b2 = float(m_range.group(1)), float(m_range.group(2))
        base_ghz = min(b1, b2)
        boost_ghz = max(b1, b2)
        
    if not boost_ghz:
        m_single = re.search(r'(\d+(?:\.\d+)?)\s*GHz', raw_cpu, re.I)
        if m_single:
            boost_ghz = float(m_single.group(1))
            
    return base_ghz, boost_ghz


def parse_battery_cells(raw_pin: str) -> Optional[int]:
    """Extract battery cell count (e.g. '3-cell', '4 cell')."""
    if not raw_pin:
        return None
    m = re.search(r'(\d+)\s*[- ]?cell', raw_pin, re.I)
    return int(m.group(1)) if m else None


def parse_rich_ports(raw_ports: str, raw_pin: str = "") -> dict:
    """Extract rich connectivity fields."""
    if not raw_ports and not raw_pin:
        return {
            'lan_present': 'false',
            'audio_jack_present': 'false',
            'hdmi_version': '',
            'thunderbolt_present': 'false',
            'sd_card_slot_present': 'false',
            'type_c_charging': 'false',
        }
    
    combined = ((raw_ports or '') + ' ' + (raw_pin or '')).lower()
    lan = 'true' if re.search(r'\b(?:lan|rj45|rj-45|ethernet)\b', combined, re.I) else 'false'
    audio = 'true' if re.search(r'3\.5|tai nghe|headset|audio', combined, re.I) else 'false'
    
    m_h = re.search(r'HDMI\s*([12]\.\d[a-z]?)', raw_ports or '', re.I)
    hdmi_ver = m_h.group(1) if m_h else ''
    
    tb = 'true' if re.search(r'thunderbolt|usb4', combined, re.I) else 'false'
    sd = 'true' if re.search(r'\b(?:micro\s*sd|khe\s*sd|khe\s*thẻ|sd\s*card)\b', combined, re.I) else 'false'
    type_c_charge = 'true' if (
        'type-c' in combined or 'typec' in combined 
        or 'thunderbolt' in combined or 'usb4' in combined or 'power delivery' in combined
        or ('usb-c' in combined and ('sạc' in combined or 'charge' in combined or 'pd' in combined or 'dc-in' in combined or 'adapter' in combined or 'nguồn' in combined))
    ) else 'false'
    
    return {
        'lan_present': lan,
        'audio_jack_present': audio,
        'hdmi_version': hdmi_ver,
        'thunderbolt_present': tb,
        'sd_card_slot_present': sd,
        'type_c_charging': type_c_charge,
    }


def load_benchmarks() -> dict:
    benchmarks = {}
    if not BENCHMARKS_CSV.exists():
        return benchmarks
    with open(BENCHMARKS_CSV, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for r in reader:
            key = (r['component_type'], r['component_name'], r['benchmark_name'])
            score = float(r['score']) if r['score'] else None
            benchmarks[key] = {
                'score': score,
                'match_level': r['match_level'],
                'source_url': r.get('source_url', ''),
                'note': r['note'],
            }
    return benchmarks


def build_standardized_catalog():
    with open(RAW_JSON, 'r', encoding='utf-8') as f:
        raw_items = json.load(f)

    benchmarks = load_benchmarks()

    standardized = []
    for item in raw_items:
        specs = item.get('specs_raw', {})
        
        # CPU
        cpu_norm = normalize_cpu(specs.get('Loại CPU', ''))
        # GPU
        gpu_norm, gpu_type, vram = normalize_gpu(specs.get('Loại card đồ họa', ''))
        # RAM & Storage
        ram_gb = parse_ram(specs.get('Dung lượng RAM', ''))
        storage_gb = parse_storage(specs.get('Ổ cứng', ''))
        # Screen
        screen_inch = parse_screen_inch(specs.get('Kích thước màn hình', ''))
        screen_w, screen_h = parse_resolution(specs.get('Độ phân giải màn hình', ''))
        panel = parse_panel_type(specs.get('Công nghệ màn hình', ''))
        hz = item.get('refresh_rate_hz') or parse_refresh_rate(specs.get('Công nghệ màn hình', ''))
        # OS & Weight
        os_name = parse_os(specs.get('Hệ điều hành khi ra mắt') or specs.get('Hệ điều hành') or '')
        weight = parse_weight(item.get('weight_raw'))
        
        # CPU Benchmark lookup
        cpu_bench_key = ("CPU", cpu_norm, "Geekbench 6 Multi-Core")
        cpu_bench = benchmarks.get(cpu_bench_key, {})
        cpu_score = cpu_bench.get('score')
        cpu_match = cpu_bench.get('match_level', 'unavailable')
        
        # CPU Single-core lookup
        cpu_sc_key = ("CPU", cpu_norm, "Geekbench 6 Single-Core")
        cpu_sc_bench = benchmarks.get(cpu_sc_key, {})
        cpu_sc_score = cpu_sc_bench.get('score')
        cpu_bench_source = cpu_bench.get('source_url', '')
        
        # GPU Benchmark lookup
        gpu_score = None
        gpu_match = 'unavailable'
        gpu_bench_source = ''
        if gpu_type == 'discrete':
            gpu_bench_key = ("GPU", gpu_norm, "3DMark Time Spy Graphics")
            gpu_bench = benchmarks.get(gpu_bench_key, {})
            gpu_score = gpu_bench.get('score')
            gpu_match = gpu_bench.get('match_level', 'unavailable')
            gpu_bench_source = gpu_bench.get('source_url', '')

        # Rich spec parsing from specs_raw
        cores, threads = parse_cpu_cores_threads(specs.get('Loại CPU', ''))
        base_ghz, boost_ghz = parse_cpu_ghz(specs.get('Loại CPU', ''))
        battery_wh = parse_battery_wh(specs.get('Pin', ''))
        battery_cells = parse_battery_cells(specs.get('Pin', ''))
        charger_w = parse_charger_w(specs.get('Pin', ''))
        brightness_nits = parse_brightness_nits(specs.get('Công nghệ màn hình', ''))
        color_gamut = parse_color_gamut(specs.get('Công nghệ màn hình', ''))
        usb_a, usb_c, hdmi = parse_ports(specs.get('Cổng giao tiếp', ''))
        rich_ports = parse_rich_ports(specs.get('Cổng giao tiếp', ''), specs.get('Pin', ''))
        slots, slots_free, max_ram = parse_ram_slots(specs.get('Số khe ram', ''), ram_gb)
        storage_type = parse_storage_type(specs.get('Ổ cứng', ''))

        # AI TOPS
        raw_ai = specs.get('Chip AI', '')
        m_tops = re.search(r'(\d+)\s*TOPS', raw_ai, re.I)
        npu_tops = int(m_tops.group(1)) if m_tops else (raw_ai if raw_ai else '')

        # Gaming eligibility
        is_gaming = 'true' if (gpu_type == 'discrete' and os_name == 'Windows' and (hz or 0) >= 144) else 'false'

        standardized.append({
            'source': 'cellphones',
            'source_product_id': item['source_product_id'],
            'product_name_raw': item['product_name_raw'],
            'source_url': item['source_url'],
            'collected_at': item.get('scraped_at', ''),
            'currency': 'VND',
            'listed_price_vnd': item['listed_price_vnd'],
            'sale_price_vnd': item['sale_price_vnd'],
            'special_price_vnd': '',
            'cpu_name_normalized': cpu_norm,
            'cpu_cores': cores if cores is not None else '',
            'cpu_threads': threads if threads is not None else '',
            'cpu_base_ghz': base_ghz if base_ghz is not None else '',
            'cpu_boost_ghz': boost_ghz if boost_ghz is not None else '',
            'gpu_name_normalized': gpu_norm,
            'gpu_type': gpu_type,
            'gpu_vram_gb': vram,
            'ram_gb': ram_gb,
            'ram_type': specs.get('Loại RAM', ''),
            'ram_slots': slots if slots is not None else '',
            'ram_slots_free': slots_free if slots_free is not None else '',
            'max_ram_gb': max_ram if max_ram is not None else '',
            'storage_total_gb': storage_gb,
            'storage_primary_type': storage_type,
            'screen_size_inch': screen_inch if screen_inch is not None else '',
            'screen_width_px': screen_w if screen_w is not None else '',
            'screen_height_px': screen_h if screen_h is not None else '',
            'panel_type': panel if panel is not None else '',
            'refresh_rate_hz': hz if hz is not None else '',
            'brightness_nits': brightness_nits if brightness_nits is not None else '',
            'color_gamut_raw': color_gamut,
            'battery_capacity_wh': battery_wh if battery_wh is not None else '',
            'battery_cells': battery_cells if battery_cells is not None else '',
            'charger_w': charger_w if charger_w is not None else '',
            'weight_kg': weight if weight is not None else '',
            'thickness_mm': '',
            'dimensions_raw': '',
            'material_raw': '',
            'color_raw': '',
            'usb_a_count': usb_a,
            'usb_c_count': usb_c,
            'hdmi_present': hdmi,
            'hdmi_version': rich_ports['hdmi_version'],
            'lan_present': rich_ports['lan_present'],
            'audio_jack_present': rich_ports['audio_jack_present'],
            'wifi_raw': '',
            'bluetooth_raw': '',
            'webcam_raw': '',
            'os_name': os_name,
            'warranty_months': item.get('warranty_months', 24),
            'cpu_benchmark_multi_core': cpu_score if cpu_score is not None else '',
            'cpu_benchmark_single_core': cpu_sc_score if cpu_sc_score is not None else '',
            'cpu_benchmark_source_url': cpu_bench_source,
            'cpu_benchmark_match_level': cpu_match,
            'gpu_benchmark_time_spy': gpu_score if gpu_score is not None else '',
            'gpu_benchmark_source_url': gpu_bench_source,
            'gpu_benchmark_match_level': gpu_match,
            'is_gaming_eligible': is_gaming,
            'image_url': item.get('image_url_local') or '/images/laptop_fallback.png',
            'npu_tops': npu_tops,
            'thunderbolt_present': rich_ports['thunderbolt_present'],
            'sd_card_slot_present': rich_ports['sd_card_slot_present'],
            'type_c_charging': rich_ports['type_c_charging'],
        })

    # Save to CSV
    if standardized:
        keys = list(standardized[0].keys())
        with open(OUT_CSV, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(standardized)

    print(f"Standardized {len(standardized)} laptops saved to {OUT_CSV}")
    return standardized


if __name__ == "__main__":
    build_standardized_catalog()
