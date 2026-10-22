"""REST API của LaptopDSS phục vụ giao diện React.

Module tích hợp bộ phân tích yêu cầu tiếng Việt, AHP-TOPSIS (D05, D10, D14),
catalog chuẩn hóa và định giá ML. API nhận bộ lọc hoặc câu yêu cầu tự nhiên,
trả xếp hạng, độ nhạy, thẩm định giá và đường dẫn ảnh cục bộ cho giao diện.
"""

import sys
import math
import json
import logging
import numpy as np
import joblib
from functools import lru_cache
from pathlib import Path
from typing import List, Optional, Dict, Tuple, Any, Literal

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, field_validator, model_validator

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from dss_ranking import (
    PRESETS,
    analyze_budget_sensitivity,
    analyze_monte_carlo_stability,
    analyze_weight_sensitivity,
    compute_ahp_weights,
    evaluate,
    load_standardized_laptops,
)
from nlp_parser import parse_requirement

logger = logging.getLogger(__name__)

app = FastAPI(title="LaptopDSS API", version="1.0.0")

# Enable CORS for local Vite dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve local image files
IMG_DIR = ROOT / "data" / "images"
if IMG_DIR.exists():
    app.mount("/images", StaticFiles(directory=str(IMG_DIR)), name="images")

ARTIFACTS_DIR = ROOT / "data" / "artifacts"
ML_OOF_FILE = ARTIFACTS_DIR / "price_model_oof.json"
ML_METRICS_FILE = ARTIFACTS_DIR / "price_model_metrics.json"
DEFAULT_ML_RANKING_WEIGHT = 0.15
MAX_ML_RANKING_WEIGHT = 0.30


@lru_cache(maxsize=2)
def _load_model_cached(path_text: str, mtime_ns: int) -> Dict[str, Any]:
    """Cache deployed model; replacing its artifact automatically invalidates it."""
    del mtime_ns
    return joblib.load(path_text)


def get_model_pipeline(model_file: Path) -> Dict[str, Any]:
    if not model_file.exists():
        raise FileNotFoundError(model_file)
    return _load_model_cached(str(model_file.resolve()), model_file.stat().st_mtime_ns)

def get_ml_enrichment() -> Tuple[Dict[str, float], float, bool]:
    """Đọc định giá OOF; trả cờ False thay vì biến lỗi đọc thành giá trị 0%."""
    oof_map: Dict[str, float] = {}
    sigma_pred = 0.1549
    available = True
    if ML_OOF_FILE.exists():
        try:
            with open(ML_OOF_FILE, "r", encoding="utf-8") as f:
                oof_map = json.load(f)
        except (OSError, ValueError) as exc:
            logger.warning("Không thể đọc dự đoán OOF ML từ %s: %s", ML_OOF_FILE, exc)
            available = False
    else:
        logger.warning("Không tìm thấy dự đoán OOF ML: %s", ML_OOF_FILE)
        available = False
    if ML_METRICS_FILE.exists():
        try:
            with open(ML_METRICS_FILE, "r", encoding="utf-8") as f:
                m = json.load(f)
                sigma_pred = float(m.get("sigma_pred_log", 0.1549))
        except (OSError, ValueError, TypeError) as exc:
            logger.warning("Không thể đọc metadata ML từ %s: %s", ML_METRICS_FILE, exc)
            available = False
    else:
        logger.warning("Không tìm thấy metadata ML: %s", ML_METRICS_FILE)
        available = False
    return oof_map, sigma_pred, available and bool(oof_map)


def is_reference_gap(observed_price_vnd: float, predicted_price_vnd: float, sigma_pred_log: float) -> bool:
    """Apply the one documented reference-gap rule shared by all ML routes."""
    if not all(math.isfinite(float(value)) and float(value) > 0 for value in (observed_price_vnd, predicted_price_vnd, sigma_pred_log)):
        return False
    lower_bound = math.exp(math.log(float(predicted_price_vnd)) - 1.96 * float(sigma_pred_log))
    return bool(15_000_000 <= float(observed_price_vnd) <= 40_000_000 and float(observed_price_vnd) < lower_bound)


def compute_ml_valuation_score(observed_price_vnd: float, predicted_price_vnd: float) -> Tuple[float, bool]:
    """Map an OOF reference-price gap to [0, 1] for optional final ranking.

    Scores outside the documented 15–40M reference-price window are neutral,
    so a less-supported segment can never receive an artificial advantage.
    """
    if not all(math.isfinite(float(value)) and float(value) > 0 for value in (observed_price_vnd, predicted_price_vnd)):
        return 0.5, False
    in_window = 15_000_000 <= float(observed_price_vnd) <= 40_000_000
    if not in_window:
        return 0.5, False
    gap = (float(predicted_price_vnd) - float(observed_price_vnd)) / float(predicted_price_vnd)
    return max(0.0, min(1.0, 0.5 + (gap / 0.5))), True


def apply_ml_assisted_ranking(
    rankings: List[Dict[str, Any]], enabled: bool, weight: float, ml_available: bool,
) -> bool:
    """Add transparent ML support to a TOPSIS ranking without hiding either score."""
    for item in rankings:
        item["topsis_rank"] = item.get("rank")
        score, eligible = compute_ml_valuation_score(
            float(item.get("sale_price_vnd") or 0), float(item.get("ml_predicted_price_vnd") or 0),
        )
        item["ml_valuation_score"] = round(score, 4)
        item["ml_ranking_eligible"] = eligible
        item["recommendation_score"] = round(
            ((1.0 - weight) * float(item.get("topsis_score") or 0)) + (weight * score)
            if enabled and ml_available else float(item.get("topsis_score") or 0),
            4,
        )

    # A zero weight must be semantically identical to pure TOPSIS, not a
    # misleading "ML-assisted" mode with no ML contribution.
    applied = bool(enabled and weight > 0.0 and ml_available and rankings)
    if applied:
        rankings.sort(key=lambda item: (item["recommendation_score"], item["topsis_score"]), reverse=True)
        for rank, item in enumerate(rankings, start=1):
            item["rank"] = rank
    return applied


def build_reference_gap_summary(
    catalog: List[Dict[str, Any]], oof_map: Dict[str, float], sigma_pred_log: float,
) -> Dict[str, Any]:
    """Derive gaps from every OOF/canonical-catalog match, never a truncated top-N list."""
    gaps = []
    for row in catalog:
        product_id = str(row.get("source_product_id") or "")
        try:
            observed = float(row.get("sale_price_vnd") or 0)
            predicted = float(oof_map[product_id])
        except (KeyError, TypeError, ValueError):
            continue
        if not is_reference_gap(observed, predicted, sigma_pred_log):
            continue
        lower_bound = math.exp(math.log(predicted) - 1.96 * sigma_pred_log)
        gaps.append({
            "source_product_id": product_id,
            "product_name": row.get("product_name_raw", "Unknown"),
            "observed_price_vnd": round(observed, -4),
            "predicted_price_vnd": round(predicted, -4),
            "lower_bound_vnd": round(lower_bound, -4),
            "value_gap_percent": round((predicted - observed) / predicted * 100, 2),
            "is_reference_gap": True,
        })
    gaps.sort(key=lambda item: (-item["value_gap_percent"], item["source_product_id"]))
    return {
        "total_evaluated": len(oof_map),
        "screened_count": len(gaps),
        "top_reference_gaps": gaps,
        "disclaimer": "Sàng lọc chênh lệch giá tham chiếu OOF trong khoảng 15–40 triệu; không phải khuyến nghị mua hay đầu tư.",
    }


class ConstraintRequest(BaseModel):
    """Shared validation for ranking and sensitivity request boundaries."""

    _VALID_BRANDS = {"acer", "apple", "asus", "dell", "hp", "lenovo", "msi", "other"}
    _VALID_CPU_FAMILIES = {"core i5", "core i7", "ultra", "ryzen", "snapdragon", "apple", "tất cả"}
    _VALID_SCREEN_SIZES = {"dưới 14 inch", "15.6 inch", "16 inch", "tất cả"}
    _VALID_PANEL_TYPES = {"oled", "ips", "va", "tn", "tất cả"}
    _VALID_OPERATING_SYSTEMS = {"windows", "macos", "tất cả"}

    @model_validator(mode="after")
    def validate_constraints(self):
        for field_name in ("min_budget_vnd", "max_budget_vnd", "min_ram_gb", "min_storage_gb", "min_refresh_rate_hz", "min_brightness_nits"):
            value = getattr(self, field_name, None)
            if value is not None and (not math.isfinite(float(value)) or value < 0):
                raise ValueError(f"{field_name} phải là số hữu hạn không âm.")
        if self.min_budget_vnd > self.max_budget_vnd:
            raise ValueError("min_budget_vnd không được lớn hơn max_budget_vnd.")
        brands = [value for value in [getattr(self, "brand", None)] if value]
        brands.extend(getattr(self, "excluded_brands", None) or [])
        invalid_brands = [brand for brand in brands if brand.strip().lower() not in self._VALID_BRANDS]
        if invalid_brands:
            raise ValueError(f"brand không hợp lệ: {', '.join(invalid_brands)}.")
        for field_name, allowed in (
            ("cpu_family", self._VALID_CPU_FAMILIES),
            ("screen_size", self._VALID_SCREEN_SIZES),
            ("panel_type", self._VALID_PANEL_TYPES),
            ("required_os", self._VALID_OPERATING_SYSTEMS),
        ):
            value = getattr(self, field_name, None)
            if value and value.strip().lower() not in allowed:
                raise ValueError(f"{field_name} không hợp lệ: {value}.")
        return self


class EvaluateRequest(ConstraintRequest):
    preset_key: str = "student_budget"
    min_budget_vnd: float = 0.0
    max_budget_vnd: float = 50_000_000.0
    brand: Optional[str] = None
    cpu_family: Optional[str] = None
    ram_gb: Optional[int] = None
    min_ram_gb: Optional[int] = None
    storage_gb: Optional[int] = None
    min_storage_gb: Optional[int] = None
    excluded_brands: Optional[List[str]] = None
    screen_size: Optional[str] = None
    panel_type: Optional[str] = None
    required_os: Optional[str] = None
    min_refresh_rate_hz: Optional[int] = None
    custom_weights: Optional[List[float]] = None
    min_brightness_nits: Optional[int] = None
    require_rj45_lan: Optional[bool] = None
    require_ram_upgradeable: Optional[bool] = None
    require_type_c_charging: Optional[bool] = None
    require_thunderbolt: Optional[bool] = None
    strict_benchmark: bool = False
    ml_assisted_ranking: bool = False
    ml_ranking_weight: float = DEFAULT_ML_RANKING_WEIGHT

    @model_validator(mode="after")
    def validate_ml_ranking(self):
        if not math.isfinite(self.ml_ranking_weight) or not 0.0 <= self.ml_ranking_weight <= MAX_ML_RANKING_WEIGHT:
            raise ValueError(f"ml_ranking_weight phải nằm trong khoảng 0 đến {MAX_ML_RANKING_WEIGHT}.")
        return self


class SensitivityRequest(ConstraintRequest):
    preset_key: str = "student_budget"
    min_budget_vnd: float = 0.0
    max_budget_vnd: float = 25_000_000.0
    brand: Optional[str] = None
    cpu_family: Optional[str] = None
    ram_gb: Optional[int] = None
    min_ram_gb: Optional[int] = None
    storage_gb: Optional[int] = None
    min_storage_gb: Optional[int] = None
    excluded_brands: Optional[List[str]] = None
    screen_size: Optional[str] = None
    panel_type: Optional[str] = None
    min_refresh_rate_hz: Optional[int] = None
    min_brightness_nits: Optional[int] = None
    require_rj45_lan: Optional[bool] = None
    require_ram_upgradeable: Optional[bool] = None
    require_type_c_charging: Optional[bool] = None
    require_thunderbolt: Optional[bool] = None
    required_os: Optional[str] = None
    strict_benchmark: bool = False
    custom_weights: Optional[List[float]] = None


class RobustnessRequest(SensitivityRequest):
    """Request for a bounded, reproducible Monte Carlo weight analysis."""

    simulations: int = 300
    seed: int = 42
    concentration: float = 80.0

    @model_validator(mode="after")
    def validate_robustness_options(self):
        if not 25 <= self.simulations <= 1000:
            raise ValueError("simulations phải nằm trong khoảng 25 đến 1000.")
        if not math.isfinite(self.concentration) or not 1.0 <= self.concentration <= 1000.0:
            raise ValueError("concentration phải là số hữu hạn trong khoảng 1 đến 1000.")
        return self


class NaturalLanguageRequest(BaseModel):
    prompt: str


@app.get("/api/health")
def health_check():
    return {"status": "ok", "app": "LaptopDSS"}


@app.get("/api/presets")
def get_presets():
    """Return available preset profiles with friendly Vietnamese labels in FPT Shop order."""
    ORDERED_KEYS = ["student_budget", "slim_mobility", "technical_coding", "gaming"]
    results = []
    for k in ORDERED_KEYS:
        if k not in PRESETS:
            continue
        v = PRESETS[k]
        weights, lmax, cr = compute_ahp_weights(v["matrix"])
        criteria_list = []
        for i, (crit_name, crit_dir) in enumerate(v["criteria"]):
            criteria_list.append({
                "key": crit_name,
                "direction": crit_dir,
                "weight": round(weights[i], 4),
                "weight_percent": round(weights[i] * 100, 1),
            })
        results.append({
            "key": k,
            "name": v["name"],
            "description": v["description"],
            "cr": round(cr, 4),
            "cr_valid": cr < 0.10,
            "criteria": criteria_list,
        })
    return results


@app.get("/api/laptops")
def get_all_laptops():
    """Return all standardized laptops with verified local image paths."""
    laptops = load_standardized_laptops()
    for l in laptops:
        pid = l.get("source_product_id")
        img_file = IMG_DIR / f"{pid}.png"
        if img_file.exists():
            l["image_url"] = f"/images/{pid}.png"
            l["image_type"] = "official" if "m5" not in str(l.get("product_name_raw", "")).lower() and "neo" not in str(l.get("product_name_raw", "")).lower() else "concept"
        else:
            l["image_url"] = "/images/laptop_fallback.png"
            l["image_type"] = "illustration"
    return laptops


@app.post("/api/parse-requirement")
def parse_natural_language_requirement(req: NaturalLanguageRequest):
    """Bóc tách câu yêu cầu tiếng Việt thành preset và bộ lọc minh bạch."""
    if not req.prompt.strip():
        raise HTTPException(status_code=400, detail="Yêu cầu tìm kiếm không được để trống.")
    return parse_requirement(req.prompt)


def apply_catalog_filters(candidates: List[Dict[str, Any]], req: Any) -> List[Dict[str, Any]]:
    """Áp dụng một nguồn bộ lọc cho xếp hạng và kiểm định độ nhạy."""
    if req.brand and req.brand != "Tất cả":
        candidates = [c for c in candidates if req.brand.lower() in c.get("product_name_raw", "").lower()]
    if req.cpu_family and req.cpu_family != "Tất cả":
        candidates = [c for c in candidates if req.cpu_family.lower() in c.get("cpu_name_normalized", "").lower()]
    if req.ram_gb:
        candidates = [c for c in candidates if str(c.get("ram_gb", "")) == str(req.ram_gb)]
    if getattr(req, "min_ram_gb", None):
        candidates = [c for c in candidates if int(c.get("ram_gb") or 0) >= req.min_ram_gb]
    if req.storage_gb:
        candidates = [c for c in candidates if str(int(float(c.get("storage_total_gb", 0) or 0))) == str(req.storage_gb)]
    if getattr(req, "min_storage_gb", None):
        candidates = [c for c in candidates if int(float(c.get("storage_total_gb", 0) or 0)) >= req.min_storage_gb]
    if getattr(req, "excluded_brands", None):
        candidates = [c for c in candidates if not any(brand.lower() in c.get("product_name_raw", "").lower() for brand in req.excluded_brands)]
    if req.screen_size and req.screen_size != "Tất cả":
        if "14" in req.screen_size:
            candidates = [c for c in candidates if float(c.get("screen_size_inch") or 0) <= 14.5]
        elif "15" in req.screen_size:
            candidates = [c for c in candidates if 14.5 < float(c.get("screen_size_inch") or 0) <= 15.6]
        elif "16" in req.screen_size:
            candidates = [c for c in candidates if float(c.get("screen_size_inch") or 0) > 15.6]
    if req.panel_type and req.panel_type != "Tất cả":
        candidates = [c for c in candidates if req.panel_type.lower() in (c.get("panel_type") or "").lower()]
    if req.min_brightness_nits:
        candidates = [c for c in candidates if float(c.get("brightness_nits") or 0) >= req.min_brightness_nits]
    if req.require_rj45_lan:
        candidates = [c for c in candidates if str(c.get("lan_present", "")).lower() == "true"]
    if req.require_ram_upgradeable:
        candidates = [c for c in candidates if int(c.get("ram_slots_free") or 0) >= 1 or int(c.get("ram_slots") or 0) >= 2 or int(c.get("max_ram_gb") or 0) > int(c.get("ram_gb") or 0)]
    if req.require_type_c_charging:
        candidates = [c for c in candidates if str(c.get("type_c_charging", "")).lower() == "true"]
    if req.require_thunderbolt:
        candidates = [c for c in candidates if str(c.get("thunderbolt_present", "")).lower() == "true"]
    return candidates


def summarize_filter_data_quality(candidates: List[Dict[str, Any]], req: Any) -> List[Dict[str, Any]]:
    """Expose unknown specs whenever a verified-only filter is active."""
    summaries: List[Dict[str, Any]] = []

    def add_boolean_filter(request_field: str, catalog_field: str, label: str) -> None:
        if not getattr(req, request_field, False):
            return
        values = [str(item.get(catalog_field, "")).strip().lower() for item in candidates]
        verified = sum(value == "true" for value in values)
        unknown = sum(not value for value in values)
        summaries.append({
            "filter": request_field,
            "label": label,
            "policy": "verified_only",
            "verified_count": verified,
            "known_false_count": len(values) - verified - unknown,
            "unknown_count": unknown,
        })

    add_boolean_filter("require_rj45_lan", "lan_present", "Cổng mạng LAN RJ45")
    add_boolean_filter("require_type_c_charging", "type_c_charging", "Sạc USB-C / Power Delivery")
    add_boolean_filter("require_thunderbolt", "thunderbolt_present", "Thunderbolt / USB4")

    if getattr(req, "require_ram_upgradeable", False):
        statuses = []
        for item in candidates:
            fields = (item.get("ram_slots_free", ""), item.get("ram_slots", ""), item.get("max_ram_gb", ""))
            if not any(str(value).strip() for value in fields):
                statuses.append("unknown")
            elif int(item.get("ram_slots_free") or 0) >= 1 or int(item.get("ram_slots") or 0) >= 2 or int(item.get("max_ram_gb") or 0) > int(item.get("ram_gb") or 0):
                statuses.append("true")
            else:
                statuses.append("false")
        summaries.append({
            "filter": "require_ram_upgradeable",
            "label": "Khả năng nâng cấp RAM",
            "policy": "verified_only",
            "verified_count": statuses.count("true"),
            "known_false_count": statuses.count("false"),
            "unknown_count": statuses.count("unknown"),
        })

    if getattr(req, "min_brightness_nits", None):
        values = [item.get("brightness_nits", "").strip() for item in candidates]
        verified = sum(float(value) >= req.min_brightness_nits for value in values if value)
        unknown = sum(not value for value in values)
        summaries.append({
            "filter": "min_brightness_nits",
            "label": f"Độ sáng ≥ {req.min_brightness_nits} nits",
            "policy": "verified_only",
            "verified_count": verified,
            "known_false_count": len(values) - verified - unknown,
            "unknown_count": unknown,
        })
    return summaries


@app.post("/api/evaluate")
def evaluate_laptops(req: EvaluateRequest):
    """Run pure in-memory AHP + TOPSIS evaluation on qualified laptops."""
    if req.preset_key not in PRESETS:
        raise HTTPException(status_code=400, detail=f"Preset không hợp lệ: {req.preset_key}")
    catalog = load_standardized_laptops()
    filter_data_quality = summarize_filter_data_quality(catalog, req)
    candidates = apply_catalog_filters(catalog, req)

    # Chạy thuật toán chuẩn TOPSIS + AHP (hoặc Direct Rating khi có custom_weights)
    try:
        res = evaluate(
            candidates=candidates,
            preset_key=req.preset_key,
            min_budget_vnd=req.min_budget_vnd,
            max_budget_vnd=req.max_budget_vnd,
            min_ram_gb=req.min_ram_gb,
            min_storage_gb=req.min_storage_gb,
            min_refresh_rate_hz=req.min_refresh_rate_hz,
            required_os=req.required_os if req.required_os != "Tất cả" else None,
            custom_weights=req.custom_weights,
            strict_benchmark=req.strict_benchmark,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Gán đường dẫn ảnh local & Thẩm định giá ML bằng OOF.
    oof_map, sigma_pred, ml_available = get_ml_enrichment()
    for l in res["rankings"]:
        pid = l.get("source_product_id")
        img_file = IMG_DIR / f"{pid}.png"
        if img_file.exists():
            l["image_url"] = f"/images/{pid}.png"
            l["image_type"] = "official" if "m5" not in str(l.get("product_name_raw", "")).lower() and "neo" not in str(l.get("product_name_raw", "")).lower() else "concept"
        else:
            l["image_url"] = "/images/laptop_fallback.png"
            l["image_type"] = "illustration"

        # Tích hợp định giá ML ngoại tuyến (OOF)
        pred_p = oof_map.get(pid)
        obs_p = float(l.get("sale_price_vnd") or 0)
        if pred_p and obs_p > 0:
            l["ml_predicted_price_vnd"] = round(float(pred_p), -4)
            log_p = math.log(float(pred_p))
            lower_b = math.exp(log_p - 1.96 * sigma_pred)
            upper_b = math.exp(log_p + 1.96 * sigma_pred)
            l["ml_lower_bound_vnd"] = round(lower_b, -4)
            l["ml_upper_bound_vnd"] = round(upper_b, -4)
            gap = (float(pred_p) - obs_p) / float(pred_p) * 100
            l["ml_value_gap_percent"] = round(gap, 1)
            # A reference-price gap is exploratory, not a buying recommendation.
            # The <15M segment has too few samples and >=40M has wider uncertainty.
            l["is_reference_gap"] = is_reference_gap(obs_p, pred_p, sigma_pred)
            l["is_good_deal"] = l["is_reference_gap"]  # backwards-compatible field for existing clients
        else:
            l["ml_predicted_price_vnd"] = None
            l["ml_lower_bound_vnd"] = None
            l["ml_upper_bound_vnd"] = None
            l["ml_value_gap_percent"] = None
            l["is_reference_gap"] = False
            l["is_good_deal"] = False

    ml_ranking_applied = apply_ml_assisted_ranking(
        res["rankings"], req.ml_assisted_ranking, req.ml_ranking_weight, ml_available,
    )
    res["pairwise_matrix"] = PRESETS[req.preset_key]["matrix"]
    res["ml_status"] = {
        "available": ml_available,
        "message": None if ml_available else "Không đủ dữ liệu thẩm định ML.",
    }
    res["ranking_mode"] = "ml_assisted" if ml_ranking_applied else "topsis_only"
    res["ml_ranking_weight"] = req.ml_ranking_weight if ml_ranking_applied else 0.0
    if ml_ranking_applied:
        topsis_percent = round((1.0 - req.ml_ranking_weight) * 100)
        ml_percent = round(req.ml_ranking_weight * 100)
        res["ml_ranking_note"] = (
            f"Điểm đề xuất = {topsis_percent}% TOPSIS phù hợp nhu cầu + "
            f"{ml_percent}% điểm định giá OOF. Ngoài khoảng giá 15–40 triệu, "
            "phần ML giữ điểm trung tính 0.5."
        )
    else:
        res["ml_ranking_note"] = "Xếp hạng chỉ dùng TOPSIS; ML chỉ hiển thị thẩm định giá."
    res["filter_data_quality"] = filter_data_quality
    return res


@app.post("/api/sensitivity")
def get_sensitivity(req: SensitivityRequest):
    """Evaluate budget and weight sensitivity (§8.4 Chuongtrinh.md)."""
    if req.preset_key not in PRESETS:
        raise HTTPException(status_code=400, detail=f"Invalid preset: {req.preset_key}")

    catalog = load_standardized_laptops()
    filter_data_quality = summarize_filter_data_quality(catalog, req)
    laptops = apply_catalog_filters(catalog, req)
    try:
        budget_sens = analyze_budget_sensitivity(
            laptops, preset_key=req.preset_key, current_max_budget=req.max_budget_vnd,
            min_budget_vnd=req.min_budget_vnd, min_ram_gb=req.min_ram_gb,
            min_storage_gb=req.min_storage_gb, min_refresh_rate_hz=req.min_refresh_rate_hz,
            required_os=req.required_os if req.required_os != "Tất cả" else None,
            strict_benchmark=req.strict_benchmark, custom_weights=req.custom_weights,
        )
        weight_sens = analyze_weight_sensitivity(
            laptops, preset_key=req.preset_key, max_budget_vnd=req.max_budget_vnd,
            min_budget_vnd=req.min_budget_vnd, min_ram_gb=req.min_ram_gb,
            min_storage_gb=req.min_storage_gb, min_refresh_rate_hz=req.min_refresh_rate_hz,
            required_os=req.required_os if req.required_os != "Tất cả" else None,
            strict_benchmark=req.strict_benchmark, custom_weights=req.custom_weights,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    return {
        "preset_key": req.preset_key,
        "ranking_mode": "topsis_only",
        "analysis_note": "Kiểm định độ nhạy chỉ đánh giá TOPSIS thuần; không kiểm định lớp ML-assisted tùy chọn.",
        "budget_sensitivity": budget_sens,
        "weight_sensitivity": weight_sens,
        "filter_data_quality": filter_data_quality,
    }


@app.post("/api/robustness")
def get_robustness(req: RobustnessRequest):
    """Run reproducible Monte Carlo TOPSIS robustness without changing ranking."""
    if req.preset_key not in PRESETS:
        raise HTTPException(status_code=400, detail=f"Invalid preset: {req.preset_key}")

    catalog = load_standardized_laptops()
    filter_data_quality = summarize_filter_data_quality(catalog, req)
    laptops = apply_catalog_filters(catalog, req)
    try:
        result = analyze_monte_carlo_stability(
            laptops,
            preset_key=req.preset_key,
            max_budget_vnd=req.max_budget_vnd,
            simulations=req.simulations,
            seed=req.seed,
            concentration=req.concentration,
            min_budget_vnd=req.min_budget_vnd,
            min_ram_gb=req.min_ram_gb,
            min_storage_gb=req.min_storage_gb,
            min_refresh_rate_hz=req.min_refresh_rate_hz,
            required_os=req.required_os if req.required_os != "Tất cả" else None,
            strict_benchmark=req.strict_benchmark,
            custom_weights=req.custom_weights,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return {
        "preset_key": req.preset_key,
        "ranking_mode": "topsis_only",
        "analysis_note": "Monte Carlo chỉ lấy mẫu trọng số AHP/Direct Rating cho TOPSIS thuần; không kiểm định lớp ML-assisted tùy chọn.",
        "filter_data_quality": filter_data_quality,
        **result,
    }


@app.get("/api/ml_valuation")
def get_ml_valuation():
    """Retrieve ML metrics and an all-catalog OOF reference-gap screening (§6.4)."""
    metrics_file = ML_METRICS_FILE
    if not metrics_file.exists():
        return {"available": False, "message": "Không đủ dữ liệu thẩm định ML."}
    try:
        with open(metrics_file, "r", encoding="utf-8") as f:
            metrics = json.load(f)
        oof_map, sigma_pred, available = get_ml_enrichment()
        if not available:
            return {"available": False, "message": "Không đủ dữ liệu thẩm định ML."}
        metrics.pop("good_deals_summary", None)  # Legacy top-10 output is not a complete screening population.
        metrics["reference_gap_summary"] = build_reference_gap_summary(
            load_standardized_laptops(), oof_map, sigma_pred,
        )
        return {"available": True, **metrics}
    except (OSError, ValueError) as exc:
        logger.warning("Không thể đọc báo cáo ML từ %s: %s", metrics_file, exc)
        return {"available": False, "message": "Không đủ dữ liệu thẩm định ML."}


class PredictPriceRequest(BaseModel):
    cpu_benchmark_multi: Optional[float] = None
    cpu_benchmark_single: Optional[float] = None
    cpu_cores: Optional[float] = None
    gpu_benchmark_time_spy: Optional[float] = None
    gpu_benchmark_compute: Optional[float] = None
    is_discrete_gpu: Optional[bool] = False
    gpu_vram_gb: Optional[float] = None
    ram_gb: Optional[float] = None
    storage_total_gb: Optional[float] = None
    screen_size_inch: Optional[float] = None
    screen_width_px: Optional[int] = None
    screen_height_px: Optional[int] = None
    is_oled_panel: Optional[bool] = False
    refresh_rate_hz: Optional[float] = None
    brightness_nits: Optional[float] = None
    battery_capacity_wh: Optional[float] = None
    weight_kg: Optional[float] = None
    is_macos: Optional[bool] = False
    brand: Optional[str] = "Other"
    observed_price_vnd: Optional[float] = None

    @field_validator("brand")
    @classmethod
    def normalize_brand(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        canonical = {brand.lower(): brand for brand in ("Acer", "Apple", "Asus", "Dell", "HP", "Lenovo", "MSI", "Other")}
        normalized = canonical.get(value.strip().lower())
        if normalized is None:
            raise ValueError("brand không hợp lệ.")
        return normalized

    @model_validator(mode="after")
    def validate_physical_inputs(self):
        numeric_fields = (
            "cpu_benchmark_multi", "cpu_benchmark_single", "cpu_cores",
            "gpu_benchmark_time_spy", "gpu_benchmark_compute", "gpu_vram_gb",
            "ram_gb", "storage_total_gb", "screen_size_inch", "screen_width_px",
            "screen_height_px", "refresh_rate_hz", "brightness_nits",
            "battery_capacity_wh", "weight_kg", "observed_price_vnd",
        )
        for field_name in numeric_fields:
            value = getattr(self, field_name)
            if value is not None and (not math.isfinite(float(value)) or value < 0):
                raise ValueError(f"{field_name} phải là số hữu hạn không âm.")
        if not self.is_discrete_gpu and self.gpu_vram_gb not in (None, 0):
            raise ValueError("GPU tích hợp không được khai báo VRAM rời.")
        return self


def build_prediction_vector(req: PredictPriceRequest, feature_names: List[str]) -> np.ndarray:
    """Build prediction input by persisted feature names, never positional assumptions."""
    mp = ((req.screen_width_px * req.screen_height_px) / 1e6
          if req.screen_width_px and req.screen_height_px else np.nan)
    values = {
        "cpu_benchmark_multi": req.cpu_benchmark_multi if req.cpu_benchmark_multi is not None else np.nan,
        "cpu_benchmark_single": req.cpu_benchmark_single if req.cpu_benchmark_single is not None else np.nan,
        "cpu_benchmark_missing": 1.0 if req.cpu_benchmark_multi is None else 0.0,
        "cpu_cores": req.cpu_cores if req.cpu_cores is not None else np.nan,
        "gpu_benchmark_time_spy": req.gpu_benchmark_time_spy if req.gpu_benchmark_time_spy is not None else (0.0 if not req.is_discrete_gpu else np.nan),
        "gpu_benchmark_compute": req.gpu_benchmark_compute if req.gpu_benchmark_compute is not None else np.nan,
        "is_discrete_gpu": 1.0 if req.is_discrete_gpu else 0.0,
        "gpu_vram_gb": req.gpu_vram_gb if req.gpu_vram_gb is not None else (0.0 if not req.is_discrete_gpu else np.nan),
        "ram_gb": req.ram_gb if req.ram_gb is not None else np.nan,
        "storage_total_gb": req.storage_total_gb if req.storage_total_gb is not None else np.nan,
        "screen_size_inch": req.screen_size_inch if req.screen_size_inch is not None else np.nan,
        "screen_pixels_mp": mp,
        "is_oled_panel": 1.0 if req.is_oled_panel else 0.0,
        "refresh_rate_hz": req.refresh_rate_hz if req.refresh_rate_hz is not None else np.nan,
        "brightness_nits": req.brightness_nits if req.brightness_nits is not None else np.nan,
        "battery_capacity_wh": req.battery_capacity_wh if req.battery_capacity_wh is not None else np.nan,
        "weight_kg": req.weight_kg if req.weight_kg is not None else np.nan,
        "is_macos": 1.0 if req.is_macos else 0.0,
    }
    values.update({name: 1.0 if name == f"brand_{req.brand}" else 0.0 for name in feature_names if name.startswith("brand_")})
    unknown = [name for name in feature_names if name not in values]
    if unknown:
        raise ValueError(f"Artifact ML chứa feature không được API hỗ trợ: {', '.join(unknown)}")
    return np.array([[values[name] for name in feature_names]], dtype=float)


@app.post("/api/predict_price")
def predict_price(req: PredictPriceRequest):
    """Real-time ML laptop price valuation and prediction interval inference (§6.4 Chuongtrinh.md)."""
    model_file = ARTIFACTS_DIR / "price_model.joblib"
    if not model_file.exists():
        raise HTTPException(status_code=503, detail="ML pipeline not trained yet")

    pipeline = get_model_pipeline(model_file)
    model = pipeline["model"]
    imputer = pipeline["imputer"]
    sigma_pred = pipeline["sigma_pred"]
    try:
        raw_vec = build_prediction_vector(req, pipeline["feature_names"])
    except ValueError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    scaler = pipeline.get("scaler")
    if scaler is not None:
        scaled_vec = scaler.transform(raw_vec)
        imputed_vec = imputer.transform(scaled_vec)
    else:
        imputed_vec = imputer.transform(raw_vec)

    pred_log = float(model.predict(imputed_vec)[0])
    pred_price = float(np.exp(pred_log))

    lower_bound = float(np.exp(pred_log - 1.96 * sigma_pred))
    upper_bound = float(np.exp(pred_log + 1.96 * sigma_pred))

    res = {
        "model_name": pipeline["model_name"],
        "predicted_price_vnd": round(pred_price, -4),
        "lower_bound_95_vnd": round(lower_bound, -4),
        "upper_bound_95_vnd": round(upper_bound, -4),
        "sigma_pred_log": round(sigma_pred, 4),
    }

    if req.observed_price_vnd and req.observed_price_vnd > 0:
        val_gap = (pred_price - req.observed_price_vnd) / pred_price
        res["observed_price_vnd"] = req.observed_price_vnd
        res["value_gap_percent"] = round(val_gap * 100, 2)
        res["is_reference_gap"] = is_reference_gap(req.observed_price_vnd, pred_price, sigma_pred)
        res["is_good_deal"] = res["is_reference_gap"]  # backwards-compatible field

    return res


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
