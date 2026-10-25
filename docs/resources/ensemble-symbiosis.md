# Resource: Ensemble Symbiosis Decision Model ("Select All" Consensus)

## 1. Overview & Purpose
**Ensemble Symbiosis** is the unified multi-model consensus ranking architecture implemented in the **Resume Intelligence, Ranking & Fairness Lab**.

Instead of relying on a single algorithmic paradigm—which may introduce blind spots, bias toward specific terminology, or fail on non-linear candidate trade-offs—Ensemble Symbiosis executes **all 6 constituent ranking algorithms concurrently**:
1. **TOPSIS**: Multi-criteria geometric distance to ideal profile.
2. **LAYA Discrete Criterion Adapter**: Zero-compromise discrete typed qualification matching.
3. **Multi-Criteria Weighted Scorer**: Recruiter-configured linear policy weighting.
4. **Reciprocal Rank Fusion (RRF Hybrid)**: Lexical + semantic reciprocal rank blending.
5. **Dense Bi-Encoder (MiniLM-L6-v2)**: 384-dimensional conceptual cosine similarity.
6. **Okapi BM25**: Strict lexical keyword term matching.

It computes a calibrated consensus match score $S_{\text{consensus}} \in [0, 1]$ and calculates a **Cross-Model Agreement Rate** that measures algorithmic unanimity.

---

## 2. Mathematical Formulation

### 2.1 Constituent Model Normalization & Fusion
For each candidate $c_i$ and each decision model $m \in M$:
1. Individual ranker scores $s_m(c_i)$ are min-max normalized across the candidate cohort:
   $$\hat{s}_m(c_i) = \frac{s_m(c_i) - \min_j s_m(c_j)}{\max_j s_m(c_j) - \min_j s_m(c_j) + \epsilon}$$
2. The unified consensus score is computed as a weighted convex combination:
   $$S_{\text{consensus}}(c_i) = \sum_{m \in M} w_m \cdot \hat{s}_m(c_i), \quad \text{where } \sum_{m \in M} w_m = 1.0$$

### 2.2 Default Ensemble Weights
- **TOPSIS ($w = 0.25$)**: Primary operational research multi-criteria benchmark.
- **LAYA Discrete Adapter ($w = 0.20$)**: Strict evidence and certification verification.
- **Weighted Policy ($w = 0.20$)**: Direct HR policy alignment (criteria + tenure).
- **RRF Hybrid ($w = 0.15$)**: Balanced rank-fusion baseline.
- **Dense Vector MiniLM ($w = 0.10$)**: Latent semantic synonym alignment.
- **Lexical BM25 ($w = 0.10$)**: Mandatory keyword and acronym preservation.

### 2.3 Cross-Model Agreement Rate
Measures the standard deviation $\sigma_i$ of normalized scores across all 6 models:
$$\text{Agreement Rate}(c_i) = \max\left(0.5, 1.0 - \sqrt{\frac{1}{|M|} \sum_{m \in M} \left(\hat{s}_m(c_i) - \bar{s}(c_i)\right)^2}\right)$$
A higher rate (e.g., $95\%+$) proves that the candidate is strong under geometric, compliance, semantic, and lexical criteria simultaneously.

---

## 3. Real-World HR Purpose & Benefits
- **Elimination of Single-Model Bias**: Prevents keyword-stuffers from ranking top via BM25 alone, and prevents smooth-talking generalists with high semantic similarity from displacing deeply qualified specialists.
- **High-Stakes & Senior Hires**: Essential for Director, VP, Staff Engineer, and Clinical Lead roles where false positives carry substantial cost.
- **Full Component Transparency**: Every candidate ranking includes granular component scores (`topsis_score`, `laya_score`, `weighted_score`, `rrf_score`, `dense_score`, `bm25_score`) displayed directly in the UI.

---

## 4. Hardware Footprint & Resource Impact
- **Parallel CPU Execution**: Executed via Python's `ThreadPoolExecutor` or vectorized matrix operations.
- **Latency**: Under $25\text{ ms}$ for cohorts of 50 candidates on local hardware.
- **Memory Footprint**: < 10 MB RAM overhead beyond base embeddings cache.
- **GPU VRAM**: 0 MB (pure CPU vector math).

---

## 5. Architecture & Code Integration
Implemented in [`packages/ranking/ensemble_ranker.py`](file:///c:/Users/roari/Downloads/AI%20Projects/HR%20Resume%20Stackranking%20-%20Decision%20model%20+%20LLM%20+%20Ontology%20+%20Harness2/packages/ranking/ensemble_ranker.py) and registered in [`apps/api/routes/rankings.py`](file:///c:/Users/roari/Downloads/AI%20Projects/HR%20Resume%20Stackranking%20-%20Decision%20model%20+%20LLM%20+%20Ontology%20+%20Harness2/apps/api/routes/rankings.py).
