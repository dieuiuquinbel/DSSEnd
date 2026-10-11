"""Thu thập URL catalog theo hãng phục vụ pipeline dữ liệu."""

import urllib.request
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
URL_FILE = ROOT / "data" / "raw" / "cellphones_target_urls.txt"

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7',
}

def harvest_comprehensive_urls():
    categories = [
        # MacBook categories
        'https://cellphones.com.vn/laptop/mac.html',
        'https://cellphones.com.vn/laptop/mac/macbook-air.html',
        'https://cellphones.com.vn/laptop/mac/macbook-pro.html',
        # Lenovo
        'https://cellphones.com.vn/laptop/lenovo.html',
        'https://cellphones.com.vn/laptop/lenovo/thinkpad.html',
        'https://cellphones.com.vn/laptop/lenovo/loq.html',
        'https://cellphones.com.vn/laptop/lenovo/legion.html',
        # MSI
        'https://cellphones.com.vn/laptop/msi.html',
        'https://cellphones.com.vn/laptop/msi/modern.html',
        'https://cellphones.com.vn/laptop/msi/gaming.html',
        # HP & Dell
        'https://cellphones.com.vn/laptop/hp.html',
        'https://cellphones.com.vn/laptop/hp/victus.html',
        'https://cellphones.com.vn/laptop/hp/pavilion.html',
        'https://cellphones.com.vn/laptop/dell.html',
        'https://cellphones.com.vn/laptop/dell/xps.html',
        'https://cellphones.com.vn/laptop/dell/inspiron.html',
        # Asus & Acer
        'https://cellphones.com.vn/laptop/asus.html',
        'https://cellphones.com.vn/laptop/acer.html',
    ]

    all_harvested = set()
    
    # Read existing URLs
    if URL_FILE.exists():
        with open(URL_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    all_harvested.add(line.strip())

    print(f"Loaded {len(all_harvested)} existing target URLs.")

    for cat in categories:
        try:
            req = urllib.request.Request(cat, headers=headers)
            with urllib.request.urlopen(req, timeout=10) as resp:
                html = resp.read().decode('utf-8', errors='ignore')
            found = set(re.findall(r'https://cellphones\.com\.vn/(?:laptop-|macbook-)[a-z0-9-]+\.html', html))
            new_links = found - all_harvested
            print(f"Category {cat.split('/')[-1]}: found {len(found)} total, {len(new_links)} NEW.")
            all_harvested.update(found)
        except Exception as e:
            print(f"Error fetching {cat}: {e}")

    # Write updated master URL list
    sorted_urls = sorted(all_harvested)
    with open(URL_FILE, 'w', encoding='utf-8') as f:
        for u in sorted_urls:
            f.write(u + '\n')

    print(f"\nSuccessfully updated {URL_FILE.relative_to(ROOT)}:")
    print(f"  Total target URLs: {len(sorted_urls)}")
    mac_count = sum(1 for u in sorted_urls if 'macbook' in u)
    lenovo_count = sum(1 for u in sorted_urls if 'lenovo' in u)
    msi_count = sum(1 for u in sorted_urls if 'msi' in u)
    dell_count = sum(1 for u in sorted_urls if 'dell' in u)
    hp_count = sum(1 for u in sorted_urls if 'hp' in u)
    print(f"  - MacBooks: {mac_count}")
    print(f"  - Lenovo:   {lenovo_count}")
    print(f"  - MSI:      {msi_count}")
    print(f"  - Dell:     {dell_count}")
    print(f"  - HP:       {hp_count}")

if __name__ == '__main__':
    harvest_comprehensive_urls()
