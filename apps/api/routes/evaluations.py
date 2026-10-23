"""
================================================================================
Open-Source Resume Intelligence, Ranking & Fairness Lab
FastAPI Routes: Evaluation Harness & Fairness Diagnostics
================================================================================
Endpoints for running model benchmark evaluations, retrieving IR metrics
(nDCG, MRR, latency, RAM), counterfactual stability audits, and group parity.
================================================================================
"""

import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from fastapi import APIRouter, HTTPException, status

from packages.common.schemas import EvaluationRun, JobDescription, ResumeProfile
from packages.common.settings import EVALUATION_OUTPUTS_DIR
from packages.common.database import (
    get_job,
    list_jobs,
    list_parsed_profiles,
    save_evaluation_run,
    list_evaluation_runs,
)
from packages.evaluation.harness import EvaluationHarness
from packages.fairness.counterfactual import CounterfactualAuditor
from packages.fairness.parity import ParityAuditor
from packages.ranking.rrf_ranker import RRFRanker
from packages.ranking.bm25_ranker import BM25Ranker

router = APIRouter(prefix="/evaluations", tags=["Evaluation & Fairness Harness"])


class BenchmarkRequest(BaseModel):
    """Payload to trigger benchmark evaluation."""
    job_id: str
    split_name: str = "golden_test_v1"
    golden_relevance: Optional[Dict[str, float]] = Field(
        default=None,
        description="Optional ground-truth graded relevance map: {candidate_id: 0.0 - 3.0}",
    )


class FairnessAuditRequest(BaseModel):
    """Payload to audit a ranker for counterfactual & group disparity."""
    job_id: str
    ranker_name: str = "rrf_hybrid"
    top_k: int = 5
    synthetic_groups: Optional[Dict[str, str]] = Field(
        default=None,
        description="Optional mapping of candidate_id to synthetic demographic group",
    )


@router.post("/benchmark", response_model=List[EvaluationRun])
def run_benchmark(req: BenchmarkRequest):
    """
    Executes all registered ranking models (BM25, Dense MiniLM, RRF, Weighted, TOPSIS, LAYA)
    against the candidate pool and records IR and resource metrics.
    """
    job = get_job(req.job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job description '{req.job_id}' not found.",
        )

    candidates = list_parsed_profiles()
    if not candidates:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No candidate profiles found in database to evaluate.",
        )

    # If golden relevance is not provided, generate heuristic relevance based on required skills
    if req.golden_relevance:
        golden_rel = req.golden_relevance
    else:
        golden_rel = {}
        job_skills = {c.description.lower() for c in job.criteria}
        for cand in candidates:
            cand_skills = {s.original_text.lower() for s in cand.skills}
            overlap = len(job_skills.intersection(cand_skills))
            rel = min(3.0, float(overlap))
            golden_rel[cand.candidate_id] = rel

    harness = EvaluationHarness()
    runs = harness.run_benchmark(
        job=job,
        candidates=candidates,
        golden_relevance=golden_rel,
        split_name=req.split_name,
    )

    # Persist each run to DB
    for r in runs:
        save_evaluation_run(r)

    return runs


@router.get("/latest", response_model=Dict[str, Any])
def get_latest_benchmark_report():
    """
    Retrieves the latest markdown benchmark comparison report.
    """
    report_file = EVALUATION_OUTPUTS_DIR / "latest_evaluation_report.md"
    if not report_file.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No benchmark evaluation report found. Run a benchmark first via POST /api/v1/evaluations/benchmark.",
        )

    content = report_file.read_text(encoding="utf-8")
    return {
        "report_path": str(report_file),
        "markdown_content": content,
    }


@router.get("/runs", response_model=List[EvaluationRun])
def list_benchmark_runs():
    """
    Lists all evaluation runs stored in the SQLite database.
    """
    return list_evaluation_runs()


@router.post("/fairness/audit", response_model=Dict[str, Any])
def audit_fairness(req: FairnessAuditRequest):
    """
    Runs Counterfactual identity perturbation and Demographic Parity audits on candidate pool.
    """
    job = get_job(req.job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job description '{req.job_id}' not found.",
        )

    candidates = list_parsed_profiles()
    if not candidates:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No candidate profiles found in database to audit.",
        )

    # Pick ranker
    if req.ranker_name == "bm25":
        ranker = BM25Ranker()
    else:
        ranker = RRFRanker()

    # 1. Counterfactual identity swap audit
    cf_res = CounterfactualAuditor.audit_ranker(ranker, job, candidates, top_k=req.top_k)

    # 2. Demographic parity audit (using synthetic groups or alternating groups if not provided)
    if req.synthetic_groups:
        group_labels = [req.synthetic_groups.get(c.candidate_id, "group_unknown") for c in candidates]
    else:
        group_labels = ["group_alpha" if i % 2 == 0 else "group_beta" for i, _ in enumerate(candidates)]

    # Compute ranking and get top-k
    ranked = ranker.rank(job, candidates, run_id="parity_audit_run")
    top_cids = {r.candidate_id for r in ranked[:req.top_k]}

    y_pred = [1 if c.candidate_id in top_cids else 0 for c in candidates]
    y_true = [1 if i < req.top_k else 0 for i in range(len(candidates))]

    parity_res = ParityAuditor.evaluate_shortlist_disparity(
        y_true=y_true,
        y_pred=y_pred,
        sensitive_features=group_labels,
    )

    return {
        "job_id": req.job_id,
        "ranker_name": req.ranker_name,
        "top_k": req.top_k,
        "counterfactual_stability": cf_res,
        "demographic_parity": parity_res,
        "advisory_notice": (
            "SAFETY ADVISORY: Statistical fairness metrics are diagnostic indicators. "
            "They do not establish absolute legal compliance or substitute for human oversight."
        ),
    }
