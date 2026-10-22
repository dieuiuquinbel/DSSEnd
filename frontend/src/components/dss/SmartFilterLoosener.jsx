import React from 'react';
import { Lightbulb } from 'lucide-react';
import { formatVnd } from '../../utils/formatters';

export default function SmartFilterLoosener({
  resultCount = 0,
  maxBudget = 0,
  presetKey = '',
  requireRj45 = false,
  requireThunderbolt = false,
  requireRamUpgrade = false,
  requireTypeCCharge = false,
  brand = 'Tất cả',
  onLoosenBudget,
  onResetHardwareFilter,
}) {
  // Only show when result count is 0 or 1 or 2
  if (resultCount > 2) return null;

  const suggestions = [];

  // 1. Budget loosening
  if (Number(maxBudget) < 50000000) {
    const higherBudget = Math.min(50000000, Number(maxBudget) + 3000000);
    suggestions.push({
      id: 'budget_plus_3m',
      icon: '💰',
      label: `Nới ngân sách lên ${formatVnd(higherBudget)}`,
      action: () => onLoosenBudget(higherBudget),
    });
  }

  // 2. Hardware constraints loosening
  if (requireRj45) {
    suggestions.push({
      id: 'drop_rj45',
      icon: '🌐',
      label: 'Bỏ lọc Cổng mạng LAN (nhiều máy mỏng nhẹ không có)',
      action: () => onResetHardwareFilter('rj45'),
    });
  }

  if (requireThunderbolt) {
    suggestions.push({
      id: 'drop_tb',
      icon: '⚡',
      label: 'Bỏ lọc Thunderbolt / USB4',
      action: () => onResetHardwareFilter('thunderbolt'),
    });
  }

  if (requireRamUpgrade) {
    suggestions.push({
      id: 'drop_ram_upgrade',
      icon: '🧠',
      label: 'Bỏ lọc Khả năng nâng cấp RAM',
      action: () => onResetHardwareFilter('ram_upgrade'),
    });
  }

  if (requireTypeCCharge) {
    suggestions.push({
      id: 'drop_type_c',
      icon: '🔌',
      label: 'Bỏ lọc Sạc USB-C',
      action: () => onResetHardwareFilter('type_c'),
    });
  }

  if (brand !== 'Tất cả') {
    suggestions.push({
      id: 'drop_brand',
      icon: '🏷️',
      label: 'Xem tất cả các hãng (bỏ lọc hãng)',
      action: () => onResetHardwareFilter('brand'),
    });
  }

  if (presetKey === 'gaming' && Number(maxBudget) < 22000000) {
    suggestions.push({
      id: 'gaming_preset_boost',
      icon: '🎮',
      label: 'Gaming chuẩn cần từ 22 - 25 triệu',
      action: () => onLoosenBudget(25000000),
    });
  }

  return (
    <div className="mb-6 rounded-2xl border border-indigo-200 bg-indigo-50/70 p-4 shadow-2xs">
      <div className="flex items-start gap-3">
        <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-xl bg-indigo-600 text-white font-bold">
          <Lightbulb className="w-4 h-4" />
        </div>
        <div className="min-w-0 flex-1">
          <h4 className="text-xs font-bold text-indigo-950">
            {resultCount === 0
              ? 'Không có laptop thỏa mãn toàn bộ tiêu chí khắt khe.'
              : `Chỉ có ${resultCount} máy phù hợp. Bạn có muốn mở rộng điều kiện?`}
          </h4>
          <p className="mt-0.5 text-[11px] text-indigo-800 leading-relaxed">
            Hệ thống nhận diện một số ràng buộc phần cứng hoặc ngân sách đang giới hạn tập ứng viên. Bấm gợi ý nhanh bên dưới để xem thêm máy:
          </p>

          <div className="mt-3 flex flex-wrap gap-2">
            {suggestions.map((item) => (
              <button
                key={item.id}
                type="button"
                onClick={item.action}
                className="inline-flex items-center gap-1.5 rounded-xl border border-indigo-300 bg-white px-3 py-1.5 text-xs font-bold text-indigo-900 shadow-2xs hover:bg-indigo-600 hover:text-white hover:border-indigo-600 transition cursor-pointer"
              >
                <span>{item.icon}</span>
                <span>{item.label}</span>
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
