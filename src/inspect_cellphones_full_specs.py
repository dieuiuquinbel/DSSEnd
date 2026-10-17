"""Tiện ích debug: kiểm tra các cặp key-value HTML và JSON-LD từ trang sản phẩm CellphoneS.

Script dùng một lần để khảo sát DOM structure, không phải module production.
Chạy: python src/inspect_cellphones_full_specs.py
"""

import urllib.request
import re
from bs4 import BeautifulSoup

url = 'https://cellphones.com.vn/laptop-acer-aspire-lite-14-al14-52m-52uu.html'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'})
with urllib.request.urlopen(req, timeout=10) as r:
    html = r.read().decode('utf-8', errors='ignore')

soup = BeautifulSoup(html, 'html.parser')

# Check what modal technical divs exist
modal = soup.find('div', id=re.compile(r'modal.*technical|technical', re.I))
if not modal:
    modal = soup.find(class_=re.compile(r'modal.*technical', re.I))

print("Modal found:", bool(modal))
if modal:
    for li in modal.find_all(['li', 'tr', 'div']):
        t = li.get_text(" : ", strip=True)
        if " : " in t and len(t) < 150:
            print("  Modal item:", t)

# Check all pairs in the document
print("\n--- ALL KEY-VALUE PAIRS FOUND IN HTML ---")
pairs = []
for el in soup.find_all(['li', 'tr']):
    t = el.get_text(" : ", strip=True)
    if " : " in t and len(t) < 200:
        parts = t.split(" : ", 1)
        k, v = parts[0].strip(), parts[1].strip()
        if len(k) > 2 and len(v) > 0 and len(k) < 40:
            pairs.append((k, v))

print(f"Total pairs found: {len(pairs)}")
for k, v in pairs[:30]:
    print(f"  [{k}] -> {v}")

# Check if there is an API endpoint or __NUXT__ or json-ld
print("\n--- JSON-LD SCRIPTS ---")
for s in soup.find_all('script', type='application/ld+json'):
    txt = s.string or ""
    if "PropertyValue" in txt:
        props = re.findall(r'\{"@type":"PropertyValue","name":"([^"]+)","value":"([^"]+)"\}', txt)
        print(f"JSON-LD PropertyValues count: {len(props)}")
        for pk, pv in props:
            print(f"  JSON-LD: [{pk}] -> {pv}")
