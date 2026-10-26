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

| Model Architecture | Paradigms & Algorithm | Intended Purpose | Upstream Link | Primary Strengths | Computational Complexity |
|---|---|---|---|---|---|
| **LAYA System-1** | Non-autoregressive ModernBERT-large (421M params) | Discrete candidate-criteria neural decision evaluation | [`convaiinnovations/laya`](https://huggingface.co/convaiinnovations/laya) | Single-pass decision classification, zero generative hallucinations | $O(N \cdot C)$ |
| **TOPSIS Scorer** | Multi-Criteria Decision Analysis (MCDA) | Distance to Positive/Negative Ideal Solutions | Classical MCDA Algorithmic | Balanced trade-offs, penalties for ungrounded claims | $O(N \cdot M)$ |
| **Qwen2.5-1.5B-Instruct** | Autoregressive Decoder LLM (1.54B params, 4-bit GGUF) | Structured JSON resume parsing & qualification summaries | [`Qwen/Qwen2.5-1.5B-Instruct`](https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct) | Local inference via `llama-cpp-python`, schema-constrained output | $O(L^2)$ |
| **all-MiniLM-L6-v2** | Dense 384-dimensional Bi-Encoder (22.7M params) | Semantic match overcoming synonym mismatch | [`sentence-transformers/all-MiniLM-L6-v2`](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2) | Bridges vocabulary gap, handles phrased experience | $O(N \cdot d)$ |
| **LambdaMART** | Gradient Boosted Decision Trees (LightGBM) | Learning-to-Rank optimizing nDCG directly | [`microsoft/LightGBM`](https://github.com/microsoft/LightGBM) | Captures nonlinear skill interactions, fast ranking inference | $O(T \cdot D)$ |
| **RRF Hybrid** | Rank Fusion ($k=60$) | Combines BM25 and Dense MiniLM ranks | Algorithmic Fusion | Mitigates individual model outliers, high stability | $O(N \log N)$ |
| **BM25Okapi** | Sparse Inverted Index Lexical Retrieval | Baseline keyword and skill token matching | Rank-BM25 Algorithmic | Deterministic, zero hallucination, sub-millisecond execution | $O(N \cdot L)$ |

---

## 3. Detailed Model Specifications

### 3.1 LAYA System-1 Neural Decision Model (`packages/decision_models/laya_adapter.py`)
- **Upstream Model Card:** [`convaiinnovations/laya` on Hugging Face](https://huggingface.co/convaiinnovations/laya)
- **Base Architecture:** ModernBERT-large backbone (421 Million Parameters).
- **Inference Mechanism:** Non-autoregressive single forward pass classification with typed choice probabilities (`MatchType.MATCH`, `MatchType.PARTIAL`, `MatchType.NO_MATCH`).
- **Key Safety Advantage:** Does not generate text token-by-token. Completely eliminates generative fabrications and hallucinations in decision outputs.
- **Hardware Profile:** Runs locally on CUDA (`torch.float16`) or CPU (`torch.float32`). Uses sandboxed cache in `models/cache/huggingface/`.

### 3.2 Qwen2.5-1.5B-Instruct Generative LLM (`packages/extraction/llm_extractor.py`, `packages/decision_models/explanation.py`)
- **Upstream Model Card:** [`Qwen/Qwen2.5-1.5B-Instruct` on Hugging Face](https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct)
- **Quantization:** 4-bit `Q4_K_M` GGUF (~1.1 GB weight footprint).
- **Runtime Engine:** `llama-cpp-python` with GPU layer offloading (28 layers offloaded to 4GB VRAM).
- **Primary Tasks:**
  1. High-fidelity entity extraction from raw resume text adhering strictly to Pydantic JSON schemas.
  2. Natural language qualification summaries grounded in extracted evidence citations for recruiter transparency.
- **Decoding Configuration:** Deterministic greedy decoding (`temperature=0.0`) for reproducible factual output.

### 3.3 TOPSIS Multi-Criteria Decision Ranker (`packages/ranking/topsis_ranker.py`)
- **Type:** Multi-Criteria Decision Analysis (Technique for Order of Preference by Similarity to Ideal Solution).
- **Dimensions Evaluated:**
  1. Exact Skill Coverage ($w_1 = 0.35$, Benefit)
  2. Semantic Criteria Similarity ($w_2 = 0.25$, Benefit)
  3. Years of Experience Fit ($w_3 = 0.20$, Benefit)
  4. Uncertainty & Ambiguity Count ($w_4 = 0.20$, Cost)
- **Mathematical Guarantee:** Candidates closest to the Positive Ideal Solution ($A^+$) and furthest from the Negative Ideal Solution ($A^-$) receive highest preference $C_i \in [0.0, 1.0]$.

### 3.4 Dense MiniLM-L6-v2 (`packages/ranking/dense_ranker.py`)
- **Upstream Model Card:** [`sentence-transformers/all-MiniLM-L6-v2` on Hugging Face](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2)
- **Type:** Dense Semantic Embedding Retrieval (6 layers, 384 dimensions, 22.7M parameters).
- **Execution Mode:** Local execution with offline cached weights (`models/weights/embeddings/`). Includes pure-Python BoW fallback under locked enterprise environments.
- **Similarity Metric:** Cosine similarity:
  $$\text{sim}(\vec{u}, \vec{v}) = \frac{\vec{u} \cdot \vec{v}}{\|\vec{u}\|_2 \|\vec{v}\|_2}$$

### 3.5 LightGBM LambdaMART Ranker (`packages/ranking/lambdamart_ranker.py`)
- **Upstream Repository:** [`microsoft/LightGBM` on GitHub](https://github.com/microsoft/LightGBM)
- **Algorithm:** LambdaMART gradient boosted decision forest directly optimizing listwise nDCG.
- **Features Used:** Semantic criteria alignment, mandatory skill coverage ratio, tenure adequacy, gap penalty, and verified citation density.

### 3.6 BM25Okapi Ranker (`packages/ranking/bm25_ranker.py`)
- **Type:** Lexical Sparse Matching.
- **Formula:**
  $$\text{score}(D, Q) = \sum_{q \in Q} \text{IDF}(q) \cdot \frac{f(q, D) \cdot (k_1 + 1)}{f(q, D) + k_1 \cdot \left(1 - b + b \cdot \frac{|D|}{\text{avgdl}}\right)}$$
- **Hyperparameters:** $k_1 = 1.5$, $b = 0.75$.
- **Score Normalization:** Min-max normalized and clamped to $[0.0, 1.0]$.

### 3.7 Reciprocal Rank Fusion (`packages/ranking/rrf_ranker.py`)
- **Type:** Score-agnostic rank ensemble.
- **Formula:**
  $$\text{RRF\_Score}(d \in D) = \sum_{m \in M} \frac{1}{k + r_m(d)}$$
  Where $k = 60$ and $r_m(d)$ is candidate $d$'s rank under ranker $m$.

---

## 4. Hardware & Quantization Profiles

- **Host Environment:** Windows 11 / Linux (tested on Intel Core i7-12650H, 16 GB RAM, NVIDIA RTX 3050 Laptop GPU 4 GB VRAM).
- **Quantization:** Support for 4-bit and 8-bit GGUF via `llama-cpp-python` within VRAM boundary ($\le 3.5$ GB allocations).
- **Zero Disk Pollution:** Hugging Face cache strictly sandboxed to `models/cache/` within project directory.
