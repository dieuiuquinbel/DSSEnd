import React, { useEffect } from 'react';
import { Heart, X } from 'lucide-react';

export default function Toast({ message, type = 'favorite', onClose, onAction, actionLabel }) {
  useEffect(() => {
    const timer = setTimeout(() => {
      onClose();
    }, 3500);
    return () => clearTimeout(timer);
  }, [onClose]);

  return (
    <div className="fixed bottom-6 right-6 z-50 flex items-center gap-3 rounded-2xl border border-slate-200 bg-white/95 px-4 py-3 shadow-2xl backdrop-blur-md animate-in slide-in-from-bottom-5 duration-200 max-w-md">
      <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-xl bg-rose-50 text-rose-600">
        <Heart className="h-4 w-4 fill-rose-600" />
      </div>

      <div className="min-w-0 flex-1">
        <p className="text-xs font-bold text-slate-900 line-clamp-1">{message}</p>
        <p className="text-[10px] text-slate-400">Đã cập nhật danh sách quan tâm</p>
      </div>

      {actionLabel && (
        <button
          type="button"
          onClick={onAction}
          className="shrink-0 text-xs font-bold text-indigo-600 hover:text-indigo-800 cursor-pointer underline"
        >
          {actionLabel}
        </button>
      )}

      <button
        type="button"
        onClick={onClose}
        className="rounded-lg p-1 text-slate-400 hover:text-slate-600 cursor-pointer"
      >
        <X className="h-3.5 w-3.5" />
      </button>
    </div>
  );
}
