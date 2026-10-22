"""Bộ ca kiểm thử công khai cho parser yêu cầu tiếng Việt theo quy tắc.

Các tình huống dương, âm, telex, nhập nhằng và phủ định giúp tái lập giới hạn
của parser; bộ này không tuyên bố xử lý mọi câu tiếng Việt tự do.
"""

import pytest

from src.nlp_parser import PARSER_VERSION, parse_requirement


@pytest.mark.parametrize(("prompt", "expected"), [
    ("tài chính 25 triệu", {"max_budget_vnd": 25_000_000}),
    ("tài chính 25tr", {"max_budget_vnd": 25_000_000}),
    ("tầm 25m", {"max_budget_vnd": 25_000_000}),
    ("ngân sách 25 củ", {"max_budget_vnd": 25_000_000}),
    ("tối đa 18.5 triệu", {"max_budget_vnd": 18_500_000}),
    ("tầm 18tr5", {"max_budget_vnd": 18_500_000}),
    ("tầm 18 củ rưỡi", {"max_budget_vnd": 18_500_000}),
    ("từ 20 đến 25 triệu", {"min_budget_vnd": 20_000_000, "max_budget_vnd": 25_000_000}),
    ("20-25tr", {"min_budget_vnd": 20_000_000, "max_budget_vnd": 25_000_000}),
    ("2 chục", {"max_budget_vnd": 20_000_000}),
    ("ngân sách 25.000.000", {"max_budget_vnd": 25_000_000}),
    ("dưới 25", {"max_budget_vnd": 25_000_000}),
    ("sinh viên học Word", {"preset_key": "student_budget"}),
    ("cần code Docker", {"preset_key": "technical_coding"}),
    ("gaming RTX", {"preset_key": "gaming"}),
    ("ultrabook hay đi lại", {"preset_key": "slim_mobility"}),
    ("máy ROG", {"brand": "ASUS"}),
    ("máy Legion", {"brand": "Lenovo"}),
    ("MacBook", {"brand": "Apple"}),
    ("laptop MSI", {"brand": "MSI"}),
    ("Acer Nitro", {"brand": "Acer"}),
    ("Dell Inspiron", {"brand": "Dell"}),
    ("HP Victus", {"brand": "HP"}),
    ("RAM 16GB", {"min_ram_gb": 16}),
    ("32GB RAM", {"min_ram_gb": 32}),
    ("SSD 512GB", {"min_storage_gb": 512}),
    ("1024GB SSD", {"min_storage_gb": 1024}),
    ("màn 15.6 inch", {"screen_size": "15.6 inch"}),
    ("màn 14 inch", {"screen_size": "Dưới 14 inch"}),
    ("màn 16 inch", {"screen_size": "16 inch"}),
    ("màn OLED", {"panel_type": "OLED"}),
    ("cổng LAN RJ45", {"require_rj45_lan": True}),
    ("có khe nâng cấp RAM", {"require_ram_upgradeable": True}),
    ("sạc Type-C", {"require_type_c_charging": True}),
    ("cần USB4", {"require_thunderbolt": True}),
    ("chạy Windows", {"required_os": "Windows"}),
    ("dùng macOS", {"required_os": "macOS"}),
    ("chuẩn D05", {"strict_benchmark": True}),
])
def test_supported_requirement_cases(prompt, expected):
    result = parse_requirement(prompt)
    for key, value in expected.items():
        assert (result[key] if key == "preset_key" else result["filters"].get(key)) == value


@pytest.mark.parametrize("prompt", ["cấu hình ngon", "máy mượt xịn", "16GB", "bộ nhớ 16GB"])
def test_ambiguous_or_vague_terms_are_not_guessed(prompt):
    result = parse_requirement(prompt)
    assert result["warnings"]
    assert result["preset_key"] is None


def test_negative_and_d05_guards():
    excluded = parse_requirement("trừ MacBook, không cần card rời")
    assert excluded["filters"]["excluded_brands"] == ["Apple"]
    assert any(warning["term"] == "khong can card roi" for warning in excluded["warnings"])
    assert parse_requirement("hàng chính hãng")["filters"].get("strict_benchmark") is None


def test_negated_brand_and_refresh_rate_are_never_reversed():
    result = parse_requirement("laptop gaming không Apple 120Hz dưới 30 triệu")
    assert result["filters"]["excluded_brands"] == ["Apple"]
    assert "brand" not in result["filters"]
    assert result["filters"]["min_refresh_rate_hz"] == 120
    assert any(warning["level"] == "constraint_override" for warning in result["warnings"])


@pytest.mark.parametrize("prompt", ["không dùng Apple", "không phải Apple", "tránh MacBook", "loại bỏ Apple"])
def test_common_brand_negations_are_excluded(prompt):
    result = parse_requirement(prompt)
    assert result["filters"]["excluded_brands"] == ["Apple"]
    assert "brand" not in result["filters"]


def test_entities_keep_source_and_original_offsets():
    prompt = "Tài chính 25 triệu"
    result = parse_requirement(prompt)
    budget = result["entities"][0]
    assert result["parser_version"] == PARSER_VERSION
    assert budget["raw"] == prompt[budget["start"]:budget["end"]]
    assert budget["source_keyword"] == "million_unit"
