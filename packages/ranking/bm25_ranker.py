"""
Module: packages.ranking.bm25_ranker
Description:
    Okapi BM25 lexical retriever implementing BaseRetriever and BaseRanker.
    Uses rank-bm25 with domain-specific tokenization preserving technical skills.

Author:
    Resume Intelligence Architect
"""
import re
from typing import List, Dict, Any, Tuple
from rank_bm25 import BM25Okapi

from packages.common.schemas import JobDescription, ResumeProfile, RankingResult, EvidenceReference
from packages.ranking.base import BaseRetriever, BaseRanker

class BM25Ranker(BaseRetriever, BaseRanker):
    """
    Lexical information retrieval model using Okapi BM25.
    """
    def __init__(self, k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b

    @staticmethod
    def tokenize(text: str) -> List[str]:
        """
        Tokenizes text while preserving symbols in C++, C#, .NET, Node.js, etc.
        """
        pattern = r"\b[A-Za-z0-9]+(?:\.[A-Za-z0-9]+)*\b|C\+\+|C\#|\.NET"
        return [t.lower() for t in re.findall(pattern, text)]

    def _build_candidate_corpus(self, candidates: List[ResumeProfile]) -> Tuple[List[str], List[List[str]]]:
        """Assembles tokenized text corpus for BM25 indexing."""
        cids = []
        tokenized_corpus = []
        for c in candidates:
            cids.append(c.candidate_id)
            # Combine skills, summary, and experience titles into document text
            doc_parts = [s.original_text for s in c.skills]
            if c.summary:
                doc_parts.append(c.summary)
            for exp in c.experience_items:
                doc_parts.append(exp.job_title)
            full_text = " ".join(doc_parts)
            tokenized_corpus.append(self.tokenize(full_text))
        return cids, tokenized_corpus

    def retrieve(
        self,
        job: JobDescription,
        candidates: List[ResumeProfile],
        top_k: int = 50,
    ) -> List[Tuple[str, float]]:
        """Retrieves candidates scored by BM25 relevance to job description."""
        if not candidates:
            return []

        cids, tokenized_corpus = self._build_candidate_corpus(candidates)
        bm25 = BM25Okapi(tokenized_corpus, k1=self.k1, b=self.b)

        query_tokens = self.tokenize(job.description_text + " " + " ".join(c.description for c in job.criteria))
        scores = bm25.get_scores(query_tokens)

        # Normalize BM25 scores into [0.0, 1.0] range
        max_score = max(scores) if len(scores) > 0 and max(scores) > 0 else 1.0
        results = [(cid, float(s / max_score)) for cid, s in zip(cids, scores)]
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:top_k]

    def rank(
        self,
        job: JobDescription,
        candidates: List[ResumeProfile],
        run_id: str,
        config: Dict[str, Any] = None,
    ) -> List[RankingResult]:
        """Ranks candidate pool and outputs structured RankingResult records."""
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
                    model_name="bm25",
                    component_scores={"bm25_lexical_score": float(score)},
                    evidence_citations=citations[:5],
                    uncertainty_markers=cand.uncertainty_flags,
                    run_id=run_id,
                )
            )

        return ranking_results
