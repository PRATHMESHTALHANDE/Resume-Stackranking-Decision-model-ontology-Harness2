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
  Plus,
  Trash2,
  RotateCcw,
  ChevronDown,
  ChevronUp,
  BrainCircuit,
} from 'lucide-react';
import { Header } from './components/Header';
import { EvidenceDrawer } from './components/EvidenceDrawer';
import { GraphViewer } from './components/GraphViewer';
import { FairnessLab } from './components/FairnessLab';
import { ResumeUploader } from './components/ResumeUploader';
import { CreateJobModal } from './components/CreateJobModal';
import { TopCandidateSpotlight } from './components/TopCandidateSpotlight';
import {
  fetchHealth,
  fetchJobs,
  fetchCandidates,
  executeRanking,
  deleteJob,
  deleteRankingsForJob,
  fetchLatestRankingForJob,
  deleteAllResumes,
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
  const [isCreateJobOpen, setIsCreateJobOpen] = useState(false);
  const [expandedCandidateId, setExpandedCandidateId] = useState<string | null>(null);

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

  // Fetch latest rankings whenever selected Job changes
  useEffect(() => {
    if (selectedJobId) {
      fetchLatestRankingForJob(selectedJobId)
        .then((data) => {
          setRankings(data || []);
        })
        .catch(() => setRankings([]));
    }
  }, [selectedJobId]);

  // Current active job
  const currentJob = jobs.find((j) => j.job_id === selectedJobId) || jobs[0];

  // Top candidate for spotlight
  const topRanking = rankings.find((r) => r.rank === 1);
  const topCandidate = topRanking ? candidates.find((c) => c.candidate_id === topRanking.candidate_id) : null;

  // Execute ranking for currently selected JD
  const handleExecuteRanking = async () => {
    if (!currentJob) return;
    setRankingLoading(true);
    try {
      const res = await executeRanking(currentJob.job_id, selectedModel);
      setRankings(res.rankings);
    } catch (err: any) {
      alert(`Ranking failed: ${err.message || 'Please check candidate pool.'}`);
    } finally {
      setRankingLoading(false);
    }
  };

  // Clear rankings for the current JD
  const handleClearRankings = async () => {
    if (!currentJob) return;
    if (!window.confirm(`Clear all stackrank results for "${currentJob.title}"?`)) return;
    try {
      await deleteRankingsForJob(currentJob.job_id);
      setRankings([]);
    } catch (err: any) {
      alert(`Failed to clear rankings: ${err.message}`);
    }
  };

  // Delete current JD
  const handleDeleteJob = async () => {
    if (!currentJob) return;
    if (jobs.length <= 1) {
      alert("Cannot delete the only job description. Please create another JD first.");
      return;
    }
    if (!window.confirm(`Delete job description "${currentJob.title}" and all its rankings?`)) return;
    try {
      await deleteJob(currentJob.job_id);
      const remaining = jobs.filter((j) => j.job_id !== currentJob.job_id);
      setJobs(remaining);
      setSelectedJobId(remaining[0]?.job_id || '');
      setRankings([]);
    } catch (err: any) {
      alert(`Failed to delete job: ${err.message}`);
    }
  };

  // Delete all uploaded resumes
  const handleDeleteAllResumes = async () => {
    if (!window.confirm("Are you sure you want to delete ALL uploaded resumes and candidate profiles? This will reset all candidate queues and rankings.")) return;
    try {
      await deleteAllResumes();
      setCandidates([]);
      setRankings([]);
    } catch (err: any) {
      alert(`Failed to delete all resumes: ${err.message}`);
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
          Ingest Resumes ({candidates.length})
        </button>
      </nav>

      {/* Active Tab Content */}
      <main className="flex-1 flex flex-col gap-6">
        {/* Tab 1: Stack-Ranking */}
        {activeTab === 'ranking' && (
          <div className="flex flex-col gap-6">
            {/* Multi-JD Selector & Management Card */}
            {currentJob && (
              <div className="neu-flat p-6 flex flex-col gap-5">
                {/* Top Row: JD Switcher & Management Actions */}
                <div className="flex flex-wrap items-center justify-between gap-4 pb-4 border-b border-slate-200 dark:border-slate-800">
                  <div className="flex flex-wrap items-center gap-3">
                    <div className="flex flex-col gap-1">
                      <span className="text-[10px] font-bold uppercase tracking-wider text-blue-600 dark:text-blue-400">
                        Active Job Description ({jobs.length} Available)
                      </span>
                      <select
                        value={selectedJobId}
                        onChange={(e) => setSelectedJobId(e.target.value)}
                        className="neu-input px-3.5 py-2 text-xs font-black text-slate-800 dark:text-slate-100 cursor-pointer min-w-[260px]"
                      >
                        {jobs.map((j) => (
                          <option key={j.job_id} value={j.job_id}>
                            {j.title} (min {j.minimum_experience_years || 0} yrs)
                          </option>
                        ))}
                      </select>
                    </div>

                    <div className="flex items-center gap-2 self-end">
                      <button
                        onClick={() => setIsCreateJobOpen(true)}
                        className="neu-button px-3.5 py-2 flex items-center gap-1.5 text-xs font-bold text-blue-600 dark:text-blue-400"
                        title="Create new Job Description"
                      >
                        <Plus className="w-3.5 h-3.5" />
                        New JD
                      </button>

                      <button
                        onClick={handleDeleteJob}
                        disabled={jobs.length <= 1}
                        className="neu-button px-3 py-2 flex items-center gap-1 text-xs font-bold text-rose-600 dark:text-rose-400 disabled:opacity-40"
                        title="Delete this Job Description"
                      >
                        <Trash2 className="w-3.5 h-3.5" />
                        Delete JD
                      </button>

                      {rankings.length > 0 && (
                        <button
                          onClick={handleClearRankings}
                          className="neu-button px-3 py-2 flex items-center gap-1 text-xs font-bold text-amber-600 dark:text-amber-400"
                          title="Reset/Clear rankings for this JD"
                        >
                          <RotateCcw className="w-3.5 h-3.5" />
                          Clear Rankings
                        </button>
                      )}
                    </div>
                  </div>

                  {/* Model Selector & Run Ranking */}
                  <div className="flex flex-wrap items-center gap-3">
                    <div className="flex flex-col gap-1">
                      <span className="text-[10px] font-bold uppercase tracking-wider text-slate-500">
                        Decision / Ranking Model
                      </span>
                      <select
                        value={selectedModel}
                        onChange={(e) => setSelectedModel(e.target.value)}
                        className="neu-input px-3 py-2 text-xs font-bold text-slate-700 dark:text-slate-200 cursor-pointer"
                      >
                        <option value="topsis">TOPSIS Ideal-Point (Decision Model)</option>
                        <option value="weighted">Weighted Multi-Feature (Decision Model)</option>
                        <option value="laya_adapter">LAYA Discrete Criterion Adapter</option>
                        <option value="lambdamart">LambdaMART (Learning to Rank)</option>
                        <option value="rrf_hybrid">RRF Hybrid (Lexical + Semantic)</option>
                        <option value="dense_minilm">Dense MiniLM-L6-v2</option>
                        <option value="bm25">BM25 (Sparse Lexical)</option>
                      </select>
                    </div>

                    <button
                      onClick={handleExecuteRanking}
                      disabled={rankingLoading || candidates.length === 0}
                      className="neu-button px-5 py-2 flex items-center gap-2 text-xs font-black text-blue-600 dark:text-blue-400 hover:text-blue-700 disabled:opacity-50 self-end"
                    >
                      <Sparkles className={`w-4 h-4 ${rankingLoading ? 'animate-spin' : ''}`} />
                      {rankingLoading ? 'Ranking Pool...' : 'Run Stack-Ranking'}
                    </button>
                  </div>
                </div>

                {/* JD Summary & Criteria Chips */}
                <div className="flex flex-col gap-3">
                  <p className="text-xs text-slate-600 dark:text-slate-400 leading-relaxed italic">
                    "{currentJob.description_text}"
                  </p>

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
                          ({c.is_required ? 'Required' : 'Preferred'} • w={c.weight})
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {/* Top Candidate Spotlight Card */}
            {topRanking && currentJob && (
              <TopCandidateSpotlight
                topRanking={topRanking}
                candidate={topCandidate}
                job={currentJob}
                onOpenEvidence={handleOpenEvidence}
                onFocusGraph={handleFocusGraphCandidate}
              />
            )}

            {/* Candidate Review Queue Table */}
            <div className="neu-flat p-6 flex flex-col gap-4">
              <div className="flex flex-wrap items-center justify-between gap-3">
                <h3 className="text-sm font-bold uppercase tracking-wider text-slate-800 dark:text-slate-200 flex items-center gap-2">
                  <Award className="w-4 h-4 text-blue-500" />
                  Candidate Queue ({rankings.length > 0 ? `${rankings.length} Ranked for ${currentJob.title}` : `${candidates.length} Ingested`})
                </h3>

                <div className="flex items-center gap-3">
                  {candidates.length > 0 && (
                    <button
                      onClick={handleDeleteAllResumes}
                      className="neu-button px-3 py-1.5 text-xs font-bold text-rose-600 dark:text-rose-400 flex items-center gap-1"
                      title="Clear all candidate resumes"
                    >
                      <Trash2 className="w-3.5 h-3.5" />
                      Delete All Resumes
                    </button>
                  )}
                  {rankings.length > 0 && (
                    <span className="text-xs text-slate-500">
                      Model: <strong className="text-blue-600">{selectedModel}</strong>
                    </span>
                  )}
                </div>
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
                        const isExpanded = expandedCandidateId === r.candidate_id;

                        return (
                          <>
                            <tr key={r.candidate_id} className="hover:bg-slate-500/5 transition-colors">
                              {/* Rank Badge */}
                              <td className="py-3.5">
                                <span
                                  className={`neu-raised-sm px-2.5 py-1 font-mono font-bold ${
                                    r.rank === 1
                                      ? 'text-amber-600 dark:text-amber-400 border border-amber-500/30'
                                      : 'text-blue-600 dark:text-blue-400'
                                  }`}
                                >
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
                                      className={`h-full rounded-full ${
                                        r.rank === 1 ? 'bg-amber-500' : 'bg-blue-600 dark:bg-blue-500'
                                      }`}
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
                                  onClick={() =>
                                    setExpandedCandidateId(isExpanded ? null : r.candidate_id)
                                  }
                                  className="neu-button px-2.5 py-1.5 text-[11px] font-bold text-slate-700 dark:text-slate-300 flex items-center gap-1"
                                  title="Toggle Decision & LLM summary"
                                >
                                  <BrainCircuit className="w-3 h-3 text-blue-500" />
                                  <span>Summary</span>
                                  {isExpanded ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
                                </button>
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

                            {/* Expandable Dual Summary Row */}
                            {isExpanded && (
                              <tr className="bg-slate-500/5">
                                <td colSpan={6} className="p-4">
                                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
                                    <div className="neu-raised-sm p-3 rounded-lg flex flex-col gap-1.5 border-l-2 border-blue-500">
                                      <span className="font-bold text-blue-600 dark:text-blue-400 flex items-center gap-1">
                                        <BrainCircuit className="w-3.5 h-3.5" />
                                        Decision Model Rationale ({r.model_name})
                                      </span>
                                      <p className="text-slate-600 dark:text-slate-300 leading-relaxed">
                                        {r.decision_summary || 'Standard algorithmic scoring applied.'}
                                      </p>
                                    </div>
                                    <div className="neu-raised-sm p-3 rounded-lg flex flex-col gap-1.5 border-l-2 border-emerald-500">
                                      <span className="font-bold text-emerald-600 dark:text-emerald-400 flex items-center gap-1">
                                        <Sparkles className="w-3.5 h-3.5" />
                                        LLM Qualification Fit
                                      </span>
                                      <p className="text-slate-600 dark:text-slate-300 leading-relaxed">
                                        {r.llm_summary || 'Candidate demonstrated verified requirement alignment.'}
                                      </p>
                                    </div>
                                  </div>
                                </td>
                              </tr>
                            )}
                          </>
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
          <div className="flex flex-col gap-4">
            <div className="flex items-center justify-between">
              <span className="text-xs text-slate-500">
                Currently holding <strong>{candidates.length}</strong> candidate profiles in SQLite.
              </span>
              {candidates.length > 0 && (
                <button
                  onClick={handleDeleteAllResumes}
                  className="neu-button px-4 py-2 text-xs font-bold text-rose-600 dark:text-rose-400 flex items-center gap-1.5"
                >
                  <Trash2 className="w-4 h-4" />
                  Delete All Uploaded Resumes
                </button>
              )}
            </div>
            <ResumeUploader
              onUploadSuccess={(profile) => {
                setCandidates((prev) => [profile, ...prev]);
                setActiveTab('ranking');
              }}
            />
          </div>
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

      {/* Create Job Description Modal */}
      <CreateJobModal
        isOpen={isCreateJobOpen}
        onClose={() => setIsCreateJobOpen(false)}
        onJobCreated={(newJob) => {
          setJobs((prev) => [newJob, ...prev]);
          setSelectedJobId(newJob.job_id);
          setRankings([]);
        }}
      />
    </div>
  );
}

export default App;
