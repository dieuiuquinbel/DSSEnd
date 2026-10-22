"""Kiểm định các bất biến về tính toàn vẹn dữ liệu, quy tắc Strict NULL và loại bỏ trang danh mục (D01, D12, D14)."""

import csv
import sqlite3
from pathlib import Path

from src.legacy.standardize_cellphones import parse_weight

ROOT = Path(__file__).resolve().parents[1]
CATALOG_CSV = ROOT / "data" / "catalog" / "laptops.csv"
BENCHMARKS_CSV = ROOT / "data" / "catalog" / "benchmarks.csv"
DB_FILE = ROOT / "data" / "artifacts" / "laptop_dss.db"


def test_catalog_exact_size_and_retailer_breakdown():
    """Khóa kích thước catalog chính xác và tỷ lệ nguồn (505 CellphoneS + 8 FPT Shop pilot)."""
    assert CATALOG_CSV.exists()
    with open(CATALOG_CSV, "r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    assert len(rows) == 513, f"Quy mô catalog phải chính xác 513 laptop, thực tế: {len(rows)}"

    cps_count = sum(1 for r in rows if r.get("source") == "cellphones")
    fpt_count = sum(1 for r in rows if r.get("source") in ("fpt_shop", "FPT Shop"))
    assert cps_count == 505, f"CellphoneS phải có đúng 505 máy, thực tế: {cps_count}"
    assert fpt_count == 8, f"FPT Shop phải có đúng 8 máy pilot, thực tế: {fpt_count}"



def test_zero_category_pages_in_catalog():
    """Đảm bảo tuyệt đối không lẫn URL trang danh mục / landing page vào catalog sản phẩm."""
    with open(CATALOG_CSV, "r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    category_slugs = {"cps_macbook-neo", "cps_macbook-air", "cps_macbook-pro"}
    generic_names = {"macbook", "macbook air", "macbook pro", "macbook neo", "laptop"}

    for r in rows:
        pid = r.get("source_product_id", "")
        url = r.get("source_url", "")
        name = r.get("product_name_raw", "").strip().lower()

        assert pid not in category_slugs, f"Phát hiện ID trang danh mục trong catalog: {pid}"
        assert "/laptop/" not in url, f"Phát hiện URL đường dẫn danh mục: {url}"
        assert name not in generic_names, f"Phát hiện tiêu đề danh mục chung chung: {name}"


def test_strict_null_and_no_fake_defaults():
    """Kiểm định nghiêm ngặt nguyên tắc Strict NULL: không gán VRAM=0, không gán mặc định LAN=false hoặc Audio=true."""
    with open(CATALOG_CSV, "r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    for r in rows:
        gpu_type = r.get("gpu_type", "")
        vram = r.get("gpu_vram_gb", "")

        # 1. GPU tích hợp không được gán VRAM giả tạo '0'
        if gpu_type != "discrete":
            assert vram == "", f"GPU onboard ({r.get('gpu_name_normalized')}) không được gán VRAM giả: {vram}"

        # 2. Không được có giá trị 'nan' dạng chuỗi
        for field, val in r.items():
            assert val.lower() != "nan", f"Trường {field} bị gán chuỗi 'nan' thay vì để rỗng"

    # Kiểm tra tỷ lệ NULL thực tế (chứng minh không gán blanket default)
    null_vram = sum(1 for r in rows if not r.get("gpu_vram_gb"))
    null_lan = sum(1 for r in rows if not r.get("lan_present"))
    null_audio = sum(1 for r in rows if not r.get("audio_jack_present"))

    assert null_vram >= 340, f"Số dòng NULL VRAM phải >= 340, thực tế: {null_vram}"
    assert null_lan >= 300, f"Số dòng NULL LAN phải >= 300, thực tế: {null_lan}"
    assert null_audio >= 50, f"Số dòng NULL Audio Jack phải >= 50, thực tế: {null_audio}"


def test_catalog_weights_are_physically_plausible():
    """A parsed gram value must never silently become tens of kilograms."""
    with open(CATALOG_CSV, "r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    invalid = [row for row in rows if row.get("weight_kg") and not 0.4 <= float(row["weight_kg"]) <= 5.0]
    assert not invalid, f"Cân nặng laptop ngoài khoảng vật lý: {[row['source_product_id'] for row in invalid]}"


def test_weight_parser_preserves_grams_and_three_decimals():
    assert parse_weight("986 g") == 0.986
    assert parse_weight("975g") == 0.975
    assert parse_weight("686 g") == 0.686
    assert parse_weight("0.986 kg") == 0.986
    assert parse_weight("1,24 kg") == 1.24
    assert parse_weight("2.1kg") == 2.1


def test_sqlite_database_bcnf_and_null_invariants():
    """Kiểm tra cơ sở dữ liệu SQLite theo chuẩn BCNF và lưu trữ NULL chuẩn mực."""
    assert DB_FILE.exists()
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM configurations")
    cfg_count = cur.fetchone()[0]
    assert cfg_count == 511, f"Bảng configurations phải có đúng 511 cấu hình, thực tế: {cfg_count}"

    cur.execute("SELECT COUNT(*) FROM retail_listings")
    listing_count = cur.fetchone()[0]
    assert listing_count == 513, f"Bảng retail_listings phải có đúng 513 listing, thực tế: {listing_count}"

    cur.execute("SELECT COUNT(*) FROM price_observations")
    price_count = cur.fetchone()[0]
    assert price_count == 513, f"Bảng price_observations phải có đúng 513 bản ghi giá, thực tế: {price_count}"

    cur.execute("SELECT COUNT(*) FROM component_benchmarks")
    bench_count = cur.fetchone()[0]
    assert bench_count == 209, f"Bảng component_benchmarks phải có đúng 209 bản ghi, thực tế: {bench_count}"

    # Kiểm tra lưu trữ NULL thực tế trong SQLite (không fake 0, không fake false)
    cur.execute("SELECT COUNT(*) FROM configurations WHERE gpu_vram_gb IS NULL")
    null_vram_db = cur.fetchone()[0]
    assert null_vram_db >= 340, f"Số cấu hình có VRAM NULL trong SQLite phải >= 340, thực tế: {null_vram_db}"

    cur.execute("SELECT COUNT(*) FROM configurations WHERE lan_present IS NULL")
    null_lan_db = cur.fetchone()[0]
    assert null_lan_db >= 300, f"Số cấu hình có LAN NULL trong SQLite phải >= 300, thực tế: {null_lan_db}"

    # Kiểm tra không có URL danh mục trong retail_listings
    cur.execute("SELECT COUNT(*) FROM retail_listings WHERE source_url LIKE '%/laptop/%'")
    cat_in_db = cur.fetchone()[0]
    assert cat_in_db == 0, f"Phát hiện {cat_in_db} URL danh mục trong retail_listings"


    conn.close()
