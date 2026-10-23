"""
Module: packages.ranking.rrf_ranker
Description:
    Reciprocal Rank Fusion (RRF) hybrid ranker combining lexical (BM25) and
    dense semantic (MiniLM) retrieval.
    Formula:
        RRF(d) = sum_{m in M} ( 1 / (k + r_m(d)) )
        where k = 60 (standard Cormack et al. constant)
        and r_m(d) is the 1-indexed rank of candidate d in model m.

Author:
    Resume Intelligence Architect
"""
from typing import List, Dict, Any, Tuple
from collections import defaultdict

from packages.common.schemas import JobDescription, ResumeProfile, RankingResult
from packages.common.settings import settings
from packages.ranking.base import BaseRanker
from packages.ranking.bm25_ranker import BM25Ranker
from packages.ranking.dense_ranker import DenseRanker

class RRFRanker(BaseRanker):
    """
    Hybrid ranker combining BM25 lexical and MiniLM dense retrieval using RRF.
    """
    def __init__(self, k: int = 60):
        self.k = k or settings.RRF_K_PARAMETER
        self.bm25 = BM25Ranker()
        self.dense = DenseRanker()

    def rank(
        self,
        job: JobDescription,
        candidates: List[ResumeProfile],
        run_id: str,
        config: Dict[str, Any] = None,
    ) -> List[RankingResult]:
        """
        Executes hybrid BM25 + MiniLM retrieval and merges candidate order via RRF.
        """
        if not candidates:
            return []

        # 1. Retrieve rankings from both models independently
        bm25_retrieved = self.bm25.retrieve(job, candidates, top_k=len(candidates))
        dense_retrieved = self.dense.retrieve(job, candidates, top_k=len(candidates))

        # 2. Compute RRF accumulated scores: sum(1 / (k + rank))
        rrf_scores: Dict[str, float] = defaultdict(float)
        component_scores: Dict[str, Dict[str, float]] = defaultdict(dict)

        # Lexical contribution
        for rank_1b, (cid, score) in enumerate(bm25_retrieved, start=1):
            rrf_scores[cid] += 1.0 / (self.k + rank_1b)
            component_scores[cid]["bm25_score"] = score
            component_scores[cid]["bm25_rank"] = rank_1b

        # Semantic contribution
        for rank_1b, (cid, score) in enumerate(dense_retrieved, start=1):
            rrf_scores[cid] += 1.0 / (self.k + rank_1b)
            component_scores[cid]["dense_cosine_score"] = score
            component_scores[cid]["dense_rank"] = rank_1b

        # 3. Sort candidates by descending RRF score
        sorted_candidates = sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)

        # Max possible theoretical RRF score for rank 1 in both systems: 2 / (k + 1)
        max_possible_rrf = 2.0 / (self.k + 1.0)

        candidate_map = {c.candidate_id: c for c in candidates}
        ranking_results = []

        for final_rank, (cid, raw_rrf) in enumerate(sorted_candidates, start=1):
            normalized_score = min(raw_rrf / max_possible_rrf, 1.0)
            cand = candidate_map[cid]
            citations = [s.evidence for s in cand.skills if s.evidence is not None]

            comps = component_scores[cid]
            comps["raw_rrf"] = float(raw_rrf)

            ranking_results.append(
                RankingResult(
                    candidate_id=cid,
                    job_id=job.job_id,
                    rank=final_rank,
                    score=float(normalized_score),
                    model_name="rrf_hybrid",
                    component_scores=comps,
                    evidence_citations=citations[:5],
                    uncertainty_markers=cand.uncertainty_flags,
                    run_id=run_id,
                )
            )

        return ranking_results
