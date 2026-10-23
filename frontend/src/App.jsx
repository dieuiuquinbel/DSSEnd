import React, { useState, useEffect, useRef } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';

// Layout & Components
import Header from './components/layout/Header';
import RecommendPage from './pages/RecommendPage';
import AnalysisPage from './pages/AnalysisPage';
import MethodologyPage from './pages/MethodologyPage';
import FavoritesModal from './components/dss/FavoritesModal';
import Toast from './components/common/Toast';
import { apiFetch } from './services/api';

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

  // Navigation State
  const [selectedLaptop, setSelectedLaptop] = useState(null);
  const [showFavoritesModal, setShowFavoritesModal] = useState(false);
  const [toast, setToast] = useState(null);

  // Dark Mode State
  const [isDarkMode, setIsDarkMode] = useState(() => {
    try {
      return localStorage.getItem('laptop_dss_theme') === 'dark';
    } catch {
      return false;
    }
  });

  useEffect(() => {
    try {
      if (isDarkMode) {
        document.documentElement.classList.add('dark');
        localStorage.setItem('laptop_dss_theme', 'dark');
      } else {
        document.documentElement.classList.remove('dark');
        localStorage.setItem('laptop_dss_theme', 'light');
      }
    } catch {}
  }, [isDarkMode]);

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
  const [activeCriteria, setActiveCriteria] = useState([]);
  const [sensitivityData, setSensitivityData] = useState(null);
  const [robustnessData, setRobustnessData] = useState(null);
  const [robustnessLoading, setRobustnessLoading] = useState(false);
  const [robustnessError, setRobustnessError] = useState('');
  const [loading, setLoading] = useState(false);
  const [evaluationError, setEvaluationError] = useState('');

  // AI NLP States
  const [nlQuery, setNlQuery] = useState('');
  const [nlResult, setNlResult] = useState(null);
  const [nlError, setNlError] = useState('');
  const [excludedBrands, setExcludedBrands] = useState([]);

  // AHP & ML States
  const [mlValuation, setMlValuation] = useState(null);
  const [ahpCr, setAhpCr] = useState(null);
  const [pairwiseMatrix, setPairwiseMatrix] = useState([]);
  const [droppedCriteria, setDroppedCriteria] = useState([]);
  const [filterDataQuality, setFilterDataQuality] = useState([]);
  const [mlAssistedRanking, setMlAssistedRanking] = useState(false);
  const [rankingMode, setRankingMode] = useState('topsis_only');
  const [mlRankingNote, setMlRankingNote] = useState('');

  // Manual Valuation Simulator
  const [manualValuation, setManualValuation] = useState({
    brand: 'Asus',
    cpu_benchmark_multi: '12000',
    cpu_benchmark_single: '2500',
    gpu_benchmark_time_spy: '6000',
    gpu_vram_gb: '6',
    ram_gb: '16',
    storage_total_gb: '512',
    refresh_rate_hz: '144',
    brightness_nits: '300',
    battery_capacity_wh: '60',
    weight_kg: '2.2',
    observed_price_vnd: '20000000',
    is_discrete_gpu: true,
    is_oled_panel: false,
    is_macos: false,
  });
  const [manualValuationResult, setManualValuationResult] = useState(null);
  const [manualValuationLoading, setManualValuationLoading] = useState(false);
  const [manualValuationError, setManualValuationError] = useState('');

  const skipNextPresetFetch = useRef(false);
  const lastEvaluationPayload = useRef(null);

  // Comparison State
  const [compareIds, setCompareIds] = useState([]);

  // Weight Customization (Direct Rating Override)
  const [customWeightValues, setCustomWeightValues] = useState(null);
  const [isCustomWeightsActive, setIsCustomWeightsActive] = useState(false);

  // Favorites (Wishlist) with LocalStorage
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
        console.error('Không thể lưu favorites:', e);
      }
      
      // Trigger user toast feedback
      const name = laptop.product_name_raw?.slice(0, 32) || 'Laptop';
      setToast({
        message: exists ? `Đã bỏ "${name}..." khỏi yêu thích` : `Đã lưu "${name}..." vào yêu thích`,
        actionLabel: exists ? null : 'Xem danh sách',
        onAction: exists ? null : () => setShowFavoritesModal(true),
      });

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

  // Comparison Toggle
  const toggleCompare = (productId) => {
    setCompareIds(prev => {
      if (prev.includes(productId)) {
        return prev.filter(id => id !== productId);
      }
      if (prev.length >= 4) {
        return prev;
      }
      return [...prev, productId];
    });
  };

  const clearCompare = () => setCompareIds([]);

  // Fetch Evaluation API
  const fetchEvaluation = async (overridePreset = null, weights = null, filterOverrides = {}) => {
    setLoading(true);
    setEvaluationError('');
    try {
      const activePreset = typeof overridePreset === 'string' ? overridePreset : presetKey;

      // Sanitize filterOverrides to prevent React SyntheticEvent / DOM elements from leaking into JSON payload
      const isPlainObject = (obj) => obj && typeof obj === 'object' && obj.constructor === Object && !obj.nativeEvent && !obj.target && !('preventDefault' in obj);
      const safeOverrides = {};
      if (isPlainObject(filterOverrides)) {
        for (const [k, v] of Object.entries(filterOverrides)) {
          if (v && typeof v === 'object' && ('nodeType' in v || 'nativeEvent' in v || 'target' in v)) continue;
          safeOverrides[k] = v;
        }
      }

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
        ml_assisted_ranking: mlAssistedRanking,
        ml_ranking_weight: 0.15,
        custom_weights: weights || null,
      };
      Object.assign(payload, safeOverrides, { preset_key: activePreset });
      lastEvaluationPayload.current = { ...payload };
      setRobustnessData(null);
      setRobustnessError('');

      const res = await apiFetch('/api/evaluate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Không thể đánh giá danh sách laptop.');
      setRankings(data.rankings || []);
      setActiveCriteria(data.active_criteria || []);
      setAhpCr(data.ahp_cr ?? null);
      setPairwiseMatrix(data.pairwise_matrix || []);
      setDroppedCriteria(data.dropped_criteria || []);
      setFilterDataQuality(data.filter_data_quality || []);
      setRankingMode(data.ranking_mode || 'topsis_only');
      setMlRankingNote(data.ml_ranking_note || '');
      setAppliedMaxBudget(Number(payload.max_budget_vnd));
      setAppliedPresetKey(activePreset);

      // Sensitivity analysis
      const { ml_assisted_ranking: _ml, ml_ranking_weight: _mlw, ...topsisPayload } = payload;
      apiFetch('/api/sensitivity', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ...topsisPayload, preset_key: activePreset })
      })
      .then(r => r.json())
      .then(sData => setSensitivityData(sData))
      .catch(err => console.error('Lỗi khi tải độ nhạy:', err));

      if (selectedLaptop) {
        const updated = (data.rankings || []).find(r => r.source_product_id === selectedLaptop.source_product_id);
        if (updated) setSelectedLaptop(updated);
      }
    } catch (err) {
      console.error('Lỗi khi tải kết quả:', err);
      setRankings([]);
      setActiveCriteria([]);
      setSensitivityData(null);
      setRobustnessData(null);
      setFilterDataQuality([]);
      setEvaluationError(
        err?.message || 'Không kết nối được Backend tại http://127.0.0.1:8000.'
      );
    } finally {
      setLoading(false);
    }
  };

  // Silent health check & auto-reconnect when evaluation error is active
  useEffect(() => {
    if (!evaluationError) return;
    const interval = setInterval(() => {
      apiFetch('/api/laptops')
        .then(res => {
          if (res.ok) {
            clearInterval(interval);
            fetchEvaluation();
          }
        })
        .catch(() => {});
    }, 2500);
    return () => clearInterval(interval);
  }, [evaluationError]);

  // Monte Carlo Dirichlet simulation
  const runMonteCarloRobustness = async () => {
    if (!lastEvaluationPayload.current) return;
    setRobustnessLoading(true);
    setRobustnessError('');
    try {
      const { ml_assisted_ranking: _ml, ml_ranking_weight: _mlw, ...topsisPayload } = lastEvaluationPayload.current;
      const response = await apiFetch('/api/robustness', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ...topsisPayload, simulations: 300, seed: 42 }),
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || 'Không thể chạy mô phỏng trọng số.');
      setRobustnessData(data);
    } catch (err) {
      console.error('Lỗi khi chạy Monte Carlo:', err);
      setRobustnessError(err?.message || 'Không kết nối được Backend để chạy mô phỏng.');
    } finally {
      setRobustnessLoading(false);
    }
  };

  // Fetch ML Valuation overview on load
  useEffect(() => {
    apiFetch('/api/ml-valuation')
      .then(res => res.ok ? res.json() : null)
      .then(data => { if (data) setMlValuation(data); })
      .catch(() => {});
  }, []);

  // Weight customization initialization
  useEffect(() => {
    if (activeCriteria.length > 0 && !customWeightValues) {
      const weights = activeCriteria.map(([, , w]) => Math.round(w * 100));
      setCustomWeightValues(weights);
    }
  }, [activeCriteria]);

  // Preset switch
  useEffect(() => {
    setCustomWeightValues(null);
    setIsCustomWeightsActive(false);
    if (skipNextPresetFetch.current) {
      skipNextPresetFetch.current = false;
      return;
    }
    fetchEvaluation();
  }, [presetKey]);

  const handleCategoryClick = (catKey) => {
    skipNextPresetFetch.current = true;
    setPresetKey(catKey);
    fetchEvaluation(catKey);
  };

  // NLP AI Search
  const handleNaturalSearch = async (query = nlQuery) => {
    setNlError('');
    try {
      const res = await apiFetch('/api/parse-requirement', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt: query })
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
    const keyByType = {
      min_budget: 'min_budget_vnd', max_budget: 'max_budget_vnd', brand: 'brand',
      excluded_brand: 'excluded_brands', min_ram: 'min_ram_gb', min_storage: 'min_storage_gb',
      min_refresh_rate: 'min_refresh_rate_hz', screen_size: 'screen_size', panel_type: 'panel_type',
      rj45: 'require_rj45_lan', ram_upgrade: 'require_ram_upgradeable',
      type_c_charging: 'require_type_c_charging', thunderbolt: 'require_thunderbolt',
      os: 'required_os', cpu: 'cpu_family', strict_benchmark: 'strict_benchmark'
    };
    const key = keyByType[entity.type];
    setNlResult(prev => {
      if (!prev || !key) return prev;
      const filters = { ...prev.filters };
      if (key === 'excluded_brands') {
        filters[key] = (filters[key] || []).filter(v => v !== entity.value);
      } else {
        delete filters[key];
      }
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
    if (f.min_refresh_rate_hz) setRefreshRate(String(f.min_refresh_rate_hz));
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
    if (nlResult.preset_key && nlResult.preset_key !== presetKey) {
      setPresetKey(nlResult.preset_key);
    }
    fetchEvaluation(nlResult.preset_key || presetKey, null, f);
  };

  // Manual Valuation Simulator Handler
  const handleManualValuation = async () => {
    setManualValuationLoading(true);
    setManualValuationError('');
    setManualValuationResult(null);
    const numericKeys = [
      'cpu_benchmark_multi', 'cpu_benchmark_single', 'gpu_benchmark_time_spy',
      'gpu_vram_gb', 'ram_gb', 'storage_total_gb', 'refresh_rate_hz',
      'brightness_nits', 'battery_capacity_wh', 'weight_kg', 'observed_price_vnd'
    ];
    const payload = { ...manualValuation };
    numericKeys.forEach(key => {
      payload[key] = payload[key] === '' ? null : Number(payload[key]);
    });
    if (!payload.is_discrete_gpu) payload.gpu_vram_gb = null;

    try {
      const response = await apiFetch('/api/predict_price', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || 'Không thể định giá cấu hình này.');
      setManualValuationResult(data);
    } catch (error) {
      setManualValuationError(error instanceof TypeError ? 'Không kết nối được Backend.' : error.message);
    } finally {
      setManualValuationLoading(false);
    }
  };

  // Filter rankings according to search query
  const displayedRankings = rankings.filter(item => {
    if (!searchQuery) return true;
    const q = searchQuery.toLowerCase();
    return (
      (item.product_name_raw || '').toLowerCase().includes(q) ||
      (item.cpu_name_normalized || '').toLowerCase().includes(q) ||
      (item.gpu_name_normalized || '').toLowerCase().includes(q)
    );
  });

  const hasPendingEvaluation = Number(maxBudget) !== appliedMaxBudget || presetKey !== appliedPresetKey;

  const handleApplyFilter = (overrides = {}) => {
    const isPlainObject = (obj) => obj && typeof obj === 'object' && obj.constructor === Object && !obj.nativeEvent && !obj.target && !('preventDefault' in obj);
    const safeOverrides = isPlainObject(overrides) ? overrides : {};
    fetchEvaluation(presetKey, isCustomWeightsActive ? customWeightValues : null, safeOverrides);
  };

  const handleResetFilter = () => {
    setMinBudget(0);
    setMaxBudget(45000000);
    setBrand('Tất cả');
    setCpuFamily('Tất cả');
    setRamGb('');
    setStorageGb('');
    setScreenSize('Tất cả');
    setPanelType('Tất cả');
    setRefreshRate('Tất cả');
    setOsName('Tất cả');
    setMinBrightness('Tất cả');
    setRequireRj45(false);
    setRequireRamUpgrade(false);
    setRequireTypeCCharge(false);
    setRequireThunderbolt(false);
    setStrictBenchmark(false);
    setExcludedBrands([]);
    setSearchQuery('');
    setCustomWeightValues(null);
    setIsCustomWeightsActive(false);
    fetchEvaluation(presetKey, null, {
      min_budget_vnd: 0,
      max_budget_vnd: 45000000,
      brand: null,
      cpu_family: null,
      min_ram_gb: null,
      min_storage_gb: null,
      screen_size: null,
      panel_type: null,
      required_os: null,
      min_refresh_rate_hz: null,
      min_brightness_nits: null,
      require_rj45_lan: null,
      require_ram_upgradeable: null,
      require_type_c_charging: null,
      require_thunderbolt: null,
      strict_benchmark: false,
      excluded_brands: [],
      custom_weights: null,
    });
  };

  const handleSaveCustomWeights = (normalizedWeights) => {
    setCustomWeightValues(normalizedWeights);
    setIsCustomWeightsActive(true);
    fetchEvaluation(presetKey, normalizedWeights);
  };

  const handleResetCustomWeights = () => {
    setCustomWeightValues(null);
    setIsCustomWeightsActive(false);
    fetchEvaluation(presetKey, null);
  };

  return (
    <div className="min-h-screen bg-slate-50/70 text-slate-900 pb-20">
      
      {/* ═══════════════════════════════════════════════════════════════ */}
      {/* GLOBAL HEADER */}
      {/* ═══════════════════════════════════════════════════════════════ */}
      <Header
        searchQuery={searchQuery}
        onChangeSearchQuery={setSearchQuery}
        currentPage={currentPage}
        onNavigate={(page) => {
          setSelectedLaptop(null);
          navigate(`/${page}`);
          window.scrollTo({ top: 0, behavior: 'smooth' });
        }}
        favoritesCount={favorites.length}
        onOpenFavorites={() => setShowFavoritesModal(true)}
        onSelectPrompt={(prompt) => {
          setSearchQuery(prompt);
          if (currentPage !== 'recommend') navigate('/recommend');
        }}
        isDarkMode={isDarkMode}
        onToggleDarkMode={() => setIsDarkMode(!isDarkMode)}
      />

      {/* ═══════════════════════════════════════════════════════════════ */}
      {/* MAIN CONTAINER */}
      {/* ═══════════════════════════════════════════════════════════════ */}
      <div className="max-w-[1440px] mx-auto px-4 lg:px-6 py-6">
        
        {currentPage === 'recommend' || currentPage === 'detail' ? (
          <RecommendPage
            presetKey={presetKey}
            onSelectPreset={handleCategoryClick}
            minBudget={minBudget}
            maxBudget={maxBudget}
            onChangeBudget={setMaxBudget}
            brand={brand}
            onChangeBrand={setBrand}
            cpuFamily={cpuFamily}
            onChangeCpuFamily={setCpuFamily}
            ramGb={ramGb}
            onChangeRamGb={setRamGb}
            storageGb={storageGb}
            onChangeStorageGb={setStorageGb}
            screenSize={screenSize}
            onChangeScreenSize={setScreenSize}
            panelType={panelType}
            onChangePanelType={setPanelType}
            refreshRate={refreshRate}
            onChangeRefreshRate={setRefreshRate}
            osName={osName}
            onChangeOsName={setOsName}
            requireRj45={requireRj45}
            onChangeRequireRj45={setRequireRj45}
            requireRamUpgrade={requireRamUpgrade}
            onChangeRequireRamUpgrade={setRequireRamUpgrade}
            requireTypeCCharge={requireTypeCCharge}
            onChangeRequireTypeCCharge={setRequireTypeCCharge}
            requireThunderbolt={requireThunderbolt}
            onChangeRequireThunderbolt={setRequireThunderbolt}
            strictBenchmark={strictBenchmark}
            onChangeStrictBenchmark={setStrictBenchmark}
            mlAssistedRanking={mlAssistedRanking}
            onChangeMlAssistedRanking={(val) => {
              setMlAssistedRanking(val);
              fetchEvaluation(presetKey, isCustomWeightsActive ? customWeightValues : null, { ml_assisted_ranking: val });
            }}
            onApplyFilters={handleApplyFilter}
            onResetFilters={handleResetFilter}
            loading={loading}
            hasPendingEvaluation={hasPendingEvaluation}
            evaluationError={evaluationError}
            rankings={rankings}
            displayedRankings={displayedRankings}
            activeCriteria={activeCriteria}
            filterDataQuality={filterDataQuality}
            droppedCriteria={droppedCriteria}
            rankingMode={rankingMode}
            mlRankingNote={mlRankingNote}
            isCustomWeightsActive={isCustomWeightsActive}
            customWeightValues={customWeightValues}
            onSaveCustomWeights={handleSaveCustomWeights}
            onResetCustomWeights={handleResetCustomWeights}
            nlQuery={nlQuery}
            onChangeNlQuery={setNlQuery}
            onNlSearch={handleNaturalSearch}
            nlResult={nlResult}
            onRemoveNlEntity={removeParsedEntity}
            onApplyNlFilters={applyNaturalRequirement}
            nlError={nlError}
            compareIds={compareIds}
            onToggleCompare={toggleCompare}
            onClearCompare={clearCompare}
            isFavorite={isFavorite}
            onToggleFavorite={toggleFavorite}
            selectedLaptop={selectedLaptop}
            onSelectLaptop={(l) => {
              setSelectedLaptop(l);
              navigate(`/laptop/${encodeURIComponent(l.source_product_id)}`);
            }}
            onClearSelectedLaptop={() => {
              setSelectedLaptop(null);
              navigate('/recommend');
            }}
          />
        ) : currentPage === 'analysis' ? (
          <AnalysisPage
            sensitivityData={sensitivityData}
            mlValuation={mlValuation}
            robustnessData={robustnessData}
            robustnessLoading={robustnessLoading}
            robustnessError={robustnessError}
            onRunMonteCarlo={runMonteCarloRobustness}
            manualValuation={manualValuation}
            onChangeManualValuation={setManualValuation}
            manualValuationResult={manualValuationResult}
            manualValuationLoading={manualValuationLoading}
            manualValuationError={manualValuationError}
            onRunManualValuation={handleManualValuation}
          />
        ) : (
          <MethodologyPage
            ahpCr={ahpCr}
            pairwiseMatrix={pairwiseMatrix}
            activeCriteria={activeCriteria}
          />
        )}

      </div>

      {/* Favorites Modal */}
      {showFavoritesModal && (
        <FavoritesModal
          favorites={favorites}
          onClose={() => setShowFavoritesModal(false)}
          onRemoveFavorite={toggleFavorite}
          onClearFavorites={clearFavorites}
          onOpenDetail={(l) => {
            setShowFavoritesModal(false);
            setSelectedLaptop(l);
            navigate(`/laptop/${encodeURIComponent(l.source_product_id)}`);
          }}
        />
      )}

      {/* Toast Notification */}
      {toast && (
        <Toast
          message={toast.message}
          actionLabel={toast.actionLabel}
          onAction={toast.onAction}
          onClose={() => setToast(null)}
        />
      )}

    </div>
  );
}
