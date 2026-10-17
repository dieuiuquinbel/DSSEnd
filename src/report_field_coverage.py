"""Báo cáo độ phủ các thông số do nhà bán lẻ công bố."""

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "raw" / "fpt_shop"
OUTPUT = ROOT / "data" / "archive" / "legacy" / "fpt_shop_field_coverage.csv"


def main():
    records = [json.loads(path.read_text(encoding="utf-8")) for path in sorted(RAW_DIR.glob("*.json"))]
    fields = sorted({field for row in records for field in row.get("specifications", {})})
    rows = []
    for field in fields:
        populated = sum(bool(row.get("specifications", {}).get(field, "").strip()) for row in records)
        rate = populated / len(records) if records else 0
        rows.append({
            "field_label": field,
            "populated_records": populated,
            "total_records": len(records),
            "coverage_percent": f"{rate * 100:.1f}",
            "provisional_role": "candidate_core" if rate >= 0.8 else "supplemental_or_insufficient",
        })
    with OUTPUT.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {len(rows)} field(s) to {OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
