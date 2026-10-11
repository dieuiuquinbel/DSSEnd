"""Kiểm tra thử quy trình thu thập danh mục MacBook."""

from .crawl_cellphones import scrape_one_laptop

mac_urls = [
    'https://cellphones.com.vn/macbook-air-m2-2022-16gb.html',
    'https://cellphones.com.vn/macbook-air-m2-2022-16gb-512gb.html',
    'https://cellphones.com.vn/macbook-pro-16-inch-m4-max-48gb-1tb.html',
    'https://cellphones.com.vn/macbook-pro-16-m4-pro-14-cpu-20-gpu-24gb-1tb-2024-sac-140w.html',
    'https://cellphones.com.vn/macbook-pro-m4-pro-14-inch-14cpu-20gpu-24gb-512gb-nano.html',
    'https://cellphones.com.vn/macbook-pro-m4-max-14-inch-14cpu-32gpu-36gb-1tb-nano.html'
]

for idx, u in enumerate(mac_urls):
    res = scrape_one_laptop(u, idx)
    if res and res.get('sale_price_vnd'):
        print(f"Scraped: {res['product_name_raw'][:50]} | Price: {res['sale_price_vnd']:,} | Specs: {len(res['specs_raw'])}")
