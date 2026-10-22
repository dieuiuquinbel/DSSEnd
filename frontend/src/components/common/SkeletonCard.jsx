import React from 'react';

export default function SkeletonCard({ count = 6 }) {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
      {Array.from({ length: count }).map((_, idx) => (
        <div
          key={idx}
          className="rounded-2xl border border-slate-200 bg-white p-4 shadow-2xs flex flex-col justify-between animate-pulse"
        >
          <div>
            {/* Top badges */}
            <div className="flex items-center justify-between mb-3">
              <div className="h-5 w-20 bg-slate-200 rounded-md" />
              <div className="h-5 w-8 bg-slate-200 rounded-full" />
            </div>

            {/* Laptop image placeholder */}
            <div className="w-full h-36 bg-slate-100 rounded-xl mb-3 flex items-center justify-center">
              <div className="w-16 h-16 bg-slate-200/80 rounded-lg" />
            </div>

            {/* Spec chips placeholder */}
            <div className="flex flex-wrap gap-1.5 mb-3">
              <div className="h-4 w-16 bg-slate-100 rounded" />
              <div className="h-4 w-14 bg-slate-100 rounded" />
              <div className="h-4 w-14 bg-slate-100 rounded" />
            </div>

            {/* Product title */}
            <div className="h-4 bg-slate-200 rounded w-5/6 mb-2" />
            <div className="h-4 bg-slate-200 rounded w-3/5 mb-4" />

            {/* Price & Value Gap */}
            <div className="flex items-center gap-2 mb-4">
              <div className="h-6 w-28 bg-slate-200 rounded" />
              <div className="h-5 w-20 bg-emerald-100/60 rounded" />
            </div>

            {/* Fit score bar */}
            <div className="h-2 w-full bg-slate-100 rounded-full overflow-hidden mb-4">
              <div className="h-full bg-slate-200 rounded-full w-2/3" />
            </div>
          </div>

          {/* Action buttons */}
          <div className="flex gap-2 pt-2 border-t border-slate-100">
            <div className="h-9 flex-1 bg-slate-100 rounded-xl" />
            <div className="h-9 w-24 bg-slate-100 rounded-xl" />
          </div>
        </div>
      ))}
    </div>
  );
}
