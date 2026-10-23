"""
Module: packages.fairness.parity
Description:
    Demographic parity and selection rate disparity metrics using Fairlearn.
    Evaluates candidate shortlists across controlled synthetic groups.

Author:
    Resume Intelligence Architect
"""
import numpy as np
from typing import Dict, Any, List

try:
    from fairlearn.metrics import MetricFrame, selection_rate, false_positive_rate
except (ImportError, OSError, Exception):
    MetricFrame = None

class ParityAuditor:
    """
    Computes diagnostic group parity and selection disparity ratios.
    """
    @staticmethod
    def evaluate_shortlist_disparity(
        y_true: List[int],               # Ground-truth binary relevance (0 or 1)
        y_pred: List[int],               # Model shortlist decision (1 if Top-K, else 0)
        sensitive_features: List[str],   # Synthetic group labels (e.g. ['group_a', 'group_b'])
    ) -> Dict[str, Any]:
        """
        Calculates selection rates, false positive rates, and demographic parity ratio.
        """
        y_t = np.array(y_true, dtype=int)
        y_p = np.array(y_pred, dtype=int)
        groups = np.array(sensitive_features)

        unique_groups = list(set(sensitive_features))
        group_counts = {g: int(np.sum(groups == g)) for g in unique_groups}

        # Check for small sample size
        small_sample = any(count < 30 for count in group_counts.values())

        if MetricFrame is not None:
            try:
                frame = MetricFrame(
                    metrics={"selection_rate": selection_rate},
                    y_true=y_t,
                    y_pred=y_p,
                    sensitive_features=groups,
                )
                sel_rates = frame.by_group["selection_rate"].to_dict()
                max_rate = max(sel_rates.values()) if sel_rates else 1.0
                min_rate = min(sel_rates.values()) if sel_rates else 0.0
                parity_ratio = float(min_rate / max_rate) if max_rate > 0 else 1.0
                diff = float(frame.difference()["selection_rate"])
            except Exception:
                sel_rates = {}
                parity_ratio = 1.0
                diff = 0.0
        else:
            # Fallback pure-Python computation
            sel_rates = {}
            for g in unique_groups:
                mask = (groups == g)
                rate = float(np.mean(y_p[mask])) if np.sum(mask) > 0 else 0.0
                sel_rates[g] = rate
            max_r = max(sel_rates.values()) if sel_rates else 1.0
            min_r = min(sel_rates.values()) if sel_rates else 0.0
            parity_ratio = float(min_r / max_r) if max_r > 0 else 1.0
            diff = float(max_r - min_r)

        return {
            "selection_rates_by_group": sel_rates,
            "demographic_parity_ratio": parity_ratio,
            "selection_rate_difference": diff,
            "group_sample_sizes": group_counts,
            "is_statistically_constrained": small_sample,
            "warning": (
                "Diagnostic audit only. Small subgroup sample sizes may limit statistical significance. "
                "Metrics do not imply legal compliance or absolute lack of bias."
            ),
        }
