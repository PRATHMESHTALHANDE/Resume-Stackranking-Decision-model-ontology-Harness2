"""
Module: packages.ranking.topsis_ranker
Description:
    TOPSIS (Technique for Order of Preference by Similarity to Ideal Solution)
    multi-criteria decision ranker.
    Evaluates candidates geometrically across 5 normalized dimensions:
    1. Required skill coverage (benefit)
    2. Preferred skill coverage (benefit)
    3. Total experience years (benefit)
    4. Missing required requirement penalty (cost)
    5. Semantic vector alignment score (benefit)

Author:
    Resume Intelligence Architect
"""
import numpy as np
from typing import List, Dict, Any, Tuple

from packages.common.schemas import JobDescription, ResumeProfile, RankingResult
from packages.ranking.base import BaseRanker
from packages.ranking.dense_ranker import DenseRanker

class TOPSISRanker(BaseRanker):
    """
    Ranks candidates using TOPSIS multi-attribute decision analysis.
    """
    def __init__(self, weights: List[float] = None, criteria_types: List[str] = None):
        # Default weights: [ReqCoverage: 0.35, PrefCoverage: 0.15, ExpYears: 0.20, MissingPenalty: 0.15, SemanticSim: 0.15]
        self.weights = np.array(weights or [0.35, 0.15, 0.20, 0.15, 0.15], dtype=np.float64)
        self.weights /= np.sum(self.weights)
        self.types = criteria_types or ["benefit", "benefit", "benefit", "cost", "benefit"]
        self.dense = DenseRanker()

    def rank(
        self,
        job: JobDescription,
        candidates: List[ResumeProfile],
        run_id: str,
        config: Dict[str, Any] = None,
    ) -> List[RankingResult]:
        """Calculates TOPSIS relative closeness to ideal candidate profile."""
        if not candidates:
            return []

        # 1. Retrieve semantic cosine alignment
        semantic_scores = dict(self.dense.retrieve(job, candidates, top_k=len(candidates)))

        # 2. Build Decision Matrix (n_candidates x 5 criteria)
        n = len(candidates)
        matrix = np.zeros((n, 5), dtype=np.float64)
        candidate_ids = []

        job_req_skills = {c.description.lower() for c in job.criteria if c.is_required}
        job_pref_skills = {c.description.lower() for c in job.criteria if not c.is_required}

        for i, cand in enumerate(candidates):
            candidate_ids.append(cand.candidate_id)
            cand_skills = {s.original_text.lower() for s in cand.skills}

            # Criterion 1: Required coverage
            matched_req = sum(1 for req in job_req_skills if any(req in s or s in req for s in cand_skills))
            req_coverage = (matched_req / len(job_req_skills)) if job_req_skills else 1.0

            # Criterion 2: Preferred coverage
            matched_pref = sum(1 for pref in job_pref_skills if any(pref in s or s in pref for s in cand_skills))
            pref_coverage = (matched_pref / len(job_pref_skills)) if job_pref_skills else 1.0

            # Criterion 3: Experience years
            exp_years = float(cand.total_experience_years)

            # Criterion 4: Missing required requirements count (cost criterion)
            missing_count = float(len(job_req_skills) - matched_req)

            # Criterion 5: Semantic similarity score
            sem_sim = float(semantic_scores.get(cand.candidate_id, 0.5))

            matrix[i] = [req_coverage, pref_coverage, exp_years, missing_count, sem_sim]

        # 3. Vector Normalization: r_ij = x_ij / sqrt(sum(x_kj^2))
        col_norms = np.sqrt(np.sum(matrix ** 2, axis=0))
        col_norms[col_norms == 0] = 1.0
        norm_matrix = matrix / col_norms

        # 4. Weighted Normalized Matrix: v_ij = w_j * r_ij
        weighted_matrix = norm_matrix * self.weights

        # 5. Determine Positive (Ideal) and Negative (Anti-Ideal) Solutions
        ideal_pos = np.zeros(5)
        ideal_neg = np.zeros(5)

        for j, c_type in enumerate(self.types):
            if c_type == "benefit":
                ideal_pos[j] = np.max(weighted_matrix[:, j])
                ideal_neg[j] = np.min(weighted_matrix[:, j])
            else: # cost criteria
                ideal_pos[j] = np.min(weighted_matrix[:, j])
                ideal_neg[j] = np.max(weighted_matrix[:, j])

        # 6. Euclidean Distances: S_i^+ = sqrt(sum((v_ij - v_j^+)^2))
        dist_pos = np.sqrt(np.sum((weighted_matrix - ideal_pos) ** 2, axis=1))
        dist_neg = np.sqrt(np.sum((weighted_matrix - ideal_neg) ** 2, axis=1))

        # 7. Relative Closeness: C_i = S_i^- / (S_i^+ + S_i^-)
        denominator = dist_pos + dist_neg
        denominator[denominator == 0] = 1.0
        closeness = dist_neg / denominator

        # Sort descending by closeness score
        sorted_indices = np.argsort(-closeness)

        candidate_map = {c.candidate_id: c for c in candidates}
        results = []

        for rank_1b, idx in enumerate(sorted_indices, start=1):
            cid = candidate_ids[idx]
            cand = candidate_map[cid]
            citations = [s.evidence for s in cand.skills if s.evidence is not None]

            results.append(
                RankingResult(
                    candidate_id=cid,
                    job_id=job.job_id,
                    rank=rank_1b,
                    score=float(closeness[idx]),
                    model_name="topsis",
                    component_scores={
                        "topsis_closeness": float(closeness[idx]),
                        "dist_to_ideal": float(dist_pos[idx]),
                        "dist_to_anti_ideal": float(dist_neg[idx]),
                    },
                    evidence_citations=citations[:5],
                    uncertainty_markers=cand.uncertainty_flags,
                    run_id=run_id,
                )
            )

        return results
