import React, { useState } from 'react';
import { Info, X, ShieldAlert } from 'lucide-react';

/**
 * ConsolidatedDataNotice replaces the 4 stacked yellow banners with a single compact,
 * non-intrusive alert banner with a modal/popover for details.
 */
export function ConsolidatedDataNotice({ filterDataQuality = [], droppedCriteria = [] }) {
  const [showModal, setShowModal] = useState(false);

  const activeQualityWarnings = filterDataQuality.filter(item => item.unknown_count > 0);
  const totalWarnings = activeQualityWarnings.length + (droppedCriteria.length > 0 ? 1 : 0);

  if (totalWarnings === 0) return null;

  return (
    <>
      <div className="mb-4 flex items-center justify-between gap-3 rounded-xl border border-amber-200/80 bg-amber-50/70 px-3.5 py-2.5 text-xs text-amber-900 shadow-2xs">
        <div className="flex items-center gap-2 overflow-hidden">
          <div className="flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-amber-200/60 text-amber-800">
            <Info className="h-3.5 w-3.5" />
          </div>
          <p className="truncate font-medium">
            <span className="font-semibold text-amber-950">Lưu ý kiểm chứng dữ liệu:</span> Một số bộ lọc cổng kết nối & tiêu chuẩn chỉ tính máy đã có thông số xác thực.
          </p>
        </div>
        <button
          type="button"
          onClick={() => setShowModal(true)}
          className="shrink-0 cursor-pointer rounded-lg bg-white px-2.5 py-1 text-[11px] font-bold text-amber-900 border border-amber-300 hover:bg-amber-100 transition"
        >
          Chi tiết ({totalWarnings})
        </button>
      </div>

      {showModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/40 backdrop-blur-xs p-4">
          <div className="w-full max-w-lg rounded-2xl bg-white p-5 shadow-2xl border border-slate-200 animate-in fade-in zoom-in-95 duration-150">
            <div className="flex items-center justify-between pb-3 border-b border-slate-100">
              <div className="flex items-center gap-2">
                <ShieldAlert className="w-5 h-5 text-amber-600" />
                <h3 className="text-sm font-bold text-slate-900">Tính Trung Thực Của Dữ Liệu Bộ Lọc</h3>
              </div>
              <button
                onClick={() => setShowModal(false)}
                className="rounded-lg p-1 text-slate-400 hover:bg-slate-100 hover:text-slate-700 cursor-pointer"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <div className="mt-3.5 space-y-3 max-h-[60vh] overflow-y-auto pr-1">
              <p className="text-xs text-slate-600 leading-relaxed">
                Để đảm bảo nguyên tắc <b>khoa học và trung thực học thuật (chuẩn D14)</b>, hệ thống không tự ý gán giá trị mặc định khi nhà bán lẻ chưa công bố rõ thông số:
              </p>

              {activeQualityWarnings.map(item => (
                <div key={item.filter} className="rounded-xl border border-amber-200 bg-amber-50/50 p-3 text-xs">
                  <div className="font-bold text-amber-950 mb-0.5">{item.label}</div>
                  <div className="text-amber-800 text-[11px] leading-relaxed">
                    Có <b>{item.unknown_count} máy</b> chưa công bố thông số này nên không bị coi là "không có" nhưng sẽ tạm không xuất hiện khi bạn bật điều kiện bắt buộc này.
                  </div>
                </div>
              ))}

              {droppedCriteria.length > 0 && (
                <div className="rounded-xl border border-indigo-200 bg-indigo-50/50 p-3 text-xs">
                  <div className="font-bold text-indigo-950 mb-0.5">Tiêu chí chưa đủ độ phủ (D14):</div>
                  <div className="text-indigo-800 text-[11px] leading-relaxed">
                    {droppedCriteria.map(item => item.criterion).join(', ')} bị tạm gác khỏi ma trận chấm TOPSIS do tỷ lệ máy có dữ liệu trong phân khúc hiện tại dưới ngưỡng thống kê.
                  </div>
                </div>
              )}
            </div>

            <div className="mt-4 pt-3 border-t border-slate-100 flex justify-end">
              <button
                onClick={() => setShowModal(false)}
                className="cursor-pointer rounded-xl bg-slate-900 hover:bg-slate-800 text-white px-4 py-2 text-xs font-bold transition"
              >
                Đã hiểu
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}

/**
 * FilterInfoTooltip provides an in-situ tooltip icon next to individual filter checkboxes.
 */
export function FilterInfoTooltip({ text }) {
  const [open, setOpen] = useState(false);

  if (!text) return null;

  return (
    <span className="relative inline-flex items-center ml-1">
      <button
        type="button"
        onClick={(e) => { e.stopPropagation(); setOpen(!open); }}
        onMouseEnter={() => setOpen(true)}
        onMouseLeave={() => setOpen(false)}
        className="text-slate-400 hover:text-amber-600 cursor-pointer p-0.5 focus:outline-none"
        title={text}
        aria-label="Thông tin bộ lọc"
      >
        <Info className="w-3.5 h-3.5" />
      </button>
      {open && (
        <span className="absolute bottom-full left-1/2 -translate-x-1/2 mb-1.5 w-52 rounded-lg bg-slate-900 px-2.5 py-1.5 text-[10px] leading-tight text-white shadow-xl z-30 pointer-events-none transition-all">
          {text}
        </span>
      )}
    </span>
  );
}
