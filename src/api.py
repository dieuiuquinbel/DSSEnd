"""REST API của LaptopDSS phục vụ giao diện React.

Module tích hợp bộ phân tích yêu cầu tiếng Việt, AHP-TOPSIS (D05, D10, D14),
catalog chuẩn hóa và định giá ML. API nhận bộ lọc hoặc câu yêu cầu tự nhiên,
trả xếp hạng, độ nhạy, thẩm định giá và đường dẫn ảnh cục bộ cho giao diện.
"""

import sys
import math
import json
import logging
from pathlib import Path
from typing import List, Optional, Dict, Tuple, Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from dss_ranking import (
    PRESETS,
    analyze_budget_sensitivity,
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

ML_OOF_FILE = ROOT / "data" / "processed" / "ml_oof_predictions.json"
ML_METRICS_FILE = ROOT / "data" / "processed" / "ml_metrics.json"

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


class EvaluateRequest(BaseModel):
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


class SensitivityRequest(BaseModel):
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


@app.post("/api/evaluate")
def evaluate_laptops(req: EvaluateRequest):
    """Run pure in-memory AHP + TOPSIS evaluation on qualified laptops."""
    candidates = apply_catalog_filters(load_standardized_laptops(), req)

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

    # Gán đường dẫn ảnh local & Thẩm định giá ML (§6.4 Chuongtrinh.md & D10)
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
            l["is_good_deal"] = bool(obs_p < lower_b)
        else:
            l["ml_predicted_price_vnd"] = None
            l["ml_lower_bound_vnd"] = None
            l["ml_upper_bound_vnd"] = None
            l["ml_value_gap_percent"] = None
            l["is_good_deal"] = False

    res["pairwise_matrix"] = PRESETS[req.preset_key]["matrix"]
    res["ml_status"] = {
        "available": ml_available,
        "message": None if ml_available else "Không đủ dữ liệu thẩm định ML.",
    }
    return res


@app.post("/api/sensitivity")
def get_sensitivity(req: SensitivityRequest):
    """Evaluate budget and weight sensitivity (§8.4 Chuongtrinh.md)."""
    if req.preset_key not in PRESETS:
        raise HTTPException(status_code=400, detail=f"Invalid preset: {req.preset_key}")

    laptops = apply_catalog_filters(load_standardized_laptops(), req)
    budget_sens = analyze_budget_sensitivity(
        laptops,
        preset_key=req.preset_key,
        current_max_budget=req.max_budget_vnd,
        min_budget_vnd=req.min_budget_vnd,
        min_ram_gb=req.min_ram_gb,
        min_storage_gb=req.min_storage_gb,
        min_refresh_rate_hz=req.min_refresh_rate_hz,
        required_os=req.required_os if req.required_os != "Tất cả" else None,
        strict_benchmark=req.strict_benchmark,
    )
    weight_sens = analyze_weight_sensitivity(
        laptops,
        preset_key=req.preset_key,
        max_budget_vnd=req.max_budget_vnd,
        min_budget_vnd=req.min_budget_vnd,
        min_ram_gb=req.min_ram_gb,
        min_storage_gb=req.min_storage_gb,
        min_refresh_rate_hz=req.min_refresh_rate_hz,
        required_os=req.required_os if req.required_os != "Tất cả" else None,
        strict_benchmark=req.strict_benchmark,
    )

    return {
        "preset_key": req.preset_key,
        "budget_sensitivity": budget_sens,
        "weight_sensitivity": weight_sens,
    }


@app.get("/api/ml_valuation")
def get_ml_valuation():
    """Retrieve ML fair price valuation metrics, SHAP drivers, and Good Deals (§6.4 GĐ4)."""
    metrics_file = ROOT / "data" / "processed" / "ml_metrics.json"
    if not metrics_file.exists():
        return {"available": False, "message": "Không đủ dữ liệu thẩm định ML."}
    try:
        with open(metrics_file, "r", encoding="utf-8") as f:
            return {"available": True, **json.load(f)}
    except (OSError, ValueError) as exc:
        logger.warning("Không thể đọc báo cáo ML từ %s: %s", metrics_file, exc)
        return {"available": False, "message": "Không đủ dữ liệu thẩm định ML."}


class PredictPriceRequest(BaseModel):
    cpu_benchmark_multi: Optional[float] = None
    cpu_benchmark_single: Optional[float] = None
    cpu_cores: Optional[float] = None
    gpu_benchmark_time_spy: Optional[float] = None
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


@app.post("/api/predict_price")
def predict_price(req: PredictPriceRequest):
    """Real-time ML laptop price valuation and prediction interval inference (§6.4 Chuongtrinh.md)."""
    model_file = ROOT / "data" / "processed" / "laptop_price_pipeline.joblib"
    if not model_file.exists():
        raise HTTPException(status_code=503, detail="ML pipeline not trained yet")

    import joblib
    import numpy as np
    pipeline = joblib.load(model_file)
    model = pipeline["model"]
    imputer = pipeline["imputer"]
    brands_list = pipeline["brands_list"]
    sigma_pred = pipeline["sigma_pred"]

    # Compute screen pixels MP
    if req.screen_width_px and req.screen_height_px:
        mp = (req.screen_width_px * req.screen_height_px) / 1e6
    else:
        mp = np.nan

    cpu_missing = 1.0 if req.cpu_benchmark_multi is None else 0.0

    num_vec = [
        req.cpu_benchmark_multi if req.cpu_benchmark_multi is not None else np.nan,
        req.cpu_benchmark_single if req.cpu_benchmark_single is not None else np.nan,
        cpu_missing,
        req.cpu_cores if req.cpu_cores is not None else np.nan,
        req.gpu_benchmark_time_spy if req.gpu_benchmark_time_spy is not None else (0.0 if not req.is_discrete_gpu else np.nan),
        1.0 if req.is_discrete_gpu else 0.0,
        req.gpu_vram_gb if req.gpu_vram_gb is not None else (0.0 if not req.is_discrete_gpu else np.nan),
        req.ram_gb if req.ram_gb is not None else np.nan,
        req.storage_total_gb if req.storage_total_gb is not None else np.nan,
        req.screen_size_inch if req.screen_size_inch is not None else np.nan,
        mp,
        1.0 if req.is_oled_panel else 0.0,
        req.refresh_rate_hz if req.refresh_rate_hz is not None else np.nan,
        req.brightness_nits if req.brightness_nits is not None else np.nan,
        req.battery_capacity_wh if req.battery_capacity_wh is not None else np.nan,
        req.weight_kg if req.weight_kg is not None else np.nan,
        1.0 if req.is_macos else 0.0,
    ]
    brand_vec = [1.0 if req.brand == b else 0.0 for b in brands_list]
    raw_vec = np.array([num_vec + brand_vec], dtype=float)

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
        res["is_good_deal"] = bool(req.observed_price_vnd < lower_bound)

    return res


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
