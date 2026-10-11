"""Gộp catalog FPT Shop và CellphoneS thành dữ liệu thống nhất.

Outputs:
- data/processed/laptops_standardized.csv (Unified 110-laptop dataset)
"""

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FPT_CSV = ROOT / "data" / "processed" / "fpt_shop_pilot_standardized.csv"
CELLPHONES_CSV = ROOT / "data" / "processed" / "cellphones_standardized.csv"
UNIFIED_CSV = ROOT / "data" / "processed" / "laptops_standardized.csv"


def merge_datasets():
    all_laptops = []
    seen_ids = set()

    # 1. Load CellphoneS (100 laptops)
    if CELLPHONES_CSV.exists():
        with open(CELLPHONES_CSV, 'r', encoding='utf-8') as f:
            for r in csv.DictReader(f):
                pid = r.get('source_product_id')
                if pid and pid not in seen_ids:
                    seen_ids.add(pid)
                    all_laptops.append(r)

    # 2. Load FPT Shop (10 laptops)
    if FPT_CSV.exists():
        with open(FPT_CSV, 'r', encoding='utf-8') as f:
            for r in csv.DictReader(f):
                pid = r.get('source_product_id')
                if pid and pid not in seen_ids:
                    seen_ids.add(pid)
                    # Align fields
                    if 'source' not in r:
                        r['source'] = 'fpt_shop'
                    all_laptops.append(r)

    print(f"Unified dataset: {len(all_laptops)} total laptops.")

    # Save to UNIFIED_CSV
    if all_laptops:
        # Collect all unique fieldnames
        fieldnames = list(all_laptops[0].keys())
        for l in all_laptops[1:]:
            for k in l.keys():
                if k not in fieldnames:
                    fieldnames.append(k)

        with open(UNIFIED_CSV, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(all_laptops)

        print(f"Saved to {UNIFIED_CSV}")
    return all_laptops


if __name__ == "__main__":
    merge_datasets()
