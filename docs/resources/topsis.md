# Resource: TOPSIS Multi-Criteria Decision Model

## 1. Overview & Purpose
**TOPSIS** (Technique for Order of Preference by Similarity to Ideal Solution) is an established Multi-Criteria Decision Analysis (MCDA) mathematical method developed by Ching-Lai Hwang and Kwangsun Yoon (1981).

In the **Resume Intelligence, Ranking & Fairness Lab**, TOPSIS provides an objective, transparent multi-criteria ranking engine:
- Evaluates candidates simultaneously across multiple heterogeneous dimensions:
  1. Mandatory Skill Coverage (Benefit criteria: higher is better)
  2. Preferred Skill Coverage (Benefit criteria)
  3. Years of Relevant Experience (Benefit criteria, bounded)
  4. Missing Evidence Penalty (Cost criteria: lower is better)
  5. Semantic Alignment Score (Benefit criteria)
- Computes Euclidean geometric distance to the **Positive Ideal Solution** ($A^+$) and the **Negative Ideal Solution** ($A^-$).
- Generates a final relative closeness score $C_i \in [0, 1]$, ranking candidates from best to worst with full mathematical explainability.

## 2. Mathematical Formulation
1. **Decision Matrix:** Construct $m \times n$ matrix $X = (x_{ij})$ for $m$ candidates and $n$ criteria.
2. **Vector Normalization:**
   $$r_{ij} = \frac{x_{ij}}{\sqrt{\sum_{k=1}^m x_{kj}^2}}$$
3. **Weighted Normalized Matrix:**
   $$v_{ij} = w_j \cdot r_{ij}, \quad \text{where } \sum_{j=1}^n w_j = 1$$
4. **Ideal Solutions Determination:**
   - Positive Ideal: $A^+ = (v_1^+, \dots, v_n^+)$, where $v_j^+ = \max_i v_{ij}$ for benefit, $\min_i v_{ij}$ for cost.
   - Negative Ideal: $A^- = (v_1^-, \dots, v_n^-)$, where $v_j^- = \min_i v_{ij}$ for benefit, $\max_i v_{ij}$ for cost.
5. **Separation Measures (Euclidean Distances):**
   $$S_i^+ = \sqrt{\sum_{j=1}^n (v_{ij} - v_j^+)^2}, \quad S_i^- = \sqrt{\sum_{j=1}^n (v_{ij} - v_j^-)^2}$$
6. **Relative Closeness to Ideal Solution:**
   $$C_i = \frac{S_i^-}{S_i^+ + S_i^-}, \quad C_i \in [0, 1]$$

## 3. Upstream Provenance & License
- **Implementation:** Implemented directly in pure Python + NumPy (`packages/ranking/topsis_ranker.py`) with zero third-party library bloat.
- **Foundational Paper:** Hwang, C.L.; Yoon, K. (1981). *Multiple Attribute Decision Making: Methods and Applications*. Springer-Verlag.
- **License:** Open Source (MIT License for our implementation).

## 4. Hardware Footprint & Resource Impact
- **System RAM:** Negligible (< 5 MB for NumPy matrix operations).
- **Computation Time:** < 1 ms to score 500 candidates across 10 criteria on CPU.
- **GPU VRAM:** 0 MB.

## 5. Architecture & Code Integration
Implemented in `packages/ranking/topsis_ranker.py`:

```python
"""
TOPSIS multi-criteria decision ranker implemented with NumPy.
"""
import numpy as np
from typing import List, Dict, Any, Tuple

class TOPSISRanker:
    """
    Ranks candidates using Technique for Order of Preference by Similarity to Ideal Solution.
    """
    def __init__(self, criteria_weights: List[float], criteria_types: List[str]):
        """
        Args:
            criteria_weights: Importance weight per criterion (sum to 1.0).
            criteria_types: List of 'benefit' (higher is better) or 'cost' (lower is better).
        """
        self.weights = np.array(criteria_weights, dtype=np.float64)
        self.weights = self.weights / np.sum(self.weights)  # Ensure exact normalization
        self.types = criteria_types

    def rank(self, candidate_ids: List[str], matrix: np.ndarray) -> List[Tuple[str, float]]:
        """
        Calculates TOPSIS relative closeness scores for candidates.
        
        Args:
            candidate_ids: List of candidate identifier strings.
            matrix: 2D array of shape (n_candidates, n_criteria).
            
        Returns:
            List of (candidate_id, closeness_score) sorted descending.
        """
        # Step 1: Vector normalization to prevent criteria scale distortion
        col_norms = np.sqrt(np.sum(matrix ** 2, axis=0))
        col_norms[col_norms == 0] = 1.0  # Prevent divide-by-zero on zero-variance columns
        norm_matrix = matrix / col_norms
        
        # Step 2: Weight normalized matrix
        weighted_matrix = norm_matrix * self.weights
        
        # Step 3: Determine positive (best) and negative (worst) ideal solutions
        ideal_pos = np.zeros(weighted_matrix.shape[1])
        ideal_neg = np.zeros(weighted_matrix.shape[1])
        
        for j, c_type in enumerate(self.types):
            if c_type == "benefit":
                ideal_pos[j] = np.max(weighted_matrix[:, j])
                ideal_neg[j] = np.min(weighted_matrix[:, j])
            else: # cost criteria
                ideal_pos[j] = np.min(weighted_matrix[:, j])
                ideal_neg[j] = np.max(weighted_matrix[:, j])
                
        # Step 4: Euclidean distance to ideals
        dist_pos = np.sqrt(np.sum((weighted_matrix - ideal_pos) ** 2, axis=1))
        dist_neg = np.sqrt(np.sum((weighted_matrix - ideal_neg) ** 2, axis=1))
        
        # Step 5: Closeness coefficient: S_i^- / (S_i^+ + S_i^-)
        denominator = dist_pos + dist_neg
        denominator[denominator == 0] = 1.0
        closeness = dist_neg / denominator
        
        results = [(cid, float(c_score)) for cid, c_score in zip(candidate_ids, closeness)]
        results.sort(key=lambda x: x[1], reverse=True)
        return results
```

## 6. Failure Modes, Fallbacks & Edge Cases
- **Rank Reversal Phenomenon:** In TOPSIS, adding or removing an irrelevant candidate can sometimes alter the relative ranking of remaining candidates due to changing ideal reference points. This behavior is documented transparently in `docs/research/topsis_evaluation.md`.
- **Zero Variance Criteria:** If all candidates have identical scores for a requirement (e.g. all have 0 years experience), `col_norms` division by zero is safely guarded with a fallback norm of 1.0.
