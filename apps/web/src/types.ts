export interface EvidenceReference {
  evidence_id: string;
  document_id: string;
  page_number?: number | null;
  section_name?: string | null;
  verbatim_snippet: string;
  extraction_confidence: number;
  extraction_method: string;
}

export interface ResumeSkill {
  original_text: string;
  esco_concept_uri?: string | null;
  canonical_label?: string | null;
  mapping_method: string;
  mapping_confidence: number;
  evidence?: EvidenceReference | null;
}

export interface ExperienceItem {
  job_title: string;
  organization?: string | null;
  start_date?: string | null;
  end_date?: string | null;
  duration_months?: number | null;
  evidence?: EvidenceReference | null;
}

export interface EducationItem {
  degree: string;
  field_of_study?: string | null;
  institution?: string | null;
  graduation_year?: number | null;
  evidence?: EvidenceReference | null;
}

export interface CandidateProfile {
  candidate_id: string;
  document_id: string;
  skills: ResumeSkill[];
  experience_items: ExperienceItem[];
  education_items: EducationItem[];
  total_experience_years: number;
  summary?: string | null;
  uncertainty_flags: string[];
  extraction_method: string;
  created_at: string;
}

export interface JobCriterion {
  criterion_id: string;
  description: string;
  is_required: boolean;
  weight: number;
  associated_esco_uri?: string | null;
}

export interface JobDescription {
  job_id: string;
  title: string;
  description_text: string;
  criteria: JobCriterion[];
  minimum_experience_years?: number | null;
  version: number;
  created_at: string;
}

export interface RankingResult {
  candidate_id: string;
  job_id: string;
  rank: number;
  score: number;
  model_name: string;
  component_scores: Record<string, number>;
  evidence_citations: EvidenceReference[];
  uncertainty_markers: string[];
  run_id: string;
  created_at: string;
}

export interface EvaluationRun {
  run_id: string;
  timestamp: string;
  model_name: string;
  dataset_split: string;
  split_hash: string;
  candidate_count: number;
  query_count: number;
  ndcg_at_5: number;
  ndcg_at_10: number;
  mrr: number;
  precision_at_5: number;
  recall_at_10: number;
  latency_median_ms: number;
  latency_p95_ms: number;
  candidates_per_second: number;
  peak_ram_mb: number;
  peak_vram_mb: number;
  counterfactual_tau?: number | null;
  shortlist_crossings?: number | null;
}

export interface SystemHealth {
  status: string;
  app_name: string;
  version: string;
  environment: string;
  advisory_disclaimer: string;
  database: {
    status: string;
    path: string;
    total_candidates: number;
    total_jobs: number;
  };
  hardware: {
    cpu_cores: number;
    ram_total_gb: number;
    ram_available_gb: number;
    cuda_available: boolean;
    gpu_device: string;
    vram_total_mb: number;
  };
}
