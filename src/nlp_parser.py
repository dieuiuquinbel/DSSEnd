"""Bộ phân tích yêu cầu tiếng Việt theo quy tắc cho LaptopDSS.

Module không phải mô hình NLP/AI được huấn luyện. Nó dùng regex và từ điển
đồng nghĩa để tạo preset cùng bộ lọc có thể kiểm tra. Đầu ra chứa thực thể có
vị trí, nguồn quy tắc, từ chưa phân giải và cảnh báo trước khi gọi AHP-TOPSIS.
"""

import re
import unicodedata
from typing import Any, Dict, List, Optional, Tuple


PARSER_VERSION = "1.1.0"
PRESET_KEYWORDS = {
    "student_budget": ("sinh vien", "kinh te", "hoc tap", "van phong", "word", "excel", "gia re", "ngon bo re", "tiet kiem", "hop tui tien"),
    "technical_coding": ("lap trinh", "code", "coder", "ky thuat", "cong nghe thong tin", "docker", "may ao", "backend", "chip khoe", "cpu manh", "ram nhieu", "da nhiem"),
    "gaming": ("choi game", "gaming", "game thu", "chien game", "esports", "fps", "do hoa", "render", "3d", "rtx", "card roi"),
    "slim_mobility": ("mong nhe", "di dong", "sieu nhe", "gon nhe", "hay di lai", "cong tac", "ultrabook", "nho gon"),
}
BRANDS = {
    "ASUS": ("asus", "rog", "tuf"), "Lenovo": ("lenovo", "loq", "legion", "ideapad", "thinkpad"),
    "Apple": ("apple", "macbook"), "MSI": ("msi", "katana", "cyborg", "modern"),
    "Acer": ("acer", "nitro", "aspire", "swift"), "Dell": ("dell", "inspiron", "vostro"), "HP": ("hp", "victus", "pavilion"),
}
VAGUE_TERMS = ("ngon", "muot", "xin", "on")


def _plain(text: str) -> str:
    """Chuyển tiếng Việt có dấu về dạng so khớp không dấu, giữ chỉ số ký tự."""
    folded = "".join(c for c in unicodedata.normalize("NFD", text.lower()) if unicodedata.category(c) != "Mn")
    return folded.replace("đ", "d")


def _entity(text: str, match: re.Match, kind: str, value: Any, source: str, label: str) -> Dict[str, Any]:
    start, end = match.span()
    return {"type": kind, "label": label, "raw": text[start:end], "value": value, "start": start, "end": end, "source_keyword": source}


def _money(text: str, normalized: str) -> Tuple[Optional[float], Optional[float], List[Dict[str, Any]]]:
    """Trích xuất ngân sách đơn/dải, gồm các cách viết tiền Việt thông dụng."""
    unit = r"(?:trieu|tr|m|cu|chai)"
    range_match = re.search(rf"(?:tu\s+)?(\d+(?:[\.,]\d+)?)\s*(?:den|toi|-)\s*(\d+(?:[\.,]\d+)?)\s*{unit}\b", normalized)
    if range_match:
        low, high = (float(value.replace(",", ".")) * 1_000_000 for value in range_match.groups())
        return low, high, [_entity(text, range_match, "min_budget", low, "budget_range", "Ngân sách tối thiểu"), _entity(text, range_match, "max_budget", high, "budget_range", "Ngân sách tối đa")]
    half_match = re.search(rf"(\d+)\s*{unit}\s*ruoi\b", normalized)
    if half_match:
        value = (int(half_match.group(1)) + 0.5) * 1_000_000
        return None, value, [_entity(text, half_match, "max_budget", value, "half_million", "Ngân sách tối đa")]
    compact_match = re.search(r"(\d+)\s*tr\s*(\d)\b", normalized)
    if compact_match:
        value = (int(compact_match.group(1)) + int(compact_match.group(2)) / 10) * 1_000_000
        return None, value, [_entity(text, compact_match, "max_budget", value, "compact_million", "Ngân sách tối đa")]
    ten_match = re.search(r"(\d+)\s*chuc\b", normalized)
    if ten_match:
        value = int(ten_match.group(1)) * 10_000_000
        return None, value, [_entity(text, ten_match, "max_budget", value, "ten_million", "Ngân sách tối đa")]
    full_vnd = re.search(r"\b(\d{1,3}(?:\.\d{3}){2})\b", normalized)
    if full_vnd:
        value = float(full_vnd.group(1).replace(".", ""))
        return None, value, [_entity(text, full_vnd, "max_budget", value, "full_vnd", "Ngân sách tối đa")]
    amount_match = re.search(rf"(\d+(?:[\.,]\d+)?)\s*{unit}\b", normalized)
    if amount_match:
        value = float(amount_match.group(1).replace(",", ".")) * 1_000_000
        return None, value, [_entity(text, amount_match, "max_budget", value, "million_unit", "Ngân sách tối đa")]
    bare_match = re.search(r"(?:duoi|toi da|khoang|tam|tai chinh|ngan sach)\s*(?:gia\s*)?(\d+(?:[\.,]\d+)?)\b", normalized)
    if bare_match and float(bare_match.group(1).replace(",", ".")) <= 100:
        value = float(bare_match.group(1).replace(",", ".")) * 1_000_000
        return None, value, [_entity(text, bare_match, "max_budget", value, "budget_context", "Ngân sách tối đa")]
    return None, None, []


def parse_requirement(prompt: str) -> Dict[str, Any]:
    """Trích xuất yêu cầu; từ mơ hồ/ngoài phạm vi được cảnh báo thay vì suy đoán."""
    normalized = _plain(prompt)
    filters: Dict[str, Any] = {}
    entities: List[Dict[str, Any]] = []
    warnings: List[Dict[str, str]] = []
    unresolved_terms: List[str] = []
    min_budget, max_budget, money_entities = _money(prompt, normalized)
    entities.extend(money_entities)
    if min_budget is not None:
        filters["min_budget_vnd"] = min_budget
    if max_budget is not None:
        filters["max_budget_vnd"] = max_budget

    for term in VAGUE_TERMS:
        match = re.search(rf"\b{term}\b", normalized)
        if match:
            unresolved_terms.append(term)
            warnings.append({"level": "vague", "term": term, "message": f"'{term}' chưa đủ cơ sở để tự gán hồ sơ hoặc cấu hình."})
    scores = {key: sum(normalized.count(word) for word in words) for key, words in PRESET_KEYWORDS.items()}
    suggested_preset, score = max(scores.items(), key=lambda item: item[1])
    preset_key = suggested_preset if score else None
    confidence = round(min(score / 2, 1.0), 2)
    if preset_key:
        keyword = next(word for word in PRESET_KEYWORDS[preset_key] if word in normalized)
        entities.append(_entity(prompt, re.search(re.escape(keyword), normalized), "preset", preset_key, keyword, "Hồ sơ nhu cầu"))
    else:
        warnings.append({"level": "unresolved", "term": "", "message": "Chưa nhận diện rõ hồ sơ; hãy chọn một trong bốn hồ sơ nhu cầu."})

    for brand, words in BRANDS.items():
        for word in words:
            match = re.search(rf"\b{re.escape(word)}\b", normalized)
            if match:
                if re.search(rf"(?:tru|khong\s+(?:chon|lay|muon))\s+{re.escape(word)}\b", normalized):
                    filters.setdefault("excluded_brands", []).append(brand)
                    entities.append(_entity(prompt, match, "excluded_brand", brand, word, "Loại trừ thương hiệu"))
                else:
                    filters["brand"] = brand
                    entities.append(_entity(prompt, match, "brand", brand, word, "Thương hiệu"))
                break
        if "brand" in filters or filters.get("excluded_brands"):
            break

    ram_match = re.search(r"(?:ram\s*)(8|16|32|64)\s*gb\b|(8|16|32|64)\s*gb\s*ram\b", normalized)
    if ram_match:
        value = int(ram_match.group(1) or ram_match.group(2))
        filters["min_ram_gb"] = value
        entities.append(_entity(prompt, ram_match, "min_ram", value, "ram", "RAM tối thiểu"))
    elif re.search(r"\b(8|16|32|64)\s*gb\b", normalized):
        match = re.search(r"\b(8|16|32|64)\s*gb\b", normalized)
        unresolved_terms.append(match.group(0))
        warnings.append({"level": "ambiguous", "term": match.group(0), "message": f"'{match.group(0)}' có thể là RAM hoặc SSD; chưa áp dụng bộ lọc."})
    storage_match = re.search(r"(?:ssd|o cung|storage)\s*(256|512|1024)\s*gb\b|(256|512|1024)\s*gb\s*(?:ssd|o cung)\b", normalized)
    if storage_match:
        value = int(storage_match.group(1) or storage_match.group(2))
        filters["min_storage_gb"] = value
        entities.append(_entity(prompt, storage_match, "min_storage", value, "ssd", "SSD tối thiểu"))

    screen_rules = ((r"\b16\s*inch\b", "16 inch", "16 inch"), (r"\b15[\.,]6\s*(?:inch)?\b|\bman lon\b", "15.6 inch", "screen_size"), (r"\b(?:13|14)\s*inch\b|\bman nho\b", "Dưới 14 inch", "screen_size"))
    for pattern, value, source in screen_rules:
        match = re.search(pattern, normalized)
        if match:
            filters["screen_size"] = value
            entities.append(_entity(prompt, match, "screen_size", value, source, "Màn hình"))
            break
    if "oled" in normalized:
        match = re.search("oled", normalized)
        filters["panel_type"] = "OLED"
        entities.append(_entity(prompt, match, "panel_type", "OLED", "oled", "Tấm nền"))
    for pattern, key, kind, label in ((r"rj45|cong lan|mang day", "require_rj45_lan", "rj45", "Cổng kết nối"), (r"nang cap ram|them ram", "require_ram_upgradeable", "ram_upgrade", "Khả năng nâng cấp"), (r"sac\s+(?:type[- ]?c|c)\b", "require_type_c_charging", "type_c_charging", "Sạc"), (r"thunderbolt|usb4", "require_thunderbolt", "thunderbolt", "Cổng kết nối")):
        match = re.search(pattern, normalized)
        if match:
            filters[key] = True
            entities.append(_entity(prompt, match, kind, True, match.group(0), label))
    os_match = re.search(r"windows|macos|mac os", normalized)
    if os_match:
        value = "Windows" if os_match.group(0) == "windows" else "macOS"
        filters["required_os"] = value
        entities.append(_entity(prompt, os_match, "os", value, os_match.group(0), "Hệ điều hành"))
    for keyword, value in (("core i7", "Core i7"), ("core i5", "Core i5"), ("ryzen", "Ryzen"), ("ultra", "Ultra"), ("snapdragon", "Snapdragon")):
        match = re.search(rf"\b{re.escape(keyword)}\b", normalized)
        if match:
            filters["cpu_family"] = value
            entities.append(_entity(prompt, match, "cpu", value, keyword, "CPU"))
            break
    d05_match = re.search(r"chuan d05|benchmark chinh thuc", normalized)
    if d05_match:
        filters["strict_benchmark"] = True
        entities.append(_entity(prompt, d05_match, "strict_benchmark", True, d05_match.group(0), "Benchmark"))
    if "pin trau" in normalized:
        warnings.append({"level": "unsupported", "term": "pin trau", "message": "Nhu cầu pin được ghi nhận nhưng không dùng để xếp hạng theo D07."})
    if "khong can card roi" in normalized:
        warnings.append({"level": "soft_preference", "term": "khong can card roi", "message": "Đã ghi nhận không ép GPU rời; hệ thống không loại máy có GPU rời."})
    return {"parser_version": PARSER_VERSION, "normalized_text": normalized, "filters": filters, "preset_key": preset_key, "preset_confidence": confidence, "entities": entities, "unresolved_terms": unresolved_terms, "warnings": warnings}
