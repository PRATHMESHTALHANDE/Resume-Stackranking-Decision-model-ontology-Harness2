# Resource: Harness 2 (Evaluation & Benchmarking Engine)

## 1. Overview & Purpose
**Harness 2** is the automated empirical evaluation and benchmarking framework powering the **Resume Intelligence, Ranking & Fairness Lab** (`packages/evaluation/harness.py`).

In real-world enterprise HR tech, deploying ranking algorithms into production without empirical guarantees risks severe legal exposure, bias litigation (e.g., EEOC / NYC Local Law 144 compliance), and degradation of candidate quality.

**Harness 2 provides an offline scientific sandbox that:**
1. Evaluates all 7+ decision models simultaneously against curated golden relevance datasets.
2. Quantifies ranking effectiveness using standard Information Retrieval (IR) metrics: $\text{nDCG}@k$, $\text{MRR}$, $\text{Precision}@k$, and $\text{Recall}@k$.
3. Measures computational performance: exact p95 latency ($\text{ms}$) and peak RAM consumption ($\text{MB}$).
4. Executes counterfactual fairness audits across protected demographic attributes (gender, ethnicity, age proxies) before a model is allowed in production.
5. Emits auditable, reproducible Markdown and JSONL benchmark reports to `outputs/evaluation/`.

---

## 2. Core Benchmarking Metrics

### 2.1 Information Retrieval (IR) Quality Metrics
- **Normalized Discounted Cumulative Gain ($\text{nDCG}@k$)**:
  Evaluates graded relevance (0 = unqualified, 1 = marginal, 2 = strong, 3 = perfect fit) with logarithmic position discounting:
  $$\text{DCG}@k = \sum_{i=1}^k \frac{2^{\text{rel}_i} - 1}{\log_2(i + 1)}, \quad \text{nDCG}@k = \frac{\text{DCG}@k}{\text{IDCG}@k}$$
- **Mean Reciprocal Rank ($\text{MRR}$)**:
  Measures how quickly the first truly qualified candidate appears in the ranking list:
  $$\text{MRR} = \frac{1}{|Q|} \sum_{q=1}^{|Q|} \frac{1}{\text{rank}_q}$$
- **Precision@K & Recall@K**:
  Evaluates the proportion of relevant candidates retrieved within the top $k$ shortlist (e.g., top 5 or top 10 interview slots).

### 2.2 System Performance Metrics
- **Inference Latency**: Measures CPU/GPU execution time in milliseconds ($\text{ms}$) per ranking run.
- **Memory Consumption**: Tracks peak heap allocation during vector encoding and matrix operations.

### 2.3 Counterfactual Fairness & Bias Audits
Integrated with `CounterfactualAuditor`:
- Generates counterfactual candidate resumes by swapping demographic identifiers (e.g., male vs. female candidate names, historically underrepresented proxies).
- Computes **Selection Rate Disparity** and **Demographic Parity Ratio**:
  $$\text{Disparity Ratio} = \frac{P(\text{Top } K \mid \text{Group } A)}{P(\text{Top } K \mid \text{Group } B)}$$
  Enforces the $4/5^{\text{th}}$ (80%) EEOC rule to flag algorithmic disparate impact.

---

## 3. Real-World HR Purpose & Benefits
- **Model Selection Validation**: Allows hiring leaders to scientifically determine whether switching from BM25 to TOPSIS or Ensemble Symbiosis actually improves top-5 candidate precision on their specific historical job descriptions.
- **Audit & Compliance Readiness**: Provides exportable evaluation reports proving that algorithms were tested for demographic fairness and statistical consistency before being used in candidate selection.

---

## 4. Hardware Footprint & Resource Impact
- **Runtime**: Completes a full 7-model comparative benchmark across 100+ candidates in under $1.5\text{ seconds}$ on standard multi-core CPUs.
- **Storage**: Generates lightweight JSONL runs and clean Markdown summaries in `outputs/evaluation/`.

---

## 5. Architecture & Code Integration
- **Harness Implementation**: [`packages/evaluation/harness.py`](file:///c:/Users/roari/Downloads/AI%20Projects/HR%20Resume%20Stackranking%20-%20Decision%20model%20+%20LLM%20+%20Ontology%20+%20Harness2/packages/evaluation/harness.py)
- **Metrics Calculator**: [`packages/evaluation/metrics.py`](file:///c:/Users/roari/Downloads/AI%20Projects/HR%20Resume%20Stackranking%20-%20Decision%20model%20+%20LLM%20+%20Ontology%20+%20Harness2/packages/evaluation/metrics.py)
- **API Endpoint**: `POST /api/v1/evaluations/benchmark`
- **Output Artifacts**: [`outputs/evaluation/latest_evaluation_report.md`](file:///c:/Users/roari/Downloads/AI%20Projects/HR%20Resume%20Stackranking%20-%20Decision%20model%20+%20LLM%20+%20Ontology%20+%20Harness2/outputs/evaluation/latest_evaluation_report.md)
