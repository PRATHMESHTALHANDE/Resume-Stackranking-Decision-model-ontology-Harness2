"""
Module: packages.ranking.lambdamart_ranker
Description:
    Supervised Learning-to-Rank ranker using LightGBM LambdaMART.
    - Directly optimizes nDCG on query-grouped candidate feature matrices.
    - Saves model checkpoints to models/weights/lightgbm/.
    - Features: BM25 score, cosine similarity, required coverage, preferred coverage, experience years.
    - Gracefully falls back to TOPSIS if trained checkpoint is not yet present.

Author:
    Resume Intelligence Architect
"""
import numpy as np
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional

from packages.common.settings import LIGHTGBM_WEIGHTS_DIR
from packages.common.schemas import JobDescription, ResumeProfile, RankingResult
from packages.ranking.base import BaseRanker
from packages.ranking.topsis_ranker import TOPSISRanker
from packages.ranking.bm25_ranker import BM25Ranker
from packages.ranking.dense_ranker import DenseRanker

try:
    import lightgbm as lgb
except ImportError:
    lgb = None

class LambdaMARTRanker(BaseRanker):
    """
    Supervised Learning-to-Rank booster optimizing nDCG on candidate feature vectors.
    """
    def __init__(self, model_file: str = "lambdamart.txt"):
        self.model_path = LIGHTGBM_WEIGHTS_DIR / model_file
        self.booster: Optional[Any] = None
        self.bm25 = BM25Ranker()
        self.dense = DenseRanker()
        self.topsis_fallback = TOPSISRanker()
        self._load_model()

    def _load_model(self) -> None:
        """Loads saved LightGBM Booster if checkpoint exists."""
        if lgb is not None and self.model_path.exists():
            try:
                self.booster = lgb.Booster(model_file=str(self.model_path))
            except Exception:
                self.booster = None

    def extract_features(self, job: JobDescription, candidates: List[ResumeProfile]) -> np.ndarray:
        """
        Extracts 5-dimensional feature matrix for query-candidate pairs:
        [BM25 Score, Dense Cosine Sim, Required Coverage, Preferred Coverage, Experience Years]
        """
        bm25_scores = dict(self.bm25.retrieve(job, candidates, top_k=len(candidates)))
        dense_scores = dict(self.dense.retrieve(job, candidates, top_k=len(candidates)))

        job_reqs = {c.description.lower() for c in job.criteria if c.is_required}
        job_prefs = {c.description.lower() for c in job.criteria if not c.is_required}

        features = np.zeros((len(candidates), 5), dtype=np.float32)

        for i, c in enumerate(candidates):
            cand_skills = {s.original_text.lower() for s in c.skills}
            
            req_matched = sum(1 for r in job_reqs if any(r in s or s in r for s in cand_skills))
            req_cov = (req_matched / len(job_reqs)) if job_reqs else 1.0

            pref_matched = sum(1 for p in job_prefs if any(p in s or s in pref for s in cand_skills))
            pref_cov = (pref_matched / len(job_prefs)) if job_prefs else 1.0

            bm25_s = bm25_scores.get(c.candidate_id, 0.0)
            dense_s = dense_scores.get(c.candidate_id, 0.5)
            exp_yrs = float(c.total_experience_years)

            features[i] = [bm25_s, dense_s, req_cov, pref_cov, exp_yrs]

        return features

    def train_model(self, X: np.ndarray, y: np.ndarray, groups: List[int]) -> None:
        """
        Trains LightGBM model with 'lambdarank' objective.

        Args:
            X: 2D feature matrix.
            y: Graded relevance labels (0 to 3).
            groups: Query group sizes (e.g. [15, 20, 18]).
        """
        if lgb is None:
            return

        train_data = lgb.Dataset(X, label=y, group=groups)
        params = {
            "objective": "lambdarank",
            "metric": "ndcg",
            "ndcg_eval_at": [5, 10],
            "learning_rate": 0.05,
            "num_leaves": 31,
            "min_data_in_leaf": 5,
            "verbose": -1,
            "seed": 42,
        }
        self.booster = lgb.train(params, train_data, num_boost_round=50)
        self.model_path.parent.mkdir(parents=True, exist_ok=True)
        self.booster.save_model(str(self.model_path))

    def rank(
        self,
        job: JobDescription,
        candidates: List[ResumeProfile],
        run_id: str,
        config: Dict[str, Any] = None,
    ) -> List[RankingResult]:
        """Ranks candidates using trained LambdaMART model or TOPSIS fallback."""
        if not candidates:
            return []

        if self.booster is None:
            # Fallback cleanly to TOPSIS with an informative notice
            fallback_results = self.topsis_fallback.rank(job, candidates, run_id, config)
            return [
                r.model_copy(
                    update={
                        "model_name": "lambdamart (fallback: topsis)",
                        "uncertainty_markers": r.uncertainty_markers + ["lambdamart_untrained: using unsupervised TOPSIS fallback"],
                    }
                )
                for r in fallback_results
            ]

        # Predict ranking scores with trained booster
        features = self.extract_features(job, candidates)
        raw_scores = self.booster.predict(features)

        # Normalize predicted scores to [0.0, 1.0] using sigmoid
        scores = 1.0 / (1.0 + np.exp(-raw_scores))

        sorted_indices = np.argsort(-scores)
        candidate_map = {c.candidate_id: c for c in candidates}
        results = []

        for rank_1b, idx in enumerate(sorted_indices, start=1):
            cand = candidates[idx]
            citations = [s.evidence for s in cand.skills if s.evidence is not None]

            results.append(
                RankingResult(
                    candidate_id=cand.candidate_id,
                    job_id=job.job_id,
                    rank=rank_1b,
                    score=float(scores[idx]),
                    model_name="lambdamart",
                    component_scores={"lambdamart_score": float(scores[idx])},
                    evidence_citations=citations[:5],
                    uncertainty_markers=cand.uncertainty_flags,
                    run_id=run_id,
                )
            )

        return results
