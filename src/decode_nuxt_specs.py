"""Tiện ích debug: phân tích cấu trúc window.__NUXT__ IIFE từ CellphoneS.

Script dùng một lần để khảo sát format dữ liệu, không phải module production.
Chạy: python src/decode_nuxt_specs.py
"""

import urllib.request
import re
import json

url = 'https://cellphones.com.vn/laptop-asus-tuf-gaming-f15-fx507zc4-hn074w.html'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'})
with urllib.request.urlopen(req, timeout=10) as r:
    html = r.read().decode('utf-8', errors='ignore')

m = re.search(r'<script>\s*window\.__NUXT__\s*=\s*\(function\((.*?)\)\{return\s*(.*?)\}\((.*?)\)\);\s*</script>', html, re.DOTALL)
if m:
    params_str = m.group(1)
    body_str = m.group(2)
    args_str = m.group(3)
    
    params = [p.strip() for p in params_str.split(',')]
    print(f"Total params: {len(params)}")
    
    # Parse args (they are JSON-like comma-separated literals: strings, numbers, booleans, null)
    # Let's inspect the first 20 and last 20 args
    print(f"Args string length: {len(args_str)}")
    print("Args head:", args_str[:200])
    print("Args tail:", args_str[-200:])
else:
    print("IIFE pattern did not match directly, let's inspect the start and end of window.__NUXT__:")
    m2 = re.search(r'<script>\s*window\.__NUXT__\s*=\s*(.*?);\s*</script>', html, re.DOTALL)
    if m2:
        txt = m2.group(1).strip()
        print("Start:", txt[:150])
        print("End:", txt[-150:])
