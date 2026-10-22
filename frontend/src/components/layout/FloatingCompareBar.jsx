import React from 'react';
import { GitCompare, X, Trash2, ArrowRight } from 'lucide-react';
import { formatVnd } from '../../utils/formatters';

export default function FloatingCompareBar({
  compareLaptops = [],
  onRemoveItem,
  onClearAll,
  onOpenModal,
}) {
  if (compareLaptops.length === 0) return null;

  return (
    <div className="fixed bottom-4 left-1/2 -translate-x-1/2 z-40 w-[95%] max-w-3xl">
      <div className="rounded-2xl border border-indigo-200 bg-white/95 p-3 shadow-2xl backdrop-blur-md flex items-center justify-between gap-3 animate-in slide-in-from-bottom duration-200">
        
        <div className="flex items-center gap-3 overflow-x-auto py-1">
          <div className="flex items-center gap-1.5 shrink-0 px-2.5 py-1 rounded-xl bg-indigo-50 text-indigo-700 font-bold text-xs border border-indigo-100">
            <GitCompare className="w-4 h-4" />
            <span>So sánh ({compareLaptops.length}/4)</span>
          </div>

          {/* Thumbnails */}
          <div className="flex items-center gap-2">
            {compareLaptops.map(laptop => (
              <div
                key={laptop.source_product_id}
                className="relative group flex items-center gap-2 rounded-xl border border-slate-200 bg-slate-50/80 p-1.5 pr-2 shrink-0 max-w-[180px]"
              >
                <img
                  src={laptop.image_url}
                  alt={laptop.product_name_raw}
                  className="w-8 h-8 object-contain bg-white rounded-lg p-0.5 border border-slate-200 shrink-0"
                  onError={(e) => { e.target.src = '/images/laptop_fallback.png'; }}
                />
                <div className="min-w-0 flex-1">
                  <div className="text-[11px] font-bold text-slate-800 truncate">
                    {laptop.product_name_raw}
                  </div>
                  <div className="text-[10px] font-black text-indigo-600">
                    {formatVnd(laptop.sale_price_vnd)}
                  </div>
                </div>
                <button
                  type="button"
                  onClick={() => onRemoveItem(laptop.source_product_id)}
                  className="rounded-full p-0.5 text-slate-400 hover:text-rose-600 hover:bg-white cursor-pointer transition"
                  title="Bỏ khỏi so sánh"
                >
                  <X className="w-3.5 h-3.5" />
                </button>
              </div>
            ))}
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex items-center gap-2 shrink-0">
          <button
            type="button"
            onClick={onClearAll}
            className="p-2 rounded-xl text-slate-400 hover:text-slate-700 hover:bg-slate-100 cursor-pointer transition"
            title="Xóa tất cả danh sách so sánh"
          >
            <Trash2 className="w-4 h-4" />
          </button>

          <button
            type="button"
            onClick={onOpenModal}
            className="py-2 px-4 rounded-xl text-xs font-bold bg-indigo-600 hover:bg-indigo-700 text-white transition flex items-center gap-1.5 cursor-pointer shadow-xs"
          >
            <span>Mở bảng đối chiếu</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </div>

      </div>
    </div>
  );
}
