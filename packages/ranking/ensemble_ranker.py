"""
================================================================================
Open-Source Resume Intelligence, Ranking & Fairness Lab
Module: packages.ranking.ensemble_ranker
================================================================================
Multi-Algorithm Symbiosis & Consensus Decision Model (ensemble_symbiosis).
Simultaneously runs all decision models and retrieval algorithms in harmony:
1. TOPSIS: Geometric distance to ideal candidate profile.
2. LAYA: Discrete typed criterion decision adapter.
3. Weighted Scorer: Multi-criteria linear weighted policy.
4. RRF Hybrid: Lexical + semantic reciprocal rank fusion.
5. Dense Vector Bi-Encoder (MiniLM): Deep semantic embedding cosine alignment.
6. BM25: Sparse keyword term frequency matching.

Computes a calibrated consensus score and captures cross-algorithm agreement.
================================================================================
"""

import math
from typing import List, Dict, Any, Optional
from collections import defaultdict

from packages.common.schemas import JobDescription, ResumeProfile, RankingResult, EvidenceReference
from packages.ranking.base import BaseRanker
from packages.ranking.topsis_ranker import TOPSISRanker
from packages.ranking.weighted_ranker import WeightedScorer
from packages.ranking.rrf_ranker import RRFRanker
from packages.ranking.dense_ranker import DenseRanker
from packages.ranking.bm25_ranker import BM25Ranker
from packages.decision_models.laya_adapter import LayaDecisionAdapter


class EnsembleSymbiosisRanker(BaseRanker):
    """
    Ensemble Consensus Ranker that runs all 6 foundational algorithms in symbiosis.
    Synthesizes diverse perspectives: geometric ideal distance, discrete compliance,
    linear policy, hybrid fusion, and semantic embedding alignment.
    """

    def __init__(self):
        self.topsis = TOPSISRanker()
        self.laya = LayaDecisionAdapter(use_mock=False)
        self.weighted = WeightedScorer()
        self.rrf = RRFRanker()
        self.dense = DenseRanker()
        self.bm25 = BM25Ranker()

    def rank(
        self,
        job: JobDescription,
        candidates: List[ResumeProfile],
        run_id: str,
        config: Optional[Dict[str, Any]] = None,
    ) -> List[RankingResult]:
        """
        Executes all ranking models across the candidate pool and calculates
        a multi-algorithm consensus score and individual component contributions.
        """
        if not candidates:
            return []

        cfg = config or {}

        # 1. Execute individual models
        topsis_results = self.topsis.rank(job, candidates, run_id=run_id, config=cfg)
        laya_results = self.laya.rank(job, candidates, run_id=run_id, config=cfg)
        weighted_results = self.weighted.rank(job, candidates, run_id=run_id, config=cfg)
        rrf_results = self.rrf.rank(job, candidates, run_id=run_id, config=cfg)

        # Vector & lexical retrievers
        dense_retrieved = dict(self.dense.retrieve(job, candidates, top_k=len(candidates)))
        bm25_retrieved = dict(self.bm25.retrieve(job, candidates, top_k=len(candidates)))

        # Normalize dense & bm25 scores to [0.0, 1.0]
        max_dense = max(dense_retrieved.values()) if dense_retrieved and max(dense_retrieved.values()) > 0 else 1.0
        max_bm25 = max(bm25_retrieved.values()) if bm25_retrieved and max(bm25_retrieved.values()) > 0 else 1.0

        topsis_map = {r.candidate_id: r for r in topsis_results}
        laya_map = {r.candidate_id: r for r in laya_results}
        weighted_map = {r.candidate_id: r for r in weighted_results}
        rrf_map = {r.candidate_id: r for r in rrf_results}

        # 2. Compute consensus across candidates
        scored_candidates = []
        cand_dict = {c.candidate_id: c for c in candidates}

        # Model weights in symbiosis (equal default 1/6th)
        w_topsis = float(cfg.get("w_topsis", 0.20))
        w_laya = float(cfg.get("w_laya", 0.20))
        w_weighted = float(cfg.get("w_weighted", 0.20))
        w_rrf = float(cfg.get("w_rrf", 0.20))
        w_dense = float(cfg.get("w_dense", 0.10))
        w_bm25 = float(cfg.get("w_bm25", 0.10))
        w_total = (w_topsis + w_laya + w_weighted + w_rrf + w_dense + w_bm25) or 1.0

        for cand in candidates:
            cid = cand.candidate_id
            s_top = topsis_map[cid].score if cid in topsis_map else 0.5
            s_lay = laya_map[cid].score if cid in laya_map else 0.5
            s_wgt = weighted_map[cid].score if cid in weighted_map else 0.5
            s_rrf = rrf_map[cid].score if cid in rrf_map else 0.5
            s_den = max(0.0, min(dense_retrieved.get(cid, 0.0) / max_dense, 1.0))
            s_bm = max(0.0, min(bm25_retrieved.get(cid, 0.0) / max_bm25, 1.0))

            consensus_score = (
                w_topsis * s_top
                + w_laya * s_lay
                + w_weighted * s_wgt
                + w_rrf * s_rrf
                + w_dense * s_den
                + w_bm25 * s_bm
            ) / w_total

            # Cross-model agreement metric (1.0 - standard deviation of the 6 scores)
            scores_list = [s_top, s_lay, s_wgt, s_rrf, s_den, s_bm]
            mean_score = sum(scores_list) / len(scores_list)
            variance = sum((x - mean_score) ** 2 for x in scores_list) / len(scores_list)
            std_dev = math.sqrt(variance)
            agreement_rate = max(0.0, min(1.0 - std_dev, 1.0))

            component_scores = {
                "topsis_score": round(s_top, 4),
                "topsis_rank": topsis_map[cid].rank if cid in topsis_map else 0,
                "laya_score": round(s_lay, 4),
                "laya_rank": laya_map[cid].rank if cid in laya_map else 0,
                "weighted_score": round(s_wgt, 4),
                "weighted_rank": weighted_map[cid].rank if cid in weighted_map else 0,
                "rrf_score": round(s_rrf, 4),
                "rrf_rank": rrf_map[cid].rank if cid in rrf_map else 0,
                "dense_score": round(s_den, 4),
                "bm25_score": round(s_bm, 4),
                "model_agreement_rate": round(agreement_rate, 4),
                "consensus_score": round(consensus_score, 4),
            }

            # Citations from candidate evidence
            citations = [s.evidence for s in cand.skills if s.evidence is not None]

            scored_candidates.append({
                "candidate_id": cid,
                "score": float(consensus_score),
                "component_scores": component_scores,
                "evidence_citations": citations[:6],
                "uncertainty_markers": cand.uncertainty_flags,
            })

        # 3. Sort descending by consensus score
        scored_candidates.sort(key=lambda x: x["score"], reverse=True)

        results = []
        for rank_1b, entry in enumerate(scored_candidates, start=1):
            results.append(
                RankingResult(
                    candidate_id=entry["candidate_id"],
                    job_id=job.job_id,
                    rank=rank_1b,
                    score=entry["score"],
                    model_name="ensemble_symbiosis",
                    component_scores=entry["component_scores"],
                    evidence_citations=entry["evidence_citations"],
                    uncertainty_markers=entry["uncertainty_markers"],
                    run_id=run_id,
                )
            )

        return results
