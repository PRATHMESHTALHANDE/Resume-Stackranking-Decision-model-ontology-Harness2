import { X, Quote, AlertTriangle, CheckCircle2, Bookmark } from 'lucide-react';
import type { CandidateProfile, RankingResult } from '../types';

interface EvidenceDrawerProps {
  candidate: CandidateProfile | null;
  ranking: RankingResult | null;
  onClose: () => void;
}

export const EvidenceDrawer: React.FC<EvidenceDrawerProps> = ({ candidate, ranking, onClose }) => {
  if (!candidate) return null;

  return (
    <div className="fixed inset-y-0 right-0 z-50 w-full max-w-xl bg-[#E8ECF2] dark:bg-[#1A1E24] shadow-2xl p-6 flex flex-col gap-5 overflow-y-auto border-l border-slate-300 dark:border-slate-800 transition-all">
      {/* Header */}
      <div className="flex items-center justify-between pb-3 border-b border-slate-300 dark:border-slate-700">
        <div>
          <span className="text-xs uppercase font-bold tracking-wider text-blue-600 dark:text-blue-400">
            Verbatim Evidence & Traceability
          </span>
          <h2 className="text-lg font-bold text-slate-800 dark:text-slate-100">
            Candidate: {candidate.candidate_id}
          </h2>
        </div>
        <button
          onClick={onClose}
          className="neu-button p-2 text-slate-500 hover:text-slate-800 dark:hover:text-slate-200"
          aria-label="Close drawer"
        >
          <X className="w-5 h-5" />
        </button>
      </div>

      {/* Ranking Summary Badge */}
      {ranking && (
        <div className="neu-inset p-4 rounded-xl flex items-center justify-between">
          <div>
            <div className="text-xs text-slate-500 dark:text-slate-400 font-medium">Model Decision Score</div>
            <div className="text-xl font-black text-blue-600 dark:text-blue-400">
              {(ranking.score * 100).toFixed(1)}% <span className="text-xs font-normal text-slate-500">({ranking.model_name})</span>
            </div>
          </div>
          <div className="text-right">
            <div className="text-xs text-slate-500 dark:text-slate-400 font-medium">Rank Queue Position</div>
            <div className="text-lg font-bold text-slate-800 dark:text-slate-200">#{ranking.rank}</div>
          </div>
        </div>
      )}

      {/* Uncertainty & Ambiguity Markers */}
      {candidate.uncertainty_flags.length > 0 && (
        <div className="flex flex-col gap-2">
          <h3 className="text-xs font-bold uppercase tracking-wider text-amber-700 dark:text-amber-400 flex items-center gap-1.5">
            <AlertTriangle className="w-3.5 h-3.5" /> Explicit Uncertainty Warnings
          </h3>
          <div className="flex flex-col gap-1.5">
            {candidate.uncertainty_flags.map((u, i) => (
              <div key={i} className="neu-raised-sm px-3 py-2 text-xs text-amber-800 dark:text-amber-300 border-l-2 border-amber-500">
                {u}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Verbatim Skills with Citations */}
      <div className="flex flex-col gap-3">
        <h3 className="text-xs font-bold uppercase tracking-wider text-slate-600 dark:text-slate-400 flex items-center gap-1.5">
          <CheckCircle2 className="w-3.5 h-3.5 text-emerald-500" /> Extracted Skills & Source Provenance
        </h3>
        <div className="flex flex-col gap-2.5">
          {candidate.skills.map((s, idx) => (
            <div key={idx} className="neu-raised p-3.5 rounded-lg flex flex-col gap-2">
              <div className="flex items-center justify-between">
                <span className="font-semibold text-sm text-slate-800 dark:text-slate-100">
                  {s.original_text}
                </span>
                <span className="text-[11px] px-2 py-0.5 rounded-full font-mono bg-blue-100 dark:bg-blue-900/40 text-blue-700 dark:text-blue-300">
                  {s.mapping_method}
                </span>
              </div>

              {s.evidence ? (
                <div className="neu-inset p-2.5 rounded-md flex items-start gap-2 text-xs text-slate-600 dark:text-slate-300">
                  <Quote className="w-3.5 h-3.5 text-blue-500 shrink-0 mt-0.5" />
                  <div className="flex flex-col gap-1">
                    <span className="italic font-serif">"{s.evidence.verbatim_snippet}"</span>
                    <span className="text-[10px] text-slate-400 font-mono">
                      Page: {s.evidence.page_number ?? 1} • Section: {s.evidence.section_name ?? 'Skills'} • Method: {s.evidence.extraction_method}
                    </span>
                  </div>
                </div>
              ) : (
                <div className="text-[11px] text-slate-400 italic">No verbatim excerpt attached</div>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Candidate Summary */}
      {candidate.summary && (
        <div className="neu-raised p-4 rounded-xl flex flex-col gap-2">
          <h3 className="text-xs font-bold uppercase tracking-wider text-slate-600 dark:text-slate-400 flex items-center gap-1.5">
            <Bookmark className="w-3.5 h-3.5 text-indigo-500" /> Extracted Summary
          </h3>
          <p className="text-xs leading-relaxed text-slate-700 dark:text-slate-300 italic">
            "{candidate.summary}"
          </p>
        </div>
      )}
    </div>
  );
};
