import React, { useState } from 'react';
import { X, SlidersHorizontal, RotateCcw, Check } from 'lucide-react';
import { CRITERIA_LABELS, CRITERIA_ICONS } from '../../utils/formatters';

export default function WeightEditorModal({
  activeCriteria = [],
  customWeightValues = null,
  onSaveWeights,
  onResetWeights,
  onClose,
}) {
  const [localWeights, setLocalWeights] = useState(() => {
    if (customWeightValues) return [...customWeightValues];
    return activeCriteria.map(([, , w]) => Math.round(w * 100));
  });

  const handleSliderChange = (idx, value) => {
    const updated = [...localWeights];
    updated[idx] = Number(value);
    setLocalWeights(updated);
  };

  const total = localWeights.reduce((sum, v) => sum + v, 0);

  const handleSave = () => {
    // Normalize to sum = 1
    const normalized = localWeights.map(v => v / (total || 1));
    onSaveWeights(normalized);
    onClose();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/50 backdrop-blur-xs p-4">
      <div className="w-full max-w-lg rounded-3xl bg-white shadow-2xl border border-slate-200 overflow-hidden flex flex-col animate-in zoom-in-95 duration-150">
        
        {/* Header */}
        <div className="px-6 py-4 border-b border-slate-200 bg-slate-50 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-7 h-7 rounded-lg bg-indigo-100 text-indigo-700 flex items-center justify-center">
              <SlidersHorizontal className="w-4 h-4" />
            </div>
            <div>
              <h3 className="text-sm font-bold text-slate-900">Tùy Biến Trọng Số Quyết Định (Direct Rating)</h3>
              <p className="text-[11px] text-slate-500">Điều chỉnh mức độ ưu tiên theo ý thích cá nhân</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded-lg text-slate-400 hover:text-slate-700 hover:bg-slate-200/60 cursor-pointer"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Sliders list */}
        <div className="p-6 space-y-4 max-h-[60vh] overflow-y-auto">
          {activeCriteria.map(([cname, , defaultWeight], idx) => {
            const currentVal = localWeights[idx] ?? Math.round(defaultWeight * 100);
            const calculatedPercent = total > 0 ? Math.round((currentVal / total) * 100) : 0;

            return (
              <div key={cname} className="space-y-1.5 bg-slate-50 p-3 rounded-xl border border-slate-100">
                <div className="flex items-center justify-between text-xs">
                  <span className="font-bold text-slate-800 flex items-center gap-1.5">
                    <span>{CRITERIA_ICONS[cname] || '📊'}</span>
                    <span>{CRITERIA_LABELS[cname] || cname}</span>
                  </span>
                  <div className="flex items-center gap-2">
                    <span className="text-[10px] text-slate-400">
                      Gốc: {Math.round(defaultWeight * 100)}%
                    </span>
                    <span className="font-black text-indigo-700 text-xs w-10 text-right">
                      {calculatedPercent}%
                    </span>
                  </div>
                </div>

                <input
                  type="range"
                  min="0"
                  max="100"
                  value={currentVal}
                  onChange={(e) => handleSliderChange(idx, e.target.value)}
                  className="w-full accent-indigo-600 cursor-pointer h-1.5 bg-slate-200 rounded-lg"
                />
              </div>
            );
          })}
        </div>

        {/* Footer */}
        <div className="px-6 py-3.5 border-t border-slate-200 bg-slate-50 flex items-center justify-between">
          <button
            type="button"
            onClick={() => {
              onResetWeights();
              onClose();
            }}
            className="flex items-center gap-1.5 text-xs font-semibold text-slate-500 hover:text-rose-600 cursor-pointer transition"
          >
            <RotateCcw className="w-3.5 h-3.5" />
            <span>Khôi phục trọng số AHP gốc</span>
          </button>

          <div className="flex gap-2">
            <button
              onClick={onClose}
              className="px-4 py-2 rounded-xl text-xs font-bold text-slate-600 hover:bg-slate-200 cursor-pointer transition"
            >
              Hủy
            </button>
            <button
              onClick={handleSave}
              className="px-5 py-2 rounded-xl text-xs font-bold bg-indigo-600 hover:bg-indigo-700 text-white cursor-pointer transition flex items-center gap-1.5 shadow-xs"
            >
              <Check className="w-3.5 h-3.5" />
              <span>Áp dụng trọng số</span>
            </button>
          </div>
        </div>

      </div>
    </div>
  );
}
