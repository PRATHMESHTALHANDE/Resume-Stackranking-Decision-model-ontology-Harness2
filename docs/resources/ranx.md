# Resource: ranx (Fast Ranking Evaluation)

## 1. Overview & Purpose
**ranx** is a blazing-fast Python library for ranking evaluation and comparison powered by Numba. It evaluates standard Information Retrieval (IR) and Learning-to-Rank (LTR) metrics across multiple models with statistical significance testing (e.g. Student's t-test, Fisher's randomization test).

In the **Resume Intelligence, Ranking & Fairness Lab**, ranx serves as the primary benchmark evaluation engine:
- Computes standard metrics:
  - $\text{nDCG}@k$ (Normalized Discounted Cumulative Gain at ranks 5 and 10)
  - $\text{MRR}$ (Mean Reciprocal Rank)
  - $\text{Precision}@k$ and $\text{Recall}@k$
  - $\text{MAP}$ (Mean Average Precision)
  - $\text{F1}@k$
- Performs automated statistical significance comparisons between baseline BM25, MiniLM dense retrieval, RRF hybrid fusion, TOPSIS, and LambdaMART.
- Exports publication-ready LaTeX, markdown, and pandas comparison tables.

## 2. Upstream Provenance & License
- **Official Documentation:** https://amenra.github.io/ranx/
- **GitHub Repository:** https://github.com/AmenRa/ranx
- **Paper:** Bassani, E. (2022). "ranx: A Blazing-Fast Python Library for Ranking Evaluation and Comparison." *ACM SIGIR 2022*.
- **License:** MIT License (Permissive open source).
- **Author:** Elias Bassani.

## 3. Local Installation & Storage Location
Installed into `.venv/` via `uv`:
```powershell
uv add ranx
```
No external models or weights required; uses JIT-compiled Numba kernels on CPU.

## 4. Hardware Footprint & Resource Impact
- **System RAM:** ~30–50 MB.
- **Speed:** Can compute nDCG@10 for 100,000 query-candidate evaluations in < 100 milliseconds due to Numba optimization.
- **GPU VRAM:** 0 MB.

## 5. Architecture & Code Integration
Implemented in `packages/evaluation/metrics.py`:

```python
"""
Ranking evaluation engine leveraging ranx for high-speed metric calculation.
"""
from ranx import Qrels, Run, evaluate, compare
from typing import Dict, Any, List

class RankingEvaluator:
    """
    Evaluates candidate rankings against human-labeled golden standards.
    """
    def __init__(self, golden_labels: Dict[str, Dict[str, int]]):
        """
        Args:
            golden_labels: Dict mapping query_id -> {candidate_id: graded_relevance}
        """
        self.qrels = Qrels(golden_labels)

    def evaluate_run(self, model_predictions: Dict[str, Dict[str, float]]) -> Dict[str, float]:
        """
        Computes nDCG@5, nDCG@10, MRR, and Precision@5 for a model run.
        """
        run = Run(model_predictions)
        scores = evaluate(
            self.qrels,
            run,
            metrics=["ndcg@5", "ndcg@10", "mrr", "precision@5", "recall@10"],
        )
        return scores

    def compare_models(self, runs: Dict[str, Run]) -> str:
        """
        Runs statistical significance comparison between candidate rankers.
        """
        report = compare(
            qrels=self.qrels,
            runs=list(runs.values()),
            metrics=["ndcg@5", "ndcg@10", "mrr"],
            max_p=0.05,
        )
        return str(report)
```

## 6. Failure Modes, Fallbacks & Edge Cases
- **Missing Query IDs:** If a model fails to rank candidates for a job query, ranx assigns a score of 0.0 for that query, correctly reflecting the failure rather than hiding incomplete evaluation runs.
- **Custom Metrics Fallback:** A pure Python fallback metric calculation is also maintained in `tests/evaluation/test_metrics_pure.py` to independently cross-verify ranx results on toy matrices.
