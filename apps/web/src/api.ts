import type {
  CandidateProfile,
  JobDescription,
  RankingResult,
  EvaluationRun,
  SystemHealth,
} from './types';

const API_BASE = '/api/v1';

export async function fetchHealth(): Promise<SystemHealth> {
  const res = await fetch(`${API_BASE}/system/health`);
  if (!res.ok) throw new Error('Failed to fetch system health');
  return res.json();
}

export async function fetchJobs(): Promise<JobDescription[]> {
  const res = await fetch(`${API_BASE}/jobs/`);
  if (!res.ok) throw new Error('Failed to fetch jobs');
  return res.json();
}

export async function fetchCandidates(): Promise<CandidateProfile[]> {
  const res = await fetch(`${API_BASE}/resumes/`);
  if (!res.ok) throw new Error('Failed to fetch candidates');
  return res.json();
}

export async function executeRanking(
  jobId: string,
  modelName: string,
  candidateIds?: string[]
): Promise<{
  run_id: string;
  job_id: string;
  model_name: string;
  total_candidates: number;
  latency_ms: number;
  rankings: RankingResult[];
  advisory_disclaimer: string;
}> {
  const res = await fetch(`${API_BASE}/rankings/${jobId}/rank`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ model_name: modelName, candidate_ids: candidateIds }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'Failed to execute ranking');
  }
  return res.json();
}

export async function fetchCytoscapeGraph(
  jobId: string,
  candidateId?: string
): Promise<{
  job_id: string;
  candidate_id?: string;
  element_count: number;
  elements: any[];
}> {
  const url = candidateId
    ? `${API_BASE}/graph/${jobId}/cytoscape?candidate_id=${encodeURIComponent(candidateId)}`
    : `${API_BASE}/graph/${jobId}/cytoscape`;
  const res = await fetch(url);
  if (!res.ok) throw new Error('Failed to fetch Cytoscape graph');
  return res.json();
}

export async function runBenchmark(
  jobId: string,
  splitName: string = 'golden_test_v1'
): Promise<EvaluationRun[]> {
  const res = await fetch(`${API_BASE}/evaluations/benchmark`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ job_id: jobId, split_name: splitName }),
  });
  if (!res.ok) throw new Error('Failed to run benchmark');
  return res.json();
}

export async function auditFairness(
  jobId: string,
  rankerName: string = 'rrf_hybrid',
  topK: number = 5
): Promise<{
  job_id: string;
  ranker_name: string;
  top_k: number;
  counterfactual_stability: {
    kendall_tau: number;
    shortlist_crossings: number;
    max_rank_delta: number;
    rank_deltas: Record<string, number>;
  };
  demographic_parity: {
    selection_rates_by_group: Record<string, number>;
    demographic_parity_ratio: number;
    selection_rate_difference: number;
    group_sample_sizes: Record<string, number>;
    is_statistically_constrained: boolean;
    warning: string;
  };
  advisory_notice: string;
}> {
  const res = await fetch(`${API_BASE}/evaluations/fairness/audit`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ job_id: jobId, ranker_name: rankerName, top_k: topK }),
  });
  if (!res.ok) throw new Error('Failed to audit fairness');
  return res.json();
}

export async function uploadResumeFile(file: File): Promise<{
  status: string;
  document: any;
  profile: CandidateProfile;
}> {
  const formData = new FormData();
  formData.append('file', file);
  const res = await fetch(`${API_BASE}/resumes/upload`, {
    method: 'POST',
    body: formData,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail?.error || 'Failed to upload resume');
  }
  return res.json();
}
