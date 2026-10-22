import React from 'react';
import { X, AlertTriangle, CheckCircle, Scale, Sparkles, ExternalLink, Calculator } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts';
import { formatVnd, CRITERIA_LABELS, formatExplanationText } from '../../utils/formatters';
import CircularScore from '../common/CircularScore';

export default function ExplainabilityDrawer({
  laptop,
  activeCriteria = [],
  rankingMode = 'topsis_only',
  onClose,
  onOpenDetail,
}) {
  if (!laptop) return null;

  const rank = laptop.rank || 1;
  const fitScore = Math.round(((laptop.recommendation_score ?? laptop.topsis_score) || 0) * 100);
  const topsisScore = Math.round((laptop.topsis_score || 0) * 100);

  // Criteria chart data
  const chartData = activeCriteria.map(([criterion, , weight]) => {
    const label = CRITERIA_LABELS[criterion] || criterion;
    const cleanLabel = label.split(' (')[0];
    const weightPercent = Math.round(weight * 100);
    return {
      name: cleanLabel,
      key: criterion,
      weight: weightPercent,
      // Sample score estimation based on rank and weights
      score: Math.min(100, Math.round(fitScore * (0.8 + 0.4 * (weightPercent / 20)))),
    };
  });

  return (
    <div className="fixed inset-0 z-50 overflow-hidden bg-slate-900/40 backdrop-blur-xs">
      <div className="absolute inset-y-0 right-0 max-w-full flex pl-10">
        <div className="w-screen max-w-xl bg-white shadow-2xl border-l border-slate-200 flex flex-col animate-in slide-in-from-right duration-250">
          
          {/* Header */}
          <div className="px-6 py-4 bg-slate-50 border-b border-slate-200 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className="flex h-7 w-7 items-center justify-center rounded-lg bg-indigo-600 text-white font-black text-xs">
                #{rank}
              </span>
              <div>
                <h2 className="text-sm font-bold text-slate-900">Giải Trình Quyết Định DSS</h2>
                <p className="text-[11px] text-slate-500">Vì sao máy đạt thứ hạng này trong hồ sơ hiện tại</p>
              </div>
            </div>
            <button
              onClick={onClose}
              className="p-1.5 rounded-lg text-slate-400 hover:text-slate-700 hover:bg-slate-200/60 cursor-pointer transition"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Drawer Body */}
          <div className="flex-1 overflow-y-auto p-6 space-y-6">

            {/* Laptop Summary Card */}
            <div className="flex items-center gap-4 p-4 rounded-2xl bg-indigo-50/60 border border-indigo-100">
              <img
                src={laptop.image_url}
                alt={laptop.product_name_raw}
                className="w-16 h-16 object-contain bg-white rounded-xl p-1 border border-slate-200 shrink-0"
                onError={(e) => { e.target.src = '/images/laptop_fallback.png'; }}
              />
              <div className="min-w-0 flex-1">
                <h3 className="text-xs font-bold text-slate-900 truncate">{laptop.product_name_raw}</h3>
                <div className="text-base font-extrabold text-indigo-700 mt-0.5">
                  {formatVnd(laptop.sale_price_vnd)}
                </div>
                <div className="text-[11px] text-slate-500">
                  {laptop.source === 'fpt_shop' ? 'FPT Shop' : 'CellphoneS'}
                </div>
              </div>
              <CircularScore score={fitScore} size="md" label="Điểm DSS" />
            </div>

            {/* AHP & TOPSIS Mathematical breakdown */}
            <div className="space-y-3">
              <div className="flex items-center gap-2 text-xs font-bold text-slate-900">
                <Calculator className="w-4 h-4 text-indigo-600" />
                <span>Cơ chế tính điểm TOPSIS (Khoảng cách phương án lý tưởng)</span>
              </div>

              <div className="rounded-xl border border-slate-200 bg-slate-50 p-3.5 text-xs text-slate-700 space-y-2">
                <p className="text-[11px] text-slate-600 leading-relaxed">
                  Thuật toán TOPSIS chuẩn hóa ma trận quyết định theo vector Euclid, sau đó nhân với vector trọng số AHP để xác định:
                </p>
                <div className="grid grid-cols-2 gap-2 text-center">
                  <div className="p-2 rounded-lg bg-emerald-50 border border-emerald-200">
                    <span className="text-[10px] text-emerald-800 font-semibold block">Khoảng cách tệ nhất (S⁻)</span>
                    <span className="text-sm font-black text-emerald-700">Tối đa hóa</span>
                  </div>
                  <div className="p-2 rounded-lg bg-rose-50 border border-rose-200">
                    <span className="text-[10px] text-rose-800 font-semibold block">Khoảng cách lý tưởng (S⁺)</span>
                    <span className="text-sm font-black text-rose-700">Tối thiểu hóa</span>
                  </div>
                </div>
                <div className="text-[11px] text-slate-500 text-center font-mono bg-white p-2 rounded-lg border border-slate-200">
                  Độ phù hợp: C* = S⁻ / (S⁺ + S⁻) = <b className="text-indigo-600">{topsisScore}%</b>
                </div>
              </div>
            </div>

            {/* Criteria Contribution Chart */}
            <div className="space-y-3">
              <div className="flex items-center justify-between text-xs font-bold text-slate-900">
                <span className="flex items-center gap-2">
                  <Scale className="w-4 h-4 text-indigo-600" />
                  <span>Trọng số AHP của các tiêu chí</span>
                </span>
                <span className="text-[11px] text-slate-400 font-normal">Tổng = 100%</span>
              </div>

              <div className="h-48 w-full bg-slate-50 rounded-xl p-2 border border-slate-200">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart
                    data={chartData}
                    layout="vertical"
                    margin={{ top: 5, right: 25, left: 20, bottom: 5 }}
                  >
                    <XAxis type="number" domain={[0, 50]} unit="%" tick={{ fontSize: 10 }} />
                    <YAxis dataKey="name" type="category" width={85} tick={{ fontSize: 10 }} />
                    <Tooltip
                      formatter={(val) => [`${val}%`, 'Trọng số AHP']}
                      contentStyle={{ fontSize: '11px', borderRadius: '8px' }}
                    />
                    <Bar dataKey="weight" radius={[0, 4, 4, 0]}>
                      {chartData.map((entry, index) => (
                        <Cell
                          key={`cell-${index}`}
                          fill={index === 0 ? '#4f46e5' : '#6366f1'}
                        />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Qualitative Explanation (Advantage & Trade-off) */}
            <div className="space-y-3">
              <div className="text-xs font-bold text-slate-900">Ưu thế vượt trội & Điểm đánh đổi</div>

              {laptop.explanation?.top_advantage && (
                <div className="rounded-xl border border-emerald-200 bg-emerald-50/70 p-3 text-xs">
                  <div className="flex items-center gap-1.5 font-bold text-emerald-900 mb-1">
                    <CheckCircle className="w-3.5 h-3.5 text-emerald-600" />
                    <span>Ưu thế lớn nhất trong tập ứng viên:</span>
                  </div>
                  <p className="text-[11px] text-emerald-800 leading-relaxed">
                    {formatExplanationText(laptop.explanation.top_advantage, 'advantage')}
                  </p>
                </div>
              )}

              {laptop.explanation?.top_penalty && (
                <div className="rounded-xl border border-amber-200 bg-amber-50/70 p-3 text-xs">
                  <div className="flex items-center gap-1.5 font-bold text-amber-900 mb-1">
                    <AlertTriangle className="w-3.5 h-3.5 text-amber-600" />
                    <span>Điểm đánh đổi / Chưa tối đa:</span>
                  </div>
                  <p className="text-[11px] text-amber-800 leading-relaxed">
                    {formatExplanationText(laptop.explanation.top_penalty, 'penalty')}
                  </p>
                </div>
              )}
            </div>

            {/* ML Valuation Gap (if available) */}
            {laptop.ml_predicted_price_vnd && (
              <div className="rounded-2xl border border-indigo-200 bg-gradient-to-br from-indigo-50/50 to-white p-4 space-y-2">
                <div className="flex items-center gap-2 font-bold text-xs text-indigo-950">
                  <Sparkles className="w-4 h-4 text-indigo-600" />
                  <span>Định giá học máy (Out-Of-Fold Reference)</span>
                </div>
                <p className="text-[11px] text-slate-600 leading-relaxed">
                  Mô hình Gradient Boosting / Random Forest dựa trên thông số phần cứng ước lượng mức giá chuẩn thị trường:
                </p>
                <div className="flex items-center justify-between pt-2 border-t border-indigo-100 text-xs">
                  <div>
                    <span className="text-slate-500 block text-[10px]">Giá dự báo mô hình</span>
                    <span className="font-bold text-slate-900">{formatVnd(laptop.ml_predicted_price_vnd)}</span>
                  </div>
                  <div>
                    <span className="text-slate-500 block text-[10px]">Giá bán thực tế</span>
                    <span className="font-bold text-indigo-700">{formatVnd(laptop.sale_price_vnd)}</span>
                  </div>
                  <div className="text-right">
                    <span className="text-slate-500 block text-[10px]">Chênh lệch Value Gap</span>
                    <span className="font-extrabold text-emerald-600">
                      +{Math.round(Number(laptop.ml_value_gap_percent || 0))}%
                    </span>
                  </div>
                </div>
              </div>
            )}

          </div>

          {/* Drawer Footer */}
          <div className="p-4 bg-slate-50 border-t border-slate-200 flex gap-3">
            <button
              onClick={() => {
                onClose();
                onOpenDetail(laptop);
              }}
              className="flex-1 py-2.5 px-4 rounded-xl text-xs font-bold bg-indigo-600 hover:bg-indigo-700 text-white transition flex items-center justify-center gap-2 cursor-pointer shadow-xs"
            >
              <span>Xem toàn bộ thông số chi tiết</span>
              <ExternalLink className="w-3.5 h-3.5" />
            </button>
            <button
              onClick={onClose}
              className="py-2.5 px-4 rounded-xl text-xs font-bold bg-white hover:bg-slate-100 text-slate-700 border border-slate-200 cursor-pointer transition"
            >
              Đóng
            </button>
          </div>

        </div>
      </div>
    </div>
  );
}
