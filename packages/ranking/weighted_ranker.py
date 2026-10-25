"""
Module: packages.ranking.weighted_ranker
Description:
    Transparent, reviewable Weighted Criterion Scoring decision model.
    Scores candidates directly against explicitly weighted job requirements:
        Score = ( sum(w_j * score_ij) ) / ( sum(w_j) )
    Where missing evidence is penalized and explicitly marked.

Author:
    Resume Intelligence Architect
"""
from typing import List, Dict, Any, Tuple
from packages.common.schemas import JobDescription, ResumeProfile, RankingResult, EvidenceReference
from packages.ranking.base import BaseRanker

class WeightedScorer(BaseRanker):
    """
    Transparent multi-attribute scoring model evaluating candidates against explicit criteria.
    """
    def rank(
        self,
        job: JobDescription,
        candidates: List[ResumeProfile],
        run_id: str,
        config: Dict[str, Any] = None,
    ) -> List[RankingResult]:
        """Ranks candidates by weighted criterion fulfillment."""
        if not candidates or not job.criteria:
            return []

        weights = [c.weight for c in job.criteria]
        total_weight = sum(weights) if sum(weights) > 0 else 1.0

        cfg = config or {}
        raw_crit_pct = float(cfg.get("criteria_weight_pct", 80.0))
        raw_exp_pct = float(cfg.get("experience_weight_pct", 20.0))
        total_raw = raw_crit_pct + raw_exp_pct
        if total_raw > 0:
            criteria_weight = raw_crit_pct / total_raw
            experience_weight = raw_exp_pct / total_raw
        else:
            criteria_weight = 0.80
            experience_weight = 0.20

        candidate_scores = []

        for cand in candidates:
            cand_skill_texts = {s.original_text.lower() for s in cand.skills}
            cand_esco_uris = {s.esco_concept_uri for s in cand.skills if s.esco_concept_uri}
            
            weighted_sum = 0.0
            criterion_breakdown = {}
            uncertainty_markers = list(cand.uncertainty_flags)
            supporting_citations = []

            for crit in job.criteria:
                w = crit.weight
                desc_lower = crit.description.lower()
                
                # Check for direct skill match
                is_matched = False
                matched_skill = None
                for s in cand.skills:
                    if s.original_text.lower() in desc_lower or desc_lower in s.original_text.lower():
                        is_matched = True
                        matched_skill = s
                        break
                    if crit.associated_esco_uri and s.esco_concept_uri == crit.associated_esco_uri:
                        is_matched = True
                        matched_skill = s
                        break

                if is_matched:
                    crit_score = 1.0
                    if matched_skill and matched_skill.evidence:
                        supporting_citations.append(matched_skill.evidence)
                else:
                    crit_score = 0.0
                    if crit.is_required:
                        uncertainty_markers.append(f"missing_required:{crit.description[:30]}")

                weighted_sum += w * crit_score
                criterion_breakdown[f"crit_{crit.criterion_id}"] = crit_score

            # Experience alignment bonus / factor
            if job.minimum_experience_years and job.minimum_experience_years > 0:
                exp_ratio = min(cand.total_experience_years / job.minimum_experience_years, 1.2) / 1.2
            else:
                exp_ratio = 1.0
                
            criterion_ratio = weighted_sum / total_weight
            criterion_breakdown["experience_ratio"] = round(exp_ratio, 4)
            criterion_breakdown["criteria_score"] = round(criterion_ratio, 4)
            criterion_breakdown["req_coverage"] = round(criterion_ratio, 4)
            criterion_breakdown["exp_score"] = round(exp_ratio, 4)
            criterion_breakdown["criteria_weight_pct"] = round(criteria_weight * 100.0, 1)
            criterion_breakdown["experience_weight_pct"] = round(experience_weight * 100.0, 1)

            # Dynamic composite score using configured percentage weights
            final_score = criteria_weight * criterion_ratio + experience_weight * exp_ratio

            candidate_scores.append((cand.candidate_id, final_score, criterion_breakdown, supporting_citations, uncertainty_markers))

        # Sort descending by score
        candidate_scores.sort(key=lambda x: x[1], reverse=True)

        results = []
        for rank_1b, (cid, score, breakdown, citations, uncert) in enumerate(candidate_scores, start=1):
            results.append(
                RankingResult(
                    candidate_id=cid,
                    job_id=job.job_id,
                    rank=rank_1b,
                    score=float(score),
                    model_name="weighted",
                    component_scores=breakdown,
                    evidence_citations=citations[:5],
                    uncertainty_markers=uncert,
                    run_id=run_id,
                )
            )

        return results
