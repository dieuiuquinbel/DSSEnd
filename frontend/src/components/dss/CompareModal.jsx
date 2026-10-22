import React from 'react';
import { X, Trophy, CheckCircle, ExternalLink } from 'lucide-react';
import { formatVnd, formatDiscount } from '../../utils/formatters';
import CircularScore from '../common/CircularScore';

export default function CompareModal({
  laptops = [],
  onClose,
  onRemoveItem,
  onOpenDetail,
}) {
  if (laptops.length === 0) return null;

  // Find best values for highlighting
  const minPrice = Math.min(...laptops.map(l => Number(l.sale_price_vnd) || Infinity));
  const maxCpuMulti = Math.max(...laptops.map(l => Number(l.cpu_benchmark_multi_core) || 0));
  const maxGpuSpy = Math.max(...laptops.map(l => Number(l.gpu_benchmark_time_spy) || 0));
  const maxRam = Math.max(...laptops.map(l => Number(l.ram_gb) || 0));
  const maxStorage = Math.max(...laptops.map(l => Number(l.storage_total_gb) || 0));
  const minWeight = Math.min(...laptops.map(l => Number(l.weight_kg) || Infinity));
  const maxScore = Math.max(...laptops.map(l => Number(l.topsis_score) || 0));

  const rows = [
    {
      label: 'Điểm phù hợp TOPSIS',
      render: (l) => {
        const score = Math.round((l.topsis_score || 0) * 100);
        const isBest = l.topsis_score === maxScore && maxScore > 0;
        return (
          <div className="flex items-center justify-center gap-2">
            <span className={`text-sm font-black ${isBest ? 'text-emerald-600' : 'text-slate-800'}`}>
              {score}/100
            </span>
            {isBest && <Trophy className="w-4 h-4 text-amber-500" />}
          </div>
        );
      },
      isBestCell: (l) => l.topsis_score === maxScore && maxScore > 0,
    },
    {
      label: 'Giá bán chính hãng',
      render: (l) => {
        const isBest = Number(l.sale_price_vnd) === minPrice;
        return (
          <div>
            <span className={`text-sm font-black ${isBest ? 'text-emerald-700' : 'text-slate-900'}`}>
              {formatVnd(l.sale_price_vnd)}
            </span>
            {isBest && <span className="block text-[10px] font-bold text-emerald-600">Giá tốt nhất</span>}
          </div>
        );
      },
      isBestCell: (l) => Number(l.sale_price_vnd) === minPrice,
    },
    {
      label: 'Bộ vi xử lý (CPU)',
      render: (l) => (
        <div>
          <div className="font-bold text-slate-900">{l.cpu_name_normalized || 'Chưa công bố'}</div>
          {l.cpu_benchmark_multi_core && (
            <div className="text-[11px] text-slate-500 mt-0.5">
              Geekbench 6: <b>{Number(l.cpu_benchmark_multi_core).toLocaleString()}</b> điểm
            </div>
          )}
        </div>
      ),
      isBestCell: (l) => Number(l.cpu_benchmark_multi_core) === maxCpuMulti && maxCpuMulti > 0,
    },
    {
      label: 'Card đồ họa (GPU)',
      render: (l) => (
        <div>
          <div className="font-bold text-slate-900">{l.gpu_name_normalized || 'GPU tích hợp'}</div>
          {l.gpu_benchmark_time_spy && (
            <div className="text-[11px] text-slate-500 mt-0.5">
              3DMark Time Spy: <b>{Number(l.gpu_benchmark_time_spy).toLocaleString()}</b> điểm
            </div>
          )}
        </div>
      ),
      isBestCell: (l) => Number(l.gpu_benchmark_time_spy) === maxGpuSpy && maxGpuSpy > 0,
    },
    {
      label: 'Bộ nhớ RAM',
      render: (l) => `${l.ram_gb || '-'} GB ${l.ram_type || ''}`,
      isBestCell: (l) => Number(l.ram_gb) === maxRam && maxRam > 0,
    },
    {
      label: 'Ổ cứng SSD',
      render: (l) => `${l.storage_total_gb ? Math.round(Number(l.storage_total_gb)) : '-'} GB SSD`,
      isBestCell: (l) => Number(l.storage_total_gb) === maxStorage && maxStorage > 0,
    },
    {
      label: 'Màn hình',
      render: (l) => `${l.screen_size_inch || '-'}" ${l.panel_type || ''} (${l.refresh_rate_hz || 60}Hz)`,
      isBestCell: (l) => false,
    },
    {
      label: 'Trọng lượng máy',
      render: (l) => `${l.weight_kg ? `${l.weight_kg} kg` : 'Chưa công bố'}`,
      isBestCell: (l) => Number(l.weight_kg) === minWeight && minWeight < Infinity,
    },
    {
      label: 'Cổng LAN (RJ45)',
      render: (l) => l.lan_present === 'true' ? '✓ Có Gigabit LAN' : (l.lan_present === 'false' ? '✗ Không' : 'Chưa rõ'),
      isBestCell: (l) => l.lan_present === 'true',
    },
    {
      label: 'Nâng cấp RAM',
      render: (l) => l.ram_upgradeable === 'true' ? '✓ Nâng cấp được' : (l.ram_upgradeable === 'false' ? 'Hàn chết' : 'Chưa rõ'),
      isBestCell: (l) => l.ram_upgradeable === 'true',
    },
    {
      label: 'Nơi bán',
      render: (l) => l.source === 'fpt_shop' ? 'FPT Shop' : 'CellphoneS',
      isBestCell: () => false,
    },
  ];

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/50 backdrop-blur-xs p-4 overflow-y-auto">
      <div className="w-full max-w-5xl rounded-3xl bg-white shadow-2xl border border-slate-200 overflow-hidden flex flex-col max-h-[92vh] animate-in zoom-in-95 duration-150">
        
        {/* Header */}
        <div className="px-6 py-4 border-b border-slate-200 bg-slate-50 flex items-center justify-between">
          <div>
            <h3 className="text-base font-black text-slate-900">Bảng Đối Chiếu So Sánh Song Song</h3>
            <p className="text-xs text-slate-500">Các thông số tốt nhất trong từng tiêu chí được tự động tô viền xanh nổi bật</p>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-xl text-slate-400 hover:text-slate-700 hover:bg-slate-200/60 cursor-pointer transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Comparison Table */}
        <div className="flex-1 overflow-x-auto p-6">
          <table className="w-full text-xs border-collapse">
            <thead>
              <tr>
                <th className="p-3 text-left font-bold text-slate-400 w-44 bg-slate-50/60 rounded-l-xl">
                  Thông số tiêu chí
                </th>
                {laptops.map(laptop => (
                  <th key={laptop.source_product_id} className="p-3 text-center align-top min-w-[200px]">
                    <div className="relative flex flex-col items-center bg-white border border-slate-200 rounded-2xl p-3 shadow-2xs">
                      <button
                        type="button"
                        onClick={() => onRemoveItem(laptop.source_product_id)}
                        className="absolute top-2 right-2 text-slate-400 hover:text-rose-600 p-1 rounded-lg hover:bg-slate-50 cursor-pointer"
                        title="Bỏ máy này khỏi so sánh"
                      >
                        <X className="w-3.5 h-3.5" />
                      </button>
                      <img
                        src={laptop.image_url}
                        alt={laptop.product_name_raw}
                        className="w-20 h-20 object-contain mb-2"
                        onError={(e) => { e.target.src = '/images/laptop_fallback.png'; }}
                      />
                      <div className="font-bold text-slate-900 text-xs line-clamp-2 text-center h-8 leading-snug">
                        {laptop.product_name_raw}
                      </div>
                      <button
                        type="button"
                        onClick={() => {
                          onClose();
                          onOpenDetail(laptop);
                        }}
                        className="mt-2 text-[11px] font-bold text-indigo-600 hover:text-indigo-800 flex items-center gap-1 cursor-pointer"
                      >
                        <span>Chi tiết</span>
                        <ExternalLink className="w-3 h-3" />
                      </button>
                    </div>
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {rows.map((row, idx) => (
                <tr key={idx} className="hover:bg-slate-50/50 transition">
                  <td className="p-3 font-bold text-slate-700 bg-slate-50/40">
                    {row.label}
                  </td>
                  {laptops.map(laptop => {
                    const isBest = row.isBestCell(laptop);
                    return (
                      <td
                        key={laptop.source_product_id}
                        className={`p-3 text-center transition ${
                          isBest ? 'bg-emerald-50/70 font-semibold text-emerald-950 border-x border-emerald-200' : 'text-slate-700'
                        }`}
                      >
                        {row.render(laptop)}
                      </td>
                    );
                  })}
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Footer */}
        <div className="px-6 py-3.5 border-t border-slate-200 bg-slate-50 flex items-center justify-end">
          <button
            onClick={onClose}
            className="px-5 py-2 rounded-xl text-xs font-bold bg-slate-900 hover:bg-slate-800 text-white cursor-pointer transition"
          >
            Đóng bảng so sánh
          </button>
        </div>

      </div>
    </div>
  );
}
