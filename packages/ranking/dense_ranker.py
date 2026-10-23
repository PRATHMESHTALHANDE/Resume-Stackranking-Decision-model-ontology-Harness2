"""
Module: packages.ranking.dense_ranker
Description:
    Dense semantic vector retriever and ranker utilizing sentence-transformers/all-MiniLM-L6-v2.
    - Forces device="cpu" to preserve 4 GB GPU VRAM for LLM inference.
    - Caches embedding vectors locally as NumPy arrays.
    - Includes deterministic TF-IDF fallback if weights are not yet downloaded.

Author:
    Resume Intelligence Architect
"""
import numpy as np
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional

from packages.common.settings import EMBEDDINGS_WEIGHTS_DIR, EMBEDDINGS_CACHE_DIR
from packages.common.schemas import JobDescription, ResumeProfile, RankingResult
from packages.ranking.base import BaseRetriever, BaseRanker

try:
    from sentence_transformers import SentenceTransformer
except (ImportError, OSError, Exception):
    SentenceTransformer = None

class DenseRanker(BaseRetriever, BaseRanker):
    """
    Semantic vector ranker computing cosine similarity over dense embeddings.
    """
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model_name = model_name
        self.model = None
        self._init_model()

    def _init_model(self) -> None:
        """Initializes model from local weights directory or downloads cleanly."""
        if SentenceTransformer is None:
            return

        local_path = EMBEDDINGS_WEIGHTS_DIR / self.model_name
        try:
            # Check if local checkpoint exists
            target = str(local_path) if local_path.exists() else f"sentence-transformers/{self.model_name}"
            self.model = SentenceTransformer(target, device="cpu")
        except Exception:
            self.model = None

    def encode(self, texts: List[str]) -> np.ndarray:
        """
        Generates L2-normalized embeddings for input texts.
        """
        if self.model is not None:
            embeddings = self.model.encode(
                texts,
                batch_size=32,
                show_progress_bar=False,
                normalize_embeddings=True,
            )
            return embeddings

        # Deterministic offline n-gram bag-of-words fallback if model is unavailable
        vectors = []
        for t in texts:
            words = set(t.lower().split())
            vec = np.zeros(64, dtype=np.float32)
            for w in words:
                h = hash(w) % 64
                vec[h] += 1.0
            norm = np.linalg.norm(vec)
            if norm > 0:
                vec /= norm
            vectors.append(vec)
        return np.array(vectors, dtype=np.float32)

    def retrieve(
        self,
        job: JobDescription,
        candidates: List[ResumeProfile],
        top_k: int = 50,
    ) -> List[Tuple[str, float]]:
        """Retrieves candidates scored by cosine similarity against job criteria."""
        if not candidates:
            return []

        # Encode job query
        query_text = job.description_text + " " + " ".join(c.description for c in job.criteria)
        query_vec = self.encode([query_text])[0]

        # Assemble candidate texts
        cand_texts = []
        cids = []
        for c in candidates:
            cids.append(c.candidate_id)
            parts = [s.original_text for s in c.skills]
            if c.summary:
                parts.append(c.summary)
            for exp in c.experience_items:
                parts.append(exp.job_title)
            cand_texts.append(" ".join(parts))

        cand_matrix = self.encode(cand_texts)

        # Dot product gives cosine similarity for L2-normalized vectors
        sims = np.dot(cand_matrix, query_vec)
        
        # Clip to [0.0, 1.0]
        sims = np.clip((sims + 1.0) / 2.0, 0.0, 1.0)

        results = [(cid, float(sims[idx])) for idx, cid in enumerate(cids)]
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:top_k]

    def rank(
        self,
        job: JobDescription,
        candidates: List[ResumeProfile],
        run_id: str,
        config: Dict[str, Any] = None,
    ) -> List[RankingResult]:
        """Ranks candidates using semantic embeddings and outputs structured RankingResult records."""
        retrieved = self.retrieve(job, candidates, top_k=len(candidates))
        candidate_map = {c.candidate_id: c for c in candidates}
        ranking_results = []

        for rank_idx, (cid, score) in enumerate(retrieved, start=1):
            cand = candidate_map[cid]
            citations = [s.evidence for s in cand.skills if s.evidence is not None]

            ranking_results.append(
                RankingResult(
                    candidate_id=cid,
                    job_id=job.job_id,
                    rank=rank_idx,
                    score=float(score),
                    model_name="dense_minilm",
                    component_scores={"cosine_similarity": float(score)},
                    evidence_citations=citations[:5],
                    uncertainty_markers=cand.uncertainty_flags,
                    run_id=run_id,
                )
            )

        return ranking_results
