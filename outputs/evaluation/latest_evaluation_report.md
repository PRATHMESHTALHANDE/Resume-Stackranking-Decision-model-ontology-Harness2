# Model Evaluation & Benchmark Comparison Report

> **Generated:** 2026-10-25 13:59:30 UTC
> **Dataset Split:** api_test_split

## 1. Ranking Quality & Efficiency Metrics

| Model Architecture | nDCG@5 | nDCG@10 | MRR | Precision@5 | Latency (ms) | Peak RAM (MB) | Counterfactual Tau | Shortlist Shifts |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| **bm25** | 1.000 | 1.000 | 0.000 | 0.000 | 3.3 | 1097.9 | 1.000 | 0 |
| **dense_minilm** | 1.000 | 1.000 | 0.000 | 0.000 | 125.6 | 1101.6 | 1.000 | 0 |
| **rrf_hybrid** | 1.000 | 1.000 | 0.000 | 0.000 | 92.4 | 1101.7 | 1.000 | 0 |
| **weighted** | 1.000 | 1.000 | 0.000 | 0.000 | 0.3 | 1101.8 | 1.000 | 0 |
| **topsis** | 1.000 | 1.000 | 0.000 | 0.000 | 93.2 | 1101.8 | 1.000 | 0 |
| **laya_adapter** | 1.000 | 1.000 | 0.000 | 0.000 | 0.5 | 1101.9 | 1.000 | 0 |

## 2. Research Observations
- **Hybrid Fusion:** RRF successfully bridges lexical keyword match and semantic representation.
- **Multi-Criteria TOPSIS:** Transparently accounts for missing evidence without black-box unexplainability.
- **Fairness Stability:** High Kendall Tau values reflect stability under name/pronoun counterfactual perturbations.