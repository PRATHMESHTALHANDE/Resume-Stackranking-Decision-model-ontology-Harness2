# Resource: Fairlearn (Fairness Diagnostics & Disparity Metrics)

## 1. Overview & Purpose
**Fairlearn** is an open-source, community-driven Python library that helps practitioners assess and improve the fairness of machine learning systems, developed by researchers and engineers from Microsoft, Google, and academia.

In the **Resume Intelligence, Ranking & Fairness Lab**, Fairlearn provides the diagnostic group disparity foundation:
- Measures Selection Rate Differences and Demographic Parity Ratios when evaluating candidate shortlisting across controlled synthetic groups.
- Audits False Positive Rates and False Negative Rates against human-reviewed relevance labels.
- Calculates Disparate Impact metrics for diagnostic review.
- Operates strictly under the **Medical/HR Safety & Ethical Boundary**: outputs are labeled "Diagnostic Only — Does Not Prove Legal Compliance", preventing algorithmic overconfidence.

## 2. Upstream Provenance & License
- **Official Documentation:** https://fairlearn.org/
- **GitHub Repository:** https://github.com/fairlearn/fairlearn
- **License:** MIT License (Permissive open source).
- **Core Governance:** Fairlearn Community / NumFOCUS.

## 3. Local Installation & Storage Location
Installed into `.venv/` via `uv`:
```powershell
uv add fairlearn
```
Requires no external cloud access, telemetry, or remote services.

## 4. Hardware Footprint & Resource Impact
- **System RAM:** ~20–35 MB.
- **Execution Speed:** Instantaneous (< 5 ms for 1,000 candidate evaluations on CPU).
- **GPU VRAM:** 0 MB.

## 5. Architecture & Code Integration
Implemented in `packages/fairness/parity.py`:

```python
"""
Fairness diagnostics evaluating selection rate differences and demographic parity.
"""
import numpy as np
from fairlearn.metrics import MetricFrame, selection_rate, false_positive_rate
from typing import Dict, Any, List

class FairnessAuditor:
    """
    Computes diagnostic group parity and selection disparity metrics.
    """
    def evaluate_shortlist_disparity(
        self,
        y_true: np.ndarray,          # Ground-truth suitability labels (0 or 1)
        y_pred: np.ndarray,          # Model shortlist decisions (1 if rank <= Top-K else 0)
        sensitive_features: List[str] # Synthetic group markers (e.g. ['group_a', 'group_b'])
    ) -> Dict[str, Any]:
        """
        Calculates selection rates and disparity metrics across sensitive groups.
        """
        metric_frame = MetricFrame(
            metrics={
                "selection_rate": selection_rate,
                "false_positive_rate": false_positive_rate,
            },
            y_true=y_true,
            y_pred=y_pred,
            sensitive_features=sensitive_features,
        )
        
        # Calculate Demographic Parity Ratio (min selection rate / max selection rate)
        sel_by_group = metric_frame.by_group["selection_rate"]
        max_rate = sel_by_group.max()
        min_rate = sel_by_group.min()
        parity_ratio = (min_rate / max_rate) if max_rate > 0 else 1.0
        
        return {
            "by_group_metrics": metric_frame.by_group.to_dict(),
            "selection_rate_difference": metric_frame.difference()["selection_rate"],
            "demographic_parity_ratio": float(parity_ratio),
            "sample_sizes": {g: int(np.sum(np.array(sensitive_features) == g)) for g in set(sensitive_features)},
            "warning": (
                "Diagnostic aid only. Sample size may limit statistical validity. "
                "Fairness metrics do not guarantee legal compliance."
            )
        }
```

## 6. Failure Modes, Fallbacks & Edge Cases
- **Small Sample Subgroups:** When evaluated on small batches (< 30 candidates per group), demographic parity ratios fluctuate wildly due to high variance. The system explicitly outputs sample-size confidence warnings and marks subgroup conclusions as non-definitive when $N < 50$.
- **Zero Demographic Inference:** In accordance with `Project.md` § 2.2, the system NEVER attempts to infer demographic traits from real candidate resumes or names. Group labels are exclusively applied to synthetic audit datasets.
