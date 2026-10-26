import React from 'react';
import { X, CheckCircle, Info, Sparkles, Compass, ShieldCheck, Sliders, Layers, Cpu, Hash } from 'lucide-react';

interface ModelGuideModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSelectModel?: (modelKey: string) => void;
}

interface ModelGuideItem {
  key: string;
  name: string;
  badge: string;
  badgeColor: string;
  icon: React.ReactNode;
  summary: string;
  howItWorks: string;
  bestFor: string;
  strengths: string[];
  tradeoffs: string[];
}

export const ModelGuideModal: React.FC<ModelGuideModalProps> = ({
  isOpen,
  onClose,
  onSelectModel,
}) => {
  if (!isOpen) return null;

  const models: ModelGuideItem[] = [
    {
      key: 'ensemble_symbiosis',
      name: 'All Models in Symbiosis (Consensus)',
      badge: 'Recommended',
      badgeColor: 'bg-indigo-500/10 text-indigo-400 border-indigo-500/30',
      icon: <Sparkles className="w-5 h-5 text-indigo-400" />,
      summary: 'Executes all 6 decision algorithms simultaneously and calculates a unified consensus score.',
      howItWorks: 'Concurrently runs TOPSIS, LAYA, Weighted Scorer, RRF Hybrid, Dense Vector MiniLM, and BM25. Combines their normalized scores and evaluates cross-model agreement rate.',
      bestFor: 'High-stakes executive hires, senior roles, or whenever HR wants maximum confidence without algorithmic bias.',
      strengths: ['Eliminates single-algorithm blind spots', 'Transparent cross-model agreement metric', 'Combines geometric, discrete, and semantic reasoning'],
      tradeoffs: ['Slightly higher compute latency as 6 models run in parallel'],
    },
    {
      key: 'weighted',
      name: 'Weighted Multi-Feature Policy',
      badge: 'HR Customizable',
      badgeColor: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30',
      icon: <Sliders className="w-5 h-5 text-emerald-400" />,
      summary: 'Direct multi-attribute linear scoring where HR configures exact percentage allocations.',
      howItWorks: 'Applies recruiter-tuned weights: e.g. Criteria Match % (80%) vs Experience Tenure % (20%), normalizing criteria importance.',
      bestFor: 'Tailored recruitment drives where hiring managers have specific policy mandates (e.g., heavily weighting tenure over pure skill lists).',
      strengths: ['100% transparent and adjustable via UI percentage sliders', 'Easy for recruiters to explain to hiring managers'],
      tradeoffs: ['Requires recruiters to choose reasonable percentage distributions'],
    },
    {
      key: 'topsis',
      name: 'TOPSIS Ideal-Point Geometric Distance',
      badge: 'MCDM Benchmark',
      badgeColor: 'bg-blue-500/10 text-blue-400 border-blue-500/30',
      icon: <Compass className="w-5 h-5 text-blue-400" />,
      summary: 'Measures candidate Euclidean distance towards a hypothetical ideal candidate and away from an anti-ideal profile.',
      howItWorks: 'Vector-normalizes criteria and evaluates relative closeness coefficient C* in [0, 1].',
      bestFor: 'Balanced senior engineering, team leads, and architects where trade-offs between depth, breadth, and experience are crucial.',
      strengths: ['Sound mathematical foundation in Operations Research', 'Penalizes one-dimensional candidates who lack core breadth'],
      tradeoffs: ['Assumes criteria weights are fixed relative to Euclidean space'],
    },
    {
      key: 'laya_adapter',
      name: 'LAYA System-1 Decision Model (convaiinnovations/laya)',
      badge: 'Neural Decision Model',
      badgeColor: 'bg-amber-500/10 text-amber-400 border-amber-500/30',
      icon: <ShieldCheck className="w-5 h-5 text-amber-400" />,
      summary: 'Non-autoregressive neural decision model (ModernBERT-large 421M params) evaluating candidate evidence against typed criteria.',
      howItWorks: 'Evaluates candidate evidence against requirements in a single forward pass into match / partial / no_match decisions with zero text-generation hallucinations.',
      bestFor: 'Regulated industries, clinical, legal, or government roles where missing a single mandatory certification is disqualifying.',
      strengths: ['Non-autoregressive (zero hallucinations)', 'Calibrated Bayesian-style confidence', 'Strict non-compensatory criteria evaluation'],
      tradeoffs: ['Higher initial download size (~840 MB) on first launch'],
    },
    {
      key: 'rrf_hybrid',
      name: 'Reciprocal Rank Fusion (RRF Hybrid)',
      badge: 'Standard Workhorse',
      badgeColor: 'bg-purple-500/10 text-purple-400 border-purple-500/30',
      icon: <Layers className="w-5 h-5 text-purple-400" />,
      summary: 'Standard industry workhorse combining lexical term frequency with semantic embeddings.',
      howItWorks: 'Accumulates reciprocal ranks 1 / (60 + rank_m) across BM25 lexical and MiniLM dense semantic retrievers.',
      bestFor: 'General technical recruiting, mid-level roles, and rapid initial applicant triage.',
      strengths: ['Balances exact technical keywords with conceptual synonyms', 'Immune to scale distortion between models'],
      tradeoffs: ['Does not separate mandatory vs preferred criteria differently'],
    },
    {
      key: 'dense_minilm',
      name: 'Dense Vector Bi-Encoder (MiniLM-L6-v2)',
      badge: 'Semantic AI',
      badgeColor: 'bg-teal-500/10 text-teal-400 border-teal-500/30',
      icon: <Cpu className="w-5 h-5 text-teal-400" />,
      summary: 'Pure 384-dimensional dense semantic embedding cosine similarity.',
      howItWorks: 'Encodes job responsibilities and resume experience into dense latent vectors, computing directional cosine alignment.',
      bestFor: 'Career switchers, interdisciplinary roles, or when candidates use varied company-specific terminology for standard concepts.',
      strengths: ['Understands conceptual context and semantic equivalents', 'Finds non-obvious candidate talent'],
      tradeoffs: ['May overlook missing exact acronyms or specific version numbers'],
    },
    {
      key: 'bm25',
      name: 'BM25 Lexical Keyword Scorer',
      badge: 'Exact Terminology',
      badgeColor: 'bg-orange-500/10 text-orange-400 border-orange-500/30',
      icon: <Hash className="w-5 h-5 text-orange-400" />,
      summary: 'Classic probabilistic information retrieval algorithm based on exact term frequency and inverse document frequency.',
      howItWorks: 'Tokenizes and matches exact job criteria keywords against resume text with document length normalization.',
      bestFor: 'Niche technical roles with strict toolsets (e.g. Kubernetes, Terraform, ISO-27001, FPGA).',
      strengths: ['Deterministic and ultra-fast', 'Prioritizes rare, distinctive technical skills'],
      tradeoffs: ['Misses synonyms (e.g. "Golang" vs "Go", "Postgres" vs "PostgreSQL")'],
    },
  ];

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm animate-fade-in">
      <div className="relative w-full max-w-4xl max-h-[90vh] overflow-hidden rounded-2xl bg-[#1e222a] border border-slate-700/60 shadow-2xl flex flex-col">
        {/* Modal Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-800 bg-slate-900/50">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-xl bg-indigo-500/10 border border-indigo-500/20 text-indigo-400">
              <Info className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-lg font-bold text-white tracking-wide">
                Detailed Breakdown: When to Pick Which Model
              </h2>
              <p className="text-xs text-slate-400">
                Decision model selection matrix & recruiter guidance for HR practitioners
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 text-slate-400 hover:text-white rounded-lg hover:bg-slate-800 transition-colors"
            title="Close Guide"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Modal Content - Scrollable */}
        <div className="flex-1 overflow-y-auto p-6 space-y-4">
          <div className="p-4 rounded-xl bg-indigo-950/30 border border-indigo-800/40 text-xs text-indigo-200 flex items-start gap-3">
            <Sparkles className="w-4 h-4 text-indigo-400 shrink-0 mt-0.5" />
            <p>
              <strong className="text-white">Recruiter Tip:</strong> If unsure which model to pick, select{' '}
              <span className="text-indigo-300 font-semibold">"All Models in Symbiosis"</span>. It synthesizes geometric closeness, strict compliance, percentage weights, and semantic embeddings to find candidates with unanimous multi-algorithm consensus.
            </p>
          </div>

          <div className="grid grid-cols-1 gap-4">
            {models.map((m) => (
              <div
                key={m.key}
                className="p-5 rounded-xl bg-[#252a34] border border-slate-800 hover:border-slate-700 transition-all hover:shadow-lg"
              >
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-3">
                  <div className="flex items-center gap-3">
                    <div className="p-2 rounded-lg bg-slate-800 border border-slate-700">
                      {m.icon}
                    </div>
                    <div>
                      <h3 className="text-sm font-semibold text-white">{m.name}</h3>
                      <p className="text-xs text-slate-400">{m.summary}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-2 self-start sm:self-auto">
                    <span className={`px-2.5 py-0.5 text-[11px] font-medium rounded-full border ${m.badgeColor}`}>
                      {m.badge}
                    </span>
                    {onSelectModel && (
                      <button
                        onClick={() => {
                          onSelectModel(m.key);
                          onClose();
                        }}
                        className="px-3 py-1 text-xs font-medium text-white bg-indigo-600 hover:bg-indigo-500 rounded-lg transition-colors"
                      >
                        Select
                      </button>
                    )}
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-3 mt-3 pt-3 border-t border-slate-800/80 text-xs">
                  <div>
                    <span className="font-semibold text-slate-300">🎯 Best Recruiter Use Case:</span>
                    <p className="text-slate-400 mt-1 leading-relaxed">{m.bestFor}</p>
                    <span className="font-semibold text-slate-300 mt-2 block">⚙️ Mechanism:</span>
                    <p className="text-slate-400 mt-1 leading-relaxed">{m.howItWorks}</p>
                  </div>
                  <div className="space-y-2">
                    <div>
                      <span className="font-semibold text-emerald-400">Key Strengths:</span>
                      <ul className="mt-1 space-y-1">
                        {m.strengths.map((s, idx) => (
                          <li key={idx} className="flex items-start gap-1.5 text-slate-300">
                            <CheckCircle className="w-3.5 h-3.5 text-emerald-400 shrink-0 mt-0.5" />
                            <span>{s}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                    <div>
                      <span className="font-semibold text-amber-400">Trade-offs:</span>
                      <ul className="mt-1 space-y-1">
                        {m.tradeoffs.map((t, idx) => (
                          <li key={idx} className="text-slate-400 list-disc list-inside">
                            {t}
                          </li>
                        ))}
                      </ul>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Modal Footer */}
        <div className="px-6 py-3 border-t border-slate-800 bg-slate-900/50 flex justify-end">
          <button
            onClick={onClose}
            className="px-4 py-2 text-xs font-medium text-slate-300 bg-slate-800 hover:bg-slate-700 rounded-xl transition-colors"
          >
            Close Guide
          </button>
        </div>
      </div>
    </div>
  );
};
