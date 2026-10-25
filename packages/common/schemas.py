"""
Module: packages.common.schemas
Description:
    Canonical data contract schemas for the Resume Intelligence, Ranking & Fairness Lab.
    Defines Pydantic v2 models for:
    - EvidenceReference: Verbatim citations linking claims to source pages & sections.
    - ResumeDocument: File metadata, parsing status, content hashing.
    - ResumeProfile: Structured candidate data (skills, experience, education, uncertainty).
    - JobDescription: Explicit required & preferred criteria, weights, minimum experience.
    - RankingResult: Candidate ranking score, component breakdown, evidence list.
    - EvaluationRun: Benchmark run metadata, nDCG, MRR, latency, and memory profiling.

Author:
    Resume Intelligence Architect
"""
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, field_validator, ConfigDict

# ==============================================================================
# 1. Evidence Citation Contract
# ==============================================================================
class EvidenceReference(BaseModel):
    """
    Verbatim citation extracted directly from a source resume document.
    Every single skill match, experience claim, or qualification score must
    anchor to an EvidenceReference to eliminate model hallucination.
    """
    model_config = ConfigDict(frozen=True, extra="forbid")

    evidence_id: str = Field(
        default_factory=lambda: str(uuid.uuid4())[:8],
        description="Unique short identifier for the evidence citation",
    )
    document_id: str = Field(
        ...,
        description="Foreign key identifier of the source resume document",
    )
    page_number: Optional[int] = Field(
        None,
        ge=1,
        description="1-indexed source document page where snippet was located",
    )
    section_name: Optional[str] = Field(
        None,
        description="Normalized resume section (e.g. 'Experience', 'Education', 'Skills')",
    )
    verbatim_snippet: str = Field(
        ...,
        min_length=1,
        description="Exact, un-altered text excerpt cited from the resume",
    )
    extraction_confidence: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Confidence score of extraction method (1.0 for deterministic, <=1.0 for model)",
    )
    extraction_method: str = Field(
        default="deterministic",
        description="Method used: 'deterministic' | 'llm_gguf' | 'mock'",
    )

    @field_validator("verbatim_snippet")
    @classmethod
    def strip_snippet(cls, v: str) -> str:
        """Ensure snippet text is cleanly stripped of surrounding whitespace."""
        clean = v.strip()
        if not clean:
            raise ValueError("Evidence snippet cannot be empty or pure whitespace.")
        return clean


# ==============================================================================
# 2. Candidate Profile & Extracted Entities
# ==============================================================================
class ResumeSkill(BaseModel):
    """
    Individual skill identified within candidate evidence, mapped to ESCO concepts.
    """
    original_text: str = Field(
        ...,
        min_length=1,
        description="Raw skill string found in the resume text",
    )
    esco_concept_uri: Optional[str] = Field(
        None,
        description="Canonical ESCO URI if normalized (e.g. 'http://data.europa.eu/esco/skill/...')",
    )
    canonical_label: Optional[str] = Field(
        None,
        description="Preferred human-readable ESCO taxonomy label",
    )
    mapping_method: str = Field(
        default="unmapped",
        description="Mapping stage: 'exact' | 'alias' | 'fuzzy' | 'semantic' | 'unmapped'",
    )
    mapping_confidence: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Confidence score of the ontology mapping stage",
    )
    evidence: Optional[EvidenceReference] = Field(
        None,
        description="Source document citation anchoring this skill",
    )


class ExperienceItem(BaseModel):
    """
    Professional work experience entry extracted from resume.
    """
    job_title: str = Field(..., min_length=1, description="Extracted job role or title")
    organization: Optional[str] = Field(None, description="Company or institution name")
    start_date: Optional[str] = Field(None, description="ISO-8601 or parsed start date string")
    end_date: Optional[str] = Field(None, description="ISO-8601, 'Present', or end date string")
    duration_months: Optional[float] = Field(
        None,
        ge=0.0,
        description="Normalized duration in months computed from dates",
    )
    evidence: Optional[EvidenceReference] = Field(
        None,
        description="Source document citation for this employment record",
    )


class EducationItem(BaseModel):
    """
    Educational credential or degree extracted from resume.
    """
    degree: str = Field(..., min_length=1, description="Degree type (e.g. 'B.S.', 'M.S.', 'Ph.D.')")
    field_of_study: Optional[str] = Field(None, description="Major or specialization")
    institution: Optional[str] = Field(None, description="College or university name")
    graduation_year: Optional[int] = Field(None, ge=1950, le=2050, description="Year of graduation")
    evidence: Optional[EvidenceReference] = None


class ResumeDocument(BaseModel):
    """
    Ingested resume file record with content hash and parsing status.
    """
    document_id: str = Field(
        default_factory=lambda: str(uuid.uuid4())[:12],
        description="Unique internal document identifier",
    )
    content_hash: str = Field(
        ...,
        description="SHA-256 hash of original file bytes for instant duplicate detection",
    )
    source_filename: str = Field(
        ...,
        description="Sanitized display filename (not used for candidate identity)",
    )
    file_type: str = Field(
        ...,
        description="MIME type or extension: 'pdf' | 'docx'",
    )
    page_count: int = Field(default=1, ge=1, description="Total number of document pages")
    file_size_bytes: int = Field(..., ge=1, description="File size in bytes")
    parser_status: str = Field(
        default="pending",
        description="'pending' | 'success' | 'warning' | 'error'",
    )
    warnings: List[str] = Field(
        default_factory=list,
        description="Non-fatal warnings (e.g. 'scanned_pdf_detected', 'low_text_density')",
    )
    requisition_id: Optional[str] = Field(
        None,
        description="Assigned corporate job requisition number (e.g. 'REQ-2026-001')",
    )
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ResumeProfile(BaseModel):
    """
    Complete structured profile of a candidate parsed from a resume document.
    """
    candidate_id: str = Field(
        ...,
        description="Anonymized candidate identifier linking to ResumeDocument",
    )
    document_id: str = Field(..., description="Foreign key to source ResumeDocument")
    requisition_id: Optional[str] = Field(
        None,
        description="Assigned corporate job requisition number (e.g. 'REQ-2026-001')",
    )
    skills: List[ResumeSkill] = Field(default_factory=list)
    experience_items: List[ExperienceItem] = Field(default_factory=list)
    education_items: List[EducationItem] = Field(default_factory=list)
    total_experience_years: float = Field(default=0.0, ge=0.0)
    summary: Optional[str] = Field(None, description="Verbatim extracted summary snippet")
    uncertainty_flags: List[str] = Field(
        default_factory=list,
        description="Explicit gaps or ambiguities (e.g. 'undated_experience', 'unrecognized_degree')",
    )
    extraction_method: str = Field(
        default="deterministic",
        description="'deterministic' | 'llm_gguf' | 'mock'",
    )
    created_at: datetime = Field(default_factory=datetime.utcnow)


# ==============================================================================
# 3. Job Description & Criteria Contracts
# ==============================================================================
class JobCriterion(BaseModel):
    """
    Specific job requirement or preferred qualification with weighting.
    """
    criterion_id: str = Field(
        default_factory=lambda: str(uuid.uuid4())[:8],
        description="Unique identifier for the requirement",
    )
    description: str = Field(..., min_length=3, description="Text description of requirement")
    is_required: bool = Field(
        default=True,
        description="True if mandatory qualification; False if preferred/nice-to-have",
    )
    weight: float = Field(
        default=1.0,
        ge=0.1,
        le=5.0,
        description="Relative importance weight in scoring (1.0 is standard)",
    )
    associated_esco_uri: Optional[str] = Field(
        None,
        description="Canonical ESCO skill URI corresponding to this criterion",
    )


class JobDescription(BaseModel):
    """
    Structured Job Posting record with explicit review criteria.
    """
    job_id: str = Field(
        default_factory=lambda: str(uuid.uuid4())[:12],
        description="Unique job identifier",
    )
    requisition_id: str = Field(
        default_factory=lambda: f"REQ-{uuid.uuid4().hex[:6].upper()}",
        description="Corporate Job Requisition Number (e.g. 'REQ-2026-001')",
    )
    title: str = Field(..., min_length=2, description="Job title")
    description_text: str = Field(..., min_length=10, description="Full job description text")
    criteria: List[JobCriterion] = Field(default_factory=list)
    minimum_experience_years: Optional[float] = Field(None, ge=0.0)
    version: int = Field(default=1, ge=1)
    created_at: datetime = Field(default_factory=datetime.utcnow)


# ==============================================================================
# 4. Ranking & Evaluation Output Contracts
# ==============================================================================
class RankingResult(BaseModel):
    """
    Scored candidate entry within a ranked review queue for a specific job.
    """
    candidate_id: str
    job_id: str
    rank: int = Field(..., ge=1, description="Calculated 1-based ordinal rank")
    score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Normalized match score in [0.0, 1.0]",
    )
    model_name: str = Field(
        ...,
        description="'bm25' | 'dense_minilm' | 'rrf_hybrid' | 'weighted' | 'topsis' | 'lambdamart' | 'laya'",
    )
    component_scores: Dict[str, float] = Field(
        default_factory=dict,
        description="Sub-scores (e.g. {'exact_skill_coverage': 0.8, 'semantic_similarity': 0.72})",
    )
    evidence_citations: List[EvidenceReference] = Field(
        default_factory=list,
        description="Verbatim citations supporting this candidate's ranking position",
    )
    uncertainty_markers: List[str] = Field(
        default_factory=list,
        description="Uncertainty warnings (e.g. 'missing_required_criterion:Docker')",
    )
    decision_summary: Optional[str] = Field(
        None,
        description="Algorithmic rationale of how the decision model scored this candidate.",
    )
    llm_summary: Optional[str] = Field(
        None,
        description="Natural language justification of why this candidate is suitable/top-ranked.",
    )
    run_id: str = Field(..., description="Unique ID of the ranking execution run")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class EvaluationRun(BaseModel):
    """
    Machine-readable record of a research benchmark evaluation run.
    """
    run_id: str = Field(
        default_factory=lambda: str(uuid.uuid4())[:12],
        description="Unique run token",
    )
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    model_name: str
    dataset_split: str = Field(..., description="e.g. 'golden_eval_v1_test'")
    split_hash: str = Field(..., description="SHA-256 hash of test split manifest")
    candidate_count: int = Field(..., ge=1)
    query_count: int = Field(..., ge=1)
    
    # Ranking Quality Metrics
    ndcg_at_5: float = Field(..., ge=0.0, le=1.0)
    ndcg_at_10: float = Field(..., ge=0.0, le=1.0)
    mrr: float = Field(..., ge=0.0, le=1.0)
    precision_at_5: float = Field(..., ge=0.0, le=1.0)
    recall_at_10: float = Field(..., ge=0.0, le=1.0)
    
    # Resource & Latency Telemetry
    latency_median_ms: float = Field(..., ge=0.0)
    latency_p95_ms: float = Field(..., ge=0.0)
    candidates_per_second: float = Field(..., ge=0.0)
    peak_ram_mb: float = Field(..., ge=0.0)
    peak_vram_mb: float = Field(..., ge=0.0)
    
    # Fairness Counterfactual Signals
    counterfactual_tau: Optional[float] = Field(
        None,
        ge=-1.0,
        le=1.0,
        description="Kendall's Tau rank correlation under identity perturbation",
    )
    shortlist_crossings: Optional[int] = Field(
        None,
        ge=0,
        description="Number of candidates crossing Top-K threshold under perturbation",
    )
