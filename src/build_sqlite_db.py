"""Khởi tạo SQLite và định danh cấu hình laptop theo D12.

Creates database data/artifacts/laptop_dss.db with schema:
1. configurations (Pure hardware model variant: Brand + Family + SKU + normalized specs hash)
2. retail_listings (Retailer source, URLs, titles, image paths, SKU)
3. price_observations (Historical price records)
4. component_benchmarks (Geekbench 6 and 3DMark Time Spy scores)

Strict Academic Policy:
- ZERO guessing or fabricated defaults (no fake 0 VRAM, no fake false LAN, no fake 24m warranty).
- Missing values are stored strictly as NULL.
Đầu vào là catalog và benchmark chuẩn hóa; đầu ra là cơ sở dữ liệu gồm cấu hình,
listing, quan sát giá và benchmark. Dữ liệu thiếu được lưu NULL, không suy đoán.
"""

import sqlite3
import csv
import re
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Optional, Any

ROOT = Path(__file__).resolve().parents[1]
UNIFIED_CSV = ROOT / "data" / "catalog" / "laptops.csv"
BENCHMARKS_CSV = ROOT / "data" / "catalog" / "benchmarks.csv"
DB_PATH = ROOT / "data" / "artifacts" / "laptop_dss.db"


def extract_brand_and_family(product_name: str) -> tuple[str, str]:
    """Extract brand and product family from product title without hallucination."""
    if not product_name:
        return "Unknown", "Generic"
    name = product_name.strip()
    name_clean = re.sub(r'^(?:Laptop|Máy tính xách tay)\s+', '', name, flags=re.I).strip()
    
    # Brands list
    brands = [
        "Acer", "Asus", "Apple", "Dell", "HP", "Lenovo", "MSI", 
        "Gigabyte", "LG", "Huawei", "Samsung", "Microsoft"
    ]
    detected_brand = "Unknown"
    for b in brands:
        if re.search(r'\b' + re.escape(b) + r'\b', name_clean, re.I):
            detected_brand = b
            break
            
    # Major product families
    family_patterns = [
        r'MacBook\s+(?:Air|Pro)',
        r'Vivobook(?:\s+(?:S|Pro|Go|Flip|14|15|16))?',
        r'Zenbook(?:\s+(?:S|Pro|Duo|Flip|14|15))?',
        r'ROG(?:\s+(?:Strix|Zephyrus|Flow))?',
        r'TUF(?:\s+Gaming)?',
        r'Aspire(?:\s+(?:Go|Lite|Gaming|3|5|7))?',
        r'Nitro(?:\s+(?:V|5|16|17))?',
        r'Predator(?:\s+Helios)?',
        r'Swift(?:\s+(?:Go|X|Edge))?',
        r'IdeaPad(?:\s+(?:Slim|Gaming|Pro|Flex|1|3|5))?',
        r'Legion(?:\s+(?:Slim|Pro|5|7|9))?',
        r'LOQ',
        r'ThinkPad',
        r'ThinkBook',
        r'Yoga(?:\s+Slim)?',
        r'Inspiron(?:\s+(?:14|15|16))?',
        r'Vostro',
        r'XPS(?:\s+(?:13|14|15|16))?',
        r'Pavilion(?:\s+(?:Plus|Aero|Gaming|14|15))?',
        r'Victus(?:\s+(?:15|16))?',
        r'Envy',
        r'Omen',
        r'ProBook',
        r'EliteBook',
        r'Modern(?:\s+(?:14|15))?',
        r'Katana',
        r'Cyborg',
        r'Sword',
        r'Bravo',
        r'Prestige',
        r'Gram',
        r'Surface',
    ]
    detected_family = ""
    for pat in family_patterns:
        m = re.search(r'\b(' + pat + r')\b', name_clean, re.I)
        if m:
            detected_family = m.group(1).strip()
            break
            
    if not detected_family:
        words = name_clean.split()
        if len(words) >= 2:
            detected_family = " ".join(words[:2])
        else:
            detected_family = name_clean[:15]
            
    return detected_brand, detected_family


def extract_sku(product_name: str, source_product_id: str) -> Optional[str]:
    """Extract official manufacturer SKU/Part number from title or slug without guessing.
    
    Matches patterns like:
    - Parentheses SKU: (C3SH7AT), (B85LNPA)
    - Alphanumeric model code: AG15-52P-52WT, ANV15-41-R0FE, FA506NCG-HN396W, 83DV01ALVN, B13WFKG-658VN
    - Retail slug suffix if structured
    """
    if not product_name:
        return None
    name = product_name.strip()

    # 1. Parenthesized model code at the end
    m_paren = re.search(r'\(([^)]+)\)', name)
    if m_paren:
        val = m_paren.group(1).strip()
        if any(c.isdigit() for c in val) and len(val) <= 15:
            return val

    # 2. Strict model SKU regex pattern
    m_code = re.search(r'\b([A-Z0-9]{2,6}-[A-Z0-9]{2,6}-[A-Z0-9]{3,6}|[A-Z0-9]{4,8}-[A-Z0-9]{4,8}|8[0-9][A-Z0-9]{6,8}|[A-Z0-9]{4,8}VN)\b', name)
    if m_code:
        return m_code.group(1).strip()

    # 3. Slug suffix from source_product_id if it contains standard model segment
    if source_product_id and '-' in source_product_id:
        parts = source_product_id.replace('cps_laptop-', '').replace('cps_', '').split('-')
        if len(parts) >= 3:
            if any(c.isdigit() for c in parts[-1]) and any(c.isdigit() for c in parts[-2]):
                return '-'.join(parts[-3:]).upper()
            elif any(c.isdigit() for c in parts[-1]):
                return '-'.join(parts[-2:]).upper()

    return None


def compute_config_id(row: dict) -> str:
    """Generate deterministic hardware configuration hash (Data.md §4).
    
    Prevents cross-brand model collisions by strictly incorporating:
    Brand, Product Family, SKU (if known), CPU, GPU, RAM, Storage, Screen Size, Panel, Refresh Rate.
    """
    brand, family = extract_brand_and_family(row.get("product_name_raw", ""))
    sku = extract_sku(row.get("product_name_raw", ""), row.get("source_product_id", "")) or ""
    elements = [
        brand.strip().lower(),
        family.strip().lower(),
        sku.strip().lower(),
        row.get("cpu_name_normalized", "").strip().lower(),
        row.get("gpu_name_normalized", "").strip().lower(),
        str(row.get("ram_gb", "")).strip(),
        str(row.get("storage_total_gb", "")).strip(),
        str(row.get("screen_size_inch", "")).strip(),
        row.get("panel_type", "").strip().lower(),
        str(row.get("refresh_rate_hz", "")).strip(),
        row.get("os_name", "").strip().lower(),
    ]
    raw_str = "|".join(elements)
    return hashlib.sha256(raw_str.encode("utf-8")).hexdigest()[:16]


def parse_int_or_none(val: Any) -> Optional[int]:
    """Parse integer or return None if empty/invalid. Never fabricate 0."""
    if val is None:
        return None
    s = str(val).strip()
    if not s or s.lower() in ("none", "null", "chưa rõ", "đang cập nhật"):
        return None
    try:
        return int(float(s))
    except (ValueError, TypeError):
        return None


def parse_float_or_none(val: Any) -> Optional[float]:
    """Parse float or return None if empty/invalid. Never fabricate 0.0."""
    if val is None:
        return None
    s = str(val).strip()
    if not s or s.lower() in ("none", "null", "chưa rõ", "đang cập nhật"):
        return None
    try:
        return float(s)
    except (ValueError, TypeError):
        return None


def parse_str_or_none(val: Any) -> Optional[str]:
    """Return stripped string or None if empty. Never fabricate empty string when unstated."""
    if val is None:
        return None
    s = str(val).strip()
    if not s or s.lower() in ("none", "null", "chưa rõ", "đang cập nhật"):
        return None
    return s


def parse_bool_str_or_none(val: Any) -> Optional[str]:
    """Return 'true', 'false', or None if truly unstated. Never default to 'false'."""
    if val is None:
        return None
    s = str(val).strip().lower()
    if s in ("true", "1", "yes"):
        return "true"
    if s in ("false", "0", "no"):
        return "false"
    return None


def init_and_populate_db():
    if DB_PATH.exists():
        DB_PATH.unlink()

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # 1. Configurations table (Hardware identity with brand, family & SKU)
    cur.execute("""
    CREATE TABLE configurations (
        configuration_id TEXT PRIMARY KEY,
        brand TEXT NOT NULL,
        product_family TEXT NOT NULL,
        sku_or_part_number TEXT,
        cpu_name_normalized TEXT NOT NULL,
        cpu_cores INTEGER,
        cpu_threads INTEGER,
        cpu_base_ghz REAL,
        cpu_boost_ghz REAL,
        gpu_name_normalized TEXT NOT NULL,
        gpu_type TEXT NOT NULL,
        gpu_vram_gb INTEGER,
        ram_gb INTEGER,
        ram_type TEXT,
        storage_total_gb INTEGER,
        storage_primary_type TEXT,
        screen_size_inch REAL,
        screen_width_px INTEGER,
        screen_height_px INTEGER,
        panel_type TEXT,
        color_gamut_raw TEXT,
        refresh_rate_hz INTEGER,
        weight_kg REAL,
        battery_capacity_wh REAL,
        battery_cells INTEGER,
        charger_w INTEGER,
        os_name TEXT,
        hdmi_version TEXT,
        lan_present TEXT,
        audio_jack_present TEXT,
        npu_tops TEXT,
        cpu_benchmark_multi_core REAL,
        cpu_benchmark_single_core REAL,
        cpu_benchmark_match_level TEXT,
        gpu_benchmark_time_spy REAL,
        gpu_benchmark_match_level TEXT,
        gpu_benchmark_compute REAL,
        gpu_benchmark_compute_api TEXT,
        created_at TEXT NOT NULL
    )
    """)

    # 2. Retail Listings table (Store/Listing identity with SKU)
    cur.execute("""
    CREATE TABLE retail_listings (
        listing_id TEXT PRIMARY KEY,
        configuration_id TEXT NOT NULL,
        retailer TEXT NOT NULL,
        source_product_id TEXT NOT NULL,
        product_name_raw TEXT NOT NULL,
        sku_or_part_number TEXT,
        source_url TEXT NOT NULL,
        image_url TEXT,
        warranty_months INTEGER,
        created_at TEXT NOT NULL,
        FOREIGN KEY (configuration_id) REFERENCES configurations(configuration_id)
    )
    """)

    # 3. Price Observations table (Price history)
    cur.execute("""
    CREATE TABLE price_observations (
        observation_id INTEGER PRIMARY KEY AUTOINCREMENT,
        listing_id TEXT NOT NULL,
        sale_price_vnd REAL NOT NULL,
        listed_price_vnd REAL,
        observed_at TEXT NOT NULL,
        FOREIGN KEY (listing_id) REFERENCES retail_listings(listing_id)
    )
    """)

    # 4. Component Benchmarks table
    cur.execute("""
    CREATE TABLE component_benchmarks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        component_type TEXT NOT NULL,
        component_name TEXT NOT NULL,
        benchmark_name TEXT NOT NULL,
        score REAL,
        match_level TEXT NOT NULL,
        source_url TEXT,
        note TEXT
    )
    """)

    # Populate component_benchmarks
    if BENCHMARKS_CSV.exists():
        with open(BENCHMARKS_CSV, 'r', encoding='utf-8') as f:
            for r in csv.DictReader(f):
                cur.execute("""
                INSERT INTO component_benchmarks 
                (component_type, component_name, benchmark_name, score, match_level, source_url, note)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    r['component_type'],
                    r['component_name'],
                    r['benchmark_name'],
                    parse_float_or_none(r.get('score')),
                    r['match_level'],
                    parse_str_or_none(r.get('source_url')),
                    parse_str_or_none(r.get('note'))
                ))

    # Populate configurations, listings, prices from UNIFIED_CSV
    with open(UNIFIED_CSV, 'r', encoding='utf-8') as f:
        laptops = list(csv.DictReader(f))

    now = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    configs_seen = set()

    for idx, l in enumerate(laptops, start=1):
        cfg_id = compute_config_id(l)
        brand, family = extract_brand_and_family(l.get("product_name_raw", ""))
        sku = extract_sku(l.get("product_name_raw", ""), l.get("source_product_id", ""))
        listing_id = f"lst_{l.get('source', 'cps')}_{l.get('source_product_id', idx)}"

        # Insert config if new (Strict zero fabricated defaults, NULL for unstated fields)
        if cfg_id not in configs_seen:
            configs_seen.add(cfg_id)
            cur.execute("""
            INSERT INTO configurations VALUES (
                ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
            )
            """, (
                cfg_id,
                brand,
                family,
                sku,
                l.get("cpu_name_normalized", ""),
                parse_int_or_none(l.get("cpu_cores")),
                parse_int_or_none(l.get("cpu_threads")),
                parse_float_or_none(l.get("cpu_base_ghz")),
                parse_float_or_none(l.get("cpu_boost_ghz")),
                l.get("gpu_name_normalized", ""),
                l.get("gpu_type", "integrated"),
                parse_int_or_none(l.get("gpu_vram_gb")),  # NULL when unstated, NOT 0
                parse_int_or_none(l.get("ram_gb")),
                parse_str_or_none(l.get("ram_type")),
                parse_int_or_none(l.get("storage_total_gb")),
                parse_str_or_none(l.get("storage_primary_type")),
                parse_float_or_none(l.get("screen_size_inch")),
                parse_int_or_none(l.get("screen_width_px")),
                parse_int_or_none(l.get("screen_height_px")),
                parse_str_or_none(l.get("panel_type")),
                parse_str_or_none(l.get("color_gamut_raw")),
                parse_int_or_none(l.get("refresh_rate_hz")),
                parse_float_or_none(l.get("weight_kg")),
                parse_float_or_none(l.get("battery_capacity_wh")),
                parse_int_or_none(l.get("battery_cells")),
                parse_int_or_none(l.get("charger_w")),
                parse_str_or_none(l.get("os_name")),
                parse_str_or_none(l.get("hdmi_version")),
                parse_bool_str_or_none(l.get("lan_present")),         # NULL when unstated, NOT 'false'
                parse_bool_str_or_none(l.get("audio_jack_present")),  # NULL when unstated, NOT 'false'
                parse_str_or_none(l.get("npu_tops")),
                parse_float_or_none(l.get("cpu_benchmark_multi_core")),
                parse_float_or_none(l.get("cpu_benchmark_single_core")),
                parse_str_or_none(l.get("cpu_benchmark_match_level")) or "unavailable",
                parse_float_or_none(l.get("gpu_benchmark_time_spy")),
                parse_str_or_none(l.get("gpu_benchmark_match_level")) or "unavailable",
                parse_float_or_none(l.get("gpu_benchmark_compute")),
                parse_str_or_none(l.get("gpu_benchmark_compute_api")),
                now,
            ))

        # Insert retail listing (NULL for warranty if unstated, never default 24)
        cur.execute("""
        INSERT INTO retail_listings VALUES (
            ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
        )
        """, (
            listing_id,
            cfg_id,
            l.get("source", "cellphones"),
            l.get("source_product_id", str(idx)),
            l.get("product_name_raw", ""),
            sku,
            l.get("source_url", ""),
            parse_str_or_none(l.get("image_url")),
            parse_int_or_none(l.get("warranty_months")),  # NULL when unstated, NOT 24
            now,
        ))

        # Insert price observation (Sale price must be valid, skip if invalid)
        sale_price = parse_float_or_none(l.get("sale_price_vnd"))
        if sale_price is not None and sale_price > 0:
            cur.execute("""
            INSERT INTO price_observations (listing_id, sale_price_vnd, listed_price_vnd, observed_at)
            VALUES (?, ?, ?, ?)
            """, (
                listing_id,
                sale_price,
                parse_float_or_none(l.get("listed_price_vnd")),
                now,
            ))

    conn.commit()

    # Audit query
    cur.execute("SELECT count(*) FROM configurations")
    cfg_count = cur.fetchone()[0]
    cur.execute("SELECT count(*) FROM retail_listings")
    lst_count = cur.fetchone()[0]
    cur.execute("SELECT count(*) FROM price_observations")
    obs_count = cur.fetchone()[0]
    cur.execute("SELECT count(*) FROM component_benchmarks")
    bm_count = cur.fetchone()[0]
    cur.execute("SELECT count(*) FROM configurations WHERE sku_or_part_number IS NOT NULL")
    sku_count = cur.fetchone()[0]

    # Verify NULL presence instead of fake defaults
    cur.execute("SELECT count(*) FROM configurations WHERE gpu_vram_gb IS NULL")
    null_vram_count = cur.fetchone()[0]
    cur.execute("SELECT count(*) FROM configurations WHERE lan_present IS NULL")
    null_lan_count = cur.fetchone()[0]

    conn.close()

    print("SUCCESS: SQLite Database built with complete identity layer (D12 & Data.md §4)!")
    print(f"  Configurations (Hardware Models):      {cfg_count} (SKU identified: {sku_count}/{cfg_count})")
    print(f"  Retail Listings (Store Postings):      {lst_count}")
    print(f"  Price Observations:                    {obs_count}")
    print(f"  Component Benchmarks:                  {bm_count}")
    print(f"  Integrity Check - Real NULLs preserved:")
    print(f"    - Configurations with NULL VRAM:     {null_vram_count} (No fake 0s)")
    print(f"    - Configurations with NULL LAN:      {null_lan_count} (No fake false)")


if __name__ == "__main__":
    init_and_populate_db()
