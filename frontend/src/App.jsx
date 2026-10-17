import React, { useState, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { 
  Laptop, Search, Filter, ArrowLeft, ShieldCheck, SlidersHorizontal, Eye,
  ExternalLink, Info, Check, Scale, TrendingUp, ArrowRight, X, GitCompare, ListFilter, ChartNoAxesCombined, BookOpen,
  Heart, Sparkles, Trash2
} from 'lucide-react';

// ═══════════════════════════════════════════════════
// 4 HONEST CATEGORIES — khớp chính xác với backend PRESETS
// ═══════════════════════════════════════════════════
const CATEGORIES = [
  { key: 'student_budget', name: 'Sinh viên & Kinh tế', sub: 'Giá rẻ, CPU đủ dùng, nhẹ cân', icon: '📚' },
  { key: 'slim_mobility', name: 'Mỏng nhẹ & Di động', sub: 'Trọng lượng ≤ 1.45kg', icon: '🪶' },
  { key: 'technical_coding', name: 'Kỹ thuật & Lập trình', sub: 'Ưu tiên CPU/RAM trong ngân sách', icon: '💻' },
  { key: 'gaming', name: 'Gaming & Đồ họa nặng', sub: 'GPU rời, 144Hz+, Windows', icon: '🎮' },
];

// Vietnamese labels cho tiêu chí — dùng động, không bịa
const CRITERIA_LABELS = {
  sale_price_vnd: 'Giá bán',
  cpu_benchmark_multi_core: 'CPU đa nhân (Geekbench 6)',
  cpu_benchmark_single_core: 'CPU đơn nhân (Geekbench 6)',
  gpu_benchmark_time_spy: 'GPU đồ họa (3DMark Time Spy)',
  ram_gb: 'Bộ nhớ RAM',
  storage_total_gb: 'Ổ cứng SSD',
  weight_kg: 'Cân nặng',
};

// Hàm chuyển đổi diễn giải khoảng cách TOPSIS sang văn phong tiêu dùng dễ hiểu
const formatExplanationText = (text, type = 'advantage') => {
  if (!text) return '';
  let res = text;
  // Thay thế tên biến kỹ thuật bằng nhãn tiếng Việt trực quan
  res = res.replace(/sale_price_vnd/g, 'Giá bán siêu tiết kiệm');
  res = res.replace(/cpu_benchmark_single_core/g, 'Sức mạnh vi xử lý CPU đơn nhân');
  res = res.replace(/cpu_benchmark_multi_core/g, 'Hiệu năng CPU đa nhân');
  res = res.replace(/gpu_benchmark_time_spy/g, 'Sức mạnh đồ họa GPU');
  res = res.replace(/ram_gb/g, 'Dung lượng bộ nhớ RAM');
  res = res.replace(/storage_total_gb/g, 'Dung lượng ổ cứng SSD');
  res = res.replace(/weight_kg/g, 'Trọng lượng mỏng nhẹ');

  // Làm mềm mại thuật ngữ toán học TOPSIS
  if (type === 'advantage') {
    res = res.replace(/\(đóng góp ([\d.]+)% vào khoảng cách ly khai phương án tệ nhất\)/g, 
      '(đóng góp $1% vào ưu thế vượt trội so với các máy đắt tiền/kém tối ưu khác)');
  } else if (type === 'penalty') {
    res = res.replace(/\(chiếm ([\d.]+)% khoảng cách tổn thất so với phương án lý tưởng\)/g, 
      '(chiếm $1% lý do máy chưa đạt điểm cấu hình tối đa khi so với dòng cao cấp)');
  }
  return res;
};

const CRITERIA_ICONS = {
  sale_price_vnd: '💰',
  cpu_benchmark_multi_core: '⚡',
  cpu_benchmark_single_core: '🎯',
  gpu_benchmark_time_spy: '🎮',
  ram_gb: '🧠',
  storage_total_gb: '💾',
  weight_kg: '⚖️',
};

export default function App() {
  const navigate = useNavigate();
  const location = useLocation();
  const currentPage = location.pathname.startsWith('/laptop/')
    ? 'detail'
    : location.pathname === '/analysis'
      ? 'analysis'
      : location.pathname === '/methodology'
        ? 'methodology'
        : 'recommend';
  // Navigation & View Mode
  const [viewMode, setViewMode] = useState('list');
  const [selectedLaptop, setSelectedLaptop] = useState(null);
  const [detailTab, setDetailTab] = useState('config');

  // Filter States
  const [presetKey, setPresetKey] = useState('student_budget');
  const [minBudget, setMinBudget] = useState(0);
  const [maxBudget, setMaxBudget] = useState(45000000);
  const [appliedMaxBudget, setAppliedMaxBudget] = useState(45000000);
  const [appliedPresetKey, setAppliedPresetKey] = useState('student_budget');
  const [brand, setBrand] = useState('Tất cả');
  const [cpuFamily, setCpuFamily] = useState('Tất cả');
  const [ramGb, setRamGb] = useState('');
  const [storageGb, setStorageGb] = useState('');
  const [screenSize, setScreenSize] = useState('Tất cả');
  const [panelType, setPanelType] = useState('Tất cả');
  const [refreshRate, setRefreshRate] = useState('Tất cả');
  const [osName, setOsName] = useState('Tất cả');
  const [minBrightness, setMinBrightness] = useState('Tất cả');
  const [requireRj45, setRequireRj45] = useState(false);
  const [requireRamUpgrade, setRequireRamUpgrade] = useState(false);
  const [requireTypeCCharge, setRequireTypeCCharge] = useState(false);
  const [requireThunderbolt, setRequireThunderbolt] = useState(false);
  const [strictBenchmark, setStrictBenchmark] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');

  // Evaluation Data
  const [rankings, setRankings] = useState([]);
  const [excluded, setExcluded] = useState([]);
  const [activeCriteria, setActiveCriteria] = useState([]);
  const [sensitivityData, setSensitivityData] = useState(null);
  const [showSensitivity, setShowSensitivity] = useState(true);
  const [loading, setLoading] = useState(false);
  const [evaluationError, setEvaluationError] = useState('');
  const [showAcademicDetails, setShowAcademicDetails] = useState(false);
  const [analysisTab, setAnalysisTab] = useState('advice');
  const [nlQuery, setNlQuery] = useState('');
  const [nlResult, setNlResult] = useState(null);
  const [nlError, setNlError] = useState('');
  const [excludedBrands, setExcludedBrands] = useState([]);
  const [mlValuation, setMlValuation] = useState(null);
  const [ahpCr, setAhpCr] = useState(null);
  const [pairwiseMatrix, setPairwiseMatrix] = useState([]);
  const [droppedCriteria, setDroppedCriteria] = useState([]);

  // Comparison State
  const [compareIds, setCompareIds] = useState([]);
  const [showCompareModal, setShowCompareModal] = useState(false);

  // Weight Customization (Direct Rating Override)
  const [showWeightEditor, setShowWeightEditor] = useState(false);
  const [customWeightValues, setCustomWeightValues] = useState(null); // null = AHP default
  const [isCustomWeightsActive, setIsCustomWeightsActive] = useState(false);

  // Tabpane Navigation for Recommendation Page
  const [mainTab, setMainTab] = useState('recommend'); // 'recommend' | 'nlp' | 'filters' | 'favorites'

  // Favorites (Wishlist) State with localStorage Persistence
  const [favorites, setFavorites] = useState(() => {
    try {
      const saved = localStorage.getItem('laptop_dss_favorites');
      return saved ? JSON.parse(saved) : [];
    } catch {
      return [];
    }
  });

  const toggleFavorite = (laptop) => {
    if (!laptop || !laptop.source_product_id) return;
    setFavorites(prev => {
      const exists = prev.some(item => item.source_product_id === laptop.source_product_id);
      const updated = exists 
        ? prev.filter(item => item.source_product_id !== laptop.source_product_id)
        : [...prev, laptop];
      try {
        localStorage.setItem('laptop_dss_favorites', JSON.stringify(updated));
      } catch (e) {
        console.error("Không thể lưu favorites:", e);
      }
      return updated;
    });
  };

  const isFavorite = (productId) => favorites.some(item => item.source_product_id === productId);

  const clearFavorites = () => {
    setFavorites([]);
    try {
      localStorage.removeItem('laptop_dss_favorites');
    } catch {}
  };

  useEffect(() => {
    const validPaths = ['/', '/recommend', '/analysis', '/methodology'];
    if (!validPaths.includes(location.pathname) && !location.pathname.startsWith('/laptop/')) {
      navigate('/recommend', { replace: true });
      return;
    }
    if (location.pathname === '/') navigate('/recommend', { replace: true });
    setViewMode(location.pathname.startsWith('/laptop/') ? 'detail' : 'list');
  }, [location.pathname, navigate]);

  // Cho phép mở lại URL chi tiết sau khi tải lại trang, không phụ thuộc state phiên trước.
  useEffect(() => {
    if (!location.pathname.startsWith('/laptop/')) return;
    const productId = decodeURIComponent(location.pathname.split('/').pop() || '');
    if (String(selectedLaptop?.source_product_id) === productId) return;

    const rankedLaptop = rankings.find(item => String(item.source_product_id) === productId);
    if (rankedLaptop) {
      setSelectedLaptop(rankedLaptop);
      return;
    }

    fetch('/api/laptops')
      .then(response => response.ok ? response.json() : [])
      .then(laptops => {
        const laptop = laptops.find(item => String(item.source_product_id) === productId);
        if (laptop) setSelectedLaptop(laptop);
        else navigate('/recommend', { replace: true });
      })
      .catch(() => navigate('/recommend', { replace: true }));
  }, [location.pathname, navigate, rankings, selectedLaptop]);

  // Fetch Evaluation from FastAPI
  const fetchEvaluation = async (overridePreset = null, weights = null, filterOverrides = {}) => {
    setLoading(true);
    setEvaluationError('');
    try {
      const activePreset = overridePreset || presetKey;
      const payload = {
        preset_key: activePreset,
        min_budget_vnd: Number(minBudget),
        max_budget_vnd: Number(maxBudget),
        brand: brand === 'Tất cả' ? null : brand,
        cpu_family: cpuFamily === 'Tất cả' ? null : cpuFamily,
        ram_gb: null,
        min_ram_gb: ramGb ? Number(ramGb) : null,
        storage_gb: null,
        min_storage_gb: storageGb ? Number(storageGb) : null,
        excluded_brands: excludedBrands,
        screen_size: screenSize === 'Tất cả' ? null : screenSize,
        panel_type: panelType === 'Tất cả' ? null : panelType,
        required_os: osName === 'Tất cả' ? null : osName,
        min_refresh_rate_hz: refreshRate === 'Tất cả' ? null : Number(refreshRate),
        min_brightness_nits: minBrightness === 'Tất cả' ? null : Number(minBrightness),
        require_rj45_lan: requireRj45 || null,
        require_ram_upgradeable: requireRamUpgrade || null,
        require_type_c_charging: requireTypeCCharge || null,
        require_thunderbolt: requireThunderbolt || null,
        strict_benchmark: strictBenchmark || false,
        custom_weights: weights || null,
      };
      Object.assign(payload, filterOverrides, { preset_key: activePreset });

      const res = await fetch('/api/evaluate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Không thể đánh giá danh sách laptop.');
      setRankings(data.rankings || []);
      setExcluded(data.excluded || []);
      setActiveCriteria(data.active_criteria || []);
      setAhpCr(data.ahp_cr ?? null);
      setPairwiseMatrix(data.pairwise_matrix || []);
      setDroppedCriteria(data.dropped_criteria || []);
      setAppliedMaxBudget(Number(payload.max_budget_vnd));
      setAppliedPresetKey(activePreset);

      // Gọi đồng thời phân tích độ nhạy (§8.4 Chuongtrinh.md)
      fetch('/api/sensitivity', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ...payload, preset_key: activePreset, custom_weights: undefined })
      })
      .then(r => r.json())
      .then(sData => setSensitivityData(sData))
      .catch(err => console.error("Lỗi khi tải độ nhạy:", err));

      // Cập nhật selected laptop nếu đang mở chi tiết
      if (selectedLaptop) {
        const updated = (data.rankings || []).find(r => r.source_product_id === selectedLaptop.source_product_id);
        if (updated) setSelectedLaptop(updated);
      }
    } catch (err) {
      console.error("Lỗi khi tải kết quả:", err);
      setRankings([]);
      setExcluded([]);
      setActiveCriteria([]);
      setSensitivityData(null);
      setEvaluationError(
        err instanceof TypeError
          ? 'Không kết nối được Backend tại http://localhost:8000. Hãy khởi động FastAPI rồi bấm Duyệt lại.'
          : err.message,
      );
    } finally {
      setLoading(false);
    }
  };

  // Initialize custom weight values from activeCriteria
  useEffect(() => {
    if (activeCriteria.length > 0 && !customWeightValues) {
      const weights = activeCriteria.map(([, , w]) => Math.round(w * 100));
      setCustomWeightValues(weights);
    }
  }, [activeCriteria]);

  // Reset weights when preset changes
  useEffect(() => {
    setCustomWeightValues(null);
    setIsCustomWeightsActive(false);
    fetchEvaluation();
  }, [presetKey]);

  const handleCategoryClick = (catKey) => {
    setPresetKey(catKey);
    if (currentPage === 'detail') navigate('/recommend');
    fetchEvaluation(catKey);
  };

  const handleNaturalSearch = async (query = nlQuery) => {
    setNlError('');
    try {
      const res = await fetch('/api/parse-requirement', {
        method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ prompt: query })
      });
      const parsed = await res.json();
      if (!res.ok) throw new Error(parsed.detail || 'Không thể phân tích yêu cầu.');
      setNlQuery(query);
      setNlResult(parsed);
    } catch (err) {
      setNlError(err.message);
    }
  };

  const removeParsedEntity = (entity) => {
    const keyByType = { min_budget: 'min_budget_vnd', max_budget: 'max_budget_vnd', brand: 'brand', excluded_brand: 'excluded_brands', min_ram: 'min_ram_gb', min_storage: 'min_storage_gb', screen_size: 'screen_size', panel_type: 'panel_type', rj45: 'require_rj45_lan', ram_upgrade: 'require_ram_upgradeable', type_c_charging: 'require_type_c_charging', thunderbolt: 'require_thunderbolt', os: 'required_os', cpu: 'cpu_family', strict_benchmark: 'strict_benchmark' };
    const key = keyByType[entity.type];
    setNlResult(prev => {
      if (!prev || !key) return prev;
      const filters = { ...prev.filters };
      if (key === 'excluded_brands') filters[key] = (filters[key] || []).filter(value => value !== entity.value);
      else delete filters[key];
      return { ...prev, filters, entities: prev.entities.filter(item => item !== entity) };
    });
  };

  const applyNaturalRequirement = () => {
    if (!nlResult) return;
    const f = nlResult.filters || {};
    if (f.min_budget_vnd) setMinBudget(f.min_budget_vnd);
    if (f.max_budget_vnd) setMaxBudget(f.max_budget_vnd);
    if (f.brand) setBrand(f.brand);
    if (f.min_ram_gb) setRamGb(String(f.min_ram_gb));
    if (f.min_storage_gb) setStorageGb(String(f.min_storage_gb));
    if (f.panel_type) setPanelType(f.panel_type);
    if (f.screen_size) setScreenSize(f.screen_size);
    if (f.required_os) setOsName(f.required_os);
    if (f.cpu_family) setCpuFamily(f.cpu_family);
    setExcludedBrands(f.excluded_brands || []);
    setRequireRj45(Boolean(f.require_rj45_lan));
    setRequireRamUpgrade(Boolean(f.require_ram_upgradeable));
    setRequireTypeCCharge(Boolean(f.require_type_c_charging));
    setRequireThunderbolt(Boolean(f.require_thunderbolt));
    setStrictBenchmark(Boolean(f.strict_benchmark));
    if (nlResult.preset_key) setPresetKey(nlResult.preset_key);
    fetchEvaluation(nlResult.preset_key || presetKey, null, f);
  };

  useEffect(() => {
    fetch('/api/ml_valuation').then(r => r.ok ? r.json() : null).then(setMlValuation).catch(() => setMlValuation(null));
  }, []);

  const handleApplyFilter = () => {
    if (isCustomWeightsActive && customWeightValues) {
      const sum = customWeightValues.reduce((a, b) => a + b, 0);
      const normalized = customWeightValues.map(v => v / sum);
      fetchEvaluation(null, normalized);
    } else {
      fetchEvaluation();
    }
  };

  const handleApplyCustomWeights = () => {
    if (!customWeightValues) return;
    const sum = customWeightValues.reduce((a, b) => a + b, 0);
    if (sum === 0) return;
    const normalized = customWeightValues.map(v => v / sum);
    setIsCustomWeightsActive(true);
    fetchEvaluation(null, normalized);
  };

  const handleResetWeights = () => {
    setCustomWeightValues(null);
    setIsCustomWeightsActive(false);
    fetchEvaluation();
  };

  const handleOpenDetail = (laptop) => {
    setSelectedLaptop(laptop);
    setDetailTab('config');
    navigate(`/laptop/${encodeURIComponent(laptop.source_product_id)}`);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const goToPage = (page) => {
    if (page === 'recommend') navigate('/recommend');
    if (page === 'analysis') {
      setAnalysisTab('advice');
      navigate('/analysis');
    }
    if (page === 'methodology') {
      setAnalysisTab('math');
      navigate('/methodology');
    }
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  // Compare toggle
  const toggleCompare = (productId) => {
    setCompareIds(prev => {
      if (prev.includes(productId)) {
        return prev.filter(id => id !== productId);
      }
      if (prev.length >= 3) return prev;
      return [...prev, productId];
    });
  };

  const formatVnd = (val) => {
    if (!val) return '—';
    try {
      return Number(val).toLocaleString('vi-VN') + '₫';
    } catch {
      return '—';
    }
  };

  const formatDiscount = (listed, sale) => {
    if (!listed || !sale) return null;
    const l = Number(listed);
    const s = Number(sale);
    if (l > s && l > 0) {
      return `-${Math.round((1 - s / l) * 100)}%`;
    }
    return null;
  };

  const buildSpecsBadgeLine = (item) => {
    const parts = [];
    let cpu = item.cpu_name_normalized || '';
    ['Intel Core ', 'Intel ', 'AMD Ryzen ', 'AMD ', 'Qualcomm Snapdragon ', 'Apple '].forEach(p => {
      cpu = cpu.replace(p, '');
    });
    if (cpu) parts.push(cpu.slice(0, 14));

    let gpu = item.gpu_name_normalized || '';
    if (gpu && item.gpu_type === 'discrete') {
      parts.push(gpu.replace('NVIDIA GeForce ', '').replace(' GDDR6', '').slice(0, 12));
    }

    if (item.ram_gb) parts.push(`${item.ram_gb}GB`);
    if (item.storage_total_gb) parts.push(`${Math.round(Number(item.storage_total_gb))}GB`);
    if (item.screen_size_inch) parts.push(`${item.screen_size_inch}"`);
    if (item.refresh_rate_hz) parts.push(`${item.refresh_rate_hz}Hz`);

    return parts.join(' · ');
  };

  // Filter theo ô tìm kiếm
  const displayedRankings = rankings.filter(item => {
    if (!searchQuery) return true;
    const q = searchQuery.toLowerCase();
    return (
      (item.product_name_raw || '').toLowerCase().includes(q) ||
      (item.cpu_name_normalized || '').toLowerCase().includes(q) ||
      (item.gpu_name_normalized || '').toLowerCase().includes(q)
    );
  });

  const top1Laptop = rankings.length > 0 ? rankings[0] : null;
  const compareLaptops = rankings.filter(r => compareIds.includes(r.source_product_id));
  const selectedCategory = CATEGORIES.find(category => category.key === presetKey);
  const appliedCategory = CATEGORIES.find(category => category.key === appliedPresetKey);
  const hasPendingEvaluation = Number(maxBudget) !== appliedMaxBudget || presetKey !== appliedPresetKey;
  const cpuCriterion = appliedPresetKey === 'student_budget' ? 'cpu_benchmark_single_core' : 'cpu_benchmark_multi_core';
  const cpuCriterionLabel = appliedPresetKey === 'student_budget' ? 'CPU Geekbench 6 đơn nhân' : 'CPU Geekbench 6 đa nhân';

  const renderEmptyState = () => {
    if (presetKey === 'gaming' && Number(maxBudget) < 19500000) {
      return (
        <div className="bg-amber-50 border border-amber-200 rounded-2xl p-8 text-center text-amber-900 max-w-2xl mx-auto my-6 shadow-xs">
          <div className="text-4xl mb-3">🎮</div>
          <div className="font-black text-slate-900 text-base mb-1">
            Không có laptop Gaming thỏa mãn ngân sách {formatVnd(maxBudget)}
          </div>
          <p className="text-xs text-amber-900/90 leading-relaxed max-w-lg mx-auto mb-4">
            Theo chuẩn học thuật <b>D06</b>, hồ sơ Gaming lọc bắt buộc <b>GPU rời (NVIDIA RTX / AMD Radeon)</b> và <b>màn hình ≥ 144Hz</b>. Trên thị trường bán lẻ chính hãng hiện nay, dòng máy gaming nhập môn (như <i>Lenovo LOQ 15, Acer Nitro V, ASUS TUF Gaming</i>) có giá khởi điểm từ <b>19.490.000₫</b>. Dưới 19 triệu chỉ có laptop văn phòng dùng GPU tích hợp.
          </p>
          <button 
            onClick={() => {
              setMaxBudget(25000000);
              setLoading(true);
              fetch('/api/evaluate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                  preset_key: 'gaming',
                  min_budget_vnd: 0,
                  max_budget_vnd: 25000000
                })
              })
              .then(r => r.json())
              .then(data => {
                setRankings(data.rankings || []);
                setExcluded(data.excluded || []);
                setActiveCriteria(data.active_criteria || []);
                setLoading(false);
              });
            }}
            className="bg-[#d70018] hover:bg-[#b80014] text-white text-xs font-bold px-6 py-2.5 rounded-xl transition cursor-pointer shadow-xs inline-flex items-center gap-2"
          >
            <span>Nâng ngân sách lên 25 triệu để xem các dòng Gaming</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </div>
      );
    }
    return (
      <div className="bg-white border border-slate-200 rounded-2xl p-12 text-center text-slate-500">
        <Laptop className="w-12 h-12 text-slate-300 mx-auto mb-3" />
        <div className="font-bold text-slate-700 text-sm">Không tìm thấy máy phù hợp</div>
        <div className="text-xs text-slate-400 mt-1">Hãy tăng ngân sách hoặc chọn nhu cầu khác.</div>
      </div>
    );
  };

  const renderProductCard = (item, showTopsis = true) => {
    const rank = item.rank;
    const discount = formatDiscount(item.listed_price_vnd, item.sale_price_vnd);
    const fitPercent = Math.round((item.topsis_score || 0) * 100);
    const isInCompare = compareIds.includes(item.source_product_id);
    const isFav = isFavorite(item.source_product_id);

    return (
      <div 
        key={item.source_product_id}
        className={`bg-white rounded-2xl border-2 hover:shadow-lg transition p-4 flex flex-col justify-between ${
          isInCompare ? 'border-indigo-400 ring-2 ring-indigo-100' : 'border-slate-200 hover:border-[#d70018]'
        }`}
      >
        <div>
          {/* Huy hiệu thứ hạng & Giảm giá & Nút Yêu thích */}
          <div className="flex items-center justify-between gap-1 mb-2">
            <div className="flex items-center gap-1.5 flex-wrap">
              <span className={`text-[10px] font-black px-2 py-0.5 rounded ${
                rank === 1 ? 'bg-amber-100 text-amber-900 border border-amber-300' :
                rank === 2 ? 'bg-slate-100 text-slate-800 border border-slate-300' :
                rank === 3 ? 'bg-orange-100 text-orange-900 border border-orange-300' :
                'bg-slate-50 text-slate-600 border border-slate-200'
              }`}>
                {rank ? (rank === 1 ? 'TOP 1 theo hồ sơ' : `TOP #${rank}`) : 'Đã lưu'}
              </span>
              <span className={`text-[9px] font-bold px-1.5 py-0.5 rounded ${
                item.source === 'fpt_shop' || item.source === 'FPT Shop'
                  ? 'bg-rose-50 text-rose-700 border border-rose-200'
                  : 'bg-red-50 text-[#d70018] border border-red-200'
              }`}>
                {item.source === 'fpt_shop' || item.source === 'FPT Shop' ? 'FPT Shop' : 'CellphoneS'}
              </span>
              {item.is_good_deal && (
                <span className="text-[9px] font-black bg-emerald-100 text-emerald-800 border border-emerald-300 px-1.5 py-0.5 rounded shadow-xs">
                  🔥 KÈO THƠM
                </span>
              )}
            </div>
            
            <div className="flex items-center gap-1">
              {discount && (
                <span className="text-[10px] font-bold bg-rose-50 text-rose-600 px-1.5 py-0.5 rounded">
                  {discount}
                </span>
              )}
              <button
                type="button"
                onClick={(e) => {
                  e.stopPropagation();
                  toggleFavorite(item);
                }}
                className={`p-1.5 rounded-lg transition cursor-pointer border ${
                  isFav
                    ? 'bg-rose-50 border-rose-300 text-rose-600 hover:bg-rose-100'
                    : 'bg-slate-50 border-slate-200 text-slate-400 hover:text-rose-600 hover:border-rose-200'
                }`}
                title={isFav ? "Bỏ khỏi danh sách yêu thích" : "Lưu vào danh sách yêu thích"}
                aria-label={isFav ? "Bỏ yêu thích" : "Thêm vào yêu thích"}
              >
                <Heart className={`w-3.5 h-3.5 ${isFav ? 'fill-rose-600 text-rose-600' : ''}`} />
              </button>
            </div>
          </div>

          {/* Cảnh báo nếu có */}
          <div className="flex flex-wrap gap-1 mb-1">
            {item.explanation?.warnings && item.explanation.warnings.length > 0 && (
              <span className="text-[9px] font-bold bg-amber-50 text-amber-700 border border-amber-200 px-1 py-0.5 rounded" title={item.explanation.warnings[0]}>
                ⚠️ Ước lượng
              </span>
            )}
            {item.cpu_benchmark_match_level === 'unreleased_hardware' && (
              <span className="text-[9px] font-bold bg-amber-50 text-amber-800 border border-amber-300 px-1 py-0.5 rounded" title="Phần cứng chưa phát hành, không có benchmark xác thực.">
                Chưa phát hành
              </span>
            )}
          </div>

          {/* Ảnh laptop */}
          <div className="w-full h-36 flex items-center justify-center p-1.5 my-1 bg-white">
            <img 
              src={item.image_url} 
              alt={item.product_name_raw}
              className="max-h-full max-w-full object-contain hover:scale-105 transition duration-200"
              onError={(e) => { e.target.src = '/images/laptop_fallback.png'; }}
            />
          </div>

          {/* Dải thông số */}
          <div className="bg-slate-50 border border-slate-100 rounded-md px-1.5 py-1 text-center text-[10px] font-bold text-slate-700 my-2">
            {buildSpecsBadgeLine(item)}
          </div>

          {/* Tên laptop */}
          <h3 className="text-xs font-bold text-slate-900 line-clamp-2 min-h-8 mb-2 leading-snug">
            {item.product_name_raw}
          </h3>

          {/* Giá bán và giá ước tính OOF */}
          <div className="mb-2">
            <div className="flex items-baseline gap-1.5">
              <span className="text-base font-black text-[#d70018]">
                {formatVnd(item.sale_price_vnd)}
              </span>
              {discount && (
                <span className="text-[11px] text-slate-400 line-through">
                  {formatVnd(item.listed_price_vnd)}
                </span>
              )}
            </div>
            {item.ml_predicted_price_vnd && (
              <div className="flex items-center gap-1.5 text-[10px] text-slate-500 mt-0.5">
                <span className="text-slate-400">Giá ước tính OOF:</span>
                <span className="font-bold text-slate-700">{formatVnd(item.ml_predicted_price_vnd)}</span>
                {item.ml_value_gap_percent > 0 && (
                  <span className="text-[9px] font-bold text-emerald-600 bg-emerald-50 px-1 py-0.2 rounded border border-emerald-200">
                    +{item.ml_value_gap_percent}%
                  </span>
                )}
              </div>
            )}
          </div>

          {/* Thanh TOPSIS score (nếu có) */}
          {showTopsis && item.topsis_score != null && (
            <div className="mb-3">
              <div className="flex justify-between items-center text-[10px] mb-1">
                <span className="text-slate-500 font-medium">Điểm TOPSIS:</span>
                <span className="font-extrabold text-emerald-600">{fitPercent}%</span>
              </div>
              <div className="w-full h-1.5 bg-slate-100 rounded-full overflow-hidden">
                <div 
                  className="h-full bg-emerald-500 rounded-full"
                  style={{ width: `${fitPercent}%` }}
                />
              </div>
            </div>
          )}
        </div>

        {/* Nút hành động */}
        <div className="flex gap-2 mt-1">
          <button
            onClick={() => handleOpenDetail(item)}
            className="flex-1 py-2 px-3 rounded-xl text-xs font-bold bg-slate-100 hover:bg-[#d70018] hover:text-white text-slate-800 transition flex items-center justify-center gap-1.5 cursor-pointer"
          >
            <Eye className="w-3.5 h-3.5" />
            <span>Chi tiết</span>
          </button>
          <button
            onClick={() => toggleCompare(item.source_product_id)}
            className={`py-2 px-3 rounded-xl text-xs font-bold transition cursor-pointer flex items-center gap-1 ${
              isInCompare 
                ? 'bg-indigo-100 text-indigo-700 border border-indigo-300'
                : 'bg-slate-50 text-slate-500 border border-slate-200 hover:border-indigo-300 hover:text-indigo-600'
            }`}
            disabled={!isInCompare && compareIds.length >= 3}
          >
            <GitCompare className="w-3.5 h-3.5" />
            {isInCompare ? '✓' : 'So sánh'}
          </button>
        </div>
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-[#f8fafc] text-slate-900 pb-16">
      
      {/* Thanh công cụ chỉ hiển thị tìm kiếm; điều hướng chính nằm ở cột trái. */}
      <header className="sticky top-0 z-40 border-b border-slate-200 bg-white/95 backdrop-blur">
        <div className="max-w-[1440px] mx-auto px-4 lg:px-6 py-3 flex items-center justify-between gap-4">
          <button onClick={() => goToPage('recommend')} className="flex items-center gap-2 font-black text-slate-900 hover:text-[#d70018] transition">
            <span className="w-8 h-8 rounded-lg bg-[#d70018] text-white flex items-center justify-center">💻</span>
            <span>Laptop<span className="text-[#d70018]">DSS</span></span>
          </button>
          <div className="flex-1 max-w-xl relative">
            <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
            <input type="text" placeholder="Tìm tên máy, CPU hoặc GPU" value={searchQuery} onChange={(e) => setSearchQuery(e.target.value)} className="w-full pl-10 pr-4 py-2 bg-slate-50 text-slate-900 placeholder:text-slate-400 rounded-xl border border-slate-200 text-xs font-medium focus:outline-none focus:ring-2 focus:ring-red-200" />
          </div>
          <div className="hidden md:flex items-center gap-2 text-xs text-slate-500"><ShieldCheck className="w-4 h-4 text-emerald-600" /><span>CSDL 513 cấu hình chuẩn hóa</span></div>
        </div>
      </header>

      <div className="max-w-[1440px] mx-auto px-4 md:px-6 py-5 md:flex md:gap-6">
        <aside className="md:w-56 md:shrink-0 mb-4 md:mb-0">
          <nav className="md:sticky md:top-20 bg-white border border-slate-200 rounded-2xl p-2 shadow-xs flex md:flex-col gap-1 overflow-x-auto" aria-label="Điều hướng chính">
            <button onClick={() => goToPage('recommend')} className={`shrink-0 text-left flex items-center gap-3 px-3 py-3 rounded-xl text-sm font-bold transition ${currentPage === 'recommend' || currentPage === 'detail' ? 'bg-red-50 text-[#d70018]' : 'text-slate-600 hover:bg-slate-50'}`}><ListFilter className="w-4 h-4" /><span>Gợi ý & bộ lọc</span></button>
            <button onClick={() => goToPage('analysis')} className={`shrink-0 text-left flex items-center gap-3 px-3 py-3 rounded-xl text-sm font-bold transition ${currentPage === 'analysis' ? 'bg-red-50 text-[#d70018]' : 'text-slate-600 hover:bg-slate-50'}`}><ChartNoAxesCombined className="w-4 h-4" /><span>Phân tích dữ liệu</span></button>
            <button onClick={() => goToPage('methodology')} className={`shrink-0 text-left flex items-center gap-3 px-3 py-3 rounded-xl text-sm font-bold transition ${currentPage === 'methodology' ? 'bg-red-50 text-[#d70018]' : 'text-slate-600 hover:bg-slate-50'}`}><BookOpen className="w-4 h-4" /><span>Phương pháp</span></button>
          </nav>
        </aside>
        <div className="min-w-0 flex-1">

      {/* ═══════════════════════════════════════════════════════════════ */}
      {/* DETAIL VIEW */}
      {/* ═══════════════════════════════════════════════════════════════ */}
      {viewMode === 'detail' && selectedLaptop ? (
        <main className="max-w-7xl mx-auto px-4 mt-5">
          <button 
            onClick={() => goToPage('recommend')}
            className="mb-4 inline-flex items-center gap-2 text-xs font-bold text-slate-600 hover:text-[#d70018] bg-white border border-slate-200 px-4 py-2 rounded-xl transition cursor-pointer shadow-xs"
          >
            <ArrowLeft className="w-4 h-4" />
            <span>Quay lại danh sách đề xuất ({displayedRankings.length} máy)</span>
          </button>

          {/* SHOWCASE SẢN PHẨM */}
          <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-xs mb-6">
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
              
              {/* Bên trái: Ảnh */}
              <div className="lg:col-span-5 flex flex-col items-center">
                <div className="w-full h-80 bg-white border border-slate-100 rounded-2xl p-4 flex items-center justify-center relative shadow-xs">
                  <span className="absolute top-3 left-3 text-[11px] font-black bg-amber-100 text-amber-900 border border-amber-300 px-2.5 py-1 rounded-md">
                    TOP #{selectedLaptop.rank} ĐỀ XUẤT
                  </span>
                  <img 
                    src={selectedLaptop.image_url} 
                    alt={selectedLaptop.product_name_raw}
                    className="max-h-full max-w-full object-contain"
                    onError={(e) => { e.target.src = '/images/laptop_fallback.png'; }}
                  />
                </div>
              </div>

              {/* Bên phải: Tên, Giá, Đánh giá DSS */}
              <div className="lg:col-span-7 flex flex-col justify-between h-full">
                <div>
                  <div className="flex items-center gap-3 text-xs text-slate-400 mb-1">
                    <span>Mã sản phẩm: <b className="text-slate-700">No.{selectedLaptop.source_product_id}</b></span>
                  </div>

                  <h1 className="text-xl font-black text-slate-900 leading-snug mb-3">
                    {selectedLaptop.product_name_raw}
                  </h1>

                  {/* Khối giá bán */}
                  <div className="bg-red-50/50 border border-red-100 rounded-2xl p-4 mb-4 flex flex-wrap items-center justify-between gap-4">
                    <div>
                      <div className="text-xs text-slate-500 font-medium">Giá bán:</div>
                      <div className="text-3xl font-black text-[#d70018] tracking-tight">
                        {formatVnd(selectedLaptop.sale_price_vnd)}
                      </div>
                      {formatDiscount(selectedLaptop.listed_price_vnd, selectedLaptop.sale_price_vnd) && (
                        <div className="flex items-center gap-2 mt-0.5">
                          <span className="text-xs text-slate-400 line-through">
                            {formatVnd(selectedLaptop.listed_price_vnd)}
                          </span>
                          <span className="text-xs font-bold bg-red-100 text-[#d70018] px-1.5 py-0.5 rounded">
                            Tiết kiệm {formatDiscount(selectedLaptop.listed_price_vnd, selectedLaptop.sale_price_vnd)}
                          </span>
                        </div>
                      )}
                    </div>

                    <div className="bg-white px-4 py-2.5 rounded-xl border border-red-200/60 shadow-xs text-center">
                      <div className="text-[11px] text-slate-500 font-bold uppercase tracking-wider">Điểm TOPSIS</div>
                      <div className="text-2xl font-black text-emerald-600">
                        {Math.round((selectedLaptop.topsis_score || 0) * 100)}%
                      </div>
                      <div className="text-[10px] text-emerald-700 font-semibold">Profile: {CATEGORIES.find(c => c.key === presetKey)?.name}</div>
                    </div>
                  </div>

                  {/* Tóm tắt thông số */}
                  <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 mb-5">
                    <div className="bg-slate-50 p-2.5 rounded-xl border border-slate-200/80">
                      <div className="text-[10px] text-slate-400 uppercase font-bold">Vi xử lý</div>
                      <div className="text-xs font-bold text-slate-800 truncate">{selectedLaptop.cpu_name_normalized}</div>
                    </div>
                    <div className="bg-slate-50 p-2.5 rounded-xl border border-slate-200/80">
                      <div className="text-[10px] text-slate-400 uppercase font-bold">Đồ họa (GPU)</div>
                      <div className="text-xs font-bold text-slate-800 truncate">{selectedLaptop.gpu_name_normalized}</div>
                    </div>
                    <div className="bg-slate-50 p-2.5 rounded-xl border border-slate-200/80">
                      <div className="text-[10px] text-slate-400 uppercase font-bold">RAM</div>
                      <div className="text-xs font-bold text-slate-800">{selectedLaptop.ram_gb} GB {selectedLaptop.ram_type}</div>
                    </div>
                    <div className="bg-slate-50 p-2.5 rounded-xl border border-slate-200/80">
                      <div className="text-[10px] text-slate-400 uppercase font-bold">Ổ cứng</div>
                      <div className="text-xs font-bold text-slate-800">{selectedLaptop.storage_total_gb} GB SSD</div>
                    </div>
                  </div>
                </div>

                {/* Nút hành động */}
                <div className="flex flex-wrap gap-3 pt-2">
                  <a 
                    href={selectedLaptop.source_url} 
                    target="_blank" 
                    rel="noreferrer"
                    className="flex-1 min-w-[200px] bg-[#d70018] hover:bg-[#b80014] text-white font-bold py-3 px-6 rounded-xl transition text-center text-sm shadow-sm flex items-center justify-center gap-2"
                  >
                    <span>Xem sản phẩm tại {selectedLaptop.source === 'cellphones' ? 'CellphoneS' : 'FPT Shop'}</span>
                    <ExternalLink className="w-4 h-4" />
                  </a>
                  <button 
                    type="button"
                    onClick={() => toggleFavorite(selectedLaptop)}
                    className={`px-4 py-3 rounded-xl font-bold text-sm transition flex items-center justify-center gap-2 cursor-pointer border ${
                      isFavorite(selectedLaptop.source_product_id)
                        ? 'bg-rose-50 border-rose-300 text-rose-700 hover:bg-rose-100'
                        : 'bg-white border-slate-200 text-slate-700 hover:border-rose-300 hover:text-rose-600'
                    }`}
                    title={isFavorite(selectedLaptop.source_product_id) ? "Bỏ khỏi danh sách yêu thích" : "Lưu vào danh sách yêu thích"}
                  >
                    <Heart className={`w-4 h-4 ${isFavorite(selectedLaptop.source_product_id) ? 'fill-rose-600 text-rose-600' : ''}`} />
                    <span>{isFavorite(selectedLaptop.source_product_id) ? 'Đã yêu thích' : 'Lưu yêu thích'}</span>
                  </button>
                  <button 
                    onClick={() => setViewMode('list')}
                    className="px-6 py-3 bg-slate-100 hover:bg-slate-200 text-slate-800 font-bold rounded-xl transition text-sm cursor-pointer"
                  >
                    Đổi máy khác
                  </button>
                </div>
              </div>
            </div>
          </div>

          {/* TAB PANE */}
          <div className="bg-white border border-slate-200 rounded-2xl shadow-xs overflow-hidden mb-8">
            <div className="flex border-b border-slate-200 bg-slate-50/50 overflow-x-auto">
              {[
                { key: 'config', label: '⚙️ Cấu hình & Bộ nhớ' },
                { key: 'screen', label: '🖥️ Màn hình' },
                { key: 'ports', label: '🔌 Cổng kết nối' },
                { key: 'design', label: '📦 Thiết kế, Pin & Trọng lượng' },
                { key: 'dss', label: '💡 Phân tích & Đánh giá DSS' },
              ].map(t => (
                <button
                  key={t.key}
                  onClick={() => setDetailTab(t.key)}
                  className={`py-3.5 px-6 font-bold text-xs sm:text-sm whitespace-nowrap transition border-b-2 cursor-pointer ${
                    detailTab === t.key
                      ? 'border-[#d70018] text-[#d70018] bg-white shadow-xs'
                      : 'border-transparent text-slate-600 hover:text-slate-900 hover:bg-slate-100/60'
                  }`}
                >
                  {t.label}
                </button>
              ))}
            </div>

            <div className="p-6">
              
              {/* TAB 1: CẤU HÌNH */}
              {detailTab === 'config' && (
                <div className="divide-y divide-slate-100 text-sm">
                  <div className="py-2.5 flex justify-between"><span className="text-slate-500">Tên vi xử lý (CPU)</span><span className="font-bold text-slate-900">{selectedLaptop.cpu_name_normalized || 'Chưa công bố'}</span></div>
                  <div className="py-2.5 flex justify-between"><span className="text-slate-500">Số nhân / Số luồng</span><span className="font-bold text-slate-900">{selectedLaptop.cpu_cores ? `${selectedLaptop.cpu_cores} nhân / ${selectedLaptop.cpu_threads || selectedLaptop.cpu_cores} luồng` : 'Chưa công bố'}</span></div>
                  <div className="py-2.5 flex justify-between"><span className="text-slate-500">Tốc độ xung nhịp</span><span className="font-bold text-slate-900">{selectedLaptop.cpu_base_ghz ? `${selectedLaptop.cpu_base_ghz} GHz (Cơ bản) – ${selectedLaptop.cpu_boost_ghz || selectedLaptop.cpu_base_ghz} GHz (Tối đa)` : 'Chưa công bố'}</span></div>
                  <div className="py-2.5 flex justify-between"><span className="text-slate-500">Card đồ họa (GPU)</span><span className="font-bold text-slate-900">{selectedLaptop.gpu_name_normalized || 'GPU tích hợp'}</span></div>
                  <div className="py-2.5 flex justify-between"><span className="text-slate-500">Bộ nhớ đồ họa VRAM</span><span className="font-bold text-slate-900">{selectedLaptop.gpu_vram_gb ? `${selectedLaptop.gpu_vram_gb} GB GDDR6` : 'Chia sẻ từ RAM'}</span></div>
                  <div className="py-2.5 flex justify-between"><span className="text-slate-500">Dung lượng RAM</span><span className="font-bold text-slate-900">{selectedLaptop.ram_gb} GB {selectedLaptop.ram_type || ''}</span></div>
                  <div className="py-2.5 flex justify-between"><span className="text-slate-500">Số khe RAM & Khả năng nâng cấp</span><span className="font-bold text-slate-900">{selectedLaptop.ram_slots ? `${selectedLaptop.ram_slots} khe (Trống ${selectedLaptop.ram_slots_free || 0}) • Tối đa ${selectedLaptop.max_ram_gb || selectedLaptop.ram_gb} GB` : 'Chưa công bố'}</span></div>
                  <div className="py-2.5 flex justify-between"><span className="text-slate-500">Ổ cứng lưu trữ</span><span className="font-bold text-slate-900">{selectedLaptop.storage_total_gb} GB {selectedLaptop.storage_primary_type || 'SSD NVMe'}</span></div>
                  <div className="py-2.5 flex justify-between"><span className="text-slate-500">Điểm kiểm chuẩn CPU Geekbench 6</span><span className="font-bold text-emerald-700">{selectedLaptop.cpu_benchmark_multi_core ? `${Number(selectedLaptop.cpu_benchmark_multi_core).toLocaleString()} điểm (${selectedLaptop.cpu_benchmark_match_level})` : 'Chưa có mẫu xác thực (theo Data.md)'}</span></div>
                  <div className="py-2.5 flex justify-between"><span className="text-slate-500">Điểm kiểm chuẩn GPU 3DMark Time Spy</span><span className="font-bold text-emerald-700">{selectedLaptop.gpu_benchmark_time_spy ? `${Number(selectedLaptop.gpu_benchmark_time_spy).toLocaleString()} điểm (${selectedLaptop.gpu_benchmark_match_level})` : 'Không dùng card rời (theo Data.md)'}</span></div>
                </div>
              )}

              {/* TAB 2: MÀN HÌNH */}
              {detailTab === 'screen' && (
                <div className="divide-y divide-slate-100 text-sm">
                  <div className="py-2.5 flex justify-between"><span className="text-slate-500">Kích thước màn hình</span><span className="font-bold text-slate-900">{selectedLaptop.screen_size_inch ? `${selectedLaptop.screen_size_inch}" inch` : 'Chưa công bố'}</span></div>
                  <div className="py-2.5 flex justify-between"><span className="text-slate-500">Độ phân giải hiển thị</span><span className="font-bold text-slate-900">{selectedLaptop.screen_width_px && selectedLaptop.screen_height_px ? `${selectedLaptop.screen_width_px} × ${selectedLaptop.screen_height_px} pixels` : 'Chưa công bố'}</span></div>
                  <div className="py-2.5 flex justify-between"><span className="text-slate-500">Công nghệ tấm nền</span><span className="font-bold text-slate-900">{selectedLaptop.panel_type || 'Chưa công bố'}</span></div>
                  <div className="py-2.5 flex justify-between"><span className="text-slate-500">Tần số quét</span><span className="font-bold text-slate-900">{selectedLaptop.refresh_rate_hz ? `${selectedLaptop.refresh_rate_hz} Hz` : 'Chưa công bố'}</span></div>
                  <div className="py-2.5 flex justify-between"><span className="text-slate-500">Độ sáng tối đa</span><span className="font-bold text-slate-900">{selectedLaptop.brightness_nits ? `${selectedLaptop.brightness_nits} nits` : 'Chưa công bố'}</span></div>
                  <div className="py-2.5 flex justify-between"><span className="text-slate-500">Độ phủ màu sắc</span><span className="font-bold text-slate-900">{selectedLaptop.color_gamut_raw || 'Chưa công bố'}</span></div>
                </div>
              )}

              {/* TAB 3: CỔNG KẾT NỐI */}
              {detailTab === 'ports' && (
                <div className="divide-y divide-slate-100 text-sm">
                  <div className="py-2.5 flex justify-between"><span className="text-slate-500">Cổng USB Type-A</span><span className="font-bold text-slate-900">{selectedLaptop.usb_a_count !== undefined && selectedLaptop.usb_a_count !== '' ? `${selectedLaptop.usb_a_count} cổng` : 'Chưa công bố'}</span></div>
                  <div className="py-2.5 flex justify-between"><span className="text-slate-500">Cổng USB Type-C</span><span className="font-bold text-slate-900">{selectedLaptop.usb_c_count !== undefined && selectedLaptop.usb_c_count !== '' ? `${selectedLaptop.usb_c_count} cổng` : 'Chưa công bố'}</span></div>
                  <div className="py-2.5 flex justify-between"><span className="text-slate-500">Cổng HDMI</span><span className="font-bold text-slate-900">{selectedLaptop.hdmi_present === 'true' ? 'Có trang bị' : (selectedLaptop.hdmi_present === 'false' ? 'Không có' : 'Chưa công bố')}</span></div>
                  <div className="py-2.5 flex justify-between"><span className="text-slate-500">Cổng mạng LAN (RJ45)</span><span className="font-bold text-slate-900">{selectedLaptop.lan_present === 'true' ? 'Có (Gigabit Ethernet)' : (selectedLaptop.lan_present === 'false' ? 'Không có' : 'Chưa công bố')}</span></div>
                  <div className="py-2.5 flex justify-between"><span className="text-slate-500">Jack tai nghe 3.5mm</span><span className="font-bold text-slate-900">{selectedLaptop.audio_jack_present === 'true' ? 'Có tích hợp' : (selectedLaptop.audio_jack_present === 'false' ? 'Không có' : 'Chưa công bố')}</span></div>
                  <div className="py-2.5 flex justify-between"><span className="text-slate-500">Wi-Fi</span><span className="font-bold text-slate-900">{selectedLaptop.wifi_raw || 'Chưa công bố'}</span></div>
                  <div className="py-2.5 flex justify-between"><span className="text-slate-500">Bluetooth</span><span className="font-bold text-slate-900">{selectedLaptop.bluetooth_raw || 'Chưa công bố'}</span></div>
                </div>
              )}

              {/* TAB 4: THIẾT KẾ & PIN */}
              {detailTab === 'design' && (
                <div className="divide-y divide-slate-100 text-sm">
                  <div className="py-2.5 flex justify-between"><span className="text-slate-500">Trọng lượng máy</span><span className="font-bold text-slate-900">{selectedLaptop.weight_kg ? `${selectedLaptop.weight_kg} kg` : 'Chưa công bố'}</span></div>
                  <div className="py-2.5 flex justify-between"><span className="text-slate-500">Độ dày thân máy</span><span className="font-bold text-slate-900">{selectedLaptop.thickness_mm ? `${selectedLaptop.thickness_mm} mm` : 'Chưa công bố'}</span></div>
                  <div className="py-2.5 flex justify-between"><span className="text-slate-500">Chất liệu vỏ</span><span className="font-bold text-slate-900">{selectedLaptop.material_raw || 'Chưa công bố'}</span></div>
                  <div className="py-2.5 flex justify-between"><span className="text-slate-500">Dung lượng Pin</span><span className="font-bold text-slate-900">{selectedLaptop.battery_capacity_wh ? `${selectedLaptop.battery_capacity_wh} Wh` : 'Chưa công bố'}</span></div>
                  <div className="py-2.5 flex justify-between"><span className="text-slate-500">Công suất sạc</span><span className="font-bold text-slate-900">{selectedLaptop.charger_w ? `${selectedLaptop.charger_w} W` : 'Chưa công bố'}</span></div>
                  <div className="py-2.5 flex justify-between"><span className="text-slate-500">Hệ điều hành</span><span className="font-bold text-slate-900">{selectedLaptop.os_name || 'Chưa công bố'}</span></div>
                  <div className="py-2.5 flex justify-between"><span className="text-slate-500">Bảo hành</span><span className="font-bold text-slate-900">{selectedLaptop.warranty_months ? `${selectedLaptop.warranty_months} tháng` : 'Chưa công bố'}</span></div>
                </div>
              )}

              {/* TAB 5: DSS */}
              {detailTab === 'dss' && (
                <div className="space-y-4 text-sm">
                  <div className="bg-emerald-50 border border-emerald-200 p-4 rounded-xl">
                    <div className="font-bold text-emerald-900 text-base mb-1">
                      ⭐ Vị trí xếp hạng: Top #{selectedLaptop.rank}
                    </div>
                    <p className="text-emerald-800 text-xs leading-relaxed">
                      Trong nhóm nhu cầu <b>{CATEGORIES.find(c => c.key === presetKey)?.name}</b>, chiếc máy này đạt 
                      điểm TOPSIS <b>{Math.round((selectedLaptop.topsis_score || 0) * 100)}%</b>. 
                      Đây là chỉ số đo khoảng cách đến phương án lý tưởng (TOPSIS — Technique for Order of Preference by Similarity to Ideal Solution).
                    </p>
                  </div>

                  {/* ML FAIR PRICE & SHAP EVALUATION (GĐ4 & D10) */}
                  <div className="bg-indigo-50/70 border border-indigo-200 rounded-2xl p-5 mb-5">
                    <div className="flex items-center justify-between mb-3">
                      <div className="flex items-center gap-2">
                        <span className="text-lg">🤖</span>
                        <h4 className="font-extrabold text-indigo-900 text-sm">
                          Thẩm định giá thị trường bằng hồi quy (GĐ4)
                        </h4>
                      </div>
                      {selectedLaptop.is_good_deal && (
                        <span className="text-[10px] font-black bg-emerald-100 text-emerald-800 border border-emerald-300 px-2.5 py-0.5 rounded-full shadow-xs animate-pulse">
                          🔥 KÈO THƠM THỊ TRƯỜNG
                        </span>
                      )}
                    </div>
                    <p className="text-xs text-indigo-800 leading-relaxed mb-4">
                      Mô hình hồi quy <b>Gradient Boosting</b> (R² = 0.9028, MAPE = 11.16%) ước tính giá trị phần cứng công bằng độc lập (Out-Of-Fold) theo nguyên tắc <b>DECISIONS.md D10</b> để kiểm chứng tính tương quan giá.
                    </p>
                    <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-center">
                      <div className="bg-white p-3 rounded-xl border border-indigo-100 shadow-xs">
                        <div className="text-[10px] text-slate-400 uppercase font-bold">Giá bán thực tế</div>
                        <div className="text-base font-black text-rose-600">{formatVnd(selectedLaptop.sale_price_vnd)}</div>
                      </div>
                      <div className="bg-white p-3 rounded-xl border border-indigo-100 shadow-xs">
                        <div className="text-[10px] text-slate-400 uppercase font-bold">Giá ước tính OOF</div>
                        <div className="text-base font-black text-indigo-700">
                          {selectedLaptop.ml_predicted_price_vnd ? formatVnd(selectedLaptop.ml_predicted_price_vnd) : 'Không đủ dữ liệu'}
                        </div>
                      </div>
                      <div className="bg-white p-3 rounded-xl border border-indigo-100 shadow-xs">
                        <div className="text-[10px] text-slate-400 uppercase font-bold">Chênh lệch giá trị (Value Gap)</div>
                        <div className={`text-base font-black ${selectedLaptop.ml_value_gap_percent > 0 ? 'text-emerald-600' : 'text-slate-700'}`}>
                          {selectedLaptop.ml_value_gap_percent == null ? 'Không đủ dữ liệu thẩm định ML' : selectedLaptop.ml_value_gap_percent > 0 ? `+${selectedLaptop.ml_value_gap_percent}% (Hời)` : `${selectedLaptop.ml_value_gap_percent}%`}
                        </div>
                      </div>
                    </div>
                    {selectedLaptop.ml_lower_bound_vnd && (
                      <div className="text-[11px] text-indigo-700 mt-3 text-center">
                        Khoảng tin cậy thống kê 95% (±1.96σ): <b>{formatVnd(selectedLaptop.ml_lower_bound_vnd)}</b> – <b>{formatVnd(selectedLaptop.ml_upper_bound_vnd)}</b>
                      </div>
                    )}
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="bg-slate-50 p-4 rounded-xl border border-slate-200">
                      <div className="font-bold text-slate-800 flex items-center gap-2 mb-2">
                        <Check className="w-4 h-4 text-emerald-600" />
                        <span>Ưu thế vượt trội:</span>
                      </div>
                      <div className="text-xs text-slate-600">
                        {selectedLaptop.explanation?.top_advantage ? (
                          <span>Điểm số cao nhờ <b>{formatExplanationText(selectedLaptop.explanation.top_advantage, 'advantage')}</b>.</span>
                        ) : 'Hiệu năng cân bằng toàn diện trong phân khúc giá.'}
                      </div>
                    </div>

                    <div className="bg-slate-50 p-4 rounded-xl border border-slate-200">
                      <div className="font-bold text-slate-800 flex items-center gap-2 mb-2">
                        <Info className="w-4 h-4 text-amber-600" />
                        <span>Điểm cần cân nhắc / đánh đổi:</span>
                      </div>
                      <div className="text-xs text-slate-600">
                        {selectedLaptop.explanation?.top_penalty ? (
                          <span>Điểm bị kéo lùi ở mục <b>{formatExplanationText(selectedLaptop.explanation.top_penalty, 'penalty')}</b>.</span>
                        ) : 'Không có hạn chế lớn trong tầm giá này.'}
                      </div>
                    </div>
                  </div>
                </div>
              )}

            </div>
          </div>
        </main>
      ) : (

      /* ═══════════════════════════════════════════════════════════════ */
      /* LIST VIEW */
      /* ═══════════════════════════════════════════════════════════════ */
      <main className="mt-0">
        {currentPage === 'recommend' && <>
        
        {/* ── 4 TAB NAVIGATION PANE ── */}
        <div className="bg-white border border-slate-200 rounded-2xl p-1.5 shadow-xs mb-6 grid grid-cols-2 md:grid-cols-4 gap-1.5">
          <button
            type="button"
            onClick={() => setMainTab('recommend')}
            className={`flex items-center gap-2.5 px-3.5 py-2.5 rounded-xl text-left transition cursor-pointer ${
              mainTab === 'recommend'
                ? 'bg-slate-900 text-white shadow-xs font-bold'
                : 'text-slate-600 hover:bg-slate-100 hover:text-slate-900 font-semibold'
            }`}
          >
            <span className="text-lg">🎯</span>
            <div className="min-w-0">
              <div className="text-xs leading-tight truncate">Gợi ý theo Nhu cầu</div>
              <div className={`text-[10px] truncate ${mainTab === 'recommend' ? 'text-slate-300' : 'text-slate-400'}`}>
                Hồ sơ & ngân sách
              </div>
            </div>
          </button>

          <button
            type="button"
            onClick={() => setMainTab('nlp')}
            className={`flex items-center gap-2.5 px-3.5 py-2.5 rounded-xl text-left transition cursor-pointer ${
              mainTab === 'nlp'
                ? 'bg-slate-900 text-white shadow-xs font-bold'
                : 'text-slate-600 hover:bg-slate-100 hover:text-slate-900 font-semibold'
            }`}
          >
            <span className="text-lg">💬</span>
            <div className="min-w-0">
              <div className="text-xs leading-tight truncate">Trợ lý Tìm kiếm AI</div>
              <div className={`text-[10px] truncate ${mainTab === 'nlp' ? 'text-slate-300' : 'text-slate-400'}`}>
                Bóc tách yêu cầu tự nhiên
              </div>
            </div>
          </button>

          <button
            type="button"
            onClick={() => setMainTab('filters')}
            className={`flex items-center gap-2.5 px-3.5 py-2.5 rounded-xl text-left transition cursor-pointer ${
              mainTab === 'filters'
                ? 'bg-slate-900 text-white shadow-xs font-bold'
                : 'text-slate-600 hover:bg-slate-100 hover:text-slate-900 font-semibold'
            }`}
          >
            <span className="text-lg">⚙️</span>
            <div className="min-w-0">
              <div className="text-xs leading-tight truncate">Bộ lọc & Trọng số</div>
              <div className={`text-[10px] truncate ${mainTab === 'filters' ? 'text-slate-300' : 'text-slate-400'}`}>
                Cấu hình chi tiết & AHP
              </div>
            </div>
          </button>

          <button
            type="button"
            onClick={() => setMainTab('favorites')}
            className={`flex items-center gap-2.5 px-3.5 py-2.5 rounded-xl text-left transition cursor-pointer ${
              mainTab === 'favorites'
                ? 'bg-rose-600 text-white shadow-xs font-bold'
                : 'text-slate-600 hover:bg-rose-50 hover:text-rose-700 font-semibold'
            }`}
          >
            <span className="text-lg">❤️</span>
            <div className="min-w-0">
              <div className="text-xs leading-tight truncate">
                Đã lưu ({favorites.length})
              </div>
              <div className={`text-[10px] truncate ${mainTab === 'favorites' ? 'text-rose-200' : 'text-slate-400'}`}>
                Laptop yêu thích
              </div>
            </div>
          </button>
        </div>

        {evaluationError && (
          <div role="alert" className="mb-4 flex items-start gap-3 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-xs text-red-800">
            <Info className="mt-0.5 h-4 w-4 shrink-0" />
            <div>
              <b>Chưa thể tạo xếp hạng.</b> {evaluationError}
              <div className="mt-1 text-red-700">Lệnh chạy backend: <code className="rounded bg-white px-1 py-0.5">python -X utf8 -m uvicorn src.api:app --host 127.0.0.1 --port 8000</code></div>
            </div>
          </div>
        )}

        {/* ═══════════════════════════════════════════════════════════════ */}
        {/* TAB 1: GỢI Ý THEO NHU CẦU (DEFAULT) */}
        {/* ═══════════════════════════════════════════════════════════════ */}
        {mainTab === 'recommend' && (
          <div>
            {/* 1. Nhu cầu sử dụng */}
            <section className="mb-6">
              <div className="flex items-center justify-between mb-3">
                <h2 className="text-base font-black text-slate-900 tracking-tight">
                  Nhu cầu sử dụng
                </h2>
                <span className="text-xs text-slate-500">Bấm chọn nhu cầu để tự động tải danh sách laptop tương ứng</span>
              </div>

              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3.5">
                {CATEGORIES.map(cat => (
                  <div 
                    key={cat.key}
                    onClick={() => handleCategoryClick(cat.key)}
                    className={`p-3.5 rounded-2xl border-2 transition cursor-pointer flex flex-col items-center text-center bg-white shadow-xs group ${
                      presetKey === cat.key 
                        ? 'border-[#d70018] ring-2 ring-red-100 bg-red-50/20' 
                        : 'border-slate-200 hover:border-slate-300 hover:bg-slate-50/40'
                    }`}
                  >
                    <div className="text-3xl mb-2">{cat.icon}</div>
                    <div className={`text-xs font-bold ${presetKey === cat.key ? 'text-[#d70018]' : 'text-slate-900'}`}>
                      {cat.name}
                    </div>
                    <div className="text-[10px] text-slate-400 mt-0.5 line-clamp-1">{cat.sub}</div>
                  </div>
                ))}
              </div>
              <div className="mt-3 rounded-xl border border-slate-200 bg-slate-50 px-3 py-2 text-xs text-slate-600 flex items-center justify-between">
                <div>
                  <b className="text-slate-800">Hồ sơ: {selectedCategory?.name}.</b> {selectedCategory?.sub}.
                </div>
                <button 
                  onClick={() => setMainTab('filters')} 
                  className="text-[#d70018] hover:underline font-bold text-xs inline-flex items-center gap-1 cursor-pointer"
                >
                  <SlidersHorizontal className="w-3.5 h-3.5" />
                  <span>Tùy biến trọng số AHP</span>
                </button>
              </div>
            </section>

            {/* Thanh lọc nhanh: Ngân sách & Hãng */}
            <section className="bg-white border border-slate-200 rounded-2xl p-4 shadow-xs mb-6">
              <div className="grid grid-cols-1 md:grid-cols-12 gap-4 items-center">
                {/* Budget Slider + Presets */}
                <div className="md:col-span-8 bg-slate-50 p-3 rounded-xl border border-slate-200">
                  <div className="flex justify-between text-xs text-slate-600 mb-1 font-medium">
                    <span className="flex items-center gap-1">
                      <span className="font-bold text-slate-800">Trần ngân sách tối đa:</span>
                      <span className="text-[10px] text-slate-400 font-normal">(≤ mức này)</span>
                    </span>
                    <span className="font-black text-[#d70018] text-sm">{formatVnd(maxBudget)}</span>
                  </div>
                  <input
                    type="range" min="0" max="50000000" step="1000000"
                    value={maxBudget}
                    onChange={(e) => setMaxBudget(e.target.value)}
                    className="w-full accent-[#d70018] cursor-pointer"
                  />
                  <div className="flex justify-between items-center text-[10px] text-slate-400 mt-1.5">
                    <div className="flex gap-1.5 flex-wrap">
                      {[15000000, 20000000, 25000000, 35000000, 50000000].map(amt => (
                        <button
                          key={amt}
                          type="button"
                          onClick={() => setMaxBudget(amt)}
                          className={`px-2 py-0.5 rounded border transition cursor-pointer text-[10px] ${
                            Number(maxBudget) === amt 
                              ? 'bg-red-50 border-[#d70018] text-[#d70018] font-bold' 
                              : 'bg-white border-slate-200 text-slate-600 hover:border-slate-300'
                          }`}
                        >
                          {amt === 50000000 ? 'Tất cả' : `≤ ${amt / 1000000}tr`}
                        </button>
                      ))}
                    </div>
                    <span>Tối đa 50tr</span>
                  </div>
                </div>

                {/* Brand & Action */}
                <div className="md:col-span-4 flex flex-col justify-between h-full gap-2">
                  <div>
                    <label className="text-[11px] font-bold text-slate-600 block mb-1">Hãng sản xuất:</label>
                    <select 
                      value={brand} 
                      onChange={(e) => setBrand(e.target.value)}
                      className="w-full bg-slate-50 border border-slate-200 rounded-xl py-2 px-3 text-xs font-semibold focus:outline-none focus:border-[#d70018]"
                    >
                      {['Tất cả', 'ASUS', 'MSI', 'Lenovo', 'Dell', 'HP', 'Acer', 'Apple'].map(b => (
                        <option key={b} value={b}>{b}</option>
                      ))}
                    </select>
                  </div>

                  <button 
                    onClick={handleApplyFilter}
                    disabled={loading}
                    className="w-full bg-[#d70018] hover:bg-[#b80014] disabled:bg-red-300 text-white text-xs font-bold py-2 px-4 rounded-xl transition flex items-center justify-center gap-1.5 cursor-pointer shadow-xs"
                  >
                    <Filter className="w-3.5 h-3.5" />
                    <span>{loading ? 'Đang đánh giá...' : 'Duyệt & Cập nhật danh sách'}</span>
                  </button>
                </div>
              </div>
              {hasPendingEvaluation && (
                <div className="mt-2 text-[11px] text-amber-700 font-semibold bg-amber-50 px-3 py-1.5 rounded-lg border border-amber-200">
                  ⚠️ Bạn đã thay đổi ngân sách hoặc nhu cầu. Bấm <b>Duyệt & Cập nhật danh sách</b> để tính toán lại điểm TOPSIS.
                </div>
              )}
            </section>

            {/* Lưới sản phẩm */}
            <section className="mb-8">
              <div className="flex items-center justify-between mb-3">
                <h2 className="text-base font-black text-slate-900 flex items-center gap-2">
                  <span>Danh sách đề xuất theo hồ sơ</span>
                  <span className="text-xs bg-red-100 text-[#d70018] font-bold px-2.5 py-0.5 rounded-full">
                    {displayedRankings.length} máy
                  </span>
                  {isCustomWeightsActive && (
                    <span className="text-xs bg-indigo-100 text-indigo-700 font-bold px-2 py-0.5 rounded-full">
                      Trọng số tùy chỉnh
                    </span>
                  )}
                </h2>
                <div className="text-xs text-slate-400">
                  Sắp xếp theo: <b className="text-slate-700">Độ phù hợp nhu cầu giảm dần (TOPSIS)</b>
                </div>
              </div>

              {displayedRankings.length === 0 ? (
                renderEmptyState()
              ) : (
                <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
                  {displayedRankings.map(item => renderProductCard(item, true))}
                </div>
              )}
            </section>
          </div>
        )}

        {/* ═══════════════════════════════════════════════════════════════ */}
        {/* TAB 2: TRỢ LÝ TÌM KIẾM AI / NLP */}
        {/* ═══════════════════════════════════════════════════════════════ */}
        {mainTab === 'nlp' && (
          <div>
            <section className="bg-white border border-slate-200 rounded-2xl p-6 shadow-xs mb-6">
              <div className="flex items-center gap-2.5 mb-2">
                <div className="w-8 h-8 rounded-xl bg-red-100 text-[#d70018] flex items-center justify-center font-bold">
                  <Sparkles className="w-4 h-4" />
                </div>
                <div>
                  <h2 className="text-base font-black text-slate-900">Trợ lý Phân tích Yêu cầu Tự nhiên</h2>
                  <p className="text-xs text-slate-500">Mô tả tự do bằng tiếng Việt, AI sẽ bóc tách ngân sách, cấu hình, màn hình, cổng kết nối và tự động chọn hồ sơ tối ưu.</p>
                </div>
              </div>

              <form onSubmit={(e) => { e.preventDefault(); handleNaturalSearch(); }} className="mt-4">
                <div className="flex flex-col sm:flex-row gap-2">
                  <input 
                    id="nl-search-input" 
                    value={nlQuery} 
                    onChange={(e) => setNlQuery(e.target.value)} 
                    placeholder="Ví dụ: Tài chính 25 triệu, laptop code RAM 16GB có cổng LAN" 
                    className="flex-1 px-4 py-3 rounded-xl border border-slate-300 text-sm focus:outline-none focus:ring-2 focus:ring-red-300" 
                  />
                  <button 
                    type="submit"
                    className="bg-[#d70018] hover:bg-[#b80014] text-white px-6 py-3 rounded-xl text-sm font-bold flex items-center justify-center gap-2 cursor-pointer shadow-xs"
                  >
                    <Sparkles className="w-4 h-4" />
                    <span>Phân tích yêu cầu</span>
                  </button>
                </div>

                <div className="flex flex-wrap items-center gap-2 mt-3.5">
                  <span className="text-[11px] font-bold text-slate-400">Gợi ý mẫu:</span>
                  {[
                    'Tài chính 25tr cấu hình ngon', 
                    'Sinh viên kinh tế dưới 15 củ', 
                    'Laptop gaming RTX tầm 28 triệu', 
                    'Ultrabook mỏng nhẹ tầm 20tr',
                    'Dân IT cần RAM 32GB có cổng LAN'
                  ].map(example => (
                    <button 
                      key={example} 
                      type="button" 
                      onClick={() => handleNaturalSearch(example)} 
                      className="text-xs border border-slate-200 bg-slate-50/50 hover:bg-red-50 rounded-full px-3 py-1.5 text-slate-600 hover:border-red-300 hover:text-[#d70018] transition cursor-pointer"
                    >
                      {example}
                    </button>
                  ))}
                </div>

                {nlError && (
                  <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-xl text-xs text-red-700">
                    {nlError}
                  </div>
                )}

                {nlResult && (
                  <div className="mt-4 rounded-xl bg-slate-50 border border-slate-200 p-4 text-xs">
                    <div className="flex items-center justify-between gap-3 mb-2.5">
                      <div className="font-bold text-slate-900 flex items-center gap-1.5">
                        <Check className="w-4 h-4 text-emerald-600" />
                        <span>Kết quả bóc tách thông số:</span>
                      </div>
                      <span className="text-[10px] text-slate-500 bg-white px-2 py-0.5 rounded border border-slate-200">
                        Parser v{nlResult.parser_version}
                      </span>
                    </div>

                    <div className="flex flex-wrap gap-2">
                      {nlResult.entities.map((entity, index) => (
                        <span 
                          key={`${entity.type}-${index}`} 
                          title={`Nguồn: ${entity.source_keyword}; vị trí ${entity.start}-${entity.end}`} 
                          className="bg-white border border-slate-200 px-2.5 py-1.5 rounded-lg shadow-2xs inline-flex items-center gap-1"
                        >
                          <b className="text-slate-700">{entity.label}:</b> 
                          <span className="text-[#d70018] font-semibold">{String(entity.value)}</span>
                          <button 
                            type="button" 
                            onClick={() => removeParsedEntity(entity)} 
                            className="ml-1 text-slate-400 hover:text-red-700 cursor-pointer font-bold" 
                            aria-label={`Bỏ ${entity.label}`}
                          >
                            ×
                          </button>
                        </span>
                      ))}
                    </div>

                    {nlResult.warnings?.map((warning, index) => (
                      <p key={index} className={`mt-2 ${warning.level === 'unsupported' ? 'text-slate-600' : 'text-amber-800'}`}>
                        ⚠️ Lưu ý: {warning.message}
                      </p>
                    ))}

                    <div className="mt-4 pt-3 border-t border-slate-200 flex flex-wrap items-center gap-3">
                      <button 
                        type="button" 
                        onClick={applyNaturalRequirement} 
                        className="bg-[#d70018] hover:bg-[#b80014] text-white px-5 py-2.5 rounded-xl font-bold cursor-pointer shadow-xs flex items-center gap-2"
                      >
                        <Check className="w-4 h-4" />
                        <span>Áp dụng yêu cầu & Đánh giá ngay</span>
                      </button>
                      {!nlResult.preset_key && (
                        <span className="text-amber-800 text-[11px]">
                          💡 Hệ thống giữ nguyên hồ sơ hiện tại hoặc bạn có thể chọn hồ sơ ở Tab 1.
                        </span>
                      )}
                    </div>
                  </div>
                )}
              </form>
            </section>

            {/* Kết quả sau khi NLP nhận diện */}
            <section className="mb-8">
              <div className="flex items-center justify-between mb-3">
                <h2 className="text-base font-black text-slate-900 flex items-center gap-2">
                  <span>Kết quả gợi ý phù hợp với yêu cầu</span>
                  <span className="text-xs bg-red-100 text-[#d70018] font-bold px-2.5 py-0.5 rounded-full">
                    {displayedRankings.length} máy
                  </span>
                </h2>
                <div className="text-xs text-slate-400">
                  Hồ sơ: <b className="text-slate-700">{appliedCategory?.name}</b> · Trần: <b className="text-slate-700">{formatVnd(appliedMaxBudget)}</b>
                </div>
              </div>

              {displayedRankings.length === 0 ? (
                renderEmptyState()
              ) : (
                <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
                  {displayedRankings.map(item => renderProductCard(item, true))}
                </div>
              )}
            </section>
          </div>
        )}

        {/* ═══════════════════════════════════════════════════════════════ */}
        {/* TAB 3: BỘ LỌC CHUYÊN SÂU & TRỌNG SỐ AHP */}
        {/* ═══════════════════════════════════════════════════════════════ */}
        {mainTab === 'filters' && (
          <div>
            <section className="bg-white border border-slate-200 rounded-2xl p-5 shadow-xs mb-6">
              <div className="flex items-center justify-between mb-3 pb-2 border-b border-slate-100">
                <div className="text-xs font-bold text-slate-700 flex items-center gap-2">
                  <Filter className="w-3.5 h-3.5 text-[#d70018]" />
                  <span>Bộ lọc chi tiết phần cứng:</span>
                </div>
                <div className="text-xs text-[#d70018] font-bold">
                  Ngân sách tối đa: {formatVnd(maxBudget)}
                </div>
              </div>

              <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3 mb-4">
                {/* Budget Slider */}
                <div className="col-span-2 bg-slate-50 p-2.5 rounded-xl border border-slate-200">
                  <div className="flex justify-between text-xs text-slate-600 mb-1 font-medium">
                    <span className="flex items-center gap-1">
                      <span>Trần ngân sách:</span>
                      <span className="text-[10px] text-slate-400 font-normal">(≤ mức này)</span>
                    </span>
                    <span className="font-bold text-[#d70018]">{formatVnd(maxBudget)}</span>
                  </div>
                  {minBudget > 0 && <div className="flex items-center justify-between text-[10px] text-slate-500 mb-1"><span>Từ {formatVnd(minBudget)}</span><button type="button" onClick={() => setMinBudget(0)} className="text-[#d70018] hover:underline">Bỏ mức tối thiểu</button></div>}
                  <input
                    type="range" min="0" max="50000000" step="1000000"
                    value={maxBudget}
                    onChange={(e) => setMaxBudget(e.target.value)}
                    className="w-full accent-[#d70018] cursor-pointer"
                  />
                  <div className="flex justify-between text-[10px] text-slate-400 mt-0.5">
                    <span>0đ</span><span>25 triệu</span><span>50 triệu</span>
                  </div>
                </div>

                {/* Hãng */}
                <div>
                  <label className="text-[11px] font-semibold text-slate-500 block mb-1">Hãng sản xuất</label>
                  <select value={brand} onChange={(e) => setBrand(e.target.value)}
                    className="w-full bg-slate-50 border border-slate-200 rounded-lg py-1.5 px-2.5 text-xs font-medium focus:outline-none focus:border-[#d70018]">
                    {['Tất cả', 'ASUS', 'MSI', 'Lenovo', 'Dell', 'HP', 'Acer', 'Apple'].map(b => (
                      <option key={b} value={b}>{b}</option>
                    ))}
                  </select>
                </div>

                {/* CPU */}
                <div>
                  <label className="text-[11px] font-semibold text-slate-500 block mb-1">Dòng CPU</label>
                  <select value={cpuFamily} onChange={(e) => setCpuFamily(e.target.value)}
                    className="w-full bg-slate-50 border border-slate-200 rounded-lg py-1.5 px-2.5 text-xs font-medium focus:outline-none focus:border-[#d70018]">
                    {['Tất cả', 'Core i5', 'Core i7', 'Ultra', 'Ryzen', 'Snapdragon', 'Apple'].map(c => (
                      <option key={c} value={c}>{c}</option>
                    ))}
                  </select>
                </div>

                {/* RAM */}
                <div>
                  <label className="text-[11px] font-semibold text-slate-500 block mb-1">RAM tối thiểu</label>
                  <select value={ramGb} onChange={(e) => setRamGb(e.target.value)}
                    className="w-full bg-slate-50 border border-slate-200 rounded-lg py-1.5 px-2.5 text-xs font-medium focus:outline-none focus:border-[#d70018]">
                    <option value="">Tất cả</option>
                    <option value="8">8 GB</option>
                    <option value="16">16 GB</option>
                    <option value="32">32 GB</option>
                  </select>
                </div>

                {/* Ổ cứng */}
                <div>
                  <label className="text-[11px] font-semibold text-slate-500 block mb-1">SSD tối thiểu</label>
                  <select value={storageGb} onChange={(e) => setStorageGb(e.target.value)}
                    className="w-full bg-slate-50 border border-slate-200 rounded-lg py-1.5 px-2.5 text-xs font-medium focus:outline-none focus:border-[#d70018]">
                    <option value="">Tất cả</option>
                    <option value="256">256 GB</option>
                    <option value="512">512 GB</option>
                    <option value="1024">1 TB (1024GB)</option>
                  </select>
                </div>

                {/* Màn hình */}
                <div>
                  <label className="text-[11px] font-semibold text-slate-500 block mb-1">Kích thước màn</label>
                  <select value={screenSize} onChange={(e) => setScreenSize(e.target.value)}
                    className="w-full bg-slate-50 border border-slate-200 rounded-lg py-1.5 px-2.5 text-xs font-medium focus:outline-none focus:border-[#d70018]">
                    <option value="Tất cả">Tất cả kích thước</option>
                    <option value="Dưới 14 inch">13 - 14 inch (Gọn nhẹ)</option>
                    <option value="15.6 inch">15.6 inch (Tiêu chuẩn)</option>
                    <option value="16 inch">16 inch (Màn lớn)</option>
                  </select>
                </div>

                {/* Tấm nền */}
                <div>
                  <label className="text-[11px] font-semibold text-slate-500 block mb-1">Công nghệ màn hình</label>
                  <select value={panelType} onChange={(e) => setPanelType(e.target.value)}
                    className="w-full bg-slate-50 border border-slate-200 rounded-lg py-1.5 px-2.5 text-xs font-medium focus:outline-none focus:border-[#d70018]">
                    <option value="Tất cả">Tất cả tấm nền</option>
                    <option value="OLED">Màn OLED</option>
                    <option value="IPS">Màn IPS</option>
                  </select>
                </div>

                {/* Tần số quét */}
                <div>
                  <label className="text-[11px] font-semibold text-slate-500 block mb-1">Tần số quét</label>
                  <select value={refreshRate} onChange={(e) => setRefreshRate(e.target.value)}
                    className="w-full bg-slate-50 border border-slate-200 rounded-lg py-1.5 px-2.5 text-xs font-medium focus:outline-none focus:border-[#d70018]">
                    <option value="Tất cả">Tất cả Hz</option>
                    <option value="60">Từ 60Hz</option>
                    <option value="120">Từ 120Hz</option>
                    <option value="144">Từ 144Hz (Chuẩn Game)</option>
                  </select>
                </div>

                {/* Hệ điều hành */}
                <div>
                  <label className="text-[11px] font-semibold text-slate-500 block mb-1">Hệ điều hành</label>
                  <select value={osName} onChange={(e) => setOsName(e.target.value)}
                    className="w-full bg-slate-50 border border-slate-200 rounded-lg py-1.5 px-2.5 text-xs font-medium focus:outline-none focus:border-[#d70018]">
                    <option value="Tất cả">Tất cả OS</option>
                    <option value="Windows">Windows</option>
                    <option value="macOS">macOS</option>
                  </select>
                </div>
              </div>

              {/* Tiêu chí phụ & Tiện ích (Secondary Utility Filters) */}
              <div className="mt-3 pt-3 border-t border-slate-100">
                <div className="text-[11px] font-bold text-slate-500 uppercase tracking-wider mb-2 flex items-center gap-1.5">
                  <span>🔌 Tiện ích & Cổng kết nối bổ sung</span>
                  <span className="text-[10px] font-normal text-slate-400">· Lọc nhanh theo nhu cầu thực tế</span>
                </div>

                <div className="flex flex-wrap items-center gap-3">
                  {/* Độ sáng màn hình */}
                  <div className="flex items-center gap-1.5 bg-slate-50 border border-slate-200 rounded-lg px-2.5 py-1 text-xs">
                    <span className="text-slate-500 text-[11px] font-medium">Độ sáng:</span>
                    <select 
                      value={minBrightness} 
                      onChange={(e) => setMinBrightness(e.target.value)}
                      className="bg-transparent text-xs font-semibold text-slate-800 focus:outline-none cursor-pointer"
                    >
                      <option value="Tất cả">Tất cả nits</option>
                      <option value="300">Từ 300 nits</option>
                      <option value="400">Từ 400 nits</option>
                    </select>
                  </div>

                  {/* Checkbox Cổng mạng LAN */}
                  <label className="flex items-center gap-1.5 bg-slate-50 border border-slate-200 rounded-lg px-2.5 py-1 text-xs cursor-pointer hover:bg-slate-100 transition">
                    <input 
                      type="checkbox" 
                      checked={requireRj45} 
                      onChange={(e) => setRequireRj45(e.target.checked)}
                      className="accent-[#d70018] cursor-pointer"
                    />
                    <span className="font-semibold text-slate-700">Cổng LAN RJ45</span>
                  </label>

                  {/* Checkbox Sạc Type-C */}
                  <label className="flex items-center gap-1.5 bg-slate-50 border border-slate-200 rounded-lg px-2.5 py-1 text-xs cursor-pointer hover:bg-slate-100 transition">
                    <input 
                      type="checkbox" 
                      checked={requireTypeCCharge} 
                      onChange={(e) => setRequireTypeCCharge(e.target.checked)}
                      className="accent-[#d70018] cursor-pointer"
                    />
                    <span className="font-semibold text-slate-700">Sạc qua USB-C</span>
                  </label>

                  {/* Checkbox Nâng cấp RAM */}
                  <label className="flex items-center gap-1.5 bg-slate-50 border border-slate-200 rounded-lg px-2.5 py-1 text-xs cursor-pointer hover:bg-slate-100 transition">
                    <input 
                      type="checkbox" 
                      checked={requireRamUpgrade} 
                      onChange={(e) => setRequireRamUpgrade(e.target.checked)}
                      className="accent-[#d70018] cursor-pointer"
                    />
                    <span className="font-semibold text-slate-700">Có khe nâng RAM</span>
                  </label>

                  {/* Checkbox Thunderbolt / USB4 */}
                  <label className="flex items-center gap-1.5 bg-slate-50 border border-slate-200 rounded-lg px-2.5 py-1 text-xs cursor-pointer hover:bg-slate-100 transition">
                    <input 
                      type="checkbox" 
                      checked={requireThunderbolt} 
                      onChange={(e) => setRequireThunderbolt(e.target.checked)}
                      className="accent-[#d70018] cursor-pointer"
                    />
                    <span className="font-semibold text-slate-700">Thunderbolt / USB4</span>
                  </label>

                  {/* Checkbox Strict Benchmark (D05) */}
                  <label className={`flex items-center gap-1.5 border rounded-lg px-2.5 py-1 text-xs cursor-pointer transition ${
                    strictBenchmark 
                      ? 'bg-amber-50 border-amber-300 text-amber-900 font-bold shadow-xs' 
                      : 'bg-slate-50 border-slate-200 text-slate-700 hover:bg-slate-100'
                  }`}>
                    <input 
                      type="checkbox" 
                      checked={strictBenchmark} 
                      onChange={(e) => setStrictBenchmark(e.target.checked)}
                      className="accent-amber-600 cursor-pointer"
                    />
                    <span>🛡️ Chuẩn D05: Chỉ nhận Benchmark chính thức (Loại ⚠️)</span>
                  </label>
                </div>
              </div>

              <div className="flex items-center justify-between pt-3">
                <div className="text-xs text-slate-500">
                  {hasPendingEvaluation ? <span className="text-amber-700">Bạn đã đổi bộ lọc. Bấm <b>Duyệt</b> để cập nhật xếp hạng.</span> : <>Kết quả đang áp dụng: <b className="text-slate-900">{appliedCategory?.name}</b>, trần <b className="text-slate-900">{formatVnd(appliedMaxBudget)}</b> · <b className="text-slate-900 font-bold">{displayedRankings.length}</b> máy</>}
                </div>
                <button 
                  onClick={handleApplyFilter}
                  disabled={loading}
                  className="bg-[#d70018] hover:bg-[#b80014] disabled:bg-red-300 text-white text-xs font-bold px-6 py-2 rounded-xl transition flex items-center gap-1.5 cursor-pointer shadow-xs"
                >
                  <Filter className="w-3.5 h-3.5" />
                  <span>{loading ? 'Đang đánh giá...' : 'Duyệt & Áp dụng bộ lọc'}</span>
                </button>
              </div>
            </section>

            {/* ── 2.5. TÙY BIẾN TRỌNG SỐ (DIRECT RATING OVERRIDE) ── */}
            <section className="bg-white border border-slate-200 rounded-2xl shadow-xs mb-6 overflow-hidden">
              <button 
                onClick={() => setShowWeightEditor(!showWeightEditor)}
                className="w-full p-4 flex items-center justify-between cursor-pointer hover:bg-slate-50/50 transition"
              >
                <div className="flex items-center gap-2">
                  <SlidersHorizontal className="w-4 h-4 text-indigo-600" />
                  <span className="text-sm font-bold text-slate-900">⚖️ Tùy biến trọng số tiêu chí (Direct Rating)</span>
                  {isCustomWeightsActive && (
                    <span className="text-[10px] font-bold bg-indigo-100 text-indigo-700 px-2 py-0.5 rounded-full border border-indigo-200">
                      Direct Rating đang bật
                    </span>
                  )}
                </div>
                <span className="text-xs text-slate-400">{showWeightEditor ? '▲ Thu gọn' : '▼ Mở rộng'}</span>
              </button>

              {showWeightEditor && activeCriteria.length > 0 && (
                <div className="px-5 pb-5 border-t border-slate-100 pt-4">
                  <p className="text-[11px] text-amber-700 bg-amber-50 border border-amber-200 px-3 py-2 rounded-lg mb-4">
                    ⚠️ Lưu ý: Khi tùy biến, bạn đang dùng <b>Direct Rating</b> (gán trọng số trực tiếp), không phải AHP. 
                    Trọng số AHP mặc định được tính từ ma trận so sánh cặp đã xác thực CR &lt; 0.10.
                  </p>

                  <div className="space-y-3">
                    {activeCriteria.map(([cname, cdir, defaultW], idx) => {
                      const currentVal = customWeightValues ? customWeightValues[idx] : Math.round(defaultW * 100);
                      const sum = customWeightValues ? customWeightValues.reduce((a, b) => a + b, 0) : 100;
                      const normalizedPct = sum > 0 ? Math.round((currentVal / sum) * 100) : 0;

                      return (
                        <div key={cname} className="flex items-center gap-3">
                          <div className="w-6 text-center text-sm">{CRITERIA_ICONS[cname] || '📊'}</div>
                          <div className="w-48 text-xs font-semibold text-slate-700 truncate">
                            {CRITERIA_LABELS[cname] || cname}
                            <span className="text-slate-400 ml-1">({cdir})</span>
                          </div>
                          <input
                            type="range" min="0" max="100" step="1"
                            value={currentVal}
                            onChange={(e) => {
                              const newVals = customWeightValues 
                                ? [...customWeightValues] 
                                : activeCriteria.map(([, , w]) => Math.round(w * 100));
                              newVals[idx] = Number(e.target.value);
                              setCustomWeightValues(newVals);
                            }}
                            className="flex-1 accent-indigo-600 cursor-pointer"
                          />
                          <div className="w-14 text-right text-xs font-bold text-indigo-700">
                            {normalizedPct}%
                          </div>
                        </div>
                      );
                    })}
                  </div>

                  <div className="flex gap-3 mt-4 pt-3 border-t border-slate-100">
                    <button
                      onClick={handleApplyCustomWeights}
                      className="bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-bold px-5 py-2 rounded-xl transition cursor-pointer"
                    >
                      Áp dụng trọng số tùy chỉnh
                    </button>
                    <button
                      onClick={handleResetWeights}
                      className="bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-bold px-5 py-2 rounded-xl transition cursor-pointer"
                    >
                      🔄 Về trọng số AHP mặc định
                    </button>
                  </div>
                </div>
              )}
            </section>

            {/* Lưới sản phẩm */}
            <section className="mb-8">
              <div className="flex items-center justify-between mb-3">
                <h2 className="text-base font-black text-slate-900 flex items-center gap-2">
                  <span>Danh sách laptop sau khi lọc chuyên sâu</span>
                  <span className="text-xs bg-red-100 text-[#d70018] font-bold px-2.5 py-0.5 rounded-full">
                    {displayedRankings.length} máy
                  </span>
                </h2>
                <div className="text-xs text-slate-400">
                  Sắp xếp theo: <b className="text-slate-700">Độ phù hợp nhu cầu giảm dần (TOPSIS)</b>
                </div>
              </div>

              {displayedRankings.length === 0 ? (
                renderEmptyState()
              ) : (
                <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
                  {displayedRankings.map(item => renderProductCard(item, true))}
                </div>
              )}
            </section>
          </div>
        )}

        {/* ═══════════════════════════════════════════════════════════════ */}
        {/* TAB 4: DANH SÁCH YÊU THÍCH (WISHLIST) */}
        {/* ═══════════════════════════════════════════════════════════════ */}
        {mainTab === 'favorites' && (
          <div>
            <section className="bg-white border border-slate-200 rounded-2xl p-5 shadow-xs mb-6">
              <div className="flex flex-wrap items-center justify-between gap-3">
                <div className="flex items-center gap-2.5">
                  <div className="w-8 h-8 rounded-xl bg-rose-100 text-rose-600 flex items-center justify-center font-bold">
                    <Heart className="w-4 h-4 fill-rose-600" />
                  </div>
                  <div>
                    <h2 className="text-base font-black text-slate-900">Danh sách Laptop Yêu thích</h2>
                    <p className="text-xs text-slate-500">Các máy bạn đã bấm lưu ❤️ được lưu trữ trên trình duyệt để tiện đối chiếu và so sánh.</p>
                  </div>
                </div>

                {favorites.length > 0 && (
                  <div className="flex items-center gap-2">
                    {compareIds.length >= 2 && (
                      <button
                        type="button"
                        onClick={() => setShowCompareModal(true)}
                        className="bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-bold px-4 py-2 rounded-xl transition cursor-pointer flex items-center gap-1.5 shadow-xs"
                      >
                        <GitCompare className="w-3.5 h-3.5" />
                        <span>So sánh {compareIds.length} máy đã chọn</span>
                      </button>
                    )}
                    <button
                      type="button"
                      onClick={clearFavorites}
                      className="bg-slate-100 hover:bg-rose-50 hover:text-rose-700 text-slate-600 text-xs font-bold px-3.5 py-2 rounded-xl transition cursor-pointer flex items-center gap-1.5 border border-slate-200 hover:border-rose-200"
                    >
                      <Trash2 className="w-3.5 h-3.5" />
                      <span>Xóa toàn bộ ({favorites.length})</span>
                    </button>
                  </div>
                )}
              </div>
            </section>

            {favorites.length === 0 ? (
              <div className="bg-white border border-slate-200 rounded-2xl p-12 text-center text-slate-500 shadow-xs max-w-2xl mx-auto my-6">
                <div className="w-16 h-16 rounded-full bg-rose-50 border border-rose-100 flex items-center justify-center mx-auto mb-4">
                  <Heart className="w-8 h-8 text-rose-400 fill-rose-100" />
                </div>
                <h3 className="font-black text-slate-900 text-base mb-1">
                  Chưa có laptop nào trong danh sách yêu thích
                </h3>
                <p className="text-xs text-slate-500 leading-relaxed max-w-md mx-auto mb-5">
                  Bấm vào biểu tượng trái tim <Heart className="w-3.5 h-3.5 inline text-rose-500 fill-rose-500" /> ở góc phải các thẻ máy để lưu lại các dòng laptop bạn đang phân vân.
                </p>
                <button
                  type="button"
                  onClick={() => setMainTab('recommend')}
                  className="bg-[#d70018] hover:bg-[#b80014] text-white text-xs font-bold px-6 py-2.5 rounded-xl transition cursor-pointer shadow-xs inline-flex items-center gap-2"
                >
                  <span>Khám phá danh sách đề xuất ngay</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </button>
              </div>
            ) : (
              <section className="mb-8">
                <div className="flex items-center justify-between mb-3">
                  <span className="text-xs font-bold text-slate-700">
                    Hiển thị <b>{favorites.length}</b> laptop đã lưu
                  </span>
                  <span className="text-xs text-slate-400">
                    Tích chọn "So sánh" trên các máy để xem bảng đối chiếu chi tiết
                  </span>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
                  {favorites.map(item => renderProductCard(item, false))}
                </div>
              </section>
            )}
          </div>
        )}

        {/* ── FLOATING COMPARE BAR ── */}
        {compareIds.length >= 2 && (
          <div className="fixed bottom-6 left-1/2 -translate-x-1/2 z-50 bg-indigo-600 text-white px-6 py-3 rounded-2xl shadow-2xl flex items-center gap-4">
            <GitCompare className="w-5 h-5" />
            <span className="font-bold text-sm">Đã chọn {compareIds.length} máy</span>
            <button
              onClick={() => setShowCompareModal(true)}
              className="bg-white text-indigo-700 font-bold text-xs px-4 py-2 rounded-xl hover:bg-indigo-50 transition cursor-pointer"
            >
              So sánh ngay
            </button>
            <button
              onClick={() => setCompareIds([])}
              className="text-white/70 hover:text-white text-xs cursor-pointer"
            >
              Xóa
            </button>
          </div>
        )}

        {/* ── COMPARISON MODAL ── */}
        {showCompareModal && compareLaptops.length >= 2 && (
          <div className="fixed inset-0 z-50 bg-black/50 flex items-start justify-center pt-10 overflow-y-auto">
            <div className="bg-white rounded-2xl shadow-2xl max-w-5xl w-full mx-4 mb-10">
              <div className="flex items-center justify-between p-5 border-b border-slate-200">
                <div><h3 className="text-lg font-black text-slate-900 flex items-center gap-2"><GitCompare className="w-5 h-5 text-indigo-600" />So sánh {compareLaptops.length} laptop</h3><p className="mt-1 text-xs text-slate-500">Dấu ★ đánh dấu giá trị tốt hơn trong từng hàng; thứ tự ưu tiên theo hồ sơ {appliedCategory?.name}.</p></div>
                <button onClick={() => setShowCompareModal(false)} className="p-2 hover:bg-slate-100 rounded-xl cursor-pointer">
                  <X className="w-5 h-5 text-slate-500" />
                </button>
              </div>

              <div className="overflow-x-auto">
                <table className="w-full text-xs">
                  <thead>
                    <tr className="border-b border-slate-200 bg-slate-50">
                      <th className="p-3 text-left text-slate-500 font-bold w-36">Tiêu chí</th>
                      {compareLaptops.map(l => (
                        <th key={l.source_product_id} className="p-3 text-center">
                          <img 
                            src={l.image_url} alt="" 
                            className="w-20 h-16 object-contain mx-auto mb-1"
                            onError={(e) => { e.target.src = '/images/laptop_fallback.png'; }}
                          />
                          <div className="font-bold text-slate-900 line-clamp-2">{l.product_name_raw}</div>
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100">
                    {/* Giá */}
                    <CompareRow label="Giá bán" values={compareLaptops.map(l => Number(l.sale_price_vnd))} format={formatVnd} best="min" />
                    {/* TOPSIS */}
                    <CompareRow label="Điểm TOPSIS" values={compareLaptops.map(l => Math.round((l.topsis_score || 0) * 100))} format={v => `${v}%`} best="max" />
                    <CompareRow label={cpuCriterionLabel} values={compareLaptops.map(l => Number(l[cpuCriterion] || 0))} format={v => v ? v.toLocaleString() : 'Chưa có dữ liệu'} best="max" />
                    <tr className="hover:bg-slate-50"><td className="p-3 font-semibold text-slate-600">GPU 3DMark</td>{compareLaptops.map(l => <td key={l.source_product_id} className="p-3 text-center text-slate-800 font-medium">{l.gpu_type === 'discrete' && Number(l.gpu_benchmark_time_spy) > 0 ? Number(l.gpu_benchmark_time_spy).toLocaleString() : 'GPU tích hợp / không có điểm rời'}</td>)}</tr>
                    {/* RAM */}
                    <CompareRow label="RAM" values={compareLaptops.map(l => Number(l.ram_gb || 0))} format={v => `${v} GB`} best="max" />
                    {/* SSD */}
                    <CompareRow label="Ổ cứng" values={compareLaptops.map(l => Number(l.storage_total_gb || 0))} format={v => `${v} GB`} best="max" />
                    {/* Màn hình */}
                    <tr className="hover:bg-slate-50">
                      <td className="p-3 font-semibold text-slate-600">Màn hình</td>
                      {compareLaptops.map(l => (
                        <td key={l.source_product_id} className="p-3 text-center text-slate-800 font-medium">
                          {[l.screen_size_inch ? `${l.screen_size_inch}"` : 'Chưa có kích thước', l.panel_type || 'Chưa có tấm nền', l.refresh_rate_hz ? `${l.refresh_rate_hz}Hz` : 'Chưa có tần số quét'].join(' · ')}
                        </td>
                      ))}
                    </tr>
                    {/* Cân nặng */}
                    <CompareRow label="Cân nặng" values={compareLaptops.map(l => Number(l.weight_kg || 99))} format={v => `${v} kg`} best="min" />
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}

        </>}

        {currentPage !== 'recommend' && <>
        <section className="bg-white border border-slate-200 rounded-2xl shadow-xs mb-6 overflow-hidden">
          <div className="p-4 border-b border-slate-200">
            <h2 className="text-sm font-black text-slate-900">{currentPage === 'methodology' ? 'Phương pháp xếp hạng có thể kiểm tra' : 'Phân tích kết quả và kiểm định'}</h2>
            <p className="mt-1 text-xs text-slate-500">{currentPage === 'methodology' ? 'Ma trận AHP, tỷ số nhất quán CR và quy trình TOPSIS của hồ sơ nhu cầu đang chọn.' : 'Giải thích phương án đứng đầu, kiểm định độ nhạy và đối chiếu giá ước tính OOF.'}</p>
          </div>
          <div className="flex overflow-x-auto border-b border-slate-200">
            {(currentPage === 'methodology' ? [['math', 'Cơ sở toán học']] : [['advice', 'Phân tích và lý do'], ['sensitivity', 'Kiểm định độ nhạy'], ['ml', 'Thẩm định giá hồi quy']]).map(([key, label]) => <button key={key} onClick={() => setAnalysisTab(key)} className={`shrink-0 px-4 py-3 text-xs font-bold border-b-2 ${analysisTab === key ? 'border-[#d70018] text-[#d70018] bg-red-50/30' : 'border-transparent text-slate-500 hover:text-slate-900'}`}>{label}</button>)}
          </div>
        </section>

        {/* ── PHÂN TÍCH ĐỘ NHẠY (§8.4) ── */}
        {analysisTab === 'sensitivity' && sensitivityData && (
          <section className="bg-white border border-slate-200 rounded-2xl p-6 shadow-xs mb-6">
            <div className="flex items-center justify-between mb-4 pb-3 border-b border-slate-100">
              <div className="flex items-center gap-2">
                <div className="w-7 h-7 rounded-lg bg-indigo-100 text-indigo-700 flex items-center justify-center font-bold text-sm">
                  <Scale className="w-4 h-4" />
                </div>
                <div>
                  <h3 className="text-sm font-black text-slate-900 flex items-center gap-2">
                    <span>Kiểm tra khi tăng ngân sách</span>
                    <span className="text-[10px] bg-indigo-50 text-indigo-700 border border-indigo-200 font-bold px-2 py-0.5 rounded-full">
                      §8.4 Chuongtrinh.md
                    </span>
                  </h3>
                  <p className="text-[11px] text-slate-500">
                    Đây là mô phỏng sau khi tăng trần ngân sách, không phải các danh sách đề xuất mới.
                  </p>
                </div>
              </div>
              <button 
                onClick={() => setShowSensitivity(!showSensitivity)}
                className="text-xs font-bold text-indigo-600 hover:text-indigo-800 cursor-pointer bg-indigo-50/60 px-3 py-1.5 rounded-xl border border-indigo-100 transition"
              >
                {showSensitivity ? 'Thu gọn' : 'Xem chi tiết'}
              </button>
            </div>

            {showSensitivity && (
              <div className="space-y-5">
                {/* Kịch bản Ngân sách */}
                <div>
                  <div className="flex items-center justify-between mb-2.5">
                    <span className="text-xs font-bold text-slate-800 flex items-center gap-1.5">
                      <TrendingUp className="w-3.5 h-3.5 text-emerald-600" />
                      <span>Nếu tăng trần ngân sách</span>
                    </span>
                    <span className="text-[11px] text-slate-500">
                      Hiện tại: <b className="text-slate-800">{formatVnd(sensitivityData.budget_sensitivity?.baseline_budget_vnd || appliedMaxBudget)}</b> · Top 1: <b className="text-slate-800">{sensitivityData.budget_sensitivity?.baseline_top1?.product_name_raw?.slice(0, 30) || 'Chưa có'}...</b>
                    </span>
                  </div>

                  <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
                    {(sensitivityData.budget_sensitivity?.scenarios || []).map((sc, idx) => (
                      <div 
                        key={idx}
                        className={`p-3.5 rounded-xl border transition ${
                          sc.is_usurped 
                            ? 'bg-amber-50/50 border-amber-300 ring-1 ring-amber-200' 
                            : 'bg-slate-50/70 border-slate-200'
                        }`}
                      >
                        <div className="flex items-center justify-between mb-1.5">
                          <span className="text-[11px] font-black text-slate-900 bg-white px-2 py-0.5 rounded border border-slate-200">
                            Trần mới: {formatVnd(sc.new_budget_vnd)}
                          </span>
                          {sc.is_usurped ? (
                            <span className="text-[10px] font-black text-amber-700 bg-amber-100 px-2 py-0.5 rounded-full flex items-center gap-1">
                              <Zap className="w-2.5 h-2.5" /> Thay đổi phương án đứng đầu
                            </span>
                          ) : (
                            <span className="text-[10px] font-bold text-emerald-700 bg-emerald-100/70 px-2 py-0.5 rounded-full">
                              ✓ Top 1 không đổi
                            </span>
                          )}
                        </div>
                        <div className="text-[11px] font-bold text-slate-800 line-clamp-1 mb-1">
                          {sc.new_top1 ? sc.new_top1.product_name_raw : 'Không có máy'}
                        </div>
                        <div className="text-[10px] text-slate-500 leading-tight">{sc.is_usurped ? sc.upgrade_benefit : `Tăng thêm ${formatVnd(sc.delta_vnd)} chưa tạo phương án phù hợp hơn.`}</div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Độ bền vững Trọng số */}
                <div className="bg-slate-50/70 border border-slate-200 rounded-xl p-4">
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-2 pb-2 border-b border-slate-200/60">
                    <div className="flex items-center gap-2">
                      <span className="text-xs font-bold text-slate-800">
                        Kiểm tra Top 1 khi thay đổi trọng số ±10%, ±20%:
                      </span>
                      <span className={`text-[10px] font-black px-2 py-0.5 rounded-full ${
                        sensitivityData.weight_sensitivity?.is_highly_robust 
                          ? 'bg-emerald-100 text-emerald-800 border border-emerald-300' 
                          : 'bg-amber-100 text-amber-800 border border-amber-300'
                      }`}>
                        Top 1 giữ nguyên: {sensitivityData.weight_sensitivity?.stability_rate_percent}%
                      </span>
                    </div>
                  </div>

                  <p className="text-[11px] text-slate-600 leading-relaxed mb-3">{sensitivityData.weight_sensitivity?.academic_summary} Chỉ số này nói về việc Top 1 có đổi hay không; không khẳng định máy đó “tốt 100%”.</p>

                  <div className="flex flex-wrap gap-2">
                    {(sensitivityData.weight_sensitivity?.criteria_evaluations || []).map((ce, cIdx) => (
                      <div 
                        key={cIdx}
                        className={`text-[10px] px-2.5 py-1 rounded-lg border flex items-center gap-1.5 ${
                          ce.is_robust 
                            ? 'bg-white border-slate-200 text-slate-700' 
                            : 'bg-amber-50 border-amber-200 text-amber-800'
                        }`}
                      >
                        <span className="font-semibold">{CRITERIA_LABELS[ce.criterion] || ce.criterion}</span>
                        <span className="text-slate-400">({Math.round(ce.base_weight * 100)}%)</span>
                        <span className={`font-bold ${ce.is_robust ? 'text-emerald-600' : 'text-amber-600'}`}>
                          {ce.is_robust ? '✓ Bền vững' : '⚠ Nhạy cảm'}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}
          </section>
        )}

        {/* ── PHÂN TÍCH VÀ LÝ DO — DỮ LIỆU TỪ API ── */}
        {analysisTab === 'advice' && <section className="bg-white border border-slate-200 rounded-2xl p-6 shadow-xs mb-6">
          <div className="flex items-center gap-2 mb-3">
            <div className="w-7 h-7 rounded-lg bg-red-100 text-[#d70018] flex items-center justify-center font-bold text-sm">
              💡
            </div>
            <h3 className="text-sm font-black text-slate-900">
              Cơ sở đánh giá & Giải thích kết quả
            </h3>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs leading-relaxed">
            {/* Cột 1: Tiêu chí — DYNAMIC */}
            <div className="bg-slate-50 p-4 rounded-xl border border-slate-200">
              <div className="font-bold text-slate-900 mb-2 flex items-center gap-1.5">
                <span className="text-[#d70018]">①</span>
                <span>Tiêu chí & Trọng số ({isCustomWeightsActive ? 'Direct Rating' : 'AHP'}):</span>
              </div>
              <div className="space-y-1.5">
                {activeCriteria.map(([cname, , weight]) => (
                  <div key={cname} className="flex items-center justify-between">
                    <span className="text-slate-600 flex items-center gap-1">
                      <span>{CRITERIA_ICONS[cname] || '📊'}</span>
                      <span>{CRITERIA_LABELS[cname] || cname}</span>
                    </span>
                    <div className="flex items-center gap-1.5">
                      <div className="w-20 h-1.5 bg-slate-200 rounded-full overflow-hidden">
                        <div className="h-full bg-[#d70018] rounded-full" style={{ width: `${Math.round(weight * 100)}%` }} />
                      </div>
                      <span className="font-bold text-slate-800 w-8 text-right">{Math.round(weight * 100)}%</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Cột 2: Vì sao Top 1 — DYNAMIC & DỄ HIỂU */}
            <div className="bg-slate-50 p-4 rounded-xl border border-slate-200">
              <div className="font-bold text-slate-900 mb-2 flex items-center justify-between">
                <span className="flex items-center gap-1.5">
                  <span className="text-emerald-600">②</span>
                  <span>Vì sao chiếc máy này đứng đầu?</span>
                </span>
                {top1Laptop && (
                  <span className="text-[11px] font-black bg-emerald-100 text-emerald-800 px-2 py-0.5 rounded-full border border-emerald-300">
                    Phù hợp {Math.round((top1Laptop.topsis_score || 0) * 100)}%
                  </span>
                )}
              </div>
              {top1Laptop ? (
                <div className="space-y-2 text-slate-600">
                  <p>
                    Chiếc <b>{top1Laptop.product_name_raw}</b> đạt điểm tổng hợp cao nhất trong nhóm <b>{CATEGORIES.find(c => c.key === presetKey)?.name}</b> nhờ sự cân bằng tối ưu giữa các tiêu chí:
                  </p>
                  <div className="bg-white p-2.5 rounded-lg border border-slate-200 text-[11px] space-y-1.5">
                    {top1Laptop.explanation?.top_advantage && (
                      <div className="flex items-start gap-1.5">
                        <span className="text-emerald-600 font-bold shrink-0">✓ Điểm mạnh:</span>
                        <span><b>{formatExplanationText(top1Laptop.explanation.top_advantage, 'advantage')}</b></span>
                      </div>
                    )}
                    {top1Laptop.explanation?.top_penalty && (
                      <div className="flex items-start gap-1.5">
                        <span className="text-amber-600 font-bold shrink-0">⚠ Đánh đổi:</span>
                        <span>{formatExplanationText(top1Laptop.explanation.top_penalty, 'penalty')}</span>
                      </div>
                    )}
                  </div>
                  <p className="text-[11px] text-slate-500 italic">
                    💡 Điểm TOPSIS đo khoảng cách đến phương án hoàn hảo. Máy đứng đầu không nhất thiết phải mạnh nhất hay đắt nhất, mà là phương án cân bằng hiệu quả nhất so với trọng số bạn chọn.
                  </p>
                </div>
              ) : (
                <p className="text-slate-600">Chưa có máy thỏa mãn bộ lọc ngân sách này.</p>
              )}
            </div>

            {/* Cột 3: Máy bị loại — DYNAMIC */}
            <div className="bg-slate-50 p-4 rounded-xl border border-slate-200">
              <div className="font-bold text-slate-900 mb-1.5 flex items-center gap-1.5">
                <span className="text-amber-600">③</span>
                <span>Máy bị loại trừ ({excluded.length} máy)</span>
              </div>
              {excluded.length > 0 ? (
                <ul className="text-slate-600 space-y-1 list-disc pl-4">
                  {excluded.slice(0, 3).map((ex, idx) => (
                    <li key={idx}>
                      <b>{ex.product_name_raw?.slice(0, 30)}</b>: {ex.reason}
                    </li>
                  ))}
                  {excluded.length > 3 && (
                    <li className="text-slate-400">...và {excluded.length - 3} máy khác</li>
                  )}
                </ul>
              ) : (
                <p className="text-slate-600">Tất cả máy trong tầm giá đều đủ điều kiện tham gia xếp hạng.</p>
              )}
            </div>
          </div>

          {/* Academic Details Toggle */}
          <div className="mt-4 pt-3 border-t border-slate-100 flex justify-end">
            <button
              onClick={() => setShowAcademicDetails(!showAcademicDetails)}
              className="text-[11px] text-slate-400 hover:text-slate-700 flex items-center gap-1 cursor-pointer transition"
            >
              <span>{showAcademicDetails ? '▲ Ẩn chi tiết AHP' : '▼ Dành cho hội đồng: Xem trọng số AHP & D14'}</span>
            </button>
          </div>

          {showAcademicDetails && (
            <div className="mt-3 p-3 bg-slate-50 rounded-xl border border-slate-200 text-[11px] text-slate-600 space-y-2">
              <div className="font-bold text-slate-800">Trọng số AHP chuẩn hóa cho nhu cầu hiện tại:</div>
              <div className="flex flex-wrap gap-2">
                {activeCriteria.map(([cname, , weight]) => (
                  <span key={cname} className="bg-white px-2 py-1 rounded border border-slate-200">
                    <b>{CRITERIA_LABELS[cname] || cname}</b>: {Math.round(weight * 1000) / 10}%
                  </span>
                ))}
              </div>
              {excluded.length > 0 && (
                <div className="pt-2 border-t border-slate-200">
                  <div className="font-bold text-slate-800 mb-1">Máy bị loại trừ do không thỏa yêu cầu tối thiểu (D14):</div>
                  <ul className="list-disc pl-4 space-y-0.5">
                    {excluded.map((ex, idx) => (
                      <li key={idx}><b>{ex.product_name_raw?.slice(0, 35)}</b>: {ex.reason}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}
        </section>}

        {analysisTab === 'ml' && <section className="bg-white border border-slate-200 rounded-2xl p-6 shadow-xs mb-6">
          <h3 className="text-sm font-black text-slate-900">Thẩm định giá thị trường bằng hồi quy</h3>
          <p className="text-xs text-slate-600 mt-1">Gradient Boosting ước tính giá tham chiếu độc lập. Kết quả không tham gia tính điểm TOPSIS theo D10.</p>
          {mlValuation?.good_deals_summary ? <div className="mt-4 overflow-x-auto"><table className="w-full text-xs"><thead className="bg-slate-50"><tr><th className="p-2 text-left">Sản phẩm</th><th className="p-2 text-right">Giá quan sát</th><th className="p-2 text-right">Giá dự báo OOF</th><th className="p-2 text-right">Value Gap</th></tr></thead><tbody>{mlValuation.good_deals_summary.top_good_deals.map(deal => <tr key={deal.source_product_id} className="border-t border-slate-100"><td className="p-2 font-semibold text-slate-800">{deal.product_name}</td><td className="p-2 text-right">{formatVnd(deal.observed_price_vnd)}</td><td className="p-2 text-right">{formatVnd(deal.predicted_price_vnd)}</td><td className="p-2 text-right font-bold text-emerald-700">+{deal.value_gap_percent}%</td></tr>)}</tbody></table><p className="mt-3 text-[11px] text-slate-500">Một máy được gắn cờ khi giá quan sát thấp hơn cận dưới của khoảng dự báo 95%.</p></div> : <p className="mt-3 text-xs text-slate-500">Không có dữ liệu thẩm định ML.</p>}
        </section>}

        {analysisTab === 'math' && <section className="bg-white border border-slate-200 rounded-2xl p-6 shadow-xs mb-6">
          <h3 className="text-sm font-black text-slate-900">Cơ sở toán học AHP và TOPSIS</h3>
          <p className="text-xs text-slate-600 mt-1">Tỷ số nhất quán Saaty: <b>{ahpCr === null ? 'chưa có' : ahpCr.toFixed(4)}</b> {ahpCr !== null && ahpCr < 0.1 ? '(đạt CR < 0.10)' : ''}.</p>
          {pairwiseMatrix.length > 0 && <div className="mt-4 overflow-x-auto"><div className="text-xs font-bold text-slate-800 mb-2">Ma trận so sánh cặp AHP của hồ sơ đang chọn</div><table className="text-xs border-collapse"><tbody>{pairwiseMatrix.map((row, i) => <tr key={i}>{row.map((value, j) => <td key={j} className="border border-slate-200 px-2 py-1.5 text-center">{Number(value).toFixed(2)}</td>)}</tr>)}</tbody></table></div>}
          <p className="mt-4 text-xs text-slate-600">TOPSIS chuẩn hóa từng tiêu chí theo vector, nhân trọng số AHP, rồi đo khoảng cách Euclid đến nghiệm lý tưởng A+ và A-.</p>
          {droppedCriteria.length > 0 && <p className="mt-2 text-xs text-amber-800">Tiêu chí loại theo D14: {droppedCriteria.map(item => item.criterion).join(', ')}.</p>}
        </section>}
        </>}

      </main>
      )}

        </div>
      </div>
    </div>
  );
}

// ═══════════════════════════════════════════════════
// COMPARISON TABLE ROW — highlight winner
// ═══════════════════════════════════════════════════
function CompareRow({ label, values, format, best }) {
  const bestVal = best === 'min' 
    ? Math.min(...values.filter(v => v > 0)) 
    : Math.max(...values);
  
  return (
    <tr className="hover:bg-slate-50">
      <td className="p-3 font-semibold text-slate-600">{label}</td>
      {values.map((v, idx) => {
        const isWinner = v > 0 && v === bestVal;
        return (
          <td key={idx} className={`p-3 text-center font-medium ${isWinner ? 'text-emerald-700 bg-emerald-50 font-bold' : 'text-slate-800'}`}>
            {format(v)}
            {isWinner && <span className="ml-1 text-[9px] text-emerald-600">★</span>}
          </td>
        );
      })}
    </tr>
  );
}
