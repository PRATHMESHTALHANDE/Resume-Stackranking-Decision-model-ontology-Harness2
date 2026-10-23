import { useState, useEffect } from 'react';
import {
  ListFilter,
  Network,
  Scale,
  UploadCloud,
  Award,
  AlertCircle,
  FileText,
  Sparkles,
} from 'lucide-react';
import { Header } from './components/Header';
import { EvidenceDrawer } from './components/EvidenceDrawer';
import { GraphViewer } from './components/GraphViewer';
import { FairnessLab } from './components/FairnessLab';
import { ResumeUploader } from './components/ResumeUploader';
import {
  fetchHealth,
  fetchJobs,
  fetchCandidates,
  executeRanking,
} from './api';
import type {
  SystemHealth,
  JobDescription,
  CandidateProfile,
  RankingResult,
} from './types';

export function App() {
  const [darkMode, setDarkMode] = useState(false);
  const [activeTab, setActiveTab] = useState<'ranking' | 'graph' | 'fairness' | 'upload'>('ranking');
  const [health, setHealth] = useState<SystemHealth | null>(null);
  const [jobs, setJobs] = useState<JobDescription[]>([]);
  const [selectedJobId, setSelectedJobId] = useState<string>('');
  const [candidates, setCandidates] = useState<CandidateProfile[]>([]);
  const [rankings, setRankings] = useState<RankingResult[]>([]);
  const [selectedModel, setSelectedModel] = useState<string>('rrf_hybrid');
  const [rankingLoading, setRankingLoading] = useState(false);
  const [activeCandidateForDrawer, setActiveCandidateForDrawer] = useState<CandidateProfile | null>(null);
  const [activeRankingForDrawer, setActiveRankingForDrawer] = useState<RankingResult | null>(null);
  const [selectedGraphCandidateId, setSelectedGraphCandidateId] = useState<string | undefined>(undefined);

  // Sync dark mode class with root html
  useEffect(() => {
    if (darkMode) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [darkMode]);

  // Initial load
  useEffect(() => {
    fetchHealth().then(setHealth).catch(console.error);
    fetchJobs().then((data) => {
      setJobs(data);
      if (data.length > 0) setSelectedJobId(data[0].job_id);
    }).catch(console.error);
    fetchCandidates().then(setCandidates).catch(console.error);
  }, []);

  // Current active job
  const currentJob = jobs.find((j) => j.job_id === selectedJobId) || jobs[0];

  // Execute ranking
  const handleExecuteRanking = async () => {
    if (!currentJob) return;
    setRankingLoading(true);
    try {
      const res = await executeRanking(currentJob.job_id, selectedModel);
      setRankings(res.rankings);
    } catch (err) {
      console.error('Ranking failed:', err);
    } finally {
      setRankingLoading(false);
    }
  };

  // Open evidence drawer for a candidate
  const handleOpenEvidence = (candidateId: string) => {
    const cand = candidates.find((c) => c.candidate_id === candidateId) || null;
    const rank = rankings.find((r) => r.candidate_id === candidateId) || null;
    setActiveCandidateForDrawer(cand);
    setActiveRankingForDrawer(rank);
  };

  // Switch to graph tab focused on a candidate
  const handleFocusGraphCandidate = (candidateId: string) => {
    setSelectedGraphCandidateId(candidateId);
    setActiveTab('graph');
  };

  return (
    <div className="min-h-screen p-4 md:p-8 flex flex-col gap-6 max-w-7xl mx-auto">
      {/* Header */}
      <Header health={health} darkMode={darkMode} setDarkMode={setDarkMode} />

      {/* Main Tabs Navigation */}
      <nav className="neu-flat p-2 flex flex-wrap gap-2">
        <button
          onClick={() => setActiveTab('ranking')}
          className={`neu-button px-5 py-2.5 flex items-center gap-2 text-xs font-bold rounded-lg transition-all ${
            activeTab === 'ranking'
              ? 'text-blue-600 dark:text-blue-400 font-black neu-inset'
              : 'text-slate-600 dark:text-slate-400'
          }`}
        >
          <ListFilter className="w-4 h-4" />
          Candidate Stack-Ranking
        </button>

        <button
          onClick={() => setActiveTab('graph')}
          className={`neu-button px-5 py-2.5 flex items-center gap-2 text-xs font-bold rounded-lg transition-all ${
            activeTab === 'graph'
              ? 'text-blue-600 dark:text-blue-400 font-black neu-inset'
              : 'text-slate-600 dark:text-slate-400'
          }`}
        >
          <Network className="w-4 h-4" />
          Skill & Ontology Graph
        </button>

        <button
          onClick={() => setActiveTab('fairness')}
          className={`neu-button px-5 py-2.5 flex items-center gap-2 text-xs font-bold rounded-lg transition-all ${
            activeTab === 'fairness'
              ? 'text-blue-600 dark:text-blue-400 font-black neu-inset'
              : 'text-slate-600 dark:text-slate-400'
          }`}
        >
          <Scale className="w-4 h-4" />
          Evaluation & Fairness Lab
        </button>

        <button
          onClick={() => setActiveTab('upload')}
          className={`neu-button px-5 py-2.5 flex items-center gap-2 text-xs font-bold rounded-lg transition-all ${
            activeTab === 'upload'
              ? 'text-blue-600 dark:text-blue-400 font-black neu-inset'
              : 'text-slate-600 dark:text-slate-400'
          }`}
        >
          <UploadCloud className="w-4 h-4" />
          Ingest Resumes
        </button>
      </nav>

      {/* Active Tab Content */}
      <main className="flex-1 flex flex-col gap-6">
        {/* Tab 1: Stack-Ranking */}
        {activeTab === 'ranking' && (
          <div className="flex flex-col gap-6">
            {/* Job Criteria Overview & Model Selector Card */}
            {currentJob && (
              <div className="neu-flat p-6 flex flex-col gap-5">
                <div className="flex flex-wrap items-center justify-between gap-4">
                  <div>
                    <span className="text-xs font-bold uppercase tracking-wider text-blue-600 dark:text-blue-400">
                      Target Role Specification
                    </span>
                    <h2 className="text-xl font-black text-slate-800 dark:text-slate-100">
                      {currentJob.title}
                    </h2>
                  </div>

                  {/* Model Selector & Action */}
                  <div className="flex items-center gap-3">
                    <select
                      value={selectedModel}
                      onChange={(e) => setSelectedModel(e.target.value)}
                      className="neu-input px-3.5 py-2.5 text-xs font-bold text-slate-700 dark:text-slate-200 cursor-pointer"
                    >
                      <option value="rrf_hybrid">RRF Hybrid (Lexical + Semantic)</option>
                      <option value="dense_minilm">Dense MiniLM-L6-v2</option>
                      <option value="bm25">BM25 (Sparse Lexical)</option>
                      <option value="weighted">Weighted Multi-Feature</option>
                      <option value="topsis">TOPSIS Ideal-Point</option>
                      <option value="lambdamart">LambdaMART (Learning to Rank)</option>
                      <option value="laya_adapter">LAYA Decision Adapter</option>
                    </select>

                    <button
                      onClick={handleExecuteRanking}
                      disabled={rankingLoading}
                      className="neu-button px-5 py-2.5 flex items-center gap-2 text-xs font-black text-blue-600 dark:text-blue-400 hover:text-blue-700 disabled:opacity-50"
                    >
                      <Sparkles className={`w-4 h-4 ${rankingLoading ? 'animate-spin' : ''}`} />
                      {rankingLoading ? 'Stack-Ranking Pool...' : 'Run Stack-Ranking'}
                    </button>
                  </div>
                </div>

                {/* Criteria Chips */}
                <div className="flex flex-wrap items-center gap-2">
                  {currentJob.criteria.map((c, i) => (
                    <div
                      key={i}
                      className={`neu-raised-sm px-3 py-1.5 rounded-lg text-xs flex items-center gap-1.5 font-medium ${
                        c.is_required
                          ? 'text-blue-700 dark:text-blue-300 font-bold border-l-2 border-blue-500'
                          : 'text-slate-600 dark:text-slate-400'
                      }`}
                    >
                      <span>{c.description}</span>
                      <span className="text-[10px] opacity-75 font-mono">
                        ({c.is_required ? 'Req' : 'Pref'} • w={c.weight})
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Candidate Review Queue Table */}
            <div className="neu-flat p-6 flex flex-col gap-4">
              <div className="flex items-center justify-between">
                <h3 className="text-sm font-bold uppercase tracking-wider text-slate-800 dark:text-slate-200 flex items-center gap-2">
                  <Award className="w-4 h-4 text-blue-500" />
                  Candidate Queue ({rankings.length > 0 ? `${rankings.length} Ranked` : `${candidates.length} Ingested`})
                </h3>
                {rankings.length > 0 && (
                  <span className="text-xs text-slate-500">
                    Model: <strong className="text-blue-600">{selectedModel}</strong>
                  </span>
                )}
              </div>

              {rankings.length > 0 ? (
                <div className="overflow-x-auto">
                  <table className="w-full text-xs text-left">
                    <thead>
                      <tr className="border-b border-slate-300 dark:border-slate-700 text-slate-500">
                        <th className="py-2.5 font-semibold">Rank</th>
                        <th className="py-2.5 font-semibold">Candidate ID</th>
                        <th className="py-2.5 font-semibold">Match Score</th>
                        <th className="py-2.5 font-semibold">Experience</th>
                        <th className="py-2.5 font-semibold">Uncertainty Warnings</th>
                        <th className="py-2.5 font-semibold text-right">Actions</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-200 dark:divide-slate-800">
                      {rankings.map((r) => {
                        const cand = candidates.find((c) => c.candidate_id === r.candidate_id);
                        return (
                          <tr key={r.candidate_id} className="hover:bg-slate-500/5 transition-colors">
                            {/* Rank Badge */}
                            <td className="py-3.5">
                              <span className="neu-raised-sm px-2.5 py-1 font-mono font-bold text-blue-600 dark:text-blue-400">
                                #{r.rank}
                              </span>
                            </td>

                            {/* Candidate ID */}
                            <td className="py-3.5 font-bold text-slate-800 dark:text-slate-200">
                              {r.candidate_id}
                            </td>

                            {/* Match Score */}
                            <td className="py-3.5">
                              <div className="flex items-center gap-2">
                                <div className="w-24 h-2 neu-inset rounded-full overflow-hidden">
                                  <div
                                    className="h-full bg-blue-600 dark:bg-blue-500 rounded-full"
                                    style={{ width: `${Math.min(100, Math.max(5, r.score * 100))}%` }}
                                  />
                                </div>
                                <span className="font-mono font-bold text-slate-700 dark:text-slate-300">
                                  {(r.score * 100).toFixed(1)}%
                                </span>
                              </div>
                            </td>

                            {/* Experience */}
                            <td className="py-3.5 font-medium text-slate-600 dark:text-slate-400">
                              {cand ? `${cand.total_experience_years} yrs` : 'N/A'}
                            </td>

                            {/* Uncertainty */}
                            <td className="py-3.5">
                              {r.uncertainty_markers.length > 0 ? (
                                <div className="flex items-center gap-1.5 text-amber-700 dark:text-amber-400">
                                  <AlertCircle className="w-3.5 h-3.5 shrink-0" />
                                  <span className="truncate max-w-[200px] text-[11px]">
                                    {r.uncertainty_markers[0]}
                                  </span>
                                </div>
                              ) : (
                                <span className="text-[11px] text-emerald-600 dark:text-emerald-400 font-medium">
                                  No Gaps
                                </span>
                              )}
                            </td>

                            {/* Actions */}
                            <td className="py-3.5 text-right flex items-center justify-end gap-2">
                              <button
                                onClick={() => handleOpenEvidence(r.candidate_id)}
                                className="neu-button px-3 py-1.5 text-[11px] font-bold text-blue-600 dark:text-blue-400 hover:text-blue-700 flex items-center gap-1"
                              >
                                <FileText className="w-3 h-3" />
                                Citations
                              </button>
                              <button
                                onClick={() => handleFocusGraphCandidate(r.candidate_id)}
                                className="neu-button px-3 py-1.5 text-[11px] font-bold text-slate-600 dark:text-slate-400 hover:text-slate-700 flex items-center gap-1"
                              >
                                <Network className="w-3 h-3" />
                                Subgraph
                              </button>
                            </td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>
              ) : (
                /* Unranked candidate pool preview */
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mt-2">
                  {candidates.map((cand) => (
                    <div key={cand.candidate_id} className="neu-raised p-4 flex flex-col justify-between gap-3">
                      <div>
                        <div className="flex items-center justify-between">
                          <span className="font-bold text-sm text-slate-800 dark:text-slate-200">
                            {cand.candidate_id}
                          </span>
                          <span className="text-[11px] font-mono text-slate-500">
                            {cand.total_experience_years} yrs exp
                          </span>
                        </div>
                        <p className="text-xs text-slate-600 dark:text-slate-400 mt-2 line-clamp-2 italic">
                          "{cand.summary || 'Profile extracted deterministically.'}"
                        </p>
                      </div>

                      <div className="flex items-center justify-between pt-2 border-t border-slate-300 dark:border-slate-800">
                        <span className="text-[11px] font-medium text-blue-600 dark:text-blue-400">
                          {cand.skills.length} skills identified
                        </span>
                        <button
                          onClick={() => handleOpenEvidence(cand.candidate_id)}
                          className="neu-button px-2.5 py-1 text-[11px] font-bold text-slate-700 dark:text-slate-300"
                        >
                          View Evidence
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}

        {/* Tab 2: Skill & Ontology Knowledge Graph */}
        {activeTab === 'graph' && currentJob && (
          <GraphViewer
            jobId={currentJob.job_id}
            selectedCandidateId={selectedGraphCandidateId}
            darkMode={darkMode}
          />
        )}

        {/* Tab 3: Evaluation & Fairness Lab */}
        {activeTab === 'fairness' && currentJob && (
          <FairnessLab jobId={currentJob.job_id} />
        )}

        {/* Tab 4: Ingest Resumes */}
        {activeTab === 'upload' && (
          <ResumeUploader
            onUploadSuccess={(profile) => {
              setCandidates((prev) => [profile, ...prev]);
              setActiveTab('ranking');
            }}
          />
        )}
      </main>

      {/* Slide-over Evidence Citation Drawer */}
      <EvidenceDrawer
        candidate={activeCandidateForDrawer}
        ranking={activeRankingForDrawer}
        onClose={() => {
          setActiveCandidateForDrawer(null);
          setActiveRankingForDrawer(null);
        }}
      />
    </div>
  );
}

export default App;
