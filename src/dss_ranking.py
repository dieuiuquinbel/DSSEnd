"""Động cơ AHP-TOPSIS của LaptopDSS.

Module thực hiện preset nhu cầu, trọng số AHP, hàm Fit RAM/SSD, xếp hạng
TOPSIS và phân tích độ nhạy. Đầu vào là catalog chuẩn hóa cùng ràng buộc; đầu
ra là xếp hạng, lý do loại trừ và chỉ số kiểm định theo D05, D14.
"""

import csv
import math
import random
from functools import lru_cache
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple


ROOT = Path(__file__).resolve().parents[1]
STANDARDIZED_CSV = ROOT / "data" / "catalog" / "laptops.csv"

# Random Consistency Index (RI) table for AHP
RI = {1: 0.0, 2: 0.0, 3: 0.58, 4: 0.90, 5: 1.12, 6: 1.24, 7: 1.32, 8: 1.41}


def compute_fit_score(
    val: float,
    threshold: float,
    cap: float,
    cap_bonus: float = 0.20,
    tail_rate: float = 0.05,
) -> float:
    """Explicit piecewise utility function for Fit criteria (RAM / Storage).
    
    Calibration notes:
    - Designed specifically for laptop workloads to represent diminishing returns.
    - Calibrated across the full catalog (8 GB, 16 GB, 32 GB, 64 GB for RAM; 256 GB, 512 GB, 1 TB for Storage).
    - Represents developer and student multitasking needs realistically.
    
    Formula:
    - val <= 0: 0.0
    - 0 < val <= threshold: val / threshold
    - threshold < val <= cap: 1.0 + cap_bonus * ((val - threshold) / (cap - threshold))
    - val > cap: 1.0 + cap_bonus + tail_rate * ((val - cap) / cap)
    """
    if val <= 0.0:
        return 0.0
    if val <= threshold:
        return val / threshold
    if val <= cap:
        denom = cap - threshold
        return 1.0 + (cap_bonus * ((val - threshold) / denom) if denom > 0 else 0.0)
    return 1.0 + cap_bonus + tail_rate * ((val - cap) / cap)


def compute_ahp_weights(matrix: List[List[float]]) -> Tuple[List[float], float, float]:
    """Calculate normalized weights and Consistency Ratio (CR) from an AHP pairwise matrix.
    
    Returns:
        weights: list of normalized weights summing to 1.0
        lambda_max: principal eigenvalue
        cr: Consistency Ratio
    """
    n = len(matrix)
    if n <= 2:
        weights = [1.0 / n] * n
        return weights, float(n), 0.0

    # Geometric mean method for priority vector
    geom_means = []
    for row in matrix:
        prod = 1.0
        for val in row:
            prod *= val
        geom_means.append(prod ** (1.0 / n))

    sum_geom = sum(geom_means)
    weights = [gm / sum_geom for gm in geom_means]

    # Calculate lambda_max: average of (A * w)_i / w_i
    lambda_max = 0.0
    for i in range(n):
        aw_i = sum(matrix[i][j] * weights[j] for j in range(n))
        lambda_max += aw_i / weights[i]
    lambda_max /= n

    ci = (lambda_max - n) / (n - 1)
    cr = ci / RI.get(n, 1.41) if RI.get(n, 1.41) > 0 else 0.0

    return weights, lambda_max, cr


# -------------------------------------------------------------
# Preset Definitions
# -------------------------------------------------------------
PRESETS = {
    "student_budget": {
        "name": "Sinh viên & Kinh tế",
        "description": "Tối ưu hóa ngân sách eo hẹp cho học tập: ưu tiên mức giá thấp nhất, CPU đơn nhân đáp ứng mượt mà tác vụ học tập/văn phòng, RAM vừa vặn, không quá nặng.",
        "criteria": [
            ("sale_price_vnd", "cost"),
            ("cpu_benchmark_single_core", "benefit"),
            ("ram_gb", "fit"),
            ("weight_kg", "cost"),
            ("storage_total_gb", "fit"),
        ],
        # Exact 5x5 pairwise comparison matrix (Order: Price, CPU Single-Core, RAM, Weight, Storage) - CR = 0.0074
        "matrix": [
            [1.0,      2.0,      3.0,      3.0,      4.0],
            [1.0/2.0,  1.0,      2.0,      2.0,      3.0],
            [1.0/3.0,  1.0/2.0,  1.0,      1.0,      2.0],
            [1.0/3.0,  1.0/2.0,  1.0,      1.0,      2.0],
            [1.0/4.0,  1.0/3.0,  1.0/2.0,  1.0/2.0,  1.0],
        ],
        "fit_params": {
            "ram_gb": {"threshold": 8.0, "cap": 16.0, "cap_bonus": 0.10, "tail_rate": 0.02},
            "storage_total_gb": {"threshold": 256.0, "cap": 512.0, "cap_bonus": 0.10, "tail_rate": 0.02},
        },
        "base_filter": lambda row: (
            row.get("gpu_type") != "discrete" or float(row.get("weight_kg") or 99) <= 1.85
        ),
    },
    "slim_mobility": {
        "name": "Mỏng nhẹ & Di động",
        "description": "Ưu tiên trọng lượng siêu nhẹ dưới 1.45kg và kích thước gọn gàng cho người thường xuyên di chuyển.",
        "criteria": [
            ("weight_kg", "cost"),
            ("sale_price_vnd", "cost"),
            ("cpu_benchmark_multi_core", "benefit"),
            ("ram_gb", "fit"),
            ("storage_total_gb", "fit"),
        ],
        # Exact 5x5 pairwise matrix (Order: Weight, Price, CPU, RAM, Storage) - CR = 0.0164
        "matrix": [
            [1.0,      2.0,      3.0,      4.0,      5.0],
            [1.0/2.0,  1.0,      2.0,      3.0,      3.0],
            [1.0/3.0,  1.0/2.0,  1.0,      2.0,      2.0],
            [1.0/4.0,  1.0/3.0,  1.0/2.0,  1.0,      2.0],
            [1.0/5.0,  1.0/3.0,  1.0/2.0,  1.0/2.0,  1.0],
        ],
        "fit_params": {
            "ram_gb": {"threshold": 8.0, "cap": 16.0, "cap_bonus": 0.10, "tail_rate": 0.02},
            "storage_total_gb": {"threshold": 256.0, "cap": 512.0, "cap_bonus": 0.10, "tail_rate": 0.02},
        },
        "base_filter": lambda row: float(row.get("weight_kg") or 99) <= 1.45,
    },
    "technical_coding": {
        "name": "Kỹ thuật & Lập trình",
        "description": "Dùng ngân sách làm ràng buộc tối đa; ưu tiên CPU đa nhân để compile/build mã nguồn, RAM cho máy ảo/container, rồi đến SSD. Giá chỉ là tiêu chí phụ sau khi máy đã nằm trong ngân sách.",
        "criteria": [
            ("cpu_benchmark_multi_core", "benefit"),
            ("ram_gb", "fit"),
            ("sale_price_vnd", "cost"),
            ("storage_total_gb", "fit"),
            ("weight_kg", "cost"),
        ],
        # Exact 5x5 matrix (Order: CPU, RAM, Price, Storage, Weight) - CR = 0.0152.
        # Khi người dùng đã chọn trần ngân sách, CPU/RAM cần được ưu tiên hơn chênh lệch giá
        # giữa các máy đều hợp lệ. Price vẫn giữ vai trò cost criterion, không bị loại bỏ.
        "matrix": [
            [1.0,      2.0,      5.0,      3.0,      5.0],
            [1.0/2.0,  1.0,      3.0,      2.0,      4.0],
            [1.0/5.0,  1.0/3.0,  1.0,      1.0/2.0,  2.0],
            [1.0/3.0,  1.0/2.0,  2.0,      1.0,      3.0],
            [1.0/5.0,  1.0/4.0,  1.0/2.0,  1.0/3.0,  1.0],
        ],
        "fit_params": {
            "ram_gb": {"threshold": 16.0, "cap": 32.0, "cap_bonus": 0.25, "tail_rate": 0.05},
            "storage_total_gb": {"threshold": 512.0, "cap": 1024.0, "cap_bonus": 0.20, "tail_rate": 0.05},
        },
        "base_filter": lambda row: True,
    },
    "gaming": {
        "name": "Gaming & Đồ họa nặng",
        "description": "Ưu tiên card đồ họa rời mạnh, CPU đa nhân cao, màn hình tần số quét cao (>= 144Hz); chỉ áp dụng cho máy Windows dGPU.",
        "criteria": [
            ("gpu_benchmark_time_spy", "benefit"),
            ("cpu_benchmark_multi_core", "benefit"),
            ("sale_price_vnd", "cost"),
            ("ram_gb", "fit"),
            ("storage_total_gb", "fit"),
        ],
        # Exact 5x5 pairwise comparison matrix (Order: GPU, CPU, Price, RAM, Storage) - CR = 0.0152
        "matrix": [
            [1.0,      2.0,      3.0,      4.0,      5.0],
            [1.0/2.0,  1.0,      2.0,      3.0,      4.0],
            [1.0/3.0,  1.0/2.0,  1.0,      2.0,      3.0],
            [1.0/4.0,  1.0/3.0,  1.0/2.0,  1.0,      2.0],
            [0.2,      1.0/4.0,  1.0/3.0,  1.0/2.0,  1.0],
        ],
        "fit_params": {
            "ram_gb": {"threshold": 16.0, "cap": 32.0, "cap_bonus": 0.20, "tail_rate": 0.05},
            "storage_total_gb": {"threshold": 512.0, "cap": 1024.0, "cap_bonus": 0.20, "tail_rate": 0.05},
        },
        # Đây là ràng buộc khả thi, không phải tiêu chí để chấm điểm.
        # Giữ ở preset để mọi caller (API, notebook, scenario) áp dụng như nhau.
        "min_refresh_rate_hz": 144,
        "base_filter": lambda row: (
            row.get("os_name") == "Windows"
            and row.get("gpu_type") == "discrete"
        ),
    },
}

# Compatibility aliases for legacy calls and transition
PRESETS["student_office"] = PRESETS["student_budget"]
PRESETS["office"] = PRESETS["student_budget"]
PRESETS["slim"] = PRESETS["slim_mobility"]
PRESETS["business"] = PRESETS["slim_mobility"]
PRESETS["coding"] = PRESETS["technical_coding"]
PRESETS["ai_pc"] = PRESETS["technical_coding"]


# -------------------------------------------------------------
# Pure In-Memory DSS Evaluation Pipeline
# -------------------------------------------------------------
def evaluate(
    candidates: List[Dict[str, Any]],
    preset_key: str,
    min_budget_vnd: Optional[float] = None,
    max_budget_vnd: Optional[float] = None,
    min_ram_gb: Optional[int] = None,
    min_storage_gb: Optional[int] = None,
    min_refresh_rate_hz: Optional[int] = None,
    required_os: Optional[str] = None,
    coverage_threshold: float = 0.80,
    custom_weights: Optional[List[float]] = None,
    strict_benchmark: bool = False,
) -> Dict[str, Any]:
    """Pure in-memory DSS evaluation executing AHP + TOPSIS with strict D14 compliance.
    
    Returns a dictionary containing:
        status: 'success' | 'single_candidate' | 'no_suitable_laptop'
        rankings: list of ranked laptops with scores and explanations
        excluded: list of excluded laptops with explicit reasons
        dropped_criteria: criteria dropped due to coverage < 80%
        active_criteria: list of (criterion, direction, weight)
        ahp_cr: Consistency Ratio of AHP matrix (0.0 if Direct Rating/custom weights)
    """
    if preset_key not in PRESETS:
        raise ValueError(f"Preset không hợp lệ: {preset_key}")
    if min_budget_vnd is not None and min_budget_vnd < 0:
        raise ValueError("Ngân sách tối thiểu không được âm.")
    if max_budget_vnd is not None and max_budget_vnd < 0:
        raise ValueError("Ngân sách tối đa không được âm.")
    if min_budget_vnd is not None and max_budget_vnd is not None and min_budget_vnd > max_budget_vnd:
        raise ValueError("Ngân sách tối thiểu không được lớn hơn ngân sách tối đa.")

    preset = PRESETS[preset_key]
    preset_min_refresh = preset.get("min_refresh_rate_hz")
    if preset_min_refresh is not None:
        min_refresh_rate_hz = max(min_refresh_rate_hz or 0, preset_min_refresh)
    if custom_weights is not None:
        expected_len = len(preset["criteria"])
        if len(custom_weights) != expected_len:
            raise ValueError(
                f"Độ dài custom_weights ({len(custom_weights)}) không khớp với số tiêu chí của preset '{preset_key}' ({expected_len})."
            )
        for idx, w in enumerate(custom_weights):
            if w is None or math.isnan(w) or math.isinf(w) or w < 0:
                raise ValueError(
                    f"Trọng số không hợp lệ tại vị trí {idx}: {w}. Trọng số phải là số thực không âm hữu hạn."
                )
        total_w = sum(custom_weights)
        if total_w <= 0.0:
            raise ValueError("Tổng trọng số tùy chỉnh phải lớn hơn 0.")
        # Chuẩn hóa về tổng = 1.0 (Direct Rating)
        weights = [w / total_w for w in custom_weights]
        cr = 0.0
    else:
        weights, lambda_max, cr = compute_ahp_weights(preset["matrix"])

    excluded: List[Dict[str, Any]] = []
    eligible_pool: List[Dict[str, Any]] = []

    # 1. Base eligibility and user constraints (budget, RAM/SSD, OS, refresh rate, strict benchmark)
    for cand in candidates:
        name = cand.get("product_name_raw", "Unknown")

        # Strict Benchmark Mode (DECISIONS.md D05)
        if strict_benchmark:
            if cand.get("cpu_benchmark_match_level") == "approximate" or cand.get("gpu_benchmark_match_level") == "approximate":
                excluded.append({
                    "product_name_raw": name,
                    "reason": "Loại bỏ theo chuẩn DECISIONS.md D05: Điểm benchmark CPU/GPU là ước lượng kiến trúc (approximate), chưa có mẫu xác thực độc lập chính thức",
                })
                continue

        # Base preset filter
        if not preset["base_filter"](cand):
            excluded.append({
                "product_name_raw": name,
                "reason": "Không thỏa mãn điều kiện cơ bản của preset (yêu cầu dGPU Windows)",
            })
            continue

        # OS constraint
        if required_os and cand.get("os_name") != required_os:
            excluded.append({
                "product_name_raw": name,
                "reason": f"Hệ điều hành ({cand.get('os_name')}) khác yêu cầu ({required_os})",
            })
            continue

        # Budget hard filters
        price_str = cand.get("sale_price_vnd", "").strip()
        if not price_str:
            excluded.append({
                "product_name_raw": name,
                "reason": "Thiếu giá bán niêm yết",
            })
            continue

        price_val = float(price_str)
        if max_budget_vnd is not None and price_val > max_budget_vnd:
            excluded.append({
                "product_name_raw": name,
                "reason": f"Vượt ngân sách tối đa ({price_val:,.0f} > {max_budget_vnd:,.0f} VND)",
            })
            continue

        if min_budget_vnd is not None and price_val < min_budget_vnd:
            excluded.append({
                "product_name_raw": name,
                "reason": f"Thấp hơn ngân sách tối thiểu ({price_val:,.0f} < {min_budget_vnd:,.0f} VND)",
            })
            continue

        if min_ram_gb is not None and int(float(cand.get("ram_gb") or 0)) < min_ram_gb:
            excluded.append({
                "product_name_raw": name,
                "reason": f"RAM thấp hơn yêu cầu tối thiểu ({cand.get('ram_gb') or 0}GB < {min_ram_gb}GB)",
            })
            continue

        if min_storage_gb is not None and int(float(cand.get("storage_total_gb") or 0)) < min_storage_gb:
            excluded.append({
                "product_name_raw": name,
                "reason": f"SSD thấp hơn yêu cầu tối thiểu ({cand.get('storage_total_gb') or 0}GB < {min_storage_gb}GB)",
            })
            continue

        # Refresh rate constraint
        if min_refresh_rate_hz is not None:
            hz_str = cand.get("refresh_rate_hz", "").strip()
            if not hz_str:
                excluded.append({
                    "product_name_raw": name,
                    "reason": "Thiếu thông tin tần số quét màn hình (hãng không công bố)",
                })
                continue
            hz_val = int(hz_str)
            if hz_val < min_refresh_rate_hz:
                excluded.append({
                    "product_name_raw": name,
                    "reason": f"Tần số quét ({hz_val}Hz) thấp hơn yêu cầu ({min_refresh_rate_hz}Hz)",
                })
                continue

        eligible_pool.append(cand)

    if not eligible_pool:
        return {
            "status": "no_suitable_laptop",
            "suggestion": "Không có máy nào thỏa mãn toàn bộ ràng buộc và ngân sách. Hãy cân nhắc nới lỏng ngân sách hoặc giảm yêu cầu lọc.",
            "rankings": [],
            "excluded": excluded,
            "dropped_criteria": [],
            "active_criteria": [],
            "ahp_cr": cr,
        }

    # 2. DECISIONS.md D14 (Clause 1): Criterion-Coverage Guard
    # Drop any criterion whose coverage across eligible candidates is < coverage_threshold
    active_criteria: List[Tuple[str, str, float]] = []
    dropped_criteria: List[Dict[str, Any]] = []

    m_pool = len(eligible_pool)
    for (crit_name, crit_dir), weight in zip(preset["criteria"], weights):
        present_count = sum(bool(c.get(crit_name, "").strip()) for c in eligible_pool)
        cov = present_count / m_pool
        if cov < coverage_threshold:
            dropped_criteria.append({
                "criterion": crit_name,
                "coverage_percent": round(cov * 100, 1),
                "threshold_percent": round(coverage_threshold * 100, 1),
                "reason": f"Độ phủ ({cov*100:.1f}%) thấp hơn ngưỡng {coverage_threshold*100:.0f}%",
            })
        else:
            active_criteria.append((crit_name, crit_dir, weight))

    if not active_criteria:
        return {
            "status": "no_suitable_laptop",
            "suggestion": "Mọi tiêu chí đều không đạt ngưỡng độ phủ dữ liệu 80%.",
            "rankings": [],
            "excluded": excluded,
            "dropped_criteria": dropped_criteria,
            "active_criteria": [],
            "ahp_cr": cr,
        }

    # Re-normalize remaining weights so they sum to 1.0.
    # Note for academic defense: This preserves the relative ratio (a_ij) between
    # surviving criteria without triggering full dynamic AHP re-solicitation (V1 scope).
    sum_w = sum(w for _, _, w in active_criteria)
    active_criteria = [(c, d, w / sum_w) for c, d, w in active_criteria]

    # 3. DECISIONS.md D14 (Clause 2): Exclude records missing any remaining active criterion
    # Strictly NO 0.0 coercion for missing data
    final_candidates: List[Dict[str, Any]] = []
    for cand in eligible_pool:
        missing_fields = [c for c, _, _ in active_criteria if not cand.get(c, "").strip()]
        if missing_fields:
            if ("cpu_benchmark_multi_core" in missing_fields or "cpu_benchmark_single_core" in missing_fields) and cand.get("cpu_benchmark_match_level") == "unreleased_hardware":
                reason_detail = "Chưa có benchmark CPU chính thức (phần cứng chưa phát hành thương mại)"
            else:
                reason_detail = f"Thiếu trường dữ liệu lõi: {', '.join(missing_fields)}"
            excluded.append({
                "product_name_raw": cand.get("product_name_raw", "Unknown"),
                "reason": reason_detail,
            })
        else:
            final_candidates.append(cand)

    m = len(final_candidates)
    if m == 0:
        return {
            "status": "no_suitable_laptop",
            "suggestion": "Các ứng viên đều thiếu một trong các trường tiêu chí lõi.",
            "rankings": [],
            "excluded": excluded,
            "dropped_criteria": dropped_criteria,
            "active_criteria": active_criteria,
            "ahp_cr": cr,
        }

    # 4. Edge Case: Single Candidate
    if m == 1:
        single = dict(final_candidates[0])
        single["rank"] = 1
        single["topsis_score"] = 1.0
        single["note"] = "Chỉ có 1 ứng viên duy nhất thỏa mãn toàn bộ tiêu chí và ràng buộc."
        single["explanation"] = {
            "top_advantage": "Ứng viên duy nhất đáp ứng trọn vẹn yêu cầu cấu hình và ngân sách.",
            "top_penalty": "Không có đối thủ để so sánh.",
            "warnings": [],
        }
        if single.get("gpu_benchmark_match_level") and single.get("gpu_benchmark_match_level") != "exact_laptop_or_tgp":
            single["explanation"]["warnings"].append("Điểm GPU là ước lượng (approximate), chưa khớp đúng cấu hình/TGP thực tế.")
        return {
            "status": "single_candidate",
            "rankings": [single],
            "excluded": excluded,
            "dropped_criteria": dropped_criteria,
            "active_criteria": active_criteria,
            "ahp_cr": cr,
        }

    # 5. TOPSIS: Build Decision Matrix X
    fit_params = preset.get("fit_params", {})
    n = len(active_criteria)
    x = []
    for cand in final_candidates:
        row_vals = []
        for crit_name, crit_dir, _ in active_criteria:
            raw_val = cand.get(crit_name, "").strip()
            try:
                val = float(raw_val)
            except (ValueError, TypeError):
                raise ValueError(f"Giá trị không thể chuyển sang số thực cho tiêu chí '{crit_name}' tại máy '{cand.get('product_name_raw')}': '{raw_val}'")
            if not math.isfinite(val):
                raise ValueError(f"Giá trị không hữu hạn (NaN/Inf) cho tiêu chí '{crit_name}' tại máy '{cand.get('product_name_raw')}': {val}")

            # Apply explicit Fit utility function if defined
            if crit_dir == "fit" and crit_name in fit_params:
                params = fit_params[crit_name]
                val = compute_fit_score(val, **params)

            row_vals.append(val)
        x.append(row_vals)

    # 6. Vector Normalization: r_ij = x_ij / sqrt(sum_k x_kj^2)
    norms = []
    for j in range(n):
        sum_sq = sum(x[i][j] ** 2 for i in range(m))
        norms.append(math.sqrt(sum_sq) if sum_sq > 0 else 1.0)

    r = [[x[i][j] / norms[j] for j in range(n)] for i in range(m)]

    # 7. Weighted Normalized Matrix: v_ij = w_j * r_ij
    v = [[active_criteria[j][2] * r[i][j] for j in range(n)] for i in range(m)]

    # 8. Ideal Best (v+) and Ideal Worst (v-)
    v_plus = []
    v_minus = []
    for j in range(n):
        col_vals = [v[i][j] for i in range(m)]
        direction = active_criteria[j][1]
        if direction in ("benefit", "fit"):
            v_plus.append(max(col_vals))
            v_minus.append(min(col_vals))
        else:  # cost
            v_plus.append(min(col_vals))
            v_minus.append(max(col_vals))

    # 9. Euclidean Distances: S+ and S-
    s_plus = []
    s_minus = []
    d_sq_plus = []
    d_sq_minus = []
    for i in range(m):
        sq_p = [(v[i][j] - v_plus[j]) ** 2 for j in range(n)]
        sq_m = [(v[i][j] - v_minus[j]) ** 2 for j in range(n)]
        d_sq_plus.append(sq_p)
        d_sq_minus.append(sq_m)
        s_plus.append(math.sqrt(sum(sq_p)))
        s_minus.append(math.sqrt(sum(sq_m)))

    # 10. Closeness Coefficient C_i and Genuine Explainability
    results = []
    for i in range(m):
        denom = s_plus[i] + s_minus[i]
        c_i = s_minus[i] / denom if denom > 0 else 0.5
        item = dict(final_candidates[i])
        item["topsis_score"] = round(c_i, 4)
        item["distance_ideal_plus"] = round(s_plus[i], 4)
        item["distance_ideal_minus"] = round(s_minus[i], 4)

        # Genuine squared Euclidean distance explainability
        sum_sq_m = sum(d_sq_minus[i])
        sum_sq_p = sum(d_sq_plus[i])

        # Top advantage: criterion with largest share of separation from worst
        best_j = max(range(n), key=lambda j: d_sq_minus[i][j])
        share_best = (d_sq_minus[i][best_j] / sum_sq_m * 100) if sum_sq_m > 0 else 0.0

        # Top penalty: criterion with largest share of shortfall from best
        worst_j = max(range(n), key=lambda j: d_sq_plus[i][j])
        share_worst = (d_sq_plus[i][worst_j] / sum_sq_p * 100) if sum_sq_p > 0 else 0.0

        warnings = []
        if item.get("cpu_benchmark_match_level") == "approximate":
            warnings.append(f"Điểm CPU ({item.get('cpu_benchmark_multi_core')}) là ước lượng suy luận kiến trúc (approximate), chưa có mẫu xác thực độc lập trên Geekbench 6.")
        if item.get("gpu_benchmark_match_level") and item.get("gpu_benchmark_match_level") != "exact_laptop_or_tgp":
            warnings.append(f"Điểm GPU ({item.get('gpu_benchmark_time_spy')}) là ước lượng ({item.get('gpu_benchmark_match_level')}), chưa khớp đúng cấu hình/TGP thực tế.")

        item["explanation"] = {
            "top_advantage": f"{active_criteria[best_j][0]} (đóng góp {share_best:.1f}% vào khoảng cách ly khai phương án tệ nhất)",
            "top_penalty": f"{active_criteria[worst_j][0]} (chiếm {share_worst:.1f}% khoảng cách tổn thất so với phương án lý tưởng)",
            "warnings": warnings,
        }
        results.append(item)

    # Sort descending by C_i
    results.sort(key=lambda r: r["topsis_score"], reverse=True)
    for rank_idx, r_item in enumerate(results, start=1):
        r_item["rank"] = rank_idx

    return {
        "status": "success",
        "rankings": results,
        "excluded": excluded,
        "dropped_criteria": dropped_criteria,
        "active_criteria": active_criteria,
        "ahp_cr": cr,
    }


@lru_cache(maxsize=4)
def _load_catalog_cached(path_text: str, mtime_ns: int) -> Tuple[Dict[str, Any], ...]:
    """Cache parsed CSV until the source file changes."""
    del mtime_ns
    with Path(path_text).open(encoding="utf-8", newline="") as file:
        return tuple(csv.DictReader(file))


def load_standardized_laptops(path: Path = STANDARDIZED_CSV) -> List[Dict[str, Any]]:
    """Read catalog with mtime-safe caching and return caller-owned row copies."""
    resolved = Path(path)
    if not resolved.exists():
        return []
    rows = _load_catalog_cached(str(resolved.resolve()), resolved.stat().st_mtime_ns)
    return [dict(row) for row in rows]


def analyze_budget_sensitivity(
    candidates: List[Dict[str, Any]],
    preset_key: str = "student_office",
    current_max_budget: float = 25_000_000.0,
    steps: Optional[List[float]] = None,
    **evaluate_kwargs,
) -> Dict[str, Any]:
    """Budget Sensitivity Analysis (§8.4 Chuongtrinh.md).
    
    Simulates 'What-If' scenarios: if the user adds +1M, +2M, +5M VND to their budget,
    does an alternative laptop usurp Top 1, and what hardware upgrade does it provide?
    """
    if steps is None:
        steps = [1_000_000.0, 2_000_000.0, 5_000_000.0, 10_000_000.0]

    base_res = evaluate(
        candidates,
        preset_key=preset_key,
        max_budget_vnd=current_max_budget,
        **evaluate_kwargs,
    )
    base_rankings = base_res.get("rankings", [])
    base_top1 = base_rankings[0] if base_rankings else None

    scenarios = []
    for delta in steps:
        new_budget = current_max_budget + delta
        res = evaluate(
            candidates,
            preset_key=preset_key,
            max_budget_vnd=new_budget,
            **evaluate_kwargs,
        )
        new_rankings = res.get("rankings", [])
        new_top1 = new_rankings[0] if new_rankings else None

        is_usurped = False
        diff_desc = []
        if new_top1 and base_top1:
            if new_top1["source_product_id"] != base_top1["source_product_id"]:
                is_usurped = True
                gpu_b = float(base_top1.get("gpu_benchmark_time_spy") or 0)
                gpu_n = float(new_top1.get("gpu_benchmark_time_spy") or 0)
                if gpu_n > gpu_b:
                    pct = ((gpu_n - gpu_b) / gpu_b * 100) if gpu_b > 0 else 100
                    diff_desc.append(f"Đồ họa mạnh hơn (+{gpu_n - gpu_b:.0f}đ 3DMark, +{pct:.0f}%)")

                cpu_b = float(base_top1.get("cpu_benchmark_multi_core") or base_top1.get("cpu_benchmark_single_core") or 0)
                cpu_n = float(new_top1.get("cpu_benchmark_multi_core") or new_top1.get("cpu_benchmark_single_core") or 0)
                if cpu_n > cpu_b:
                    diff_desc.append(f"CPU khỏe hơn (+{cpu_n - cpu_b:.0f}đ Geekbench 6)")

                w_b = float(base_top1.get("weight_kg") or 99)
                w_n = float(new_top1.get("weight_kg") or 99)
                if w_n < w_b:
                    diff_desc.append(f"Mỏng nhẹ hơn (-{w_b - w_n:.2f} kg)")

                if new_top1.get("panel_type") == "OLED" and base_top1.get("panel_type") != "OLED":
                    diff_desc.append("Nâng cấp màn hình OLED cao cấp")

                if not diff_desc:
                    diff_desc.append(f"Điểm tương thích TOPSIS cao hơn ({new_top1.get('topsis_score')} vs {base_top1.get('topsis_score')})")

        scenarios.append({
            "delta_vnd": delta,
            "new_budget_vnd": new_budget,
            "is_usurped": is_usurped,
            "new_top1": {
                "source_product_id": new_top1["source_product_id"],
                "product_name_raw": new_top1["product_name_raw"],
                "sale_price_vnd": new_top1["sale_price_vnd"],
                "topsis_score": new_top1["topsis_score"],
            } if new_top1 else None,
            "upgrade_benefit": ", ".join(diff_desc) if diff_desc else "Lựa chọn hiện tại vẫn tối ưu nhất",
        })

    return {
        "baseline_budget_vnd": current_max_budget,
        "baseline_top1": {
            "source_product_id": base_top1["source_product_id"],
            "product_name_raw": base_top1["product_name_raw"],
            "sale_price_vnd": base_top1["sale_price_vnd"],
            "topsis_score": base_top1["topsis_score"],
        } if base_top1 else None,
        "scenarios": scenarios,
    }


def analyze_weight_sensitivity(
    candidates: List[Dict[str, Any]],
    preset_key: str = "student_office",
    max_budget_vnd: Optional[float] = None,
    variation_percentages: Optional[List[float]] = None,
    **evaluate_kwargs,
) -> Dict[str, Any]:
    """One-At-A-Time (OAT) Weight Sensitivity Analysis (§8.4 Chuongtrinh.md).
    
    Tests whether perturbations (±10%, ±20%) in AHP weights invert the top rankings.
    """
    if variation_percentages is None:
        variation_percentages = [-0.20, -0.10, 0.10, 0.20]

    custom_base_weights = evaluate_kwargs.pop("custom_weights", None)
    base_res = evaluate(
        candidates,
        preset_key=preset_key,
        max_budget_vnd=max_budget_vnd,
        custom_weights=custom_base_weights,
        **evaluate_kwargs,
    )
    if base_res["status"] != "success" or not base_res["rankings"]:
        return {
            "status": "insufficient_candidates",
            "stability_rate_percent": 0.0,
            "is_highly_robust": False,
            "criteria_evaluations": [],
            "academic_summary": "Không đủ ứng viên đạt chuẩn để phân tích độ nhạy.",
        }

    base_top1_id = base_res["rankings"][0]["source_product_id"]
    base_top1_name = base_res["rankings"][0]["product_name_raw"]

    preset = PRESETS[preset_key]
    if custom_base_weights is None:
        base_weights, _, _ = compute_ahp_weights(preset["matrix"])
    else:
        total_weight = sum(custom_base_weights)
        base_weights = [weight / total_weight for weight in custom_base_weights]

    results_per_criterion = []
    total_tests = 0
    stable_tests = 0

    for crit_idx, (crit_name, crit_dir) in enumerate(preset["criteria"]):
        orig_w = base_weights[crit_idx]
        variations = []

        for var_pct in variation_percentages:
            total_tests += 1
            perturbed_w = orig_w * (1.0 + var_pct)

            remaining_orig_sum = sum(w for idx, w in enumerate(base_weights) if idx != crit_idx)
            scale = (1.0 - perturbed_w) / remaining_orig_sum if remaining_orig_sum > 0 else 1.0

            custom_weights = []
            for idx, w in enumerate(base_weights):
                if idx == crit_idx:
                    custom_weights.append(perturbed_w)
                else:
                    custom_weights.append(w * scale)

            test_res = evaluate(
                candidates,
                preset_key=preset_key,
                max_budget_vnd=max_budget_vnd,
                custom_weights=custom_weights,
                **evaluate_kwargs,
            )

            new_top1 = test_res["rankings"][0] if test_res["rankings"] else None
            is_same = (new_top1["source_product_id"] == base_top1_id) if new_top1 else False
            if is_same:
                stable_tests += 1

            variations.append({
                "variation_percent": round(var_pct * 100),
                "perturbed_weight": round(perturbed_w, 4),
                "top1_id": new_top1["source_product_id"] if new_top1 else None,
                "top1_name": new_top1["product_name_raw"] if new_top1 else "None",
                "rank_preserved": is_same,
            })

        is_robust = all(v["rank_preserved"] for v in variations)
        results_per_criterion.append({
            "criterion": crit_name,
            "direction": crit_dir,
            "base_weight": round(orig_w, 4),
            "is_robust": is_robust,
            "variations": variations,
        })

    stability_rate = (stable_tests / total_tests * 100) if total_tests > 0 else 100.0
    is_highly_robust = stability_rate >= 75.0

    academic_summary = (
        f"Độ bền vững thứ hạng đạt {stability_rate:.1f}% qua các kịch bản rung lắc trọng số (±10%, ±20%). "
        + ("Phương án Top 1 duy trì ổn định cao, chứng minh quyết định không bị ngẫu nhiên hay nhạy cảm thái quá."
           if is_highly_robust else
           "Thứ hạng có độ nhạy nhất định với một số tiêu chí cốt lõi, người dùng nên cân nhắc kỹ giữa các phương án sát nút.")
    )

    return {
        "status": "success",
        "baseline_top1": {"id": base_top1_id, "name": base_top1_name},
        "stability_rate_percent": round(stability_rate, 1),
        "is_highly_robust": is_highly_robust,
        "criteria_evaluations": results_per_criterion,
        "academic_summary": academic_summary,
    }


def analyze_monte_carlo_stability(
    candidates: List[Dict[str, Any]],
    preset_key: str = "student_office",
    max_budget_vnd: Optional[float] = None,
    simulations: int = 300,
    seed: int = 42,
    concentration: float = 80.0,
    **evaluate_kwargs,
) -> Dict[str, Any]:
    """Estimate TOPSIS Top-1 stability under simultaneous weight uncertainty.

    The analysis samples Dirichlet-distributed weights centred on either the
    preset AHP weights or Direct Rating weights supplied by the user.  It keeps
    candidates and all feasibility filters fixed; therefore this is a weight
    robustness analysis, not a claim about future prices or new products.
    """
    if simulations < 1:
        raise ValueError("Số lần mô phỏng phải lớn hơn 0.")
    if not math.isfinite(concentration) or concentration <= 0:
        raise ValueError("concentration phải là số hữu hạn lớn hơn 0.")

    custom_base_weights = evaluate_kwargs.pop("custom_weights", None)
    base_res = evaluate(
        candidates,
        preset_key=preset_key,
        max_budget_vnd=max_budget_vnd,
        custom_weights=custom_base_weights,
        **evaluate_kwargs,
    )
    if base_res["status"] != "success" or not base_res["rankings"]:
        return {
            "status": "insufficient_candidates",
            "simulations": simulations,
            "top1_stability_percent": 0.0,
            "top1_frequency": [],
            "academic_summary": "Không đủ ứng viên đạt chuẩn để mô phỏng độ bền trọng số.",
        }

    preset = PRESETS[preset_key]
    if custom_base_weights is None:
        base_weights, _, _ = compute_ahp_weights(preset["matrix"])
    else:
        total_weight = sum(custom_base_weights)
        base_weights = [weight / total_weight for weight in custom_base_weights]

    rng = random.Random(seed)
    top1_counts: Dict[str, Dict[str, Any]] = {}
    completed = 0
    for _ in range(simulations):
        # Keep an explicitly-zero Direct Rating weight at zero.  Positive
        # dimensions follow a Dirichlet draw generated via independent Gamma.
        gamma_draws = [
            rng.gammavariate(max(weight * concentration, 1e-9), 1.0) if weight > 0 else 0.0
            for weight in base_weights
        ]
        draw_total = sum(gamma_draws)
        sampled_weights = (
            [value / draw_total for value in gamma_draws]
            if draw_total > 0 else list(base_weights)
        )
        result = evaluate(
            candidates,
            preset_key=preset_key,
            max_budget_vnd=max_budget_vnd,
            custom_weights=sampled_weights,
            **evaluate_kwargs,
        )
        if not result["rankings"]:
            continue
        completed += 1
        top1 = result["rankings"][0]
        product_id = str(top1["source_product_id"])
        entry = top1_counts.setdefault(product_id, {
            "id": product_id,
            "name": top1["product_name_raw"],
            "count": 0,
        })
        entry["count"] += 1

    baseline = base_res["rankings"][0]
    baseline_id = str(baseline["source_product_id"])
    baseline_count = top1_counts.get(baseline_id, {}).get("count", 0)
    frequency = sorted(
        (
            {
                **entry,
                "percent": round(entry["count"] / completed * 100, 1) if completed else 0.0,
            }
            for entry in top1_counts.values()
        ),
        key=lambda item: (-item["count"], item["id"]),
    )
    stability = baseline_count / completed * 100 if completed else 0.0
    return {
        "status": "success" if completed else "insufficient_candidates",
        "method": "Dirichlet weight simulation",
        "simulations": simulations,
        "completed_simulations": completed,
        "seed": seed,
        "concentration": concentration,
        "baseline_top1": {"id": baseline_id, "name": baseline["product_name_raw"]},
        "top1_stability_percent": round(stability, 1),
        "top1_frequency": frequency[:10],
        "academic_summary": (
            f"Phương án đứng đầu ban đầu xuất hiện ở {stability:.1f}% trong {completed} mô phỏng trọng số đồng thời. "
            "Kết quả chỉ đo độ nhạy với trọng số, với catalogue và các bộ lọc được giữ cố định."
        ),
    }


def main():
    laptops = load_standardized_laptops()
    print("=" * 85)
    print("BÁO CÁO TOÁN HỌC DSS (AHP + TOPSIS) ĐÃ TÁI CẤU TRÚC — TUÂN THỦ D14 & CHUONGTRINH.MD")
    print("=" * 85)

    for pkey in ["student_budget", "slim_mobility", "technical_coding", "gaming"]:
        res = evaluate(laptops, preset_key=pkey)
        pname = PRESETS[pkey]["name"]
        print(f"\n>>> PRESET: {pname.upper()}")
        print(f"Trạng thái: {res['status']} | AHP CR: {res['ahp_cr']:.4f} (ĐẠT: CR < 0.10)")

        if res["dropped_criteria"]:
            print("Cảnh báo tiêu chí bị loại bỏ theo quy tắc D14 (coverage < 80%):")
            for dc in res["dropped_criteria"]:
                print(f"  - {dc['criterion']}: độ phủ {dc['coverage_percent']}% < 80%")

        print("Tiêu chí tính điểm và trọng số AHP đã chuẩn hóa:")
        for cname, cdir, w in res["active_criteria"]:
            print(f"  - {cname:<25} ({cdir:<7}): {w * 100:.1f}%")

        print(f"\nSố lượng máy được xếp hạng: {len(res['rankings'])} | Số máy bị loại: {len(res['excluded'])}")
        print("-" * 85)
        print(f"{'Hạng':<5} | {'Điểm TOPSIS':<12} | {'Giá bán':<13} | Tên Laptop")
        print("-" * 85)
        for r in res["rankings"]:
            price_str = f"{int(float(r['sale_price_vnd'])):,}"
            print(f"#{r['rank']:<4} | {r['topsis_score']:<12.4f} | {price_str:<13} | {r['product_name_raw'][:45]}")
            print(f"       Ưu thế:  {r['explanation']['top_advantage']}")
            print(f"       Tổn thất: {r['explanation']['top_penalty']}")
            for w in r['explanation']['warnings']:
                print(f"       [!] CẢNH BÁO: {w}")

        if res["excluded"]:
            print("\n  Danh sách máy bị loại trừ & lý do:")
            for ex in res["excluded"]:
                print(f"  - {ex['product_name_raw'][:40]}: {ex['reason']}")
        print("=" * 85)


if __name__ == "__main__":
    main()
