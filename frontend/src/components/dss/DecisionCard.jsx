import React from 'react';
import { Heart, GitCompare, Sparkles, Cpu, HardDrive, MemoryStick, Monitor, Layers, ArrowUpRight } from 'lucide-react';
import CircularScore from '../common/CircularScore';
import { formatVnd, formatDiscount } from '../../utils/formatters';

export default function DecisionCard({
  item,
  rankingMode = 'topsis_only',
  isInCompare = false,
  isFav = false,
  onToggleFavorite,
  onToggleCompare,
  onOpenExplainDrawer,
  onOpenDetail,
}) {
  const rank = item.rank;
  const discount = formatDiscount(item.listed_price_vnd, item.sale_price_vnd);
  const topsisScore = item.topsis_score != null ? Math.round(item.topsis_score * 100) : 0;
  const fitScore = Math.round(((item.recommendation_score ?? item.topsis_score) || 0) * 100);

  // Extract clean spec items
  let cleanCpu = item.cpu_name_normalized || '';
  ['Intel Core ', 'Intel ', 'AMD Ryzen ', 'AMD ', 'Qualcomm Snapdragon ', 'Apple '].forEach(p => {
    cleanCpu = cleanCpu.replace(p, '');
  });

  let cleanGpu = item.gpu_name_normalized || '';
  if (cleanGpu && item.gpu_type === 'discrete') {
    cleanGpu = cleanGpu.replace('NVIDIA GeForce ', '').replace(' GDDR6', '');
  } else if (!cleanGpu || item.gpu_type !== 'discrete') {
    cleanGpu = 'iGPU';
  }

  // Value gap calculation
  const hasValueGap = item.ml_value_gap_percent != null && Number(item.ml_value_gap_percent) > 0;
  const valueGapFormatted = hasValueGap ? Math.round(Number(item.ml_value_gap_percent)) : null;

  // Rank styling
  const rankBadgeStyle = {
    1: 'bg-gradient-to-r from-amber-400 to-amber-500 text-white shadow-xs font-black',
    2: 'bg-gradient-to-r from-slate-400 to-slate-500 text-white shadow-xs font-black',
    3: 'bg-gradient-to-r from-amber-600 to-amber-700 text-white shadow-xs font-black',
  }[rank] || 'bg-slate-100 text-slate-700 font-bold border border-slate-200';

  return (
    <div
      className={`group relative flex flex-col justify-between rounded-2xl border-2 bg-white p-4 transition-all duration-200 hover:shadow-lg ${
        isInCompare
          ? 'border-indigo-500 ring-3 ring-indigo-100 shadow-md'
          : rank === 1
            ? 'border-amber-300/80 hover:border-indigo-500 shadow-2xs'
            : 'border-slate-200/90 hover:border-indigo-400'
      }`}
    >
      <div>
        {/* Header: Rank + Merchant + Favorite */}
        <div className="flex items-center justify-between gap-1.5 mb-2.5">
          <div className="flex items-center gap-1.5 flex-wrap">
            <span className={`text-[11px] px-2.5 py-0.5 rounded-lg flex items-center gap-1 ${rankBadgeStyle}`}>
              {rank ? (rank === 1 ? '🏆 TOP 1' : `#${rank}`) : 'Đã lưu'}
            </span>
            <span className="text-[10px] font-bold px-2 py-0.5 rounded-md bg-slate-100 text-slate-600 border border-slate-200">
              {item.source === 'fpt_shop' || item.source === 'FPT Shop' ? 'FPT Shop' : 'CellphoneS'}
            </span>
            {item.is_reference_gap && (
              <span className="text-[9px] font-black bg-emerald-50 text-emerald-700 border border-emerald-200 px-1.5 py-0.5 rounded">
                GIÁ THAM CHIẾU
              </span>
            )}
          </div>

          <div className="flex items-center gap-1">
            {discount && (
              <span className="text-[11px] font-extrabold text-rose-600 bg-rose-50 border border-rose-200 px-1.5 py-0.5 rounded">
                {discount}
              </span>
            )}
            <button
              type="button"
              onClick={(e) => {
                e.stopPropagation();
                onToggleFavorite(item);
              }}
              className={`p-1.5 rounded-xl transition cursor-pointer border ${
                isFav
                  ? 'bg-rose-50 border-rose-300 text-rose-600'
                  : 'bg-white border-slate-200 text-slate-400 hover:text-rose-600 hover:border-rose-200'
              }`}
              title={isFav ? "Bỏ khỏi danh sách yêu thích" : "Lưu vào yêu thích"}
              aria-label="Yêu thích"
            >
              <Heart className={`w-4 h-4 ${isFav ? 'fill-rose-600 text-rose-600' : ''}`} />
            </button>
          </div>
        </div>

        {/* Product image & score circle overlay */}
        <div className="relative w-full h-40 bg-white rounded-xl p-2 mb-2 flex items-center justify-center overflow-hidden">
          <img
            src={item.image_url}
            alt={item.product_name_raw}
            className="max-h-full max-w-full object-contain group-hover:scale-105 transition-transform duration-300"
            onError={(e) => { e.target.src = '/images/laptop_fallback.png'; }}
          />

          {/* DSS Fit Score Ring */}
          <div className="absolute top-1 right-1 bg-white/95 backdrop-blur-xs rounded-xl p-1 shadow-xs border border-slate-100">
            <CircularScore
              score={fitScore}
              size="sm"
            />
          </div>
        </div>

        {/* Spec Chips (CPU, GPU, RAM, SSD, Screen) */}
        <div className="flex flex-wrap gap-1 mb-2.5">
          <span className="inline-flex items-center gap-1 rounded-md bg-slate-50 border border-slate-200/80 px-2 py-0.5 text-[11px] font-semibold text-slate-700" title="Bộ xử lý CPU">
            <Cpu className="w-3 h-3 text-indigo-500" />
            <span className="truncate max-w-[130px]">{cleanCpu}</span>
          </span>
          {cleanGpu !== 'iGPU' && (
            <span className="inline-flex items-center gap-1 rounded-md bg-amber-50/80 border border-amber-200 px-2 py-0.5 text-[11px] font-semibold text-amber-800" title="Card đồ họa GPU">
              <Layers className="w-3 h-3 text-amber-600" />
              <span className="truncate max-w-[110px]">{cleanGpu}</span>
            </span>
          )}
          {item.ram_gb && (
            <span className="inline-flex items-center gap-1 rounded-md bg-slate-50 border border-slate-200/80 px-2 py-0.5 text-[11px] font-semibold text-slate-700">
              <MemoryStick className="w-3 h-3 text-emerald-500" />
              {item.ram_gb}GB
            </span>
          )}
          {item.storage_total_gb && (
            <span className="inline-flex items-center gap-1 rounded-md bg-slate-50 border border-slate-200/80 px-2 py-0.5 text-[11px] font-semibold text-slate-700">
              <HardDrive className="w-3 h-3 text-cyan-500" />
              {Math.round(Number(item.storage_total_gb))}GB
            </span>
          )}
          {item.screen_size_inch && (
            <span className="inline-flex items-center gap-1 rounded-md bg-slate-50 border border-slate-200/80 px-2 py-0.5 text-[11px] font-semibold text-slate-700">
              <Monitor className="w-3 h-3 text-slate-400" />
              {item.screen_size_inch}"
            </span>
          )}
        </div>

        {/* Product Title */}
        <h3
          onClick={() => onOpenDetail(item)}
          className="text-xs font-bold text-slate-900 line-clamp-2 min-h-9 mb-2 leading-relaxed hover:text-indigo-600 cursor-pointer transition-colors"
          title={item.product_name_raw}
        >
          {item.product_name_raw}
        </h3>

        {/* Pricing & ML Value Gap */}
        <div className="mb-3">
          <div className="flex items-baseline gap-2">
            <span className="text-lg font-black text-slate-900 tracking-tight">
              {formatVnd(item.sale_price_vnd)}
            </span>
            {discount && (
              <span className="text-xs text-slate-400 line-through">
                {formatVnd(item.listed_price_vnd)}
              </span>
            )}
          </div>

          {/* Machine Learning Value Gap Indicator */}
          {valueGapFormatted && (
            <div className="mt-1 flex items-center gap-1.5 text-[11px]">
              <span className="inline-flex items-center gap-1 px-1.5 py-0.5 rounded-md font-bold text-emerald-800 bg-emerald-100/80 border border-emerald-300">
                <Sparkles className="w-3 h-3 text-emerald-600" />
                Rẻ hơn định giá ML {valueGapFormatted}%
              </span>
            </div>
          )}
        </div>

        {/* DSS Score breakdown bar */}
        <div className="mb-3 rounded-xl bg-slate-50 border border-slate-100 p-2 text-[11px]">
          <div className="flex justify-between items-center text-slate-600 mb-1">
            <span className="font-medium text-slate-500">
              {rankingMode === 'ml_assisted' ? 'Điểm Đề xuất (85% TOPSIS + 15% ML):' : 'Độ phù hợp TOPSIS:'}
            </span>
            <span className="font-extrabold text-indigo-700">{fitScore}/100</span>
          </div>
          <div className="w-full h-1.5 bg-slate-200 rounded-full overflow-hidden">
            <div
              className="h-full bg-indigo-600 rounded-full transition-all duration-500"
              style={{ width: `${fitScore}%` }}
            />
          </div>
          {rankingMode === 'ml_assisted' && (
            <div className="mt-1 flex justify-between text-[10px] text-slate-400">
              <span>TOPSIS: {topsisScore}%</span>
              <span>Định giá ML: {Math.round((item.ml_valuation_score ?? 0.5) * 100)}%</span>
            </div>
          )}
        </div>
      </div>

      {/* Action Buttons: Explainability & Compare */}
      <div className="flex gap-2 pt-2 border-t border-slate-100">
        <button
          type="button"
          onClick={() => onOpenExplainDrawer(item)}
          className="flex-1 py-2 px-3 rounded-xl text-xs font-bold bg-indigo-50 hover:bg-indigo-600 text-indigo-700 hover:text-white transition-all flex items-center justify-center gap-1.5 cursor-pointer shadow-2xs"
          title="Xem giải trình vì sao máy này được xếp hạng này"
        >
          <span>Vì sao máy xếp #{rank}?</span>
          <ArrowUpRight className="w-3.5 h-3.5" />
        </button>

        <button
          type="button"
          onClick={() => onToggleCompare(item.source_product_id)}
          className={`py-2 px-3 rounded-xl text-xs font-bold transition cursor-pointer flex items-center gap-1.5 ${
            isInCompare
              ? 'bg-indigo-600 text-white border border-indigo-600 shadow-2xs'
              : 'bg-slate-100 hover:bg-slate-200 text-slate-700 border border-slate-200'
          }`}
          title={isInCompare ? "Bỏ khỏi so sánh" : "Thêm vào so sánh"}
        >
          <GitCompare className="w-3.5 h-3.5" />
          <span>{isInCompare ? 'Đã chọn' : 'So sánh'}</span>
        </button>
      </div>
    </div>
  );
}
