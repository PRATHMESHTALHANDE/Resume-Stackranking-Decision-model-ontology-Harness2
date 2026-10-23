import { useState } from 'react';
import { BarChart3, Scale, Play, CheckCircle, AlertTriangle } from 'lucide-react';
import { runBenchmark, auditFairness } from '../api';
import type { EvaluationRun } from '../types';

interface FairnessLabProps {
  jobId: string;
}

export const FairnessLab: React.FC<FairnessLabProps> = ({ jobId }) => {
  const [runs, setRuns] = useState<EvaluationRun[]>([]);
  const [loadingBenchmark, setLoadingBenchmark] = useState(false);
  const [fairnessAudit, setFairnessAudit] = useState<any>(null);
  const [loadingAudit, setLoadingAudit] = useState(false);

  const handleRunBenchmark = async () => {
    setLoadingBenchmark(true);
    try {
      const data = await runBenchmark(jobId);
      setRuns(data);
    } catch (err) {
      console.error('Benchmark failed:', err);
    } finally {
      setLoadingBenchmark(false);
    }
  };

  const handleAuditFairness = async () => {
    setLoadingAudit(true);
    try {
      const data = await auditFairness(jobId, 'rrf_hybrid', 3);
      setFairnessAudit(data);
    } catch (err) {
      console.error('Fairness audit failed:', err);
    } finally {
      setLoadingAudit(false);
    }
  };

  return (
    <div className="flex flex-col gap-6">
      {/* Action Row */}
      <div className="neu-flat p-6 flex flex-wrap items-center justify-between gap-4">
        <div>
          <h2 className="text-lg font-bold text-slate-800 dark:text-slate-100 flex items-center gap-2">
            <Scale className="w-5 h-5 text-blue-600 dark:text-blue-400" />
            Evaluation Benchmark & Algorithmic Fairness Harness
          </h2>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
            Deterministic IR metrics (nDCG, MRR), memory profiling, and identity counterfactual audits.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={handleRunBenchmark}
            disabled={loadingBenchmark}
            className="neu-button px-4 py-2.5 flex items-center gap-2 text-xs font-bold text-blue-600 dark:text-blue-400 hover:text-blue-700 disabled:opacity-50"
          >
            <Play className={`w-3.5 h-3.5 ${loadingBenchmark ? 'animate-spin' : ''}`} />
            {loadingBenchmark ? 'Evaluating Models...' : 'Run Benchmark Grid'}
          </button>

          <button
            onClick={handleAuditFairness}
            disabled={loadingAudit}
            className="neu-button px-4 py-2.5 flex items-center gap-2 text-xs font-bold text-indigo-600 dark:text-indigo-400 hover:text-indigo-700 disabled:opacity-50"
          >
            <Scale className={`w-3.5 h-3.5 ${loadingAudit ? 'animate-spin' : ''}`} />
            {loadingAudit ? 'Auditing Identity Shifts...' : 'Run Fairness Audit'}
          </button>
        </div>
      </div>

      {/* Benchmark Matrix Table */}
      {runs.length > 0 && (
        <div className="neu-flat p-6 flex flex-col gap-4">
          <h3 className="text-sm font-bold uppercase tracking-wider text-slate-700 dark:text-slate-300 flex items-center gap-2">
            <BarChart3 className="w-4 h-4 text-emerald-500" /> Multi-Model Performance Matrix
          </h3>

          <div className="overflow-x-auto">
            <table className="w-full text-xs text-left">
              <thead>
                <tr className="border-b border-slate-300 dark:border-slate-700 text-slate-500">
                  <th className="py-2.5 font-semibold">Model Architecture</th>
                  <th className="py-2.5 font-semibold">nDCG@5</th>
                  <th className="py-2.5 font-semibold">nDCG@10</th>
                  <th className="py-2.5 font-semibold">MRR</th>
                  <th className="py-2.5 font-semibold">Precision@5</th>
                  <th className="py-2.5 font-semibold">Latency (ms)</th>
                  <th className="py-2.5 font-semibold">Peak RAM</th>
                  <th className="py-2.5 font-semibold">Counterfactual Tau (τ)</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-200 dark:divide-slate-800">
                {runs.map((r, i) => (
                  <tr key={i} className="hover:bg-slate-500/5 transition-colors">
                    <td className="py-3 font-bold text-slate-800 dark:text-slate-200">{r.model_name}</td>
                    <td className="py-3 font-mono font-semibold text-blue-600 dark:text-blue-400">
                      {r.ndcg_at_5.toFixed(3)}
                    </td>
                    <td className="py-3 font-mono">{r.ndcg_at_10.toFixed(3)}</td>
                    <td className="py-3 font-mono">{r.mrr.toFixed(3)}</td>
                    <td className="py-3 font-mono">{r.precision_at_5.toFixed(3)}</td>
                    <td className="py-3 font-mono text-slate-600 dark:text-slate-400">
                      {r.latency_median_ms.toFixed(1)} ms
                    </td>
                    <td className="py-3 font-mono text-slate-600 dark:text-slate-400">
                      {r.peak_ram_mb.toFixed(0)} MB
                    </td>
                    <td className="py-3 font-mono font-bold text-emerald-600 dark:text-emerald-400">
                      {r.counterfactual_tau !== null && r.counterfactual_tau !== undefined
                        ? `τ = ${r.counterfactual_tau.toFixed(3)}`
                        : 'N/A'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Fairness Audit Breakdown Cards */}
      {fairnessAudit && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Identity Counterfactual Stability Card */}
          <div className="neu-flat p-6 flex flex-col gap-3">
            <h3 className="text-sm font-bold uppercase tracking-wider text-slate-800 dark:text-slate-200 flex items-center gap-2">
              <CheckCircle className="w-4 h-4 text-emerald-500" />
              Counterfactual Perturbation Stability
            </h3>
            <p className="text-xs text-slate-500 dark:text-slate-400">
              Evaluates rank displacement when gender pronouns and names are swapped in candidate summaries.
            </p>

            <div className="neu-inset p-4 rounded-xl flex items-center justify-between mt-2">
              <div>
                <span className="text-xs text-slate-500">Kendall's Rank Correlation</span>
                <div className="text-2xl font-black text-emerald-600 dark:text-emerald-400">
                  τ = {fairnessAudit.counterfactual_stability.kendall_tau.toFixed(3)}
                </div>
              </div>
              <div className="text-right">
                <span className="text-xs text-slate-500">Shortlist Crossings</span>
                <div className="text-2xl font-black text-slate-800 dark:text-slate-200">
                  {fairnessAudit.counterfactual_stability.shortlist_crossings}
                </div>
              </div>
            </div>

            <span className="text-[11px] text-slate-500 mt-1">
              Max Rank Displacement: <strong>{fairnessAudit.counterfactual_stability.max_rank_delta} positions</strong>
            </span>
          </div>

          {/* Demographic Parity & 4/5ths Rule Card */}
          <div className="neu-flat p-6 flex flex-col gap-3">
            <h3 className="text-sm font-bold uppercase tracking-wider text-slate-800 dark:text-slate-200 flex items-center gap-2">
              <AlertTriangle className="w-4 h-4 text-amber-500" />
              Demographic Parity & Adverse Impact
            </h3>
            <p className="text-xs text-slate-500 dark:text-slate-400">
              Assesses the Four-Fifths Rule (80% selection rate ratio) across synthetic reference groups.
            </p>

            <div className="neu-inset p-4 rounded-xl flex items-center justify-between mt-2">
              <div>
                <span className="text-xs text-slate-500">Disparate Impact Ratio</span>
                <div className="text-2xl font-black text-indigo-600 dark:text-indigo-400">
                  {(fairnessAudit.demographic_parity.demographic_parity_ratio * 100).toFixed(1)}%
                </div>
              </div>
              <div className="text-right">
                <span className="text-xs text-slate-500">Selection Rate Difference</span>
                <div className="text-xl font-bold text-slate-800 dark:text-slate-200">
                  {(fairnessAudit.demographic_parity.selection_rate_difference * 100).toFixed(1)}%
                </div>
              </div>
            </div>

            <p className="text-[11px] text-amber-800 dark:text-amber-300 italic mt-1">
              {fairnessAudit.demographic_parity.warning}
            </p>
          </div>
        </div>
      )}
    </div>
  );
};
