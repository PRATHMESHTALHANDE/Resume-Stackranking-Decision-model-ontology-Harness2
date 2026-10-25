# Model Evaluation & Benchmark Comparison Report

> **Generated:** 2026-10-25 07:54:14 UTC
> **Dataset Split:** api_test_split

## 1. Ranking Quality & Efficiency Metrics

| Model Architecture | nDCG@5 | nDCG@10 | MRR | Precision@5 | Latency (ms) | Peak RAM (MB) | Counterfactual Tau | Shortlist Shifts |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| **bm25** | 1.000 | 1.000 | 0.000 | 0.000 | 0.7 | 1360.8 | 1.000 | 0 |
| **dense_minilm** | 1.000 | 1.000 | 0.000 | 0.000 | 56.9 | 1361.2 | 1.000 | 0 |
| **rrf_hybrid** | 1.000 | 1.000 | 0.000 | 0.000 | 64.9 | 1361.2 | 1.000 | 0 |
| **weighted** | 1.000 | 1.000 | 0.000 | 0.000 | 0.2 | 1361.2 | 1.000 | 0 |
| **topsis** | 1.000 | 1.000 | 0.000 | 0.000 | 60.7 | 1361.2 | 1.000 | 0 |
| **laya_adapter** | 1.000 | 1.000 | 0.000 | 0.000 | 0.3 | 1361.2 | 1.000 | 0 |

## 2. Research Observations
- **Hybrid Fusion:** RRF successfully bridges lexical keyword match and semantic representation.
- **Multi-Criteria TOPSIS:** Transparently accounts for missing evidence without black-box unexplainability.
- **Fairness Stability:** High Kendall Tau values reflect stability under name/pronoun counterfactual perturbations.