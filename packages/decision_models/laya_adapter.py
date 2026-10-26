"""
================================================================================
Open-Source Resume Intelligence, Ranking & Fairness Lab
Module: packages.decision_models.laya_adapter
================================================================================
Official integration of the Laya System-1 Decision Model:
- Model: convaiinnovations/laya (ModernBERT-large 421M non-autoregressive decision model)
- Library: official 'laya' Python package (pip install laya)
- Method: Evaluates candidate evidence against typed choice questions in a single forward pass
- Output: Strict discrete decisions ('match': 1.0, 'partial': 0.5, 'no_match': 0.0)
          alongside calibrated Bayesian-style confidence probabilities
- Resilience: Graceful fallback to deterministic rubric if offline or during fast testing
================================================================================
"""

import logging
from typing import Dict, Any, List, Optional
from packages.common.schemas import JobDescription, ResumeProfile, RankingResult, EvidenceReference
from packages.ranking.base import BaseRanker, BaseDecisionModel

logger = logging.getLogger(__name__)

# Module-level cached Laya agent to avoid reloading weights repeatedly
_CACHED_LAYA_AGENT = None
_LAYA_LOAD_FAILED = False


def get_laya_agent(device: Optional[str] = None):
    """
    Lazy loader for the official convaiinnovations/laya decision model.
    Caches the loaded agent in memory.
    """
    global _CACHED_LAYA_AGENT, _LAYA_LOAD_FAILED
    if _CACHED_LAYA_AGENT is not None:
        return _CACHED_LAYA_AGENT
    if _LAYA_LOAD_FAILED:
        return None

    try:
        import laya
        logger.info("Initializing official Laya decision model (convaiinnovations/laya)...")
        _CACHED_LAYA_AGENT = laya.load("convaiinnovations/laya", device=device)
        logger.info("Successfully loaded Laya System-1 Decision Model.")
        return _CACHED_LAYA_AGENT
    except Exception as exc:
        logger.warning(
            f"Unable to load real Laya model from Hugging Face ({exc}). "
            f"Operating in deterministic rubric fallback mode."
        )
        _LAYA_LOAD_FAILED = True
        return None


class LayaDecisionAdapter(BaseRanker, BaseDecisionModel):
    """
    Production adapter interfacing with the official Laya non-autoregressive decision model.
    Falls back gracefully to a deterministic criteria rubric if offline or uninitialized.
    """

    def __init__(self, use_mock: bool = False, device: Optional[str] = None):
        """
        Args:
            use_mock: If True, forces deterministic rubric execution (useful for CI/unit tests).
                      If False, attempts real neural inference via convaiinnovations/laya.
            device: Optional torch device string ('cuda', 'cpu'). If None, Laya auto-detects.
        """
        self.use_mock = use_mock
        self.device = device
        self._agent = None if use_mock else get_laya_agent(device=device)

    @property
    def is_neural_active(self) -> bool:
        """Returns True if the real neural Laya model is currently loaded in memory."""
        return self._agent is not None and not self.use_mock

    def evaluate_criterion(
        self,
        criterion_description: str,
        candidate_evidence_text: str,
    ) -> Dict[str, Any]:
        """
        Evaluates candidate evidence against a single job criterion using Laya's typed choice primitive.

        Returns:
            Dict containing:
            - decision: 'match' | 'partial' | 'no_match'
            - score: float in [0.0, 1.0] (1.0 for match, 0.5 for partial, 0.0 for no_match)
            - confidence: float calibrated confidence probability
            - is_neural: bool indicating whether neural inference was executed
        """
        # 1. Attempt real neural inference if agent is active
        if self.is_neural_active:
            try:
                state = {
                    "evidence": candidate_evidence_text[:2500] if candidate_evidence_text else "No evidence provided."
                }
                questions = {
                    "criterion_match": {
                        "type": "choice",
                        "instructions": (
                            f"Evaluate whether the candidate's verified evidence satisfies the requirement: "
                            f"'{criterion_description}'"
                        ),
                        "criteria": {
                            "match": "Evidence explicitly demonstrates full competence or meets the requirement",
                            "partial": "Evidence demonstrates related, foundational, or partial competence",
                            "no_match": "No supporting evidence found or candidate fails the requirement",
                        },
                    }
                }
                prediction = self._agent.predict(state, questions)
                eval_res = prediction.get("criterion_match", {})
                decision = str(eval_res.get("answer", "no_match")).lower()
                confidence = float(eval_res.get("confidence", 0.85))

                if decision == "match":
                    score = 1.0
                elif decision == "partial":
                    score = 0.5
                else:
                    decision = "no_match"
                    score = 0.0

                return {
                    "decision": decision,
                    "score": score,
                    "confidence": confidence,
                    "is_neural": True,
                }
            except Exception as e:
                logger.debug(f"Laya neural inference error for criterion '{criterion_description}': {e}. Using fallback.")

        # 2. Deterministic fallback rubric (keyword & ontology overlap)
        crit_words = set(w for w in criterion_description.lower().split() if len(w) > 2)
        ev_words = set(w for w in candidate_evidence_text.lower().split() if len(w) > 2)

        if not crit_words:
            return {"decision": "no_match", "score": 0.0, "confidence": 0.5, "is_neural": False}

        overlap = crit_words.intersection(ev_words)
        ratio = len(overlap) / max(len(crit_words), 1)

        if ratio >= 0.5:
            return {"decision": "match", "score": 1.0, "confidence": 0.90, "is_neural": False}
        elif ratio >= 0.2:
            return {"decision": "partial", "score": 0.5, "confidence": 0.75, "is_neural": False}
        else:
            return {"decision": "no_match", "score": 0.0, "confidence": 0.85, "is_neural": False}

    def rank(
        self,
        job: JobDescription,
        candidates: List[ResumeProfile],
        run_id: str,
        config: Dict[str, Any] = None,
    ) -> List[RankingResult]:
        """
        Ranks candidates by aggregating discrete criterion-level decisions across the job specification.
        """
        if not candidates:
            return []

        scored_candidates = []
        is_neural = self.is_neural_active

        for cand in candidates:
            cand_evidence_text = " ".join(
                s.original_text + " " + (s.evidence.verbatim_snippet if s.evidence else "")
                for s in cand.skills
            )

            total_score = 0.0
            breakdown = {}
            confidences = []

            for crit in job.criteria:
                decision = self.evaluate_criterion(crit.description, cand_evidence_text)
                weight = crit.weight
                total_score += weight * decision["score"]
                breakdown[f"crit_{crit.criterion_id}"] = decision["score"]
                confidences.append(decision.get("confidence", 0.8))

            total_weights = sum(c.weight for c in job.criteria) or 1.0
            norm_score = total_score / total_weights
            avg_conf = sum(confidences) / max(len(confidences), 1)
            breakdown["avg_confidence"] = round(avg_conf, 3)

            citations = [s.evidence for s in cand.skills if s.evidence is not None]
            scored_candidates.append(
                (cand.candidate_id, norm_score, breakdown, citations, cand.uncertainty_flags)
            )

        scored_candidates.sort(key=lambda x: x[1], reverse=True)

        results = []
        model_label = (
            "laya (convaiinnovations/laya System-1)"
            if is_neural
            else "laya (deterministic_rubric_fallback)"
        )

        for rank_1b, (cid, score, bdown, cits, uncerts) in enumerate(scored_candidates, start=1):
            results.append(
                RankingResult(
                    candidate_id=cid,
                    job_id=job.job_id,
                    rank=rank_1b,
                    score=float(score),
                    model_name=model_label,
                    component_scores=bdown,
                    evidence_citations=cits[:5],
                    uncertainty_markers=uncerts + [f"laya_engine: {'neural_modernbert' if is_neural else 'deterministic_rubric'}"],
                    run_id=run_id,
                )
            )

        return results
