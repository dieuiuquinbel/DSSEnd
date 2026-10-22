// Utility formatters and domain constants for LaptopDSS

export const CATEGORIES = [
  { key: 'student_budget', name: 'Sinh viên & Kinh tế', sub: 'Giá rẻ, CPU đủ dùng, nhẹ cân', icon: '📚' },
  { key: 'slim_mobility', name: 'Mỏng nhẹ & Di động', sub: 'Trọng lượng ≤ 1.45kg', icon: '🪶' },
  { key: 'technical_coding', name: 'Kỹ thuật & Lập trình', sub: 'Ưu tiên CPU/RAM trong ngân sách', icon: '💻' },
  { key: 'gaming', name: 'Gaming & Đồ họa nặng', sub: 'GPU rời, 144Hz+, Windows', icon: '🎮' },
];

export const CRITERIA_LABELS = {
  sale_price_vnd: 'Giá bán',
  cpu_benchmark_multi_core: 'CPU đa nhân (Geekbench 6)',
  cpu_benchmark_single_core: 'CPU đơn nhân (Geekbench 6)',
  gpu_benchmark_time_spy: 'GPU đồ họa (3DMark Time Spy)',
  ram_gb: 'Bộ nhớ RAM',
  storage_total_gb: 'Ổ cứng SSD',
  weight_kg: 'Cân nặng',
};

export const CRITERIA_ICONS = {
  sale_price_vnd: '💰',
  cpu_benchmark_multi_core: '⚡',
  cpu_benchmark_single_core: '🎯',
  gpu_benchmark_time_spy: '🎮',
  ram_gb: '🧠',
  storage_total_gb: '💾',
  weight_kg: '⚖️',
};

export const formatVnd = (val) => {
  if (val == null || val === '') return '-';
  try {
    return Number(val).toLocaleString('vi-VN') + '₫';
  } catch {
    return '-';
  }
};

export const formatDiscount = (listed, sale) => {
  if (!listed || !sale) return null;
  const l = Number(listed);
  const s = Number(sale);
  if (l > s && l > 0) {
    return `-${Math.round((1 - s / l) * 100)}%`;
  }
  return null;
};

export const buildSpecsBadgeLine = (item) => {
  if (!item) return '';
  const parts = [];
  let cpu = item.cpu_name_normalized || '';
  ['Intel Core ', 'Intel ', 'AMD Ryzen ', 'AMD ', 'Qualcomm Snapdragon ', 'Apple '].forEach(p => {
    cpu = cpu.replace(p, '');
  });
  if (cpu) parts.push(cpu.slice(0, 16));

  let gpu = item.gpu_name_normalized || '';
  if (gpu && item.gpu_type === 'discrete') {
    parts.push(gpu.replace('NVIDIA GeForce ', '').replace(' GDDR6', '').slice(0, 14));
  }

  if (item.ram_gb) parts.push(`${item.ram_gb}GB RAM`);
  if (item.storage_total_gb) parts.push(`${Math.round(Number(item.storage_total_gb))}GB SSD`);
  if (item.screen_size_inch) parts.push(`${item.screen_size_inch}"`);
  if (item.refresh_rate_hz && Number(item.refresh_rate_hz) > 60) parts.push(`${item.refresh_rate_hz}Hz`);

  return parts.join(' · ');
};

export const formatExplanationText = (text, type = 'advantage') => {
  if (!text) return '';
  let res = text;
  res = res.replace(/sale_price_vnd/g, 'Giá bán siêu tiết kiệm');
  res = res.replace(/cpu_benchmark_single_core/g, 'Sức mạnh vi xử lý CPU đơn nhân');
  res = res.replace(/cpu_benchmark_multi_core/g, 'Hiệu năng CPU đa nhân');
  res = res.replace(/gpu_benchmark_time_spy/g, 'Sức mạnh đồ họa GPU');
  res = res.replace(/ram_gb/g, 'Dung lượng bộ nhớ RAM');
  res = res.replace(/storage_total_gb/g, 'Dung lượng ổ cứng SSD');
  res = res.replace(/weight_kg/g, 'Trọng lượng mỏng nhẹ');

  if (type === 'advantage') {
    res = res.replace(
      /\(đóng góp ([\d.]+)% vào khoảng cách ly khai phương án tệ nhất\)/g,
      '(đóng góp $1% vào ưu thế vượt trội so với các máy khác)'
    );
  } else if (type === 'penalty') {
    res = res.replace(
      /\(chiếm ([\d.]+)% khoảng cách tổn thất so với phương án lý tưởng\)/g,
      '(chiếm $1% lý do máy chưa đạt điểm tối đa khi so với dòng cao cấp)'
    );
  }
  return res;
};
