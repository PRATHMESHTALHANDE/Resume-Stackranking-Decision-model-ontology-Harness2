# Resource: Multi-Criteria Linear Weighted Scoring Model

## 1. Overview & Purpose
The **Multi-Criteria Linear Weighted Scorer** (`WeightedScorer`) provides direct, transparent stakeholder control over how candidate attributes are balanced.

In many recruitment scenarios, hiring committees have explicit mandates:
- Some teams demand heavy emphasis on verified years of production tenure over long laundry lists of buzzwords.
- Other teams hiring for entry-to-mid roles or niche emerging technologies care almost exclusively about specific skill coverage rather than total years in the workforce.

The Weighted Scorer allows HR professionals to dynamically configure exact percentage allocations (e.g., Criteria Weightage vs. Experience Tenure Weightage) directly from the UI with real-time validation and preset configurations.

---

## 2. Mathematical Formulation

### 2.1 Dynamic Weight Normalization
The model accepts configuration parameters:
- `criteria_weight_pct` ($P_c \in [0, 100]$, default: $80\%$)
- `experience_weight_pct` ($P_e \in [0, 100]$, default: $20\%$)

Normalized weights:
$$W_c = \frac{P_c}{P_c + P_e}, \quad W_e = \frac{P_e}{P_c + P_e}$$

### 2.2 Criteria Coverage Formulation
For a job specification with $N$ criteria consisting of mandatory requirements ($M$) and preferred qualifications ($P$):
- **Mandatory Criterion Weight**: $w_{\text{req}} = 2.0$
- **Preferred Criterion Weight**: $w_{\text{pref}} = 1.0$

For each criterion $k$ and candidate skills set $\mathcal{S}$:
$$\text{match}(k) = \begin{cases} 1.0 & \text{if keyword or synonym in } \mathcal{S} \\ 0.0 & \text{otherwise} \end{cases}$$

$$\text{Coverage}_{\text{criteria}} = \frac{\sum_{k \in M} 2.0 \cdot \text{match}(k) + \sum_{k \in P} 1.0 \cdot \text{match}(k)}{\sum_{k \in M} 2.0 + \sum_{k \in P} 1.0}$$

### 2.3 Experience Tenure Scoring
Given required minimum experience $Y_{\text{min}}$ and candidate total experience $Y_{\text{cand}}$:
$$\text{Score}_{\text{exp}} = \min\left(1.0, \frac{Y_{\text{cand}}}{\max(1.0, Y_{\text{min}})}\right)$$

### 2.4 Composite Match Score
$$\text{Composite Score} = W_c \cdot \text{Coverage}_{\text{criteria}} + W_e \cdot \text{Score}_{\text{exp}}$$

---

## 3. Real-World HR Purpose & Presets
- **Recruiter Explanability**: When hiring managers ask *"Why did candidate A score 88% while candidate B scored 74%?"*, recruiters can point to exact linear weights: *"Candidate A met 90% of requirements and exceeded the 5-year tenure bar (80% * 0.90 + 20% * 1.0 = 92%)"*.
- **Quick HR Presets**:
  1. **80% Criteria / 20% Tenure (Balanced Standard)**: Default for mid-to-senior technical roles.
  2. **60% Criteria / 40% Tenure (Tenure Heavy)**: Designed for Principal, Staff, or Leadership roles where years of proven resilience matter heavily.
  3. **95% Criteria / 5% Tenure (Skills & Competencies Only)**: Designed for junior, intern, or rapidly emerging technology hiring (e.g., GenAI, Rust) where candidates cannot have 10+ years of tenure.

---

## 4. Hardware Footprint & Resource Impact
- **Latency**: < 1 ms to score 500 candidates.
- **CPU RAM**: < 2 MB.
- **GPU VRAM**: 0 MB.

---

## 5. Architecture & Code Integration
Implemented in [`packages/ranking/weighted_ranker.py`](file:///c:/Users/roari/Downloads/AI%20Projects/HR%20Resume%20Stackranking%20-%20Decision%20model%20+%20LLM%20+%20Ontology%20+%20Harness2/packages/ranking/weighted_ranker.py) and configured via [`apps/web/src/components/WeightedConfigurator.tsx`](file:///c:/Users/roari/Downloads/AI%20Projects/HR%20Resume%20Stackranking%20-%20Decision%20model%20+%20LLM%20+%20Ontology%20+%20Harness2/apps/web/src/components/WeightedConfigurator.tsx).
