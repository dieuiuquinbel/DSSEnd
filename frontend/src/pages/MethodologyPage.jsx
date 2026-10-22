import React, { useState } from 'react';
import {
  BookOpen, Database, Filter, Scale, Calculator, Brain, Award, ArrowRight
} from 'lucide-react';
import { CRITERIA_LABELS } from '../utils/formatters';

export default function MethodologyPage({
  ahpCr = null,
  pairwiseMatrix = [],
  activeCriteria = [],
}) {
  const [selectedStep, setSelectedStep] = useState(4); // Default to TOPSIS (step 4)

  const steps = [
    {
      id: 1,
      name: 'Thu Thập Dữ Liệu',
      tag: 'Scraping',
      icon: Database,
      desc: 'Cào tự động thông số kỹ thuật thực tế từ hệ thống bán lẻ chính hãng (FPT Shop, CellphoneS).',
      detail: 'Dữ liệu được thu thập định kỳ từ các chuỗi bán lẻ lớn tại Việt Nam, bao gồm giá niêm yết, giá khuyến mãi, chi tiết CPU, GPU, RAM, SSD, màn hình, cổng kết nối và dung lượng pin.',
    },
    {
      id: 2,
      name: 'Làm Sạch & Chuẩn Hóa',
      tag: 'Preprocessing',
      icon: Filter,
      desc: 'Quy chuẩn tên linh kiện và ánh xạ điểm Benchmark xác thực (Geekbench 6, 3DMark).',
      detail: 'Chuẩn hóa tên vi xử lý, card đồ họa về định dạng quy chuẩn. Điểm benchmark được crawl và đối soát tự động từ cơ sở dữ liệu Geekbench 6 (CPU single/multi) và 3DMark Time Spy (GPU). Tuân thủ nguyên tắc D14 không tự bịa số.',
    },
    {
      id: 3,
      name: 'Xác Định Trọng Số AHP',
      tag: 'AHP Matrix',
      icon: Scale,
      desc: 'Lập ma trận so sánh cặp Saaty 1-9 cho từng nhóm nhu cầu, kiểm soát tỷ số nhất quán CR < 0.1.',
      detail: 'Phương pháp phân tích thứ bậc (Analytic Hierarchy Process - Thomas Saaty). Chuyên gia xác lập mức độ ưu tiên giữa các tiêu chí theo từng hồ sơ (Sinh viên, Mỏng nhẹ, Lập trình, Gaming). Tỷ số nhất quán CR được giám sát nghiêm ngặt dưới 10%.',
    },
    {
      id: 4,
      name: 'Xếp Hạng TOPSIS',
      tag: 'TOPSIS Algorithm',
      icon: Calculator,
      desc: 'Chuẩn hóa vector Euclid, tính khoảng cách tới phương án lý tưởng (S+) và phương án tồi nhất (S-).',
      detail: 'Technique for Order of Preference by Similarity to Ideal Solution (Hwang & Yoon). Máy đứng đầu là phương án có khoảng cách hình học ngắn nhất tới điểm lý tưởng (S+) và xa nhất điểm tồi tệ (S-). Điểm độ phù hợp C* = S- / (S+ + S-).',
    },
    {
      id: 5,
      name: 'Thẩm Định Giá ML',
      tag: 'Machine Learning',
      icon: Brain,
      desc: 'Dự báo giá tham chiếu không rò rỉ dữ liệu (Out-of-Fold) để phát hiện máy có giá trị hời (Value Gap).',
      detail: 'Huấn luyện 6 mô hình hồi quy (Gradient Boosting, CatBoost, LightGBM, Random Forest, Ridge, Linear Regression). Điểm định giá được dùng để nhận diện mức độ tiết kiệm thực tế (Value for Money) của từng sản phẩm.',
    },
    {
      id: 6,
      name: 'Tổng Hợp & Đề Xuất DSS',
      tag: 'Final Ranking',
      icon: Award,
      desc: 'Kết hợp điểm TOPSIS (85%) và điểm định giá ML (15%) kèm giải trình minh bạch quyết định.',
      detail: 'Hệ thống xuất bảng xếp hạng tối ưu kèm lý do giải thích bằng ngôn ngữ tự nhiên: chỉ rõ ưu thế cạnh tranh lớn nhất, điểm đánh đổi phần cứng và cảnh báo nếu có linh kiện chưa qua kiểm chứng.',
    },
  ];

  return (
    <div className="space-y-6 pb-12 animate-in fade-in duration-200">
      
      {/* Title */}
      <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-2xs">
        <div className="flex items-center gap-2">
          <span className="p-1.5 rounded-lg bg-indigo-100 text-indigo-700">
            <BookOpen className="w-5 h-5" />
          </span>
          <h1 className="text-lg font-black text-slate-900">
            Phương Pháp Luận Khoa Học Của Hệ Hỗ Trợ Ra Quyết Định (DSS)
          </h1>
        </div>
        <p className="mt-1 text-xs text-slate-500 leading-relaxed max-w-3xl">
          Quy trình ra quyết định đa tiêu chí (MCDM) kết hợp giữa phương pháp phân tích thứ bậc AHP, thuật toán tối ưu TOPSIS và mô hình hồi quy học máy định giá tham chiếu OOF.
        </p>
      </div>

      {/* 6-Step Pipeline Grid */}
      <div>
        <h2 className="text-xs font-bold text-slate-800 mb-3 uppercase tracking-wider">
          Quy trình xử lý dữ liệu & Ra quyết định 6 bước:
        </h2>
        
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-6 gap-3">
          {steps.map((st) => {
            const Icon = st.icon;
            const isSelected = selectedStep === st.id;
            return (
              <div
                key={st.id}
                onClick={() => setSelectedStep(st.id)}
                className={`p-3.5 rounded-2xl border-2 transition cursor-pointer flex flex-col justify-between ${
                  isSelected
                    ? 'border-indigo-600 bg-indigo-50/70 shadow-md ring-2 ring-indigo-200'
                    : 'border-slate-200 bg-white hover:border-slate-300 hover:bg-slate-50'
                }`}
              >
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-[10px] font-black px-1.5 py-0.5 rounded bg-indigo-100 text-indigo-700">
                      BƯỚC {st.id}
                    </span>
                    <Icon className={`w-4 h-4 ${isSelected ? 'text-indigo-600' : 'text-slate-400'}`} />
                  </div>
                  <h3 className={`text-xs font-bold mb-1 ${isSelected ? 'text-indigo-950' : 'text-slate-900'}`}>
                    {st.name}
                  </h3>
                  <p className="text-[10px] text-slate-500 line-clamp-3 leading-snug">
                    {st.desc}
                  </p>
                </div>
                <div className="mt-3 pt-2 border-t border-slate-100 flex items-center justify-between text-[10px] font-bold text-indigo-600">
                  <span>{st.tag}</span>
                  <ArrowRight className="w-3 h-3" />
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Step Detail Card */}
      {selectedStep && (
        <div className="rounded-2xl border border-indigo-200 bg-white p-5 shadow-2xs">
          <div className="flex items-center gap-2 mb-2">
            <span className="flex h-6 w-6 items-center justify-center rounded-full bg-indigo-600 text-white font-bold text-xs">
              {selectedStep}
            </span>
            <h3 className="text-sm font-bold text-slate-900">
              Chi tiết Bước {selectedStep}: {steps.find(s => s.id === selectedStep)?.name}
            </h3>
          </div>
          <p className="text-xs text-slate-600 leading-relaxed">
            {steps.find(s => s.id === selectedStep)?.detail}
          </p>
        </div>
      )}

      {/* Mathematical Foundations */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        
        {/* TOPSIS Math */}
        <div className="lg:col-span-6 rounded-2xl border border-slate-200 bg-white p-5 shadow-2xs space-y-3">
          <h3 className="text-xs font-bold text-slate-900 flex items-center gap-2">
            <Calculator className="w-4 h-4 text-indigo-600" />
            <span>Công Thức Toán Học Thuật Toán TOPSIS</span>
          </h3>

          <div className="space-y-3 text-xs text-slate-600">
            <div className="bg-slate-50 p-3 rounded-xl border border-slate-100 space-y-1">
              <span className="font-bold text-slate-800 block text-[11px]">1. Chuẩn hóa vector ma trận quyết định:</span>
              <p className="font-mono text-[11px] text-indigo-700 bg-white p-1.5 rounded border border-slate-200 text-center">
                r_ij = x_ij / √(∑ x_kj²)
              </p>
            </div>

            <div className="bg-slate-50 p-3 rounded-xl border border-slate-100 space-y-1">
              <span className="font-bold text-slate-800 block text-[11px]">2. Nhân trọng số AHP (w_j):</span>
              <p className="font-mono text-[11px] text-indigo-700 bg-white p-1.5 rounded border border-slate-200 text-center">
                v_ij = w_j × r_ij
              </p>
            </div>

            <div className="bg-slate-50 p-3 rounded-xl border border-slate-100 space-y-1">
              <span className="font-bold text-slate-800 block text-[11px]">3. Khoảng cách Euclid tới phương án lý tưởng & tồi nhất:</span>
              <p className="font-mono text-[11px] text-indigo-700 bg-white p-1.5 rounded border border-slate-200 text-center">
                S_i⁺ = √(∑(v_ij - v_j⁺)²), &nbsp; S_i⁻ = √(∑(v_ij - v_j⁻)²)
              </p>
            </div>

            <div className="bg-slate-50 p-3 rounded-xl border border-slate-100 space-y-1">
              <span className="font-bold text-slate-800 block text-[11px]">4. Điểm số tương đối C_i (Fit Score):</span>
              <p className="font-mono text-[11px] text-indigo-700 bg-white p-1.5 rounded border border-slate-200 text-center font-bold">
                C_i = S_i⁻ / (S_i⁺ + S_i⁻) ∈ [0, 1]
              </p>
            </div>
          </div>
        </div>

        {/* AHP Consistency Ratio & Matrix */}
        <div className="lg:col-span-6 rounded-2xl border border-slate-200 bg-white p-5 shadow-2xs space-y-3">
          <div className="flex items-center justify-between">
            <h3 className="text-xs font-bold text-slate-900 flex items-center gap-2">
              <Scale className="w-4 h-4 text-indigo-600" />
              <span>Kiểm Định Nhất Quán Ma Trận AHP (CR)</span>
            </h3>
            {ahpCr != null && (
              <span className={`text-[11px] font-black px-2.5 py-0.5 rounded-full border ${
                ahpCr < 0.1
                  ? 'bg-emerald-50 text-emerald-800 border-emerald-300'
                  : 'bg-amber-50 text-amber-800 border-amber-300'
              }`}>
                CR = {(ahpCr * 100).toFixed(2)}% {ahpCr < 0.1 ? '(Đạt chuẩn < 10%)' : '(Cảnh báo)'}
              </span>
            )}
          </div>

          <p className="text-[11px] text-slate-500 leading-relaxed">
            Theo giáo trình Thomas Saaty, tỷ số nhất quán CR (Consistency Ratio) phải nhỏ hơn 0.10 để đảm bảo các đánh giá so sánh cặp không mâu thuẫn bắc cầu (transitivity).
          </p>

          {/* Active criteria weights table */}
          <div className="border border-slate-200 rounded-xl overflow-hidden">
            <table className="w-full text-xs">
              <thead className="bg-slate-50 border-b border-slate-200 text-slate-500 font-semibold">
                <tr>
                  <th className="p-2.5 text-left">Tiêu chí đánh giá</th>
                  <th className="p-2.5 text-center">Loại tiêu chí</th>
                  <th className="p-2.5 text-right">Trọng số AHP chuẩn hóa</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {activeCriteria.map(([cname, isBenefit, weight]) => (
                  <tr key={cname} className="hover:bg-slate-50/50">
                    <td className="p-2.5 font-bold text-slate-800">
                      {CRITERIA_LABELS[cname] || cname}
                    </td>
                    <td className="p-2.5 text-center">
                      <span className={`text-[10px] font-bold px-1.5 py-0.5 rounded ${
                        isBenefit ? 'bg-emerald-50 text-emerald-700' : 'bg-rose-50 text-rose-700'
                      }`}>
                        {isBenefit ? 'Càng cao càng tốt' : 'Càng thấp càng tốt (Chi phí)'}
                      </span>
                    </td>
                    <td className="p-2.5 text-right font-black text-indigo-700 font-mono">
                      {(weight * 100).toFixed(1)}%
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Pairwise Matrix display if available */}
          {pairwiseMatrix && pairwiseMatrix.length > 0 && (
            <div className="mt-4 pt-3 border-t border-slate-100">
              <h4 className="text-[11px] font-bold text-slate-700 mb-1.5">
                Ma trận so sánh cặp AHP chuẩn (Saaty Scale 1–9):
              </h4>
              <div className="overflow-x-auto">
                <table className="text-[11px] border-collapse border border-slate-200">
                  <tbody>
                    {pairwiseMatrix.map((row, i) => (
                      <tr key={i}>
                        {row.map((val, j) => (
                          <td key={j} className="border border-slate-200 px-2 py-1 text-center font-mono">
                            {Number(val).toFixed(2)}
                          </td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>

      </div>

    </div>
  );
}
