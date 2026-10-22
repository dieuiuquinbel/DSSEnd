import React, { useState } from 'react';
import { Sparkles, X, Check, HelpCircle, ArrowRight, CornerDownLeft } from 'lucide-react';
import { formatVnd } from '../../utils/formatters';

export default function NlQueryParserBox({
  nlQuery,
  onChangeNlQuery,
  onSearch,
  nlResult,
  onRemoveEntity,
  onApplyFilters,
  nlError,
  loading = false,
}) {
  const samplePrompts = [
    'Tài chính 25 triệu cần máy lập trình RAM 16GB có cổng LAN',
    'Sinh viên kinh tế dưới 15 củ mỏng nhẹ',
    'Laptop gaming RTX tầm 28 triệu màn 144Hz',
    'Máy làm đồ họa không lấy Dell RAM 32GB',
  ];

  const entityTypeLabels = {
    min_budget: 'Ngân sách tối thiểu',
    max_budget: 'Ngân sách tối đa',
    brand: 'Hãng máy',
    excluded_brand: 'Loại trừ hãng',
    min_ram: 'RAM tối thiểu',
    min_storage: 'SSD tối thiểu',
    min_refresh_rate: 'Tần số quét',
    screen_size: 'Kích cỡ màn',
    panel_type: 'Tấm nền',
    rj45: 'Cổng LAN',
    ram_upgrade: 'Nâng RAM',
    type_c_charging: 'Sạc Type-C',
    thunderbolt: 'Thunderbolt',
    os: 'Hệ điều hành',
    cpu: 'Dòng chip CPU',
    strict_benchmark: 'Chuẩn benchmark',
  };

  const formatEntityValue = (entity) => {
    if (entity.type === 'max_budget' || entity.type === 'min_budget') {
      return formatVnd(entity.value);
    }
    if (entity.type === 'min_ram') return `${entity.value} GB`;
    if (entity.type === 'min_storage') return `${entity.value} GB`;
    if (entity.type === 'min_refresh_rate') return `${entity.value} Hz`;
    return String(entity.value);
  };

  return (
    <div className="rounded-2xl border border-indigo-200 bg-white p-5 shadow-2xs mb-6">
      
      {/* Header */}
      <div className="flex items-center gap-2.5 mb-3">
        <div className="w-8 h-8 rounded-xl bg-indigo-100 text-indigo-700 flex items-center justify-center font-bold">
          <Sparkles className="w-4 h-4" />
        </div>
        <div>
          <h3 className="text-sm font-bold text-slate-900">Trợ Lý Bóc Tách Yêu Cầu Tự Nhiên (AI NLP)</h3>
          <p className="text-xs text-slate-500">Nhập câu mô tả tự do, hệ thống tự động trích xuất các điều kiện và phân loại hồ sơ tối ưu.</p>
        </div>
      </div>

      {/* Input Form */}
      <form
        onSubmit={(e) => {
          e.preventDefault();
          if (nlQuery.trim()) onSearch(nlQuery);
        }}
        className="space-y-3"
      >
        <div className="flex gap-2">
          <input
            type="text"
            value={nlQuery}
            onChange={(e) => onChangeNlQuery(e.target.value)}
            placeholder="Ví dụ: Tài chính 25 triệu, laptop code RAM 16GB có cổng LAN không lấy Dell"
            className="flex-1 px-4 py-2.5 rounded-xl border border-slate-300 text-xs font-medium focus:outline-none focus:border-indigo-600 focus:ring-2 focus:ring-indigo-100 text-slate-900 placeholder:text-slate-400"
          />
          <button
            type="submit"
            disabled={loading || !nlQuery.trim()}
            className="px-5 py-2.5 rounded-xl text-xs font-bold bg-indigo-600 hover:bg-indigo-700 disabled:bg-indigo-300 text-white transition flex items-center gap-1.5 cursor-pointer shadow-xs"
          >
            <Sparkles className="w-3.5 h-3.5" />
            <span>Phân tích</span>
          </button>
        </div>

        {/* Sample queries */}
        <div className="flex flex-wrap items-center gap-1.5 text-[11px]">
          <span className="text-slate-400 font-semibold">Gợi ý mẫu:</span>
          {samplePrompts.map(p => (
            <button
              key={p}
              type="button"
              onClick={() => {
                onChangeNlQuery(p);
                onSearch(p);
              }}
              className="px-2.5 py-1 rounded-full bg-slate-50 hover:bg-indigo-50 border border-slate-200 text-slate-600 hover:text-indigo-600 transition cursor-pointer"
            >
              {p}
            </button>
          ))}
        </div>
      </form>

      {/* Error message */}
      {nlError && (
        <div className="mt-3 p-3 bg-rose-50 border border-rose-200 rounded-xl text-xs text-rose-700">
          {nlError}
        </div>
      )}

      {/* Parsed Result Display */}
      {nlResult && (
        <div className="mt-4 pt-4 border-t border-slate-100 space-y-3 animate-in fade-in duration-200">
          
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-slate-800">
              Các điều kiện hệ thống đã bóc tách được:
            </span>
            {nlResult.preset_key && (
              <span className="text-[11px] font-bold text-indigo-700 bg-indigo-50 px-2.5 py-0.5 rounded-full border border-indigo-200">
                Khớp hồ sơ: {nlResult.preset_name || nlResult.preset_key}
              </span>
            )}
          </div>

          {/* Interactive Removable Chips */}
          <div className="flex flex-wrap gap-2">
            {(nlResult.entities || []).map((entity, idx) => (
              <div
                key={idx}
                className="inline-flex items-center gap-1.5 rounded-xl border border-indigo-200 bg-indigo-50/80 px-2.5 py-1 text-xs text-indigo-950 font-medium"
              >
                <span className="text-slate-500 text-[10px]">
                  {entityTypeLabels[entity.type] || entity.type}:
                </span>
                <span className="font-bold text-indigo-700">
                  {formatEntityValue(entity)}
                </span>
                <button
                  type="button"
                  onClick={() => onRemoveEntity(entity)}
                  className="rounded-full p-0.5 text-indigo-400 hover:text-rose-600 hover:bg-white cursor-pointer transition ml-0.5"
                  title="Xóa điều kiện này"
                >
                  <X className="w-3 h-3" />
                </button>
              </div>
            ))}
          </div>

          {/* Unparsed tokens notice */}
          {nlResult.unparsed_tokens && nlResult.unparsed_tokens.length > 0 && (
            <div className="flex items-center gap-2 p-2.5 rounded-xl bg-slate-50 border border-slate-200 text-[11px] text-slate-600">
              <HelpCircle className="w-4 h-4 text-slate-400 shrink-0" />
              <div>
                <span className="font-semibold text-slate-700">Từ chưa được phân loại vào bộ lọc: </span>
                <span className="font-mono text-slate-500">
                  {nlResult.unparsed_tokens.join(', ')}
                </span>
              </div>
            </div>
          )}

          {/* Apply button */}
          <div className="flex justify-end pt-2">
            <button
              type="button"
              onClick={onApplyFilters}
              className="px-4 py-2 rounded-xl text-xs font-bold bg-indigo-600 hover:bg-indigo-700 text-white transition flex items-center gap-1.5 cursor-pointer shadow-xs"
            >
              <Check className="w-3.5 h-3.5" />
              <span>Áp dụng các điều kiện này vào bộ lọc</span>
            </button>
          </div>

        </div>
      )}

    </div>
  );
}
