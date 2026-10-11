"""Script kiểm tra lịch sử cho luồng thu thập URL catalog."""

import urllib.request
import re
from bs4 import BeautifulSoup

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7',
}

def harvest_urls():
    categories = [
        'https://cellphones.com.vn/laptop/mac.html',
        'https://cellphones.com.vn/laptop/lenovo.html',
        'https://cellphones.com.vn/laptop/msi.html',
        'https://cellphones.com.vn/laptop/dell.html',
        'https://cellphones.com.vn/laptop/hp.html',
        'https://cellphones.com.vn/laptop/asus.html',
    ]

    all_links = set()
    for cat in categories:
        try:
            req = urllib.request.Request(cat, headers=headers)
            with urllib.request.urlopen(req, timeout=10) as resp:
                html = resp.read().decode('utf-8', errors='ignore')
            # Extract product links
            matches = re.findall(r'https://cellphones\.com\.vn/(?:laptop-|macbook-)[a-z0-9-]+\.html', html)
            print(f"Cat {cat.split('/')[-1]}: found {len(matches)} product links")
            all_links.update(matches)
        except Exception as e:
            print(f"Error {cat}: {e}")

    print(f"Total unique product links harvested: {len(all_links)}")
    return all_links

if __name__ == '__main__':
    harvest_urls()
