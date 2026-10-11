"""Script lịch sử tải ảnh sản phẩm xác thực từ URL FPT Shop.
Saves them locally to data/images/{source_product_id}.png.
"""

import json
import re
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = ROOT / "data" / "raw" / "fpt_shop"
IMG_DIR = ROOT / "data" / "images"
IMG_DIR.mkdir(parents=True, exist_ok=True)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}


def download_image(url: str, dest_path: Path):
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=15) as resp:
        data = resp.read()
        dest_path.write_bytes(data)


def main():
    json_files = list(RAW_DIR.glob("*.json"))
    print(f"Processing {len(json_files)} raw laptop files...")

    for jf in json_files:
        try:
            doc = json.loads(jf.read_text(encoding="utf-8"))
            pid = doc.get("source_product_id")
            source_url = doc.get("source_url")
            pname = doc.get("product_name_raw", "")

            if not pid or not source_url:
                continue

            target_path = IMG_DIR / f"{pid}.png"

            # Check if this is an unreleased test machine
            if "m5" in jf.name or "neo" in jf.name:
                print(f"Skipping unreleased concept machine: {jf.name} (Using placeholder)")
                continue

            print(f"\nFetching product: {pname[:40]} ({pid})")
            print(f"URL: {source_url}")

            req = urllib.request.Request(source_url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=15) as r:
                html = r.read().decode("utf-8", errors="ignore")

            # Look for product specific cdn2.fptshop.com.vn image with pid or product slug
            pattern = re.compile(rf'https://cdn2\.fptshop\.com\.vn/unsafe/[^\s"\'<>]*(?:{pid}|laptop|gaming)[^\s"\'<>]*(?:\.png|\.jpg|\.webp)', re.IGNORECASE)
            matches = pattern.findall(html)

            chosen_url = None
            for m in matches:
                # filter out small icons or generic banners
                if "small" not in m and "icon" not in m and "menu" not in m and "logo" not in m and "promotion" not in m:
                    chosen_url = m
                    break

            if not chosen_url and matches:
                chosen_url = matches[0]

            if not chosen_url:
                # Fallback: search general image with large dimensions
                all_imgs = re.findall(r'https://cdn2\.fptshop\.com\.vn/unsafe/[^\s"\'<>]+(?:\.png|\.jpg|\.webp)', html)
                for img in all_imgs:
                    if "750x0" in img or "360x0" in img:
                        chosen_url = img
                        break

            if chosen_url:
                # Normalize url to clean png
                print(f"Found image: {chosen_url}")
                download_image(chosen_url, target_path)
                print(f"Downloaded -> {target_path} ({target_path.stat().st_size} bytes)")
            else:
                print(f"No product image found in HTML for {pid}")

        except Exception as e:
            print(f"Error processing {jf.name}: {e}")


if __name__ == "__main__":
    main()
