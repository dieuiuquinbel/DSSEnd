import React, { useState } from 'react';
import { X, ExternalLink, Cpu, Monitor, Wifi, Battery, Heart, GitCompare } from 'lucide-react';
import { formatVnd, formatDiscount } from '../../utils/formatters';

export default function LaptopDetailModal({
  laptop,
  onClose,
  isFav = false,
  isInCompare = false,
  onToggleFavorite,
  onToggleCompare,
}) {
  const [activeTab, setActiveTab] = useState('config'); // 'config' | 'screen' | 'ports' | 'design'

  if (!laptop) return null;

  const discount = formatDiscount(laptop.listed_price_vnd, laptop.sale_price_vnd);

  const tabs = [
    { key: 'config', label: 'Cấu hình & Benchmark', icon: Cpu },
    { key: 'screen', label: 'Màn hình hiển thị', icon: Monitor },
    { key: 'ports', label: 'Cổng & Kết nối', icon: Wifi },
    { key: 'design', label: 'Thiết kế & Pin sạc', icon: Battery },
  ];

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/50 backdrop-blur-xs p-4 overflow-y-auto">
      <div className="w-full max-w-4xl rounded-3xl bg-white shadow-2xl border border-slate-200 overflow-hidden flex flex-col max-h-[92vh] animate-in zoom-in-95 duration-150">
        
        {/* Header */}
        <div className="px-6 py-4 border-b border-slate-200 bg-slate-50 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="text-[11px] font-bold px-2 py-0.5 rounded-md bg-indigo-100 text-indigo-700">
              {laptop.source === 'fpt_shop' ? 'FPT Shop' : 'CellphoneS'}
            </span>
            <span className="text-xs text-slate-500">Mã: {laptop.source_product_id}</span>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-xl text-slate-400 hover:text-slate-700 hover:bg-slate-200/60 cursor-pointer transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Product Showcase */}
        <div className="p-6 border-b border-slate-100 bg-white">
          <div className="grid grid-cols-1 md:grid-cols-12 gap-6 items-center">
            
            {/* Image */}
            <div className="md:col-span-4 flex items-center justify-center h-48 bg-slate-50/50 rounded-2xl border border-slate-100 p-3">
              <img
                src={laptop.image_url}
                alt={laptop.product_name_raw}
                className="max-h-full max-w-full object-contain"
                onError={(e) => { e.target.src = '/images/laptop_fallback.png'; }}
              />
            </div>

            {/* Title & Pricing */}
            <div className="md:col-span-8 space-y-3">
              <h2 className="text-base font-bold text-slate-900 leading-snug">
                {laptop.product_name_raw}
              </h2>

              <div className="flex items-baseline gap-3">
                <span className="text-2xl font-black text-indigo-700">
                  {formatVnd(laptop.sale_price_vnd)}
                </span>
                {discount && (
                  <span className="text-xs text-slate-400 line-through">
                    {formatVnd(laptop.listed_price_vnd)}
                  </span>
                )}
                {discount && (
                  <span className="text-xs font-black text-rose-600 bg-rose-50 border border-rose-200 px-2 py-0.5 rounded-md">
                    {discount}
                  </span>
                )}
              </div>

              {/* Action Buttons */}
              <div className="flex flex-wrap items-center gap-2.5 pt-1">
                {laptop.product_url && (
                  <a
                    href={laptop.product_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="px-4 py-2 rounded-xl text-xs font-bold bg-indigo-600 hover:bg-indigo-700 text-white transition flex items-center gap-1.5 cursor-pointer shadow-xs"
                  >
                    <span>Xem tại nơi bán</span>
                    <ExternalLink className="w-3.5 h-3.5" />
                  </a>
                )}

                <button
                  type="button"
                  onClick={() => onToggleCompare(laptop.source_product_id)}
                  className={`px-4 py-2 rounded-xl text-xs font-bold transition flex items-center gap-1.5 cursor-pointer border ${
                    isInCompare
                      ? 'bg-indigo-50 border-indigo-300 text-indigo-700'
                      : 'bg-white border-slate-200 text-slate-700 hover:bg-slate-50'
                  }`}
                >
                  <GitCompare className="w-3.5 h-3.5" />
                  <span>{isInCompare ? 'Đã trong so sánh' : 'Thêm so sánh'}</span>
                </button>

                <button
                  type="button"
                  onClick={() => onToggleFavorite(laptop)}
                  className={`px-3 py-2 rounded-xl text-xs font-bold transition flex items-center gap-1.5 cursor-pointer border ${
                    isFav
                      ? 'bg-rose-50 border-rose-300 text-rose-600'
                      : 'bg-white border-slate-200 text-slate-700 hover:bg-slate-50'
                  }`}
                >
                  <Heart className={`w-3.5 h-3.5 ${isFav ? 'fill-rose-600 text-rose-600' : ''}`} />
                  <span>{isFav ? 'Đã lưu' : 'Lưu máy'}</span>
                </button>
              </div>

            </div>

          </div>
        </div>

        {/* Tab navigation */}
        <div className="px-6 border-b border-slate-200 bg-slate-50 flex gap-2 overflow-x-auto">
          {tabs.map(tab => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.key;
            return (
              <button
                key={tab.key}
                onClick={() => setActiveTab(tab.key)}
                className={`py-3 px-3 text-xs font-bold flex items-center gap-1.5 border-b-2 transition cursor-pointer shrink-0 ${
                  isActive
                    ? 'border-indigo-600 text-indigo-700 bg-white/70'
                    : 'border-transparent text-slate-500 hover:text-slate-900'
                }`}
              >
                <Icon className="w-4 h-4" />
                <span>{tab.label}</span>
              </button>
            );
          })}
        </div>

        {/* Tab Content */}
        <div className="flex-1 p-6 overflow-y-auto">
          
          {/* TAB 1: CẤU HÌNH */}
          {activeTab === 'config' && (
            <div className="divide-y divide-slate-100 text-xs">
              <div className="py-2.5 flex justify-between">
                <span className="text-slate-500">Bộ xử lý (CPU)</span>
                <span className="font-bold text-slate-900">{laptop.cpu_name_normalized || 'Chưa công bố'}</span>
              </div>
              <div className="py-2.5 flex justify-between">
                <span className="text-slate-500">Số nhân / Số luồng</span>
                <span className="font-bold text-slate-900">{laptop.cpu_cores ? `${laptop.cpu_cores} nhân / ${laptop.cpu_threads || laptop.cpu_cores} luồng` : 'Chưa công bố'}</span>
              </div>
              <div className="py-2.5 flex justify-between">
                <span className="text-slate-500">Card đồ họa (GPU)</span>
                <span className="font-bold text-slate-900">{laptop.gpu_name_normalized || 'GPU tích hợp'}</span>
              </div>
              <div className="py-2.5 flex justify-between">
                <span className="text-slate-500">Dung lượng RAM</span>
                <span className="font-bold text-slate-900">{laptop.ram_gb} GB {laptop.ram_type || ''}</span>
              </div>
              <div className="py-2.5 flex justify-between">
                <span className="text-slate-500">Khả năng nâng cấp RAM</span>
                <span className="font-bold text-slate-900">
                  {laptop.ram_slots ? `${laptop.ram_slots} khe (Trống ${laptop.ram_slots_free || 0}) · Tối đa ${laptop.max_ram_gb || laptop.ram_gb} GB` : (laptop.ram_upgradeable === 'true' ? 'Có hỗ trợ' : (laptop.ram_upgradeable === 'false' ? 'Hàn onboard' : 'Chưa công bố'))}
                </span>
              </div>
              <div className="py-2.5 flex justify-between">
                <span className="text-slate-500">Ổ cứng lưu trữ SSD</span>
                <span className="font-bold text-slate-900">{laptop.storage_total_gb ? Math.round(Number(laptop.storage_total_gb)) : '-'} GB {laptop.storage_primary_type || 'SSD NVMe'}</span>
              </div>
              <div className="py-2.5 flex justify-between">
                <span className="text-slate-500">Geekbench 6 Multi-core (CPU)</span>
                <span className="font-bold text-emerald-700">
                  {laptop.cpu_benchmark_multi_core ? `${Number(laptop.cpu_benchmark_multi_core).toLocaleString()} điểm (${laptop.cpu_benchmark_match_level || 'xác thực'})` : 'Chưa có mẫu xác thực'}
                </span>
              </div>
              <div className="py-2.5 flex justify-between">
                <span className="text-slate-500">3DMark Time Spy (GPU)</span>
                <span className="font-bold text-emerald-700">
                  {laptop.gpu_benchmark_time_spy ? `${Number(laptop.gpu_benchmark_time_spy).toLocaleString()} điểm` : 'Dùng GPU tích hợp'}
                </span>
              </div>
            </div>
          )}

          {/* TAB 2: MÀN HÌNH */}
          {activeTab === 'screen' && (
            <div className="divide-y divide-slate-100 text-xs">
              <div className="py-2.5 flex justify-between">
                <span className="text-slate-500">Kích thước màn hình</span>
                <span className="font-bold text-slate-900">{laptop.screen_size_inch ? `${laptop.screen_size_inch}" inch` : 'Chưa công bố'}</span>
              </div>
              <div className="py-2.5 flex justify-between">
                <span className="text-slate-500">Độ phân giải hiển thị</span>
                <span className="font-bold text-slate-900">{laptop.screen_width_px && laptop.screen_height_px ? `${laptop.screen_width_px} x ${laptop.screen_height_px} px` : 'Chưa công bố'}</span>
              </div>
              <div className="py-2.5 flex justify-between">
                <span className="text-slate-500">Công nghệ tấm nền</span>
                <span className="font-bold text-slate-900">{laptop.panel_type || 'Chưa công bố'}</span>
              </div>
              <div className="py-2.5 flex justify-between">
                <span className="text-slate-500">Tần số quét</span>
                <span className="font-bold text-slate-900">{laptop.refresh_rate_hz ? `${laptop.refresh_rate_hz} Hz` : '60 Hz'}</span>
              </div>
              <div className="py-2.5 flex justify-between">
                <span className="text-slate-500">Độ sáng tối đa</span>
                <span className="font-bold text-slate-900">{laptop.brightness_nits ? `${laptop.brightness_nits} nits` : 'Chưa công bố'}</span>
              </div>
            </div>
          )}

          {/* TAB 3: CỔNG & KẾT NỐI */}
          {activeTab === 'ports' && (
            <div className="divide-y divide-slate-100 text-xs">
              <div className="py-2.5 flex justify-between">
                <span className="text-slate-500">Cổng Type-C / Sạc Power Delivery</span>
                <span className="font-bold text-slate-900">{laptop.type_c_charging_present === 'true' ? 'Có hỗ trợ sạc PD' : (laptop.type_c_charging_present === 'false' ? 'Không' : 'Chưa công bố')}</span>
              </div>
              <div className="py-2.5 flex justify-between">
                <span className="text-slate-500">Thunderbolt / USB4</span>
                <span className="font-bold text-slate-900">{laptop.thunderbolt_present === 'true' ? 'Có trang bị' : (laptop.thunderbolt_present === 'false' ? 'Không' : 'Chưa công bố')}</span>
              </div>
              <div className="py-2.5 flex justify-between">
                <span className="text-slate-500">Cổng mạng LAN (RJ45)</span>
                <span className="font-bold text-slate-900">{laptop.lan_present === 'true' ? 'Có (Gigabit Ethernet)' : (laptop.lan_present === 'false' ? 'Không' : 'Chưa công bố')}</span>
              </div>
              <div className="py-2.5 flex justify-between">
                <span className="text-slate-500">Cổng HDMI</span>
                <span className="font-bold text-slate-900">{laptop.hdmi_present === 'true' ? 'Có trang bị' : (laptop.hdmi_present === 'false' ? 'Không' : 'Chưa công bố')}</span>
              </div>
            </div>
          )}

          {/* TAB 4: THIẾT KẾ & PIN */}
          {activeTab === 'design' && (
            <div className="divide-y divide-slate-100 text-xs">
              <div className="py-2.5 flex justify-between">
                <span className="text-slate-500">Trọng lượng máy</span>
                <span className="font-bold text-slate-900">{laptop.weight_kg ? `${laptop.weight_kg} kg` : 'Chưa công bố'}</span>
              </div>
              <div className="py-2.5 flex justify-between">
                <span className="text-slate-500">Độ dày thân máy</span>
                <span className="font-bold text-slate-900">{laptop.thickness_mm ? `${laptop.thickness_mm} mm` : 'Chưa công bố'}</span>
              </div>
              <div className="py-2.5 flex justify-between">
                <span className="text-slate-500">Dung lượng Pin</span>
                <span className="font-bold text-slate-900">{laptop.battery_capacity_wh ? `${laptop.battery_capacity_wh} Wh` : 'Chưa công bố'}</span>
              </div>
              <div className="py-2.5 flex justify-between">
                <span className="text-slate-500">Hệ điều hành</span>
                <span className="font-bold text-slate-900">{laptop.os_name || 'Chưa công bố'}</span>
              </div>
            </div>
          )}

        </div>

      </div>
    </div>
  );
}
