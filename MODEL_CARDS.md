# Model Cards: Resume Intelligence & Fairness Lab

> **Document Version:** 1.0.0  
> **Release Target:** Open-Source Release v1.0.0  
> **Repository:** Open-Source Resume Intelligence, Ranking & Fairness Lab  

---

## 1. Ethical Boundary & Intended Use Notice

```
========================================================================================
                          MANDATORY ADVISORY NOTICE
========================================================================================
This software system is strictly designed as an evidence-grounded decision-support
tool for educational, research, and human-in-the-loop review.
It does NOT make autonomous hiring, candidate rejection, or automated employment
decisions. All match scores represent relative criteria alignment and must be verified
by qualified human reviewers alongside verbatim evidence citations.
========================================================================================
```

---

## 2. Model Architecture Matrix

| Model Architecture | Paradigms & Algorithm | Intended Purpose | Primary Strengths | Computational Complexity |
|---|---|---|---|---|
| **BM25Okapi** | Sparse Inverted Index Lexical Retrieval | Baseline keyword and skill token matching | Deterministic, zero hallucination, sub-millisecond execution | $O(N \cdot L)$ |
| **all-MiniLM-L6-v2** | Dense 384-dimensional Bi-Encoder Embeddings | Semantic match overcoming synonym mismatch | Bridges vocabulary gap, handles phrased experience | $O(N \cdot d)$ |
| **RRF Hybrid** | Rank Fusion ($k=60$) | Combines BM25 and Dense MiniLM ranks | Mitigates individual model outliers, high stability | $O(N \log N)$ |
| **Weighted Scorer** | Multi-attribute linear combination | Explicit criteria weighting ($w_i$) | Transparent sub-score attribution, auditable | $O(N \cdot M)$ |
| **TOPSIS** | Multi-Criteria Decision Analysis (MCDA) | Distance to Positive/Negative Ideal Solutions | Balanced trade-offs, penalties for ungrounded claims | $O(N \cdot M)$ |
| **LambdaMART** | Gradient Boosted Decision Trees (LightGBM) | Learning-to-Rank optimizing nDCG directly | Captures nonlinear skill interactions | $O(T \cdot D)$ |
| **LAYA Adapter** | Multi-attribute decision model interface | External decision model integration | Pluggable contract, verified schema mapping | $O(N)$ |

---

## 3. Detailed Model Specifications

### 3.1 BM25Okapi Ranker (`packages/ranking/bm25_ranker.py`)
- **Type:** Lexical Sparse Matching.
- **Formula:**
  $$\text{score}(D, Q) = \sum_{q \in Q} \text{IDF}(q) \cdot \frac{f(q, D) \cdot (k_1 + 1)}{f(q, D) + k_1 \cdot \left(1 - b + b \cdot \frac{|D|}{\text{avgdl}}\right)}$$
- **Hyperparameters:** $k_1 = 1.5$, $b = 0.75$.
- **Score Normalization:** Min-max normalized and clamped to $[0.0, 1.0]$.
- **Hardware Footprint:** < 50 MB RAM, runs instantly on CPU.

### 3.2 Dense MiniLM-L6-v2 (`packages/ranking/dense_ranker.py`)
- **Type:** Dense Semantic Embedding Retrieval.
- **Underlying Checkpoint:** `sentence-transformers/all-MiniLM-L6-v2` (6 layers, 384 dimensions, 22.7M parameters).
- **Execution Mode:** Local execution with offline cached weights (`models/weights/embeddings/`). Includes pure-Python BoW fallback under locked enterprise environments.
- **Similarity Metric:** Cosine similarity:
  $$\text{sim}(\vec{u}, \vec{v}) = \frac{\vec{u} \cdot \vec{v}}{\|\vec{u}\|_2 \|\vec{v}\|_2}$$

### 3.3 Reciprocal Rank Fusion (`packages/ranking/rrf_ranker.py`)
- **Type:** Score-agnostic rank ensemble.
- **Formula:**
  $$\text{RRF\_Score}(d \in D) = \sum_{m \in M} \frac{1}{k + r_m(d)}$$
  Where $k = 60$ and $r_m(d)$ is candidate $d$'s rank under ranker $m$.
- **Safety Properties:** Immune to score scale disparities between dense cosine scores and sparse BM25 scores.

### 3.4 TOPSIS Decision Ranker (`packages/ranking/topsis_ranker.py`)
- **Type:** Multi-Criteria Decision Analysis (Technique for Order of Preference by Similarity to Ideal Solution).
- **Dimensions Evaluated:**
  1. Exact Skill Coverage ($w_1 = 0.35$, Benefit)
  2. Semantic Criteria Similarity ($w_2 = 0.25$, Benefit)
  3. Years of Experience Fit ($w_3 = 0.20$, Benefit)
  4. Uncertainty & Ambiguity Count ($w_4 = 0.20$, Cost)
- **Mathematical Guarantee:** Candidates closest to the Positive Ideal Solution ($A^+$) and furthest from the Negative Ideal Solution ($A^-$) receive highest preference $C_i \in [0.0, 1.0]$.

---

## 4. Hardware & Quantization Profiles

- **Host Environment:** Windows 11 / Linux (tested on Intel Core i7-12650H, 16 GB RAM, NVIDIA RTX 3050 Laptop GPU 4 GB VRAM).
- **Quantization:** Support for 4-bit and 8-bit GGUF via `llama-cpp-python` within VRAM boundary ($\le 3.5$ GB allocations).
- **Zero Disk Pollution:** Hugging Face cache strictly sandboxed to `models/cache/` within project directory.
