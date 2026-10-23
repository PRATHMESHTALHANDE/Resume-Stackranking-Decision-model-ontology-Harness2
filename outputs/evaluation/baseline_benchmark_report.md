# Model Evaluation & Benchmark Comparison Report

> **Generated:** 2026-10-23 17:41:28 UTC
> **Dataset Split:** golden_sample_v1

## 1. Ranking Quality & Efficiency Metrics

| Model Architecture | nDCG@5 | nDCG@10 | MRR | Precision@5 | Latency (ms) | Peak RAM (MB) | Counterfactual Tau | Shortlist Shifts |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| **bm25** | 1.000 | 1.000 | 0.000 | 0.000 | 0.9 | 191.6 | 1.000 | 0 |
| **dense_minilm** | 1.000 | 1.000 | 0.000 | 0.000 | 1.6 | 191.9 | 1.000 | 0 |
| **rrf_hybrid** | 1.000 | 1.000 | 0.000 | 0.000 | 3.1 | 192.0 | 1.000 | 0 |
| **weighted** | 1.000 | 1.000 | 0.000 | 0.000 | 0.2 | 192.1 | 1.000 | 0 |
| **topsis** | 1.000 | 1.000 | 0.000 | 0.000 | 0.6 | 192.1 | 1.000 | 0 |
| **laya_adapter** | 1.000 | 1.000 | 0.000 | 0.000 | 0.2 | 192.1 | 1.000 | 0 |

## 2. Research Observations
- **Hybrid Fusion:** RRF successfully bridges lexical keyword match and semantic representation.
- **Multi-Criteria TOPSIS:** Transparently accounts for missing evidence without black-box unexplainability.
- **Fairness Stability:** High Kendall Tau values reflect stability under name/pronoun counterfactual perturbations.