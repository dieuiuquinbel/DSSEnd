import React from 'react';
import { Search, ShieldCheck, Heart, Sparkles, BookOpen, BarChart3, Sliders, X } from 'lucide-react';

export default function Header({
  searchQuery,
  onChangeSearchQuery,
  currentPage,
  onNavigate,
  favoritesCount = 0,
  onOpenFavorites,
  onSelectPrompt,
}) {
  const samplePrompts = [
    'Laptop sinh viên dưới 15tr',
    'Gaming RTX 4050 144Hz',
    'Ultrabook mỏng nhẹ RAM 16GB',
    'Lập trình Core i7 / Ryzen 7',
  ];

  return (
    <header className="sticky top-0 z-40 border-b border-slate-200 bg-white/95 backdrop-blur-md">
      <div className="max-w-[1440px] mx-auto px-4 lg:px-6">
        
        {/* Main Header Bar */}
        <div className="py-3 flex items-center justify-between gap-4">
          
          {/* Logo */}
          <button
            type="button"
            onClick={() => onNavigate('recommend')}
            className="flex items-center gap-2.5 cursor-pointer text-left focus:outline-none"
          >
            <div className="w-9 h-9 rounded-xl bg-indigo-600 text-white flex items-center justify-center font-black shadow-xs">
              <span className="text-lg">💻</span>
            </div>
            <div>
              <span className="text-base font-black tracking-tight text-slate-900 block leading-tight">
                Laptop<span className="text-indigo-600">DSS</span>
              </span>
              <span className="text-[10px] font-bold text-slate-400 block tracking-normal">
                Hệ Hỗ Trợ Ra Quyết Định
              </span>
            </div>
          </button>

          {/* Large Search Box with suggestions */}
          <div className="flex-1 max-w-xl hidden md:block">
            <div className="relative">
              <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
              <input
                type="text"
                placeholder="Tìm tên máy, chip CPU, card GPU (Ví dụ: LOQ 15, RTX 4060, Core i5...)"
                value={searchQuery}
                onChange={(e) => onChangeSearchQuery(e.target.value)}
                className="w-full pl-10 pr-9 py-2 bg-slate-100/80 hover:bg-slate-100 text-slate-900 placeholder:text-slate-400 rounded-xl border border-slate-200 text-xs font-medium focus:outline-none focus:border-indigo-600 focus:bg-white transition-all shadow-2xs"
              />
              {searchQuery && (
                <button
                  type="button"
                  onClick={() => onChangeSearchQuery('')}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600"
                >
                  <X className="w-3.5 h-3.5" />
                </button>
              )}
            </div>
          </div>

          {/* Top Right Navigation & Favorites */}
          <div className="flex items-center gap-2">
            
            {/* Database indicator */}
            <div className="hidden lg:flex items-center gap-1.5 text-xs text-slate-500 bg-slate-50 border border-slate-200 px-3 py-1.5 rounded-xl font-medium">
              <ShieldCheck className="w-4 h-4 text-emerald-600" />
              <span>513 cấu hình chuẩn hóa</span>
            </div>

            {/* Favorites Button */}
            <button
              type="button"
              onClick={onOpenFavorites}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl border border-slate-200 hover:border-rose-300 hover:bg-rose-50/50 text-slate-700 hover:text-rose-600 text-xs font-bold transition cursor-pointer"
            >
              <Heart className={`w-3.5 h-3.5 ${favoritesCount > 0 ? 'text-rose-500 fill-rose-500' : ''}`} />
              <span className="hidden sm:inline">Đã lưu</span>
              {favoritesCount > 0 && (
                <span className="w-4 h-4 rounded-full bg-rose-500 text-white text-[10px] flex items-center justify-center font-extrabold">
                  {favoritesCount}
                </span>
              )}
            </button>
          </div>

        </div>

        {/* Secondary Bar: Navigation Tabs & Sample Prompts */}
        <div className="py-2 border-t border-slate-100 flex flex-col sm:flex-row sm:items-center justify-between gap-2">
          
          {/* Navigation Links */}
          <nav className="flex items-center gap-1 overflow-x-auto pb-1 sm:pb-0" aria-label="Menu chính">
            <button
              onClick={() => onNavigate('recommend')}
              className={`px-3 py-1.5 rounded-lg text-xs font-bold transition flex items-center gap-1.5 cursor-pointer shrink-0 ${
                currentPage === 'recommend' || currentPage === 'detail'
                  ? 'bg-indigo-600 text-white shadow-2xs'
                  : 'text-slate-600 hover:bg-slate-100 hover:text-slate-900'
              }`}
            >
              <Sliders className="w-3.5 h-3.5" />
              <span>Gợi ý & Bộ lọc</span>
            </button>

            <button
              onClick={() => onNavigate('analysis')}
              className={`px-3 py-1.5 rounded-lg text-xs font-bold transition flex items-center gap-1.5 cursor-pointer shrink-0 ${
                currentPage === 'analysis'
                  ? 'bg-indigo-600 text-white shadow-2xs'
                  : 'text-slate-600 hover:bg-slate-100 hover:text-slate-900'
              }`}
            >
              <BarChart3 className="w-3.5 h-3.5" />
              <span>Phân tích dữ liệu</span>
            </button>

            <button
              onClick={() => onNavigate('methodology')}
              className={`px-3 py-1.5 rounded-lg text-xs font-bold transition flex items-center gap-1.5 cursor-pointer shrink-0 ${
                currentPage === 'methodology'
                  ? 'bg-indigo-600 text-white shadow-2xs'
                  : 'text-slate-600 hover:bg-slate-100 hover:text-slate-900'
              }`}
            >
              <BookOpen className="w-3.5 h-3.5" />
              <span>Phương pháp DSS</span>
            </button>
          </nav>

          {/* Sample Prompts Pills */}
          <div className="flex items-center gap-1.5 overflow-x-auto text-[11px]">
            <span className="text-slate-400 font-medium shrink-0 flex items-center gap-1">
              <Sparkles className="w-3 h-3 text-indigo-500" />
              <span>Gợi ý:</span>
            </span>
            {samplePrompts.map(prompt => (
              <button
                key={prompt}
                type="button"
                onClick={() => onSelectPrompt(prompt)}
                className="shrink-0 px-2 py-0.5 rounded-md bg-slate-50 hover:bg-indigo-50 text-slate-600 hover:text-indigo-600 border border-slate-200/80 transition cursor-pointer"
              >
                {prompt}
              </button>
            ))}
          </div>

        </div>

      </div>
    </header>
  );
}
