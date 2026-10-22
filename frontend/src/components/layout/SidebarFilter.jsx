import React from 'react';
import { Filter, SlidersHorizontal, Sparkles, RotateCcw } from 'lucide-react';
import { CATEGORIES, formatVnd } from '../../utils/formatters';
import { FilterInfoTooltip } from '../common/TooltipNotice';

export default function SidebarFilter({
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
  onOpenWeightEditor,
  onApplyFilters,
  onResetFilters,
  loading = false,
  hasPendingEvaluation = false,
  isCustomWeightsActive = false,
}) {
  const quickBudgets = [
    { label: '≤ 15tr', value: 15000000 },
    { label: '≤ 20tr', value: 20000000 },
    { label: '≤ 25tr', value: 25000000 },
    { label: '≤ 35tr', value: 35000000 },
    { label: 'Tất cả', value: 50000000 },
  ];

  return (
    <aside className="w-full lg:w-80 shrink-0">
      <div className="sticky top-20 space-y-4">
        
        {/* Main Filter Box */}
        <div className="rounded-2xl border border-slate-200 bg-white p-4.5 shadow-2xs">
          
          <div className="flex items-center justify-between pb-3 border-b border-slate-100 mb-4">
            <div className="flex items-center gap-2">
              <Filter className="w-4 h-4 text-indigo-600" />
              <h3 className="text-sm font-bold text-slate-900">Bộ Lọc & Hồ Sơ Nhu Cầu</h3>
            </div>
            <button
              type="button"
              onClick={onResetFilters}
              className="text-[11px] font-semibold text-slate-400 hover:text-indigo-600 flex items-center gap-1 cursor-pointer transition"
              title="Đặt lại tất cả bộ lọc về mặc định"
            >
              <RotateCcw className="w-3 h-3" />
              <span>Đặt lại</span>
            </button>
          </div>

          {/* 1. Nhu cầu sử dụng (4 Presets) */}
          <div className="mb-4">
            <label className="text-xs font-bold text-slate-800 block mb-2">
              1. Mục đích & Nhu cầu:
            </label>
            <div className="grid grid-cols-2 gap-2">
              {CATEGORIES.map(cat => {
                const isActive = presetKey === cat.key;
                return (
                  <button
                    key={cat.key}
                    type="button"
                    onClick={() => onSelectPreset(cat.key)}
                    className={`p-2.5 rounded-xl border text-left transition cursor-pointer flex flex-col justify-between ${
                      isActive
                        ? 'border-indigo-600 bg-indigo-50/70 text-indigo-950 ring-2 ring-indigo-200'
                        : 'border-slate-200 hover:border-slate-300 hover:bg-slate-50 text-slate-700 bg-white'
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <span className="text-xl">{cat.icon}</span>
                      {isActive && (
                        <span className="w-2 h-2 rounded-full bg-indigo-600" />
                      )}
                    </div>
                    <div className="mt-1.5">
                      <div className={`text-xs font-bold truncate ${isActive ? 'text-indigo-700' : 'text-slate-900'}`}>
                        {cat.name}
                      </div>
                      <div className="text-[10px] text-slate-400 truncate mt-0.5">
                        {cat.sub}
                      </div>
                    </div>
                  </button>
                );
              })}
            </div>

            {/* AHP Customization link */}
            <div className="mt-2.5 flex items-center justify-between px-2 py-1.5 bg-slate-50 rounded-xl border border-slate-100 text-[11px]">
              <span className="text-slate-500 font-medium">Trọng số AHP:</span>
              <button
                type="button"
                onClick={onOpenWeightEditor}
                className="text-indigo-600 hover:text-indigo-800 font-bold flex items-center gap-1 cursor-pointer"
              >
                <SlidersHorizontal className="w-3 h-3" />
                <span>{isCustomWeightsActive ? 'Đang tùy biến' : 'Chỉnh trọng số'}</span>
              </button>
            </div>
          </div>

          {/* 2. Switch ML-Assisted Ranking */}
          <div className="mb-4 rounded-xl border border-indigo-200/80 bg-indigo-50/50 p-2.5 flex items-center justify-between gap-2">
            <div>
              <div className="text-xs font-bold text-indigo-950 flex items-center gap-1">
                <Sparkles className="w-3.5 h-3.5 text-indigo-600" />
                <span>ML hỗ trợ xếp hạng</span>
              </div>
              <div className="text-[10px] text-indigo-800 mt-0.5">
                85% TOPSIS + 15% Định giá OOF
              </div>
            </div>
            <button
              type="button"
              role="switch"
              aria-checked={mlAssistedRanking}
              onClick={() => onChangeMlAssistedRanking(!mlAssistedRanking)}
              disabled={loading}
              className={`relative inline-flex h-6 w-11 shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none ${
                mlAssistedRanking ? 'bg-indigo-600' : 'bg-slate-300'
              }`}
            >
              <span
                className={`pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow-sm ring-0 transition duration-200 ease-in-out ${
                  mlAssistedRanking ? 'translate-x-5' : 'translate-x-0'
                }`}
              />
            </button>
          </div>

          {/* 3. Ngân sách tối đa */}
          <div className="mb-4">
            <div className="flex items-center justify-between mb-1.5">
              <label className="text-xs font-bold text-slate-800">
                2. Trần ngân sách tối đa:
              </label>
              <span className="text-xs font-black text-indigo-600">
                {formatVnd(maxBudget)}
              </span>
            </div>

            <input
              type="range"
              min="8000000"
              max="50000000"
              step="500000"
              value={maxBudget}
              onChange={(e) => onChangeBudget(Number(e.target.value))}
              className="w-full accent-indigo-600 cursor-pointer h-1.5 bg-slate-200 rounded-lg"
            />

            {/* Quick budget chips */}
            <div className="grid grid-cols-5 gap-1 mt-2">
              {quickBudgets.map(qb => (
                <button
                  key={qb.label}
                  type="button"
                  onClick={() => onChangeBudget(qb.value)}
                  className={`py-1 text-[10px] font-bold rounded-lg border text-center transition cursor-pointer ${
                    Number(maxBudget) === qb.value
                      ? 'bg-indigo-600 text-white border-indigo-600'
                      : 'bg-slate-50 text-slate-600 border-slate-200 hover:bg-slate-100'
                  }`}
                >
                  {qb.label}
                </button>
              ))}
            </div>
          </div>

          {/* 4. Hãng sản xuất & CPU Family */}
          <div className="grid grid-cols-2 gap-2 mb-4">
            <div>
              <label className="text-[11px] font-bold text-slate-700 block mb-1">
                Hãng máy:
              </label>
              <select
                value={brand}
                onChange={(e) => onChangeBrand(e.target.value)}
                className="w-full bg-slate-50 border border-slate-200 rounded-xl py-1.5 px-2 text-xs font-semibold focus:outline-none focus:border-indigo-600 text-slate-800"
              >
                {['Tất cả', 'ASUS', 'MSI', 'Lenovo', 'Dell', 'HP', 'Acer', 'Apple'].map(b => (
                  <option key={b} value={b}>{b}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="text-[11px] font-bold text-slate-700 block mb-1">
                Dòng CPU:
              </label>
              <select
                value={cpuFamily}
                onChange={(e) => onChangeCpuFamily(e.target.value)}
                className="w-full bg-slate-50 border border-slate-200 rounded-xl py-1.5 px-2 text-xs font-semibold focus:outline-none focus:border-indigo-600 text-slate-800"
              >
                {['Tất cả', 'Intel Core i5', 'Intel Core i7', 'Intel Core Ultra', 'AMD Ryzen 5', 'AMD Ryzen 7', 'Apple M'].map(c => (
                  <option key={c} value={c}>{c}</option>
                ))}
              </select>
            </div>
          </div>

          {/* 5. RAM & Ổ cứng SSD */}
          <div className="grid grid-cols-2 gap-2 mb-4">
            <div>
              <label className="text-[11px] font-bold text-slate-700 block mb-1">
                RAM tối thiểu:
              </label>
              <select
                value={ramGb}
                onChange={(e) => onChangeRamGb(e.target.value)}
                className="w-full bg-slate-50 border border-slate-200 rounded-xl py-1.5 px-2 text-xs font-semibold focus:outline-none focus:border-indigo-600 text-slate-800"
              >
                <option value="">Tất cả</option>
                <option value="8">≥ 8 GB</option>
                <option value="16">≥ 16 GB</option>
                <option value="24">≥ 24 GB</option>
                <option value="32">≥ 32 GB</option>
              </select>
            </div>

            <div>
              <label className="text-[11px] font-bold text-slate-700 block mb-1">
                SSD tối thiểu:
              </label>
              <select
                value={storageGb}
                onChange={(e) => onChangeStorageGb(e.target.value)}
                className="w-full bg-slate-50 border border-slate-200 rounded-xl py-1.5 px-2 text-xs font-semibold focus:outline-none focus:border-indigo-600 text-slate-800"
              >
                <option value="">Tất cả</option>
                <option value="256">≥ 256 GB</option>
                <option value="512">≥ 512 GB</option>
                <option value="1024">≥ 1 TB (1024GB)</option>
              </select>
            </div>
          </div>

          {/* 6. Màn hình & Tần số quét */}
          <div className="grid grid-cols-2 gap-2 mb-4">
            <div>
              <label className="text-[11px] font-bold text-slate-700 block mb-1">
                Kích thước màn:
              </label>
              <select
                value={screenSize}
                onChange={(e) => onChangeScreenSize(e.target.value)}
                className="w-full bg-slate-50 border border-slate-200 rounded-xl py-1.5 px-2 text-xs font-semibold focus:outline-none focus:border-indigo-600 text-slate-800"
              >
                <option value="Tất cả">Tất cả</option>
                <option value="13.3">13.3 - 14.0 inch</option>
                <option value="15.6">15.6 inch</option>
                <option value="16.0">16.0 inch</option>
              </select>
            </div>

            <div>
              <label className="text-[11px] font-bold text-slate-700 block mb-1">
                Tần số quét:
              </label>
              <select
                value={refreshRate}
                onChange={(e) => onChangeRefreshRate(e.target.value)}
                className="w-full bg-slate-50 border border-slate-200 rounded-xl py-1.5 px-2 text-xs font-semibold focus:outline-none focus:border-indigo-600 text-slate-800"
              >
                <option value="Tất cả">Tất cả</option>
                <option value="60">60 Hz+</option>
                <option value="120">120 Hz+</option>
                <option value="144">144 Hz+ (Gaming)</option>
              </select>
            </div>
          </div>

          {/* 7. Bộ lọc phần cứng nâng cao (với in-situ tooltip) */}
          <div className="mb-4 pt-2 border-t border-slate-100">
            <label className="text-[11px] font-bold text-slate-700 block mb-2">
              Tiêu chuẩn phần cứng bắt buộc:
            </label>
            <div className="space-y-2">
              
              <label className="flex items-center justify-between text-xs cursor-pointer hover:bg-slate-50 p-1.5 rounded-lg transition">
                <div className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    checked={requireRj45}
                    onChange={(e) => onChangeRequireRj45(e.target.checked)}
                    className="accent-indigo-600 rounded cursor-pointer"
                  />
                  <span className="text-slate-700 font-medium">Cổng LAN (RJ45)</span>
                </div>
                <FilterInfoTooltip text="Có 527 máy chưa công bố rõ thông số LAN. Chỉ xếp máy có thông tin xác minh." />
              </label>

              <label className="flex items-center justify-between text-xs cursor-pointer hover:bg-slate-50 p-1.5 rounded-lg transition">
                <div className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    checked={requireRamUpgrade}
                    onChange={(e) => onChangeRequireRamUpgrade(e.target.checked)}
                    className="accent-indigo-600 rounded cursor-pointer"
                  />
                  <span className="text-slate-700 font-medium">Khả năng nâng RAM</span>
                </div>
                <FilterInfoTooltip text="Có 100 máy chưa công bố số khe RAM. Bỏ qua máy chưa xác thực." />
              </label>

              <label className="flex items-center justify-between text-xs cursor-pointer hover:bg-slate-50 p-1.5 rounded-lg transition">
                <div className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    checked={requireTypeCCharge}
                    onChange={(e) => onChangeRequireTypeCCharge(e.target.checked)}
                    className="accent-indigo-600 rounded cursor-pointer"
                  />
                  <span className="text-slate-700 font-medium">Sạc qua USB-C PD</span>
                </div>
                <FilterInfoTooltip text="Có 142 máy chưa công bố rõ chuẩn sạc Type-C." />
              </label>

              <label className="flex items-center justify-between text-xs cursor-pointer hover:bg-slate-50 p-1.5 rounded-lg transition">
                <div className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    checked={requireThunderbolt}
                    onChange={(e) => onChangeRequireThunderbolt(e.target.checked)}
                    className="accent-indigo-600 rounded cursor-pointer"
                  />
                  <span className="text-slate-700 font-medium">Thunderbolt / USB4</span>
                </div>
                <FilterInfoTooltip text="Có 333 máy chưa công bố thông số Thunderbolt." />
              </label>

            </div>
          </div>

          {/* Action Button: Apply */}
          <div className="pt-2">
            <button
              type="button"
              onClick={onApplyFilters}
              disabled={loading}
              className="w-full py-2.5 px-4 rounded-xl text-xs font-bold bg-indigo-600 hover:bg-indigo-700 disabled:bg-indigo-300 text-white transition flex items-center justify-center gap-2 cursor-pointer shadow-xs"
            >
              <Filter className="w-4 h-4" />
              <span>{loading ? 'Đang tính điểm TOPSIS...' : 'Duyệt & Cập Nhật Danh Sách'}</span>
            </button>

            {hasPendingEvaluation && (
              <div className="mt-2 text-[10px] text-amber-800 bg-amber-50 border border-amber-200 rounded-lg p-2 font-medium text-center">
                ⚠️ Điều kiện vừa đổi. Bấm <b>Duyệt & Cập nhật</b> để tính toán lại điểm.
              </div>
            )}
          </div>

        </div>

      </div>
    </aside>
  );
}
