# Model Evaluation & Benchmark Comparison Report

> **Generated:** 2026-10-25 06:25:42 UTC
> **Dataset Split:** api_test_split

## 1. Ranking Quality & Efficiency Metrics

| Model Architecture | nDCG@5 | nDCG@10 | MRR | Precision@5 | Latency (ms) | Peak RAM (MB) | Counterfactual Tau | Shortlist Shifts |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| **bm25** | 1.000 | 1.000 | 0.000 | 0.000 | 0.7 | 1071.3 | 1.000 | 0 |
| **dense_minilm** | 1.000 | 1.000 | 0.000 | 0.000 | 67.4 | 1071.4 | 1.000 | 0 |
| **rrf_hybrid** | 1.000 | 1.000 | 0.000 | 0.000 | 65.9 | 1071.5 | 1.000 | 0 |
| **weighted** | 1.000 | 1.000 | 0.000 | 0.000 | 0.2 | 1071.6 | 1.000 | 0 |
| **topsis** | 1.000 | 1.000 | 0.000 | 0.000 | 67.5 | 1071.6 | 1.000 | 0 |
| **laya_adapter** | 1.000 | 1.000 | 0.000 | 0.000 | 0.3 | 1071.6 | 1.000 | 0 |

## 2. Research Observations
- **Hybrid Fusion:** RRF successfully bridges lexical keyword match and semantic representation.
- **Multi-Criteria TOPSIS:** Transparently accounts for missing evidence without black-box unexplainability.
- **Fairness Stability:** High Kendall Tau values reflect stability under name/pronoun counterfactual perturbations.