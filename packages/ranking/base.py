"""
Module: packages.ranking.base
Description:
    Abstract base interfaces for retrievers, rankers, and decision models.
    Guarantees plug-and-play modularity across BM25, MiniLM vectors, RRF fusion,
    TOPSIS, LambdaMART, and Laya adapters.

Author:
    Resume Intelligence Architect
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Tuple
from packages.common.schemas import JobDescription, ResumeProfile, RankingResult

class BaseRetriever(ABC):
    """Abstract interface for sparse/dense candidate retrievers."""

    @abstractmethod
    def retrieve(
        self,
        job: JobDescription,
        candidates: List[ResumeProfile],
        top_k: int = 50,
    ) -> List[Tuple[str, float]]:
        """
        Retrieves candidate IDs with retrieval relevance scores.

        Args:
            job: Job description query contract.
            candidates: Pool of candidate profiles to search.
            top_k: Maximum number of candidates to return.

        Returns:
            List of (candidate_id, score) tuples sorted descending by score.
        """
        pass

class BaseRanker(ABC):
    """Abstract interface for multi-criteria rankers and decision models."""

    @abstractmethod
    def rank(
        self,
        job: JobDescription,
        candidates: List[ResumeProfile],
        run_id: str,
        config: Dict[str, Any] = None,
    ) -> List[RankingResult]:
        """
        Ranks candidates against explicit job criteria and returns structured RankingResults.
        """
        pass

class BaseDecisionModel(ABC):
    """Abstract interface for discrete criterion-level decision judges."""

    @abstractmethod
    def evaluate_criterion(
        self,
        criterion_description: str,
        candidate_evidence_text: str,
    ) -> Dict[str, Any]:
        """
        Scores candidate evidence against a single job requirement.

        Returns:
            Dict containing decision ('match' | 'partial' | 'no_match'), score, and confidence.
        """
        pass
