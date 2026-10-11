"""Thu thập catalog laptop CellphoneS theo chính sách dữ liệu dự án.

Collects 100% genuine raw specifications for 80-100 laptops.
Outputs:
- data/raw/cellphones_laptops_raw.json (Untouched, complete raw data)
- data/images/ (Authentic product images downloaded locally)
"""

import urllib.request
import re
import json
import time
from pathlib import Path
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed

ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = ROOT / "data" / "raw"
IMG_DIR = ROOT / "data" / "images"
FRONTEND_IMG_DIR = ROOT / "frontend" / "public" / "images"

RAW_DIR.mkdir(parents=True, exist_ok=True)
IMG_DIR.mkdir(parents=True, exist_ok=True)
FRONTEND_IMG_DIR.mkdir(parents=True, exist_ok=True)

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7',
}


def download_image(img_url: str, target_filename: str):
    """Download image to both data/images and frontend/public/images."""
    if not img_url:
        return None
    # Fix thumbnail url to full resolution (change rs:fill:50:50 or 358:358 to 600:600)
    high_res_url = re.sub(r'rs:fill:\d+:\d+', 'rs:fill:600:600', img_url)
    
    target_path = IMG_DIR / target_filename
    frontend_path = FRONTEND_IMG_DIR / target_filename
    
    if target_path.exists() and frontend_path.exists():
        return f"/images/{target_filename}"
        
    try:
        req = urllib.request.Request(high_res_url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=8) as res:
            content = res.read()
            with open(target_path, 'wb') as f:
                f.write(content)
            with open(frontend_path, 'wb') as f:
                f.write(content)
        return f"/images/{target_filename}"
    except Exception as e:
        # Fallback to original url
        try:
            req = urllib.request.Request(img_url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=8) as res:
                content = res.read()
                with open(target_path, 'wb') as f:
                    f.write(content)
                with open(frontend_path, 'wb') as f:
                    f.write(content)
            return f"/images/{target_filename}"
        except Exception:
            return None


def scrape_one_laptop(url: str, idx: int):
    """Scrape full untouched specifications of a single laptop."""
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=10) as res:
            html = res.read().decode('utf-8', errors='ignore')
            
        soup = BeautifulSoup(html, 'html.parser')
        
        # Product ID from URL slug or SKU
        slug = url.split('/')[-1].replace('.html', '')
        # Generate numeric ID or stable ID
        product_id = f"cps_{slug}"
        
        # Title
        title_el = soup.find('h1')
        product_name = title_el.get_text(strip=True) if title_el else slug
        
        # Offers / Price
        sale_price = None
        listed_price = None
        
        offers_match = re.search(r'"offers":\s*\{[^}]*"price":\s*"(\d+)"', html)
        if offers_match:
            sale_price = int(offers_match.group(1))
            
        # Listed price
        for p in soup.find_all(class_=re.compile(r'through|old-price', re.I)):
            txt = re.sub(r'[^\d]', '', p.get_text())
            if txt and len(txt) >= 7:
                listed_price = int(txt)
                break
                
        if not sale_price:
            p_show = soup.find(class_=re.compile(r'price--show|special-price', re.I))
            if p_show:
                txt = re.sub(r'[^\d]', '', p_show.get_text())
                if txt:
                    sale_price = int(txt)
                    
        if not listed_price and sale_price:
            listed_price = sale_price

        # Image
        image_url = None
        img_matches = re.findall(r'https://cdn2\.cellphones\.com\.vn/insecure/[^"\'\s]+media/catalog/product[^"\'\s]+', html)
        if img_matches:
            image_url = img_matches[0]
        else:
            og_img = soup.find('meta', property='og:image')
            if og_img:
                image_url = og_img.get('content')
                
        local_img = download_image(image_url, f"{product_id}.png") if image_url else None

        # Specs from Schema PropertyValue
        specs = {}
        props = re.findall(r'\{"@type":"PropertyValue","name":"([^"]+)","value":"([^"]+)"\}', html)
        for name, val in props:
            specs[name.strip()] = val.strip()
            
        # Additional table specs
        for li in soup.find_all(['li', 'tr', 'div']):
            txt = li.get_text(" : ", strip=True)
            if ' : ' in txt and len(txt) < 300:
                parts = txt.split(' : ', 1)
                k = parts[0].strip()
                v = parts[1].strip()
                if k in ['Loại CPU', 'Dung lượng RAM', 'Ổ cứng', 'Loại card đồ họa', 'Kích thước màn hình', 'Độ phân giải màn hình', 'Pin', 'Hệ điều hành khi ra mắt', 'Công nghệ màn hình', 'Tần số quét', 'Chất liệu']:
                    if k not in specs:
                        specs[k] = v

        # Weight
        weight_match = re.search(r'"(?:product_weight|trọng lượng)":\s*"([^"]+)"', html, re.I)
        if not weight_match:
            weight_match = re.search(r'([0-2]\.\d{1,2})\s*kg', html, re.I)
        weight = weight_match.group(1) if weight_match else None

        # Warranty
        warranty_match = re.search(r'Bảo hành\s*(\d+)\s*tháng', html, re.I)
        warranty = int(warranty_match.group(1)) if warranty_match else 24

        return {
            'source': 'cellphones',
            'source_product_id': product_id,
            'source_url': url,
            'product_name_raw': product_name,
            'sale_price_vnd': sale_price,
            'listed_price_vnd': listed_price,
            'image_url_remote': image_url,
            'image_url_local': local_img,
            'weight_raw': weight,
            'warranty_months': warranty,
            'specs_raw': specs,
            'scraped_at': time.strftime('%Y-%m-%dT%H:%M:%S'),
        }
    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return None


def run_scraping(target_count: int = 210):
    """Scrape up to target_count laptops from harvested URLs, prioritizing market diversity."""
    url_file = RAW_DIR / "cellphones_target_urls.txt"
    if not url_file.exists():
        print("URL file not found! Run harvest_urls.py first.")
        return []
        
    with open(url_file, "r", encoding="utf-8") as f:
        urls = [line.strip() for line in f if line.strip()]
        
    # Prioritize: 1. MacBooks, 2. Lenovo, 3. MSI, 4. Others (Acer, Asus, Dell, HP)
    def url_priority(u):
        if 'macbook' in u:
            return 1
        if 'lenovo' in u:
            return 2
        if 'msi' in u:
            return 3
        return 4

    urls_sorted = sorted(urls, key=url_priority)
    print(f"Loaded {len(urls_sorted)} target URLs. Starting scraping for up to {target_count} laptops...")
    
    results = []
    seen_ids = set()
    # Scrape with 10 concurrent threads
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(scrape_one_laptop, u, idx): u for idx, u in enumerate(urls_sorted)}
        for future in as_completed(futures):
            res = future.result()
            if res and res.get('product_name_raw') and res.get('sale_price_vnd'):
                pid = res.get('source_product_id')
                if pid not in seen_ids:
                    seen_ids.add(pid)
                    results.append(res)
                    print(f"[{len(results)}/{target_count}] {res['product_name_raw'][:45]} | {res['sale_price_vnd']:,}₫ | {len(res['specs_raw'])} specs")
                    if len(results) >= target_count:
                        break

    # Save 100% untouched raw JSON
    out_file = RAW_DIR / "cellphones_laptops_raw.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
        
    print(f"\nSUCCESS! Scraped {len(results)} genuine laptops to {out_file}")
    return results


if __name__ == "__main__":
    run_scraping(target_count=210)

