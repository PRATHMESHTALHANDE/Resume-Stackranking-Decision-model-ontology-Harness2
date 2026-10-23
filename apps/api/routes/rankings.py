"""
================================================================================
Open-Source Resume Intelligence, Ranking & Fairness Lab
FastAPI Routes: Multi-Model Ranking Engine
================================================================================
Executes candidate stack-ranking across BM25, Dense MiniLM, RRF Hybrid,
Weighted Scorer, TOPSIS, LambdaMART, and LAYA Decision Adapter.
================================================================================
"""

import time
import uuid
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from fastapi import APIRouter, HTTPException, Query, status

from packages.common.schemas import RankingResult, ResumeProfile, JobDescription
from packages.common.database import (
    get_job,
    list_parsed_profiles,
    save_ranking_results,
    get_rankings_by_run,
)
from packages.ranking.bm25_ranker import BM25Ranker
from packages.ranking.dense_ranker import DenseRanker
from packages.ranking.rrf_ranker import RRFRanker
from packages.ranking.weighted_ranker import WeightedScorer
from packages.ranking.topsis_ranker import TOPSISRanker
from packages.ranking.lambdamart_ranker import LambdaMARTRanker
from packages.decision_models.laya_adapter import LayaDecisionAdapter

router = APIRouter(prefix="/rankings", tags=["Ranking Engine"])

# Model registry
RANKER_REGISTRY = {
    "bm25": BM25Ranker,
    "dense_minilm": DenseRanker,
    "rrf_hybrid": RRFRanker,
    "weighted": WeightedScorer,
    "topsis": TOPSISRanker,
    "lambdamart": LambdaMARTRanker,
    "laya_adapter": lambda: LayaDecisionAdapter(use_mock=True),
}


class RankingRequest(BaseModel):
    """Payload for triggering a ranking run."""
    model_name: str = Field(
        default="rrf_hybrid",
        description="Ranker architecture: 'bm25' | 'dense_minilm' | 'rrf_hybrid' | 'weighted' | 'topsis' | 'lambdamart' | 'laya_adapter'",
    )
    candidate_ids: Optional[List[str]] = Field(
        default=None,
        description="Optional subset of candidate IDs to rank. If None, ranks all in database.",
    )


class RankingResponse(BaseModel):
    """Response containing ranked candidates and run telemetry."""
    run_id: str
    job_id: str
    model_name: str
    total_candidates: int
    latency_ms: float
    rankings: List[RankingResult]
    advisory_disclaimer: str = (
        "HUMAN REVIEW ONLY: Stack ranking scores represent relative algorithmic matches. "
        "They do not constitute automated hiring, shortlisting, or rejection determinations."
    )


@router.post("/{job_id}/rank", response_model=RankingResponse)
def execute_ranking(job_id: str, req: RankingRequest):
    """
    Ranks candidates against a JobDescription using the specified ranker.
    1. Loads job and candidates.
    2. Instantiates selected model from RANKER_REGISTRY.
    3. Computes component scores, evidence citations, and final stack ranking.
    4. Persists the run results to SQLite.
    """
    job = get_job(job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job description '{job_id}' not found.",
        )

    all_profiles = list_parsed_profiles()
    if req.candidate_ids:
        c_set = set(req.candidate_ids)
        candidates = [p for p in all_profiles if p.candidate_id in c_set]
    else:
        candidates = all_profiles

    if not candidates:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No candidates found in database to rank.",
        )

    model_key = req.model_name.lower()
    if model_key not in RANKER_REGISTRY:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unknown model '{req.model_name}'. Supported: {list(RANKER_REGISTRY.keys())}",
        )

    # Initialize ranker
    factory = RANKER_REGISTRY[model_key]
    ranker = factory()

    run_id = f"run_{model_key}_{uuid.uuid4().hex[:8]}"
    t0 = time.perf_counter()
    results = ranker.rank(job, candidates, run_id=run_id)
    latency_ms = round((time.perf_counter() - t0) * 1000.0, 2)

    # Save to DB
    save_ranking_results(results)

    return RankingResponse(
        run_id=run_id,
        job_id=job_id,
        model_name=model_key,
        total_candidates=len(results),
        latency_ms=latency_ms,
        rankings=results,
    )


@router.get("/runs/{run_id}", response_model=List[RankingResult])
def get_run_results(run_id: str):
    """
    Retrieves previous ranking results by run ID.
    """
    results = get_rankings_by_run(run_id)
    if not results:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No ranking results found for run '{run_id}'.",
        )
    return results
