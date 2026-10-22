import React, { useState, useEffect } from 'react';

/**
 * CircularScore renders a circular progress gauge representing the DSS/TOPSIS fit score.
 * Features an animated number counter.
 */
export default function CircularScore({ score = 0, size = 'md', label = '', showPercent = true }) {
  const normalizedScore = Math.max(0, Math.min(100, Math.round(score)));
  const [displayScore, setDisplayScore] = useState(0);

  // Animated counter effect
  useEffect(() => {
    let start = 0;
    const duration = 600; // ms
    const stepTime = 20; // ms
    const steps = duration / stepTime;
    const increment = normalizedScore / steps;

    const timer = setInterval(() => {
      start += increment;
      if (start >= normalizedScore) {
        setDisplayScore(normalizedScore);
        clearInterval(timer);
      } else {
        setDisplayScore(Math.round(start));
      }
    }, stepTime);

    return () => clearInterval(timer);
  }, [normalizedScore]);

  // Size configurations
  const config = {
    sm: { dimension: 40, stroke: 3.5, textClass: 'text-[11px] font-black' },
    md: { dimension: 48, stroke: 4, textClass: 'text-xs font-black' },
    lg: { dimension: 64, stroke: 5, textClass: 'text-base font-black' }
  }[size] || { dimension: 48, stroke: 4, textClass: 'text-xs font-black' };

  const radius = (config.dimension - config.stroke * 2) / 2;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (normalizedScore / 100) * circumference;

  // Color gradient based on score tier
  let colorClass = 'text-emerald-600 stroke-emerald-500';
  if (normalizedScore < 60) {
    colorClass = 'text-slate-600 stroke-slate-400';
  } else if (normalizedScore < 75) {
    colorClass = 'text-indigo-600 stroke-indigo-500';
  }

  return (
    <div className="flex flex-col items-center justify-center">
      <div 
        className="relative flex items-center justify-center select-none"
        style={{ width: config.dimension, height: config.dimension }}
        title={`Điểm phù hợp DSS: ${normalizedScore}/100`}
      >
        <svg
          className="w-full h-full -rotate-90 transform"
          viewBox={`0 0 ${config.dimension} ${config.dimension}`}
        >
          {/* Track circle */}
          <circle
            cx={config.dimension / 2}
            cy={config.dimension / 2}
            r={radius}
            className="stroke-slate-100 dark:stroke-slate-700 text-slate-100"
            strokeWidth={config.stroke}
            fill="transparent"
          />
          {/* Progress circle */}
          <circle
            cx={config.dimension / 2}
            cy={config.dimension / 2}
            r={radius}
            className={`${colorClass} transition-all duration-700 ease-out`}
            strokeWidth={config.stroke}
            strokeDasharray={circumference}
            strokeDashoffset={offset}
            strokeLinecap="round"
            fill="transparent"
          />
        </svg>
        <div className={`absolute inset-0 flex items-center justify-center ${config.textClass} text-slate-900 dark:text-white font-mono`}>
          {displayScore}
          {showPercent && <span className="text-[9px] font-bold text-slate-400 ml-0.5">%</span>}
        </div>
      </div>
      {label && <span className="text-[10px] font-bold text-slate-500 dark:text-slate-400 mt-1">{label}</span>}
    </div>
  );
}
