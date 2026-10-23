"""
Module: packages.fairness.counterfactual
Description:
    Controlled identity perturbation suite for counterfactual fairness auditing.
    - Swaps names, pronouns, and demographic markers in candidate profiles.
    - Measures rank shift (Delta rank), Kendall's Tau correlation, and shortlist threshold crossings.
    - Operates under strict diagnostic boundary (does not infer real demographics from text).

Author:
    Resume Intelligence Architect
"""
import re
from typing import List, Dict, Any, Tuple
from scipy.stats import kendalltau

from packages.common.schemas import JobDescription, ResumeProfile, RankingResult
from packages.ranking.base import BaseRanker

# Name and pronoun perturbation mappings
NAME_SWAPS = {
    "john": "jane",
    "david": "sarah",
    "michael": "emily",
    "robert": "jessica",
    "james": "amanda",
    "jane": "john",
    "sarah": "david",
    "emily": "michael",
    "jessica": "robert",
    "amanda": "james",
}

PRONOUN_SWAPS = {
    r"\bhe\b": "she",
    r"\bhim\b": "her",
    r"\bhis\b": "her",
    r"\bshe\b": "he",
    r"\bher\b": "him",
}

class CounterfactualAuditor:
    """
    Audits ranker sensitivity to identity counterfactual perturbations.
    """

    @classmethod
    def perturb_profile(cls, profile: ResumeProfile) -> ResumeProfile:
        """
        Creates a counterfactual clone of a candidate profile with perturbed identity markers.
        """
        # Perturb summary if present
        perturbed_summary = profile.summary
        if perturbed_summary:
            text = perturbed_summary

            # 1. Pronoun swaps (single-pass)
            pronoun_map = {
                "he": "she", "she": "he",
                "him": "her", "her": "him",
                "his": "her",
            }
            pronoun_pattern = re.compile(r"\b(" + "|".join(pronoun_map.keys()) + r")\b", re.IGNORECASE)
            def _replace_pronoun(m: re.Match) -> str:
                w = m.group(0).lower()
                repl = pronoun_map.get(w, w)
                return repl.capitalize() if m.group(0).istitle() else repl

            text = pronoun_pattern.sub(_replace_pronoun, text)

            # 2. Name swaps (single-pass)
            name_pattern = re.compile(r"\b(" + "|".join(re.escape(k) for k in NAME_SWAPS.keys()) + r")\b", re.IGNORECASE)
            def _replace_name(m: re.Match) -> str:
                w = m.group(0).lower()
                repl = NAME_SWAPS.get(w, w)
                return repl.capitalize() if m.group(0).istitle() else repl

            text = name_pattern.sub(_replace_name, text)
            perturbed_summary = text

        return profile.model_copy(
            update={
                "candidate_id": f"{profile.candidate_id}_cf",
                "summary": perturbed_summary,
            }
        )

    @classmethod
    def audit_ranker(
        cls,
        ranker: BaseRanker,
        job: JobDescription,
        candidates: List[ResumeProfile],
        top_k: int = 5,
    ) -> Dict[str, Any]:
        """
        Ranks original candidates, then ranks perturbed counterfactuals,
        and computes rank shifts and Kendall's Tau correlation.

        Returns:
            Dict containing:
            - kendall_tau: float in [-1.0, 1.0]
            - p_value: float
            - shortlist_crossings: int (number of candidates crossing Top-K threshold)
            - max_rank_shift: int
            - rank_shifts: dict of {candidate_id: delta_rank}
            - warning: disclaimer notice
        """
        if len(candidates) < 2:
            return {"kendall_tau": 1.0, "p_value": 1.0, "shortlist_crossings": 0, "max_rank_shift": 0, "rank_shifts": {}}

        # 1. Baseline ranking
        base_results = ranker.rank(job, candidates, run_id="audit_baseline")
        base_ranks = {r.candidate_id: r.rank for r in base_results}

        # 2. Perturbed ranking
        cf_candidates = [cls.perturb_profile(c) for c in candidates]
        cf_results = ranker.rank(job, cf_candidates, run_id="audit_counterfactual")
        cf_ranks = {r.candidate_id.replace("_cf", ""): r.rank for r in cf_results}

        # 3. Calculate rank shifts
        rank_shifts = {}
        crossings = 0
        max_shift = 0

        y_base = []
        y_cf = []

        for cid, b_rank in base_ranks.items():
            c_rank = cf_ranks.get(cid, b_rank)
            shift = abs(b_rank - c_rank)
            rank_shifts[cid] = b_rank - c_rank
            max_shift = max(max_shift, shift)

            # Check if candidate crossed Top-K shortlist boundary
            in_base_topk = b_rank <= top_k
            in_cf_topk = c_rank <= top_k
            if in_base_topk != in_cf_topk:
                crossings += 1

            y_base.append(b_rank)
            y_cf.append(c_rank)

        # 4. Compute Kendall's Tau rank correlation
        tau, p_val = kendalltau(y_base, y_cf)
        if math.isnan(tau):
            tau = 1.0

        return {
            "kendall_tau": float(tau),
            "p_value": float(p_val) if not math.isnan(p_val) else 1.0,
            "shortlist_crossings": int(crossings),
            "max_rank_shift": int(max_shift),
            "rank_shifts": rank_shifts,
            "warning": (
                "Counterfactual diagnostic aid only. High stability does not guarantee lack of bias. "
                "Advisory metric for recruiter auditing."
            ),
        }
import math
