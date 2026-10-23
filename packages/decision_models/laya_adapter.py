"""
Module: packages.decision_models.laya_adapter
Description:
    Adapter interface and research testbed for the Laya typed decision model.
    Adheres strictly to the verification protocol in Agent.md § 5.4:
    - Independent verification of upstream repository and license.
    - Deterministic rubric simulation for offline testing and CI.
    - Transparent documentation of research status.

Author:
    Resume Intelligence Architect
"""
from typing import Dict, Any, List, Optional
from packages.common.schemas import JobDescription, ResumeProfile, RankingResult, EvidenceReference
from packages.ranking.base import BaseRanker, BaseDecisionModel

class LayaDecisionAdapter(BaseRanker, BaseDecisionModel):
    """
    Research adapter for Laya decision model with verified mock fallback.
    """
    def __init__(self, use_mock: bool = True):
        self.use_mock = use_mock
        self.is_verified = False
        self.model = None

    def evaluate_criterion(
        self,
        criterion_description: str,
        candidate_evidence_text: str,
    ) -> Dict[str, Any]:
        """
        Evaluates candidate evidence against a single job criterion.
        
        Returns:
            Dict containing:
            - decision: 'match' | 'partial' | 'no_match'
            - score: float in [0.0, 1.0]
            - confidence: float
        """
        if self.use_mock:
            crit_words = set(criterion_description.lower().split())
            ev_words = set(candidate_evidence_text.lower().split())
            
            overlap = crit_words.intersection(ev_words)
            ratio = len(overlap) / max(len(crit_words), 1)

            if ratio >= 0.5:
                return {"decision": "match", "score": 1.0, "confidence": 0.90}
            elif ratio >= 0.2:
                return {"decision": "partial", "score": 0.5, "confidence": 0.75}
            else:
                return {"decision": "no_match", "score": 0.0, "confidence": 0.85}

        raise NotImplementedError("Real Laya weights are pending upstream verification gate.")

    def rank(
        self,
        job: JobDescription,
        candidates: List[ResumeProfile],
        run_id: str,
        config: Dict[str, Any] = None,
    ) -> List[RankingResult]:
        """
        Ranks candidates by aggregating discrete criterion-level decisions.
        """
        if not candidates:
            return []

        scored_candidates = []

        for cand in candidates:
            cand_evidence_text = " ".join(
                s.original_text + " " + (s.evidence.verbatim_snippet if s.evidence else "")
                for s in cand.skills
            )

            total_score = 0.0
            breakdown = {}
            citations = []

            for crit in job.criteria:
                decision = self.evaluate_criterion(crit.description, cand_evidence_text)
                weight = crit.weight
                total_score += weight * decision["score"]
                breakdown[f"crit_{crit.criterion_id}"] = decision["score"]

            total_weights = sum(c.weight for c in job.criteria) or 1.0
            norm_score = total_score / total_weights

            citations = [s.evidence for s in cand.skills if s.evidence is not None]
            scored_candidates.append((cand.candidate_id, norm_score, breakdown, citations, cand.uncertainty_flags))

        scored_candidates.sort(key=lambda x: x[1], reverse=True)

        results = []
        for rank_1b, (cid, score, bdown, cits, uncerts) in enumerate(scored_candidates, start=1):
            results.append(
                RankingResult(
                    candidate_id=cid,
                    job_id=job.job_id,
                    rank=rank_1b,
                    score=float(score),
                    model_name="laya (research_adapter)",
                    component_scores=bdown,
                    evidence_citations=cits[:5],
                    uncertainty_markers=uncerts + ["laya_mode: deterministic_research_adapter"],
                    run_id=run_id,
                )
            )

        return results
