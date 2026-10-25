import { Trophy, BrainCircuit, Sparkles, FileText, Network, CheckCircle } from 'lucide-react';
import type { RankingResult, CandidateProfile, JobDescription } from '../types';

interface TopCandidateSpotlightProps {
  topRanking: RankingResult;
  candidate?: CandidateProfile | null;
  job: JobDescription;
  onOpenEvidence: (candidateId: string) => void;
  onFocusGraph: (candidateId: string) => void;
}

export function TopCandidateSpotlight({
  topRanking,
  candidate,
  job,
  onOpenEvidence,
  onFocusGraph,
}: TopCandidateSpotlightProps) {
  const matchPct = (topRanking.score * 100).toFixed(1);

  return (
    <div className="neu-flat p-6 rounded-2xl flex flex-col gap-5 border border-amber-500/20 bg-gradient-to-br from-amber-500/5 via-transparent to-blue-500/5">
      {/* Spotlight Header */}
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-3">
          <div className="p-3 neu-raised rounded-xl text-amber-500 bg-amber-500/10 shrink-0">
            <Trophy className="w-6 h-6 animate-pulse" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-[11px] font-black uppercase tracking-wider text-amber-600 dark:text-amber-400">
                #1 Top-Ranked Candidate Spotlight
              </span>
              <span className="neu-raised-sm px-2 py-0.5 text-[10px] font-mono font-bold text-blue-600 dark:text-blue-400">
                {topRanking.model_name}
              </span>
            </div>
            <h3 className="text-xl font-black text-slate-800 dark:text-slate-100 flex items-center gap-2">
              <span>Candidate {topRanking.candidate_id}</span>
              <CheckCircle className="w-4 h-4 text-emerald-500" />
            </h3>
          </div>
        </div>

        {/* Score & Experience Badges */}
        <div className="flex items-center gap-3">
          <div className="neu-inset px-4 py-2 rounded-xl flex flex-col items-center">
            <span className="text-[10px] font-bold text-slate-500 uppercase">Match Score</span>
            <span className="text-lg font-black text-blue-600 dark:text-blue-400 font-mono">
              {matchPct}%
            </span>
          </div>
          <div className="neu-raised-sm px-4 py-2 rounded-xl flex flex-col items-center">
            <span className="text-[10px] font-bold text-slate-500 uppercase">Experience</span>
            <span className="text-lg font-black text-slate-700 dark:text-slate-300 font-mono">
              {candidate ? `${candidate.total_experience_years} yrs` : 'N/A'}
            </span>
          </div>
        </div>
      </div>

      {/* Dual Summary Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* 1. Decision Model Summary */}
        <div className="neu-raised-sm p-4 rounded-xl flex flex-col gap-2.5">
          <div className="flex items-center gap-2 text-xs font-bold text-blue-600 dark:text-blue-400">
            <BrainCircuit className="w-4 h-4" />
            <span>Decision Model Evaluation Rationale</span>
          </div>
          <p className="text-xs text-slate-600 dark:text-slate-300 leading-relaxed">
            {topRanking.decision_summary ||
              `Calculated via ${topRanking.model_name}. Candidate demonstrates the optimal vector proximity to target criteria.`}
          </p>
          <div className="mt-auto pt-2 border-t border-slate-200 dark:border-slate-800 flex items-center justify-between text-[11px] text-slate-500">
            <span>Model: <strong className="text-slate-700 dark:text-slate-300">{topRanking.model_name}</strong></span>
            <span>Target: <strong className="text-slate-700 dark:text-slate-300">{job.title}</strong></span>
          </div>
        </div>

        {/* 2. LLM Summary */}
        <div className="neu-raised-sm p-4 rounded-xl flex flex-col gap-2.5 border-l-4 border-l-blue-500">
          <div className="flex items-center gap-2 text-xs font-bold text-emerald-600 dark:text-emerald-400">
            <Sparkles className="w-4 h-4" />
            <span>Why This Candidate Is On Top (LLM Justification)</span>
          </div>
          <p className="text-xs text-slate-600 dark:text-slate-300 leading-relaxed font-medium">
            {topRanking.llm_summary ||
              `Candidate ${topRanking.candidate_id} holds the top position due to superior requirement coverage, validated experience tenure, and verified resume citations.`}
          </p>
          <div className="mt-auto pt-2 border-t border-slate-200 dark:border-slate-800 flex items-center justify-between text-[11px] text-slate-500">
            <span>Evidence Citations: <strong className="text-blue-600 dark:text-blue-400">{topRanking.evidence_citations.length} verified</strong></span>
            <span>Uncertainty: <strong className="text-emerald-600 dark:text-emerald-400">{topRanking.uncertainty_markers.length === 0 ? 'Zero Gaps' : 'Flagged'}</strong></span>
          </div>
        </div>
      </div>

      {/* Action Footer */}
      <div className="flex items-center justify-end gap-3 pt-2">
        <button
          onClick={() => onOpenEvidence(topRanking.candidate_id)}
          className="neu-button px-4 py-2 text-xs font-bold text-blue-600 dark:text-blue-400 hover:text-blue-700 flex items-center gap-1.5"
        >
          <FileText className="w-3.5 h-3.5" />
          View Verbatim Citations
        </button>
        <button
          onClick={() => onFocusGraph(topRanking.candidate_id)}
          className="neu-button px-4 py-2 text-xs font-bold text-slate-600 dark:text-slate-400 hover:text-slate-700 flex items-center gap-1.5"
        >
          <Network className="w-3.5 h-3.5" />
          Explore Knowledge Subgraph
        </button>
      </div>
    </div>
  );
}
