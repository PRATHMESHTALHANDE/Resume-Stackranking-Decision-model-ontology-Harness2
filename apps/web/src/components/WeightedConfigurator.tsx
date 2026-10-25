import React from 'react';
import { Sliders, RotateCcw } from 'lucide-react';

interface WeightedConfiguratorProps {
  criteriaPct: number;
  experiencePct: number;
  onChange: (criteriaPct: number, experiencePct: number) => void;
}

export const WeightedConfigurator: React.FC<WeightedConfiguratorProps> = ({
  criteriaPct,
  experiencePct,
  onChange,
}) => {
  const handleCriteriaChange = (val: number) => {
    const clamped = Math.max(5, Math.min(95, val));
    onChange(clamped, 100 - clamped);
  };

  const handleExperienceChange = (val: number) => {
    const clamped = Math.max(5, Math.min(95, val));
    onChange(100 - clamped, clamped);
  };

  const applyPreset = (crit: number, exp: number) => {
    onChange(crit, exp);
  };

  return (
    <div className="p-4 rounded-xl bg-[#232731] border border-emerald-500/30 shadow-inner space-y-3 animate-fade-in">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
        <div className="flex items-center gap-2">
          <Sliders className="w-4 h-4 text-emerald-400" />
          <span className="text-xs font-semibold text-white tracking-wide">
            Weighted Model Policy Configuration
          </span>
          <span className="text-[11px] px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 font-mono">
            Total: 100%
          </span>
        </div>

        {/* Quick Presets */}
        <div className="flex items-center gap-1.5 self-start sm:self-auto">
          <span className="text-[10px] text-slate-400">Presets:</span>
          <button
            type="button"
            onClick={() => applyPreset(80, 20)}
            className={`px-2 py-0.5 text-[10px] rounded-lg transition-colors border ${
              criteriaPct === 80
                ? 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40 font-semibold'
                : 'bg-slate-800 text-slate-300 border-slate-700 hover:bg-slate-700'
            }`}
          >
            80/20 Standard
          </button>
          <button
            type="button"
            onClick={() => applyPreset(60, 40)}
            className={`px-2 py-0.5 text-[10px] rounded-lg transition-colors border ${
              criteriaPct === 60
                ? 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40 font-semibold'
                : 'bg-slate-800 text-slate-300 border-slate-700 hover:bg-slate-700'
            }`}
          >
            60/40 Tenure Heavy
          </button>
          <button
            type="button"
            onClick={() => applyPreset(95, 5)}
            className={`px-2 py-0.5 text-[10px] rounded-lg transition-colors border ${
              criteriaPct === 95
                ? 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40 font-semibold'
                : 'bg-slate-800 text-slate-300 border-slate-700 hover:bg-slate-700'
            }`}
          >
            95/5 Skills Only
          </button>
          <button
            type="button"
            onClick={() => applyPreset(80, 20)}
            className="p-1 text-slate-400 hover:text-slate-200 rounded-lg hover:bg-slate-800 transition-colors"
            title="Reset to 80/20 Default"
          >
            <RotateCcw className="w-3 h-3" />
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-1">
        {/* Criteria Weight Slider */}
        <div className="space-y-1.5 p-3 rounded-lg bg-slate-900/60 border border-slate-800">
          <div className="flex items-center justify-between text-xs">
            <span className="text-slate-300 font-medium">Criteria Skill Match:</span>
            <span className="font-mono text-emerald-400 font-bold text-sm">{criteriaPct}%</span>
          </div>
          <input
            type="range"
            min="5"
            max="95"
            step="5"
            value={criteriaPct}
            onChange={(e) => handleCriteriaChange(Number(e.target.value))}
            className="w-full accent-emerald-500 cursor-pointer h-1.5 bg-slate-700 rounded-lg"
          />
          <p className="text-[10px] text-slate-400">
            Relative weight assigned to fulfilling mandatory and preferred technical criteria.
          </p>
        </div>

        {/* Experience Weight Slider */}
        <div className="space-y-1.5 p-3 rounded-lg bg-slate-900/60 border border-slate-800">
          <div className="flex items-center justify-between text-xs">
            <span className="text-slate-300 font-medium">Experience Tenure:</span>
            <span className="font-mono text-indigo-400 font-bold text-sm">{experiencePct}%</span>
          </div>
          <input
            type="range"
            min="5"
            max="95"
            step="5"
            value={experiencePct}
            onChange={(e) => handleExperienceChange(Number(e.target.value))}
            className="w-full accent-indigo-500 cursor-pointer h-1.5 bg-slate-700 rounded-lg"
          />
          <p className="text-[10px] text-slate-400">
            Relative weight assigned to candidate total tenure against minimum experience target.
          </p>
        </div>
      </div>
    </div>
  );
};
