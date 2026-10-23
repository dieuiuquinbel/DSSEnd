import React, { useState } from 'react';
import { Sparkles, Laptop } from 'lucide-react';
import SidebarFilter from '../components/layout/SidebarFilter';
import DecisionCard from '../components/dss/DecisionCard';
import ExplainabilityDrawer from '../components/dss/ExplainabilityDrawer';
import SmartFilterLoosener from '../components/dss/SmartFilterLoosener';
import SkeletonCard from '../components/common/SkeletonCard';
import { ConsolidatedDataNotice } from '../components/common/TooltipNotice';
import NlQueryParserBox from '../components/ai/NlQueryParserBox';
import WeightEditorModal from '../components/dss/WeightEditorModal';
import CompareModal from '../components/dss/CompareModal';
import FloatingCompareBar from '../components/layout/FloatingCompareBar';
import LaptopDetailModal from '../components/dss/LaptopDetailModal';
import { CATEGORIES } from '../utils/formatters';

export default function RecommendPage({
  // Filter states
  presetKey,
  onSelectPreset,
  minBudget,
  maxBudget,
  onChangeBudget,
  brand,
  onChangeBrand,
  cpuFamily,
  onChangeCpuFamily,
  ramGb,
  onChangeRamGb,
  storageGb,
  onChangeStorageGb,
  screenSize,
  onChangeScreenSize,
  panelType,
  onChangePanelType,
  refreshRate,
  onChangeRefreshRate,
  osName,
  onChangeOsName,
  requireRj45,
  onChangeRequireRj45,
  requireRamUpgrade,
  onChangeRequireRamUpgrade,
  requireTypeCCharge,
  onChangeRequireTypeCCharge,
  requireThunderbolt,
  onChangeRequireThunderbolt,
  strictBenchmark,
  onChangeStrictBenchmark,
  mlAssistedRanking,
  onChangeMlAssistedRanking,
  onApplyFilters,
  onResetFilters,
  loading = false,
  hasPendingEvaluation = false,
  evaluationError = '',

  // Evaluation results
  rankings = [],
  displayedRankings = [],
  activeCriteria = [],
  filterDataQuality = [],
  droppedCriteria = [],
  rankingMode = 'topsis_only',
  mlRankingNote = '',
  isCustomWeightsActive = false,
  customWeightValues = null,
  onSaveCustomWeights,
  onResetCustomWeights,

  // NLP AI states
  nlQuery,
  onChangeNlQuery,
  onNlSearch,
  nlResult,
  onRemoveNlEntity,
  onApplyNlFilters,
  nlError,

  // Comparison states
  compareIds = [],
  onToggleCompare,
  onClearCompare,

  // Favorites states
  isFavorite,
  onToggleFavorite,

  // Selected laptop for details
  selectedLaptop,
  onSelectLaptop,
  onClearSelectedLaptop,
}) {
  const [showNlParser, setShowNlParser] = useState(false);
  const [showWeightEditor, setShowWeightEditor] = useState(false);
  const [showCompareModal, setShowCompareModal] = useState(false);
  const [explainLaptop, setExplainLaptop] = useState(null);

  const compareLaptops = rankings.filter(r => compareIds.includes(r.source_product_id));
  const currentCategory = CATEGORIES.find(c => c.key === presetKey);

  // Smart loosening handlers
  const handleLoosenBudget = (newBudget) => {
    onChangeBudget(newBudget);
    onApplyFilters({ max_budget_vnd: newBudget });
  };

  const handleResetHardwareFilter = (filterKey) => {
    if (filterKey === 'rj45') onChangeRequireRj45(false);
    if (filterKey === 'thunderbolt') onChangeRequireThunderbolt(false);
    if (filterKey === 'ram_upgrade') onChangeRequireRamUpgrade(false);
    if (filterKey === 'type_c') onChangeRequireTypeCCharge(false);
    if (filterKey === 'brand') onChangeBrand('Tất cả');
    onApplyFilters({});
  };

  return (
    <div className="flex flex-col lg:flex-row gap-6 items-start">
      
      {/* ═══════════════════════════════════════════════════════════════ */}
      {/* LEFT COLUMN: FIXED / STICKY FILTER SIDEBAR (320px) */}
      {/* ═══════════════════════════════════════════════════════════════ */}
      <SidebarFilter
        presetKey={presetKey}
        onSelectPreset={onSelectPreset}
        minBudget={minBudget}
        maxBudget={maxBudget}
        onChangeBudget={onChangeBudget}
        brand={brand}
        onChangeBrand={onChangeBrand}
        cpuFamily={cpuFamily}
        onChangeCpuFamily={onChangeCpuFamily}
        ramGb={ramGb}
        onChangeRamGb={onChangeRamGb}
        storageGb={storageGb}
        onChangeStorageGb={onChangeStorageGb}
        screenSize={screenSize}
        onChangeScreenSize={onChangeScreenSize}
        panelType={panelType}
        onChangePanelType={onChangePanelType}
        refreshRate={refreshRate}
        onChangeRefreshRate={onChangeRefreshRate}
        osName={osName}
        onChangeOsName={onChangeOsName}
        requireRj45={requireRj45}
        onChangeRequireRj45={onChangeRequireRj45}
        requireRamUpgrade={requireRamUpgrade}
        onChangeRequireRamUpgrade={onChangeRequireRamUpgrade}
        requireTypeCCharge={requireTypeCCharge}
        onChangeRequireTypeCCharge={onChangeRequireTypeCCharge}
        requireThunderbolt={requireThunderbolt}
        onChangeRequireThunderbolt={onChangeRequireThunderbolt}
        strictBenchmark={strictBenchmark}
        onChangeStrictBenchmark={onChangeStrictBenchmark}
        mlAssistedRanking={mlAssistedRanking}
        onChangeMlAssistedRanking={onChangeMlAssistedRanking}
        onOpenWeightEditor={() => setShowWeightEditor(true)}
        onApplyFilters={onApplyFilters}
        onResetFilters={onResetFilters}
        loading={loading}
        hasPendingEvaluation={hasPendingEvaluation}
        isCustomWeightsActive={isCustomWeightsActive}
      />

      {/* ═══════════════════════════════════════════════════════════════ */}
      {/* RIGHT COLUMN: MAIN CONTENT & RESULTS GRID */}
      {/* ═══════════════════════════════════════════════════════════════ */}
      <main className="flex-1 min-w-0 w-full space-y-4">
        
        {/* Top Control Bar: Quick AI Assistant toggle & Results Summary */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 bg-white border border-slate-200 rounded-2xl p-4 shadow-2xs">
          <div>
            <div className="flex items-center gap-2">
              <h2 className="text-sm font-black text-slate-900">
                {rankingMode === 'ml_assisted' ? 'Đề xuất tối ưu (TOPSIS + ML OOF)' : 'Xếp hạng theo độ phù hợp (TOPSIS thuần)'}
              </h2>
              <span className="text-xs font-bold px-2.5 py-0.5 rounded-full bg-indigo-50 text-indigo-700 border border-indigo-200">
                {displayedRankings.length} máy
              </span>
              {isCustomWeightsActive && (
                <span className="text-[11px] font-bold px-2 py-0.5 rounded-full bg-emerald-50 text-emerald-700 border border-emerald-200">
                  Trọng số tùy biến
                </span>
              )}
            </div>
            <p className="text-[11px] text-slate-500 mt-0.5">
              Hồ sơ: <b className="text-slate-800">{currentCategory?.name}</b> · {currentCategory?.sub}
            </p>
          </div>

          <button
            type="button"
            onClick={() => setShowNlParser(!showNlParser)}
            className={`px-3.5 py-2 rounded-xl text-xs font-bold transition flex items-center gap-1.5 cursor-pointer shrink-0 border ${
              showNlParser
                ? 'bg-indigo-600 text-white border-indigo-600 shadow-2xs'
                : 'bg-indigo-50/60 hover:bg-indigo-100/70 text-indigo-700 border-indigo-200'
            }`}
          >
            <Sparkles className="w-4 h-4" />
            <span>{showNlParser ? 'Thu gọn trợ lý AI' : 'Trợ lý AI bóc tách yêu cầu'}</span>
          </button>
        </div>

        {/* AI NLP Search Box (Collapsible) */}
        {showNlParser && (
          <NlQueryParserBox
            nlQuery={nlQuery}
            onChangeNlQuery={onChangeNlQuery}
            onSearch={onNlSearch}
            nlResult={nlResult}
            onRemoveEntity={onRemoveNlEntity}
            onApplyFilters={onApplyNlFilters}
            nlError={nlError}
            loading={loading}
          />
        )}

        {/* Evaluation Error Alert */}
        {evaluationError && (
          <div className="rounded-2xl border border-rose-200 bg-rose-50 p-4 text-xs text-rose-800 shadow-2xs flex flex-col sm:flex-row sm:items-center justify-between gap-3">
            <div>
              <b className="text-rose-950 font-bold block mb-0.5">Chưa thể tải dữ liệu đánh giá:</b>
              <span>{evaluationError}</span>
              <div className="mt-1 text-rose-700 font-mono text-[11px]">
                Backend: python -X utf8 -m uvicorn src.api:app --host 127.0.0.1 --port 8000
              </div>
            </div>
            <button
              type="button"
              onClick={() => onApplyFilters()}
              disabled={loading}
              className="shrink-0 px-4 py-2 bg-rose-600 hover:bg-rose-700 disabled:bg-rose-300 text-white rounded-xl font-bold cursor-pointer transition shadow-xs flex items-center justify-center gap-1.5 self-start sm:self-auto"
            >
              <span>{loading ? 'Đang kết nối lại...' : 'Thử kết nối lại ngay'}</span>
            </button>
          </div>
        )}

        {/* Consolidated Data Quality Alert Notice (Replaces the 4 banners!) */}
        <ConsolidatedDataNotice
          filterDataQuality={filterDataQuality}
          droppedCriteria={droppedCriteria}
        />

        {/* ML Ranking Note (if enabled) */}
        {rankingMode === 'ml_assisted' && mlRankingNote && (
          <div className="text-xs text-indigo-900 bg-indigo-50/70 border border-indigo-200 rounded-xl px-3.5 py-2 flex items-center gap-2">
            <span className="text-base">🤖</span>
            <span>{mlRankingNote}</span>
          </div>
        )}

        {/* Smart Filter Loosener (Triggered when result count <= 2) */}
        {!loading && (
          <SmartFilterLoosener
            resultCount={displayedRankings.length}
            maxBudget={maxBudget}
            presetKey={presetKey}
            requireRj45={requireRj45}
            requireThunderbolt={requireThunderbolt}
            requireRamUpgrade={requireRamUpgrade}
            requireTypeCCharge={requireTypeCCharge}
            brand={brand}
            onLoosenBudget={handleLoosenBudget}
            onResetHardwareFilter={handleResetHardwareFilter}
          />
        )}

        {/* Product Grid / Skeleton Loading / Empty State */}
        {loading ? (
          <SkeletonCard count={6} />
        ) : displayedRankings.length === 0 ? (
          <div className="rounded-3xl border border-slate-200 bg-white p-12 text-center shadow-2xs">
            <Laptop className="w-12 h-12 text-slate-300 mx-auto mb-3" />
            <h3 className="text-sm font-bold text-slate-800">
              Không tìm thấy laptop phù hợp với điều kiện hiện tại
            </h3>
            <p className="text-xs text-slate-500 mt-1 max-w-md mx-auto">
              Các ràng buộc về hãng máy, trần ngân sách hoặc tiêu chuẩn phần cứng đang quá chặt chẽ.
            </p>
            <div className="mt-4 flex justify-center gap-2">
              <button
                type="button"
                onClick={onResetFilters}
                className="px-4 py-2 rounded-xl text-xs font-bold bg-indigo-600 hover:bg-indigo-700 text-white cursor-pointer transition shadow-xs"
              >
                Đặt lại bộ lọc về mặc định
              </button>
            </div>
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {displayedRankings.map((laptop) => (
              <DecisionCard
                key={laptop.source_product_id}
                item={laptop}
                rankingMode={rankingMode}
                isInCompare={compareIds.includes(laptop.source_product_id)}
                isFav={isFavorite(laptop.source_product_id)}
                onToggleFavorite={onToggleFavorite}
                onToggleCompare={onToggleCompare}
                onOpenExplainDrawer={(l) => setExplainLaptop(l)}
                onOpenDetail={(l) => onSelectLaptop(l)}
              />
            ))}
          </div>
        )}

      </main>

      {/* ═══════════════════════════════════════════════════════════════ */}
      {/* FLOATING COMPARE BAR & MODALS */}
      {/* ═══════════════════════════════════════════════════════════════ */}
      <FloatingCompareBar
        compareLaptops={compareLaptops}
        onRemoveItem={onToggleCompare}
        onClearAll={onClearCompare}
        onOpenModal={() => setShowCompareModal(true)}
      />

      {showCompareModal && (
        <CompareModal
          laptops={compareLaptops}
          onClose={() => setShowCompareModal(false)}
          onRemoveItem={onToggleCompare}
          onOpenDetail={(l) => {
            setShowCompareModal(false);
            onSelectLaptop(l);
          }}
        />
      )}

      {explainLaptop && (
        <ExplainabilityDrawer
          laptop={explainLaptop}
          activeCriteria={activeCriteria}
          rankingMode={rankingMode}
          onClose={() => setExplainLaptop(null)}
          onOpenDetail={(l) => {
            setExplainLaptop(null);
            onSelectLaptop(l);
          }}
        />
      )}

      {selectedLaptop && (
        <LaptopDetailModal
          laptop={selectedLaptop}
          onClose={onClearSelectedLaptop}
          isFav={isFavorite(selectedLaptop.source_product_id)}
          isInCompare={compareIds.includes(selectedLaptop.source_product_id)}
          onToggleFavorite={onToggleFavorite}
          onToggleCompare={onToggleCompare}
        />
      )}

      {showWeightEditor && (
        <WeightEditorModal
          activeCriteria={activeCriteria}
          customWeightValues={customWeightValues}
          onSaveWeights={onSaveCustomWeights}
          onResetWeights={onResetCustomWeights}
          onClose={() => setShowWeightEditor(false)}
        />
      )}

    </div>
  );
}
