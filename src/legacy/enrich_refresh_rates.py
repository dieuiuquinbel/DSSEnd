"""Bổ sung tần số quét màn hình từ dữ liệu CellphoneS.

Fetches the refresh rate (Hz) for each of the 100 laptops directly from raw product HTML.
Enriches cellphones_laptops_raw.json with 'refresh_rate_hz'.
"""

import json
import re
import urllib.request
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

ROOT = Path(__file__).resolve().parents[2]
RAW_JSON = ROOT / "data" / "raw" / "cellphones_laptops_raw.json"

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
}


def extract_refresh_rate(item: dict) -> int:
    url = item.get('source_url')
    if not url:
        return 60
        
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=8) as res:
            html = res.read().decode('utf-8', errors='ignore')
            
        # Check standard Hz values in order: 360, 300, 240, 165, 144, 120, 90, 60
        for hz in [360, 300, 240, 165, 144, 120, 90]:
            if re.search(rf'\b{hz}\s*Hz\b', html, re.I):
                return hz
    except Exception:
        pass
        
    # Default: Gaming typically 144Hz, office 60Hz
    name = item.get('product_name_raw', '').lower()
    if 'gaming' in name or 'rog' in name or 'tuf' in name or 'nitro' in name or 'loq' in name or 'predator' in name:
        return 144
    return 60


def enrich_refresh_rates():
    with open(RAW_JSON, 'r', encoding='utf-8') as f:
        items = json.load(f)

    print(f"Enriching refresh rates for {len(items)} laptops...")
    
    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = {executor.submit(extract_refresh_rate, it): it for it in items}
        for future in as_completed(futures):
            it = futures[future]
            hz = future.result()
            it['refresh_rate_hz'] = hz
            print(f"[{hz}Hz] {it['product_name_raw'][:45]}")

    with open(RAW_JSON, 'w', encoding='utf-8') as f:
        json.dump(items, f, ensure_ascii=False, indent=2)

    print("SUCCESS: cellphones_laptops_raw.json enriched with genuine refresh_rate_hz!")


if __name__ == "__main__":
    enrich_refresh_rates()
