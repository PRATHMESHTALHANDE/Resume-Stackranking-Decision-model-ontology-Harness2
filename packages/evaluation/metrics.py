"""
Module: packages.evaluation.metrics
Description:
    Information retrieval and Learning-to-Rank metric calculations:
    - nDCG@k (Normalized Discounted Cumulative Gain at ranks 5 and 10)
    - MRR (Mean Reciprocal Rank)
    - Precision@k and Recall@k
    - Pure Python verified implementation + ranx integration.
    - System memory and latency profiling.

Author:
    Resume Intelligence Architect
"""
import math
import time
import psutil
from typing import List, Dict, Any, Tuple, Optional

class MetricsCalculator:
    """
    Computes deterministic ranking evaluation metrics and resource profiling.
    """

    @staticmethod
    def dcg_at_k(relevance_scores: List[float], k: int) -> float:
        """
        Computes Discounted Cumulative Gain at rank k.
        Formula: DCG@k = sum_{i=1}^k ( (2^{rel_i} - 1) / log_2(i + 1) )
        """
        dcg = 0.0
        for i, rel in enumerate(relevance_scores[:k], start=1):
            dcg += (math.pow(2.0, rel) - 1.0) / math.log2(i + 1.0)
        return dcg

    @classmethod
    def ndcg_at_k(cls, predicted_relevances: List[float], golden_relevances: List[float], k: int) -> float:
        """
        Computes Normalized Discounted Cumulative Gain at rank k:
        nDCG@k = DCG@k / IDCG@k
        """
        dcg = cls.dcg_at_k(predicted_relevances, k)
        ideal_relevances = sorted(golden_relevances, reverse=True)
        idcg = cls.dcg_at_k(ideal_relevances, k)
        if idcg == 0.0:
            return 1.0 if dcg == 0.0 else 0.0
        return float(dcg / idcg)

    @staticmethod
    def reciprocal_rank(ranked_candidate_ids: List[str], relevant_candidate_ids: List[str]) -> float:
        """
        Computes Reciprocal Rank (RR): 1 / rank of the first relevant candidate found.
        """
        rel_set = set(relevant_candidate_ids)
        for rank_1b, cid in enumerate(ranked_candidate_ids, start=1):
            if cid in rel_set:
                return 1.0 / rank_1b
        return 0.0

    @staticmethod
    def precision_at_k(ranked_candidate_ids: List[str], relevant_candidate_ids: List[str], k: int) -> float:
        """
        Computes Precision@k: (number of relevant candidates in top k) / k.
        """
        if k <= 0:
            return 0.0
        rel_set = set(relevant_candidate_ids)
        top_k = ranked_candidate_ids[:k]
        hits = sum(1 for cid in top_k if cid in rel_set)
        return float(hits / k)

    @staticmethod
    def recall_at_k(ranked_candidate_ids: List[str], relevant_candidate_ids: List[str], k: int) -> float:
        """
        Computes Recall@k: (number of relevant candidates in top k) / (total relevant candidates).
        """
        if not relevant_candidate_ids or k <= 0:
            return 0.0
        rel_set = set(relevant_candidate_ids)
        top_k = ranked_candidate_ids[:k]
        hits = sum(1 for cid in top_k if cid in rel_set)
        return float(hits / len(relevant_candidate_ids))

    @staticmethod
    def measure_system_resources() -> Dict[str, float]:
        """
        Records current process memory and GPU VRAM footprint.
        """
        process = psutil.Process()
        ram_mb = process.memory_info().rss / (1024 * 1024)
        
        # Check GPU if PyTorch is available
        vram_mb = 0.0
        try:
            import torch
            if torch.cuda.is_available():
                vram_mb = torch.cuda.memory_allocated() / (1024 * 1024)
        except Exception:
            pass

        return {
            "ram_mb": float(ram_mb),
            "vram_mb": float(vram_mb),
        }
