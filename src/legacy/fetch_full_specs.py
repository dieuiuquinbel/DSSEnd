"""Lấy thông số đầy đủ cho sản phẩm pilot từ nguồn FPT Shop chính thức.

Strict rule: No hallucination, no fabricated values. Keep exact values as published by FPT Shop.
"""

import glob
import json
import urllib.parse
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = ROOT / "data" / "raw" / "fpt_shop"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json",
    "Origin": "https://fptshop.com.vn",
    "order-channel": "1",
}


def fetch_product_specs(source_url: str) -> dict:
    slug = source_url.replace("https://fptshop.com.vn/", "").strip("/")
    quoted_slug = urllib.parse.quote(slug)
    url = f"https://papi.fptshop.com.vn/gw/v1/public/bff-before-order/product/attribute?slug={quoted_slug}"
    
    headers = dict(HEADERS)
    headers["Referer"] = source_url
    
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=10) as resp:
        data = json.loads(resp.read().decode("utf-8"))
        
    items = data.get("data", {}).get("attributeItem", [])
    specs = {}
    for group in items:
        for attr in group.get("attributes", []):
            name = attr.get("displayName", "").strip()
            if not name:
                continue
            val = attr.get("value")
            display_str = ""
            if isinstance(val, bool):
                display_str = "Có" if val else "Không"
            elif isinstance(val, (int, float)):
                display_str = str(val)
            elif isinstance(val, str):
                display_str = val.strip()
            elif isinstance(val, list):
                vals = []
                for item in val:
                    if isinstance(item, str) and item.strip():
                        vals.append(item.strip())
                    elif isinstance(item, dict):
                        v = item.get("displayValue") or str(item.get("value", ""))
                        if v.strip():
                            vals.append(v.strip())
                display_str = "; ".join(vals)
            elif isinstance(val, dict):
                display_str = (val.get("displayValue") or str(val.get("value", ""))).strip()
            
            unit = (attr.get("unit") or "").strip()
            if unit and display_str and not display_str.endswith(unit):
                display_str = f"{display_str} {unit}"
                
            if display_str:
                specs[name] = display_str

    return specs


def update_raw_files():
    for path in sorted(RAW_DIR.glob("*.json")):
        raw = json.loads(path.read_text(encoding="utf-8"))
        source_url = raw.get("source_url", "")
        if not source_url:
            continue
        
        print(f"Fetching full specs for {path.name}...")
        api_specs = fetch_product_specs(source_url)
        
        # Merge api_specs into existing specifications (preserving any specific existing keys)
        current_specs = raw.get("specifications", {})
        # Update with official API specs
        current_specs.update(api_specs)
        raw["specifications"] = current_specs
        
        path.write_text(json.dumps(raw, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"  -> Saved {len(current_specs)} spec fields to {path.name}")


if __name__ == "__main__":
    update_raw_files()
