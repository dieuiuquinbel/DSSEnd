import React from 'react';
import { X, Heart, Trash2 } from 'lucide-react';
import { formatVnd } from '../../utils/formatters';

export default function FavoritesModal({
  favorites = [],
  onClose,
  onRemoveFavorite,
  onClearFavorites,
  onOpenDetail,
}) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/50 backdrop-blur-xs p-4 overflow-y-auto">
      <div className="w-full max-w-2xl rounded-3xl bg-white shadow-2xl border border-slate-200 overflow-hidden flex flex-col max-h-[85vh] animate-in zoom-in-95 duration-150">
        
        {/* Header */}
        <div className="px-6 py-4 border-b border-slate-200 bg-slate-50 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Heart className="w-4 h-4 text-rose-500 fill-rose-500" />
            <h3 className="text-sm font-bold text-slate-900">Danh Sách Laptop Đã Lưu ({favorites.length})</h3>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded-lg text-slate-400 hover:text-slate-700 hover:bg-slate-200/60 cursor-pointer"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Body */}
        <div className="p-6 flex-1 overflow-y-auto">
          {favorites.length === 0 ? (
            <div className="text-center py-10 text-slate-400 text-xs">
              <Heart className="w-10 h-10 mx-auto text-slate-200 mb-2" />
              <p className="font-semibold text-slate-600">Bạn chưa lưu chiếc laptop nào.</p>
              <p className="mt-1">Bấm biểu tượng trái tim ♥ trên bất kỳ thẻ máy nào để lưu lại đối chiếu sau.</p>
            </div>
          ) : (
            <div className="divide-y divide-slate-100">
              {favorites.map(laptop => (
                <div key={laptop.source_product_id} className="py-3 flex items-center justify-between gap-3">
                  <div className="flex items-center gap-3 min-w-0 flex-1">
                    <img
                      src={laptop.image_url}
                      alt={laptop.product_name_raw}
                      className="w-12 h-12 object-contain bg-slate-50 rounded-lg p-1 border border-slate-200 shrink-0"
                      onError={(e) => { e.target.src = '/images/laptop_fallback.png'; }}
                    />
                    <div className="min-w-0 flex-1">
                      <h4
                        onClick={() => {
                          onClose();
                          onOpenDetail(laptop);
                        }}
                        className="text-xs font-bold text-slate-900 truncate hover:text-indigo-600 cursor-pointer"
                      >
                        {laptop.product_name_raw}
                      </h4>
                      <div className="text-xs font-black text-indigo-700 mt-0.5">
                        {formatVnd(laptop.sale_price_vnd)}
                      </div>
                    </div>
                  </div>

                  <div className="flex items-center gap-2">
                    <button
                      type="button"
                      onClick={() => {
                        onClose();
                        onOpenDetail(laptop);
                      }}
                      className="p-1.5 rounded-lg text-slate-500 hover:text-indigo-600 hover:bg-indigo-50 text-xs font-semibold"
                    >
                      Chi tiết
                    </button>
                    <button
                      type="button"
                      onClick={() => onRemoveFavorite(laptop)}
                      className="p-1.5 rounded-lg text-slate-400 hover:text-rose-600 hover:bg-rose-50"
                      title="Bỏ lưu"
                    >
                      <Trash2 className="w-3.5 h-3.5" />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Footer */}
        {favorites.length > 0 && (
          <div className="px-6 py-3 border-t border-slate-200 bg-slate-50 flex items-center justify-between">
            <button
              type="button"
              onClick={onClearFavorites}
              className="text-xs font-semibold text-rose-600 hover:text-rose-800 cursor-pointer"
            >
              Xóa tất cả
            </button>
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 rounded-xl text-xs font-bold bg-slate-900 text-white hover:bg-slate-800 cursor-pointer"
            >
              Đóng
            </button>
          </div>
        )}

      </div>
    </div>
  );
}
