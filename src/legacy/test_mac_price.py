"""Script kiểm tra lịch sử dữ liệu giá MacBook."""

import urllib.request
import re

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
}

sample_macs = [
    'https://cellphones.com.vn/macbook-air-m2-2022-16gb.html',
    'https://cellphones.com.vn/macbook-air-m2-2022-16gb-512gb.html',
    'https://cellphones.com.vn/macbook-pro-14-inch-m3-max-2023-128gb-8tb.html',
    'https://cellphones.com.vn/macbook-pro-16-inch-m4-max-48gb-1tb.html',
    'https://cellphones.com.vn/macbook-pro-16-m4-pro-14-cpu-20-gpu-24gb-1tb-2024-sac-140w.html',
]

for url in sample_macs:
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as r:
            html = r.read().decode('utf-8')
        m_price = re.search(r'"price":\s*"(\d+)"', html)
        m_show = re.search(r'class="[^"]*price--show[^"]*">([^<]+)<', html)
        title = re.search(r'<h1[^>]*>([^<]+)</h1>', html)
        print(f"URL: {url.split('/')[-1]}")
        print(f"  Title: {title.group(1).strip() if title else 'None'}")
        print(f"  Offers Price: {m_price.group(1) if m_price else 'None'}")
        print(f"  Show Price: {m_show.group(1).strip() if m_show else 'None'}")
    except Exception as e:
        print(url, e)
