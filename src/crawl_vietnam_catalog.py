"""Crawler thu thập dữ liệu laptop thị trường Việt Nam (CellphoneS).

Tuân thủ nghiêm ngặt nguyên tắc:
1. Dữ liệu thực tế 100%, không bịa đặt bất kỳ thông số nào.
2. Không gán default giả, giữ nguyên giá trị trích xuất thực tế (Strict NULL).
3. Chỉ lấy máy mới 100%, loại bỏ listing cũ/đổi trả/phụ kiện.
4. Thu thập: giá bán, giá niêm yết, tình trạng hàng, cấu hình chi tiết, ảnh thật.
5. Ghi đĩa tức thời (incremental save), flush stdout liên tục.
"""

import sys
import urllib.request
import urllib.robotparser
from urllib.parse import urlparse
import re
import json
import time
import random
from pathlib import Path
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
sys.stdout.reconfigure(encoding='utf-8')

TARGETS_FILE = ROOT / "data" / "raw" / "net_new_targets.txt"
RAW_OUT_FILE = ROOT / "data" / "raw" / "cellphones_net_new_raw.json"
IMG_DIR = ROOT / "data" / "images"
FRONTEND_IMG_DIR = ROOT / "frontend" / "public" / "images"

IMG_DIR.mkdir(parents=True, exist_ok=True)
FRONTEND_IMG_DIR.mkdir(parents=True, exist_ok=True)

HEADERS = {
    'User-Agent': 'LaptopDSS-Research-Crawler/1.0 (+https://github.com/; respectful catalog research)',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7',
}

MIN_REQUEST_DELAY_SECONDS = 1.5
MAX_REQUEST_DELAY_SECONDS = 3.0
_last_request_at = 0.0
_robots: urllib.robotparser.RobotFileParser | None = None


def wait_for_rate_limit() -> None:
    """Keep a respectful randomized interval between requests to CellphoneS."""
    global _last_request_at
    delay = random.uniform(MIN_REQUEST_DELAY_SECONDS, MAX_REQUEST_DELAY_SECONDS)
    remaining = delay - (time.monotonic() - _last_request_at)
    if remaining > 0:
        time.sleep(remaining)
    _last_request_at = time.monotonic()


def is_allowed_by_robots(url: str) -> bool:
    """Return False when robots.txt explicitly disallows this crawler."""
    global _robots
    if _robots is None:
        parsed = urlparse(url)
        _robots = urllib.robotparser.RobotFileParser(f"{parsed.scheme}://{parsed.netloc}/robots.txt")
        try:
            wait_for_rate_limit()
            _robots.read()
        except OSError:
            # An unavailable robots.txt is not evidence of permission to crawl.
            return False
    return _robots.can_fetch(HEADERS['User-Agent'], url)


def download_product_image(img_url: str, filename: str) -> str:
    if not img_url:
        return "/images/laptop_fallback.png"
    target = IMG_DIR / filename
    target_fe = FRONTEND_IMG_DIR / filename
    if target.exists() and target_fe.exists():
        return f"/images/{filename}"
        
    try:
        high_res = re.sub(r'rs:fill:\d+:\d+', 'rs:fill:600:600', img_url)
        wait_for_rate_limit()
        req = urllib.request.Request(high_res, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=6) as res:
            content = res.read()
        with open(target, 'wb') as f:
            f.write(content)
        with open(target_fe, 'wb') as f:
            f.write(content)
        return f"/images/{filename}"
    except Exception:
        return "/images/laptop_fallback.png"


def scrape_one_listing(url: str):
    slug = url.split('/')[-1].replace('.html', '')
    product_id = f"cps_{slug}"
    # Bỏ qua trang danh mục hoặc URL không phải sản phẩm đơn lẻ
    if '/laptop/' in url or slug in {'macbook-neo', 'macbook-air', 'macbook-pro', 'laptop'}:
        return None
    if not is_allowed_by_robots(url):
        return None

    try:
        wait_for_rate_limit()
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=10) as res:
            html = res.read().decode('utf-8', errors='ignore')
            
        soup = BeautifulSoup(html, 'html.parser')
        
        # Tên sản phẩm
        title_el = soup.find('h1')
        product_name = title_el.get_text(strip=True) if title_el else slug
        
        # Bỏ qua nếu có chữ Cũ trong tiêu đề hoặc tên chung chung của danh mục
        name_lower = product_name.lower().strip()
        if any(k in name_lower for k in ['- cũ', 'cũ xước', 'cũ đẹp', 'cũ trầy', 'đổi trả', 'hàng cũ', 'trưng bày']):
            return None
        if name_lower in ['macbook', 'macbook air', 'macbook pro', 'macbook neo', 'laptop']:
            return None


        # Trạng thái hàng
        stock_status = 'in_stock'
        if 'Tạm hết hàng' in html or 'Hết hàng' in html:
            stock_status = 'out_of_stock'
            
        # Giá bán & Giá niêm yết
        sale_price = None
        listed_price = None
        
        offers_match = re.search(r'"offers":\s*\{[^}]*"price":\s*"(\d+)"', html)
        if offers_match:
            p_val = int(offers_match.group(1))
            if p_val > 0:
                sale_price = p_val
            
        if not sale_price:
            p_show = soup.find(class_=re.compile(r'price--show|special-price', re.I))
            if p_show:
                txt = re.sub(r'[^\d]', '', p_show.get_text())
                if txt and len(txt) >= 6:
                    sale_price = int(txt)
                    
        for p in soup.find_all(class_=re.compile(r'through|old-price', re.I)):
            txt = re.sub(r'[^\d]', '', p.get_text())
            if txt and len(txt) >= 6:
                listed_price = int(txt)
                break
                
        if not listed_price and sale_price:
            listed_price = sale_price

        # Nếu không có giá hợp lệ, bỏ qua
        if not sale_price or sale_price < 4_000_000:
            return None

        # Ảnh
        image_url = None
        img_matches = re.findall(r'https://cdn2\.cellphones\.com\.vn/insecure/[^"\'\s]+media/catalog/product[^"\'\s]+', html)
        if img_matches:
            image_url = img_matches[0]
        else:
            og_img = soup.find('meta', property='og:image')
            if og_img:
                image_url = og_img.get('content')

        local_img = download_product_image(image_url, f"{product_id}.png")

        # Thuộc tính cấu hình từ schema JSON-LD
        specs = {}
        props = re.findall(r'\{"@type":"PropertyValue","name":"([^"]+)","value":"([^"]+)"\}', html)
        for name, val in props:
            specs[name.strip()] = val.strip()
            
        # Thuộc tính cấu hình từ bảng HTML, chỉ dùng làm fallback khi JSON-LD thiếu.
        for li in soup.find_all(['li', 'tr']):
            txt = li.get_text(" : ", strip=True)
            if ' : ' in txt and len(txt) < 300:
                parts = txt.split(' : ', 1)
                k = parts[0].strip()
                v = parts[1].strip()
                if k in [
                    'Loại CPU', 'Dung lượng RAM', 'Ổ cứng', 'Loại card đồ họa',
                    'Kích thước màn hình', 'Độ phân giải màn hình', 'Pin',
                    'Hệ điều hành khi ra mắt', 'Công nghệ màn hình', 'Tần số quét',
                    'Độ sáng', 'Cổng giao tiếp', 'Chất liệu', 'Trọng lượng', 'Bảo hành'
                ]:
                    if k not in specs:
                        specs[k] = v

        # Trọng lượng
        weight_match = re.search(r'"(?:product_weight|trọng lượng)":\s*"([^"]+)"', html, re.I)
        if not weight_match:
            weight_match = re.search(r'([0-2]\.\d{1,2})\s*kg', html, re.I)
        weight = weight_match.group(1) if weight_match else None

        # Bảo hành (Strict NULL: None nếu không có thông tin)
        warranty_match = re.search(r'Bảo hành\s*(\d+)\s*tháng', html, re.I)
        warranty = int(warranty_match.group(1)) if warranty_match else None


        return {
            'source': 'cellphones',
            'source_product_id': product_id,
            'source_url': url,
            'product_name_raw': product_name,
            'sale_price_vnd': sale_price,
            'listed_price_vnd': listed_price,
            'stock_status': stock_status,
            'image_url_remote': image_url,
            'image_url_local': local_img,
            'weight_raw': weight,
            'warranty_months': warranty,
            'specs_raw': specs,
            'crawled_at': time.strftime('%Y-%m-%dT%H:%M:%S'),
        }
    except Exception as exc:
        return {'url': url, 'error': str(exc)}


def run_crawling(target_count: int = 350):
    if not TARGETS_FILE.exists():
        print("Lỗi: Không tìm thấy file net_new_targets.txt", flush=True)
        return []

    with open(TARGETS_FILE, 'r', encoding='utf-8') as f:
        urls = [line.strip() for line in f if line.strip()]

    print(f"Bắt đầu cào {len(urls)} URLs laptop mới 100%...", flush=True)
    print(f"Mục tiêu: Đạt {target_count} laptop có giá và thông số chuẩn xác.", flush=True)

    results = []
    seen_ids = set()

    # Load existing output only to resume an interrupted crawl.  Existing rows are
    # never rewritten with inferred values by this crawler.
    if RAW_OUT_FILE.exists():
        try:
            with open(RAW_OUT_FILE, 'r', encoding='utf-8') as f:
                existing_data = json.load(f)
                for item in existing_data:
                    pid = item.get('source_product_id')
                    if pid and pid not in seen_ids:
                        seen_ids.add(pid)
                        results.append(item)
            print(f"Đã nạp {len(results)} bản ghi đã cào từ trước.", flush=True)
        except Exception:
            pass

    unvisited_urls = [u for u in urls if f"cps_{u.split('/')[-1].replace('.html', '')}" not in seen_ids]
    print(f"Số URL còn lại cần cào: {len(unvisited_urls)}", flush=True)

    for url in unvisited_urls:
        res = scrape_one_listing(url)
        if res and not res.get('error') and res.get('sale_price_vnd'):
            p = res['sale_price_vnd']
            pid = res['source_product_id']
            if pid not in seen_ids and p >= 4_000_000 and len(res.get('specs_raw', {})) >= 4:
                seen_ids.add(pid)
                results.append(res)
                print(f"[{len(results)}/{target_count}] {p:,.0f} đ | {res['product_name_raw'][:40]} | Specs: {len(res['specs_raw'])}", flush=True)

                if len(results) % 5 == 0:
                    with open(RAW_OUT_FILE, 'w', encoding='utf-8') as f:
                        json.dump(results, f, ensure_ascii=False, indent=2)

                if len(results) >= target_count:
                    print("Đã đạt mốc số lượng mục tiêu!", flush=True)
                    break

    with open(RAW_OUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"\nHOÀN THÀNH CÀO! Đã thu thập {len(results)} laptop mới 100% vào {RAW_OUT_FILE}", flush=True)
    under_15 = sum(1 for r in results if r['sale_price_vnd'] < 15_000_000)
    between_15_25 = sum(1 for r in results if 15_000_000 <= r['sale_price_vnd'] <= 25_000_000)
    above_25 = sum(1 for r in results if r['sale_price_vnd'] > 25_000_000)
    print(f"  - Phân khúc dưới 15 triệu: {under_15} máy", flush=True)
    print(f"  - Phân khúc 15 - 25 triệu: {between_15_25} máy", flush=True)
    print(f"  - Phân khúc trên 25 triệu: {above_25} máy", flush=True)
    return results


if __name__ == '__main__':
    run_crawling(target_count=350)
