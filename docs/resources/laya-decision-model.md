# Resource: Laya Decision Model (Research Investigation)

## 1. Overview & Purpose
**Laya** is a candidate compact typed-decision model designed for discrete criteria scoring, decision extraction, and multi-choice evaluation.

In the **Resume Intelligence, Ranking & Fairness Lab**, Laya represents a specific research investigation:
- Explores whether a specialized decision model outperforms general-purpose generative LLMs, heuristic weighted scoring, and supervised ranking (LambdaMART) in speed, VRAM footprint, and criterion scoring accuracy.
- Accepts structured inputs: `[Job Requirement, Verbatim Candidate Evidence]`.
- Generates structured decision judgments (`MATCH`, `PARTIAL_MATCH`, `NO_MATCH` + confidence score).
- Operates under strict verification gates per `Agent.md` and `Project.md` to prevent unauthenticated model execution.

## 2. Upstream Provenance & Verification Gate
- **Candidate Upstream Repository:** https://github.com/NandhaKishorM/laya
- **Candidate Hugging Face Namespace:** https://huggingface.co/convaiinnovations/laya
- **Verification Gate Requirement (Agent.md § 5.4):**
  - Verify official maintainer identity, official repository commit history, and model card availability.
  - Inspect model architecture, quantization format, parameter count, and license terms.
  - Test whether inference can execute on the target hardware (4 GB VRAM GPU or CPU) without out-of-memory errors.
  - **Status:** Under active investigation. If verification fails or models cannot be authenticated, the system maintains a typed mock adapter and documents a formal blocker report in `docs/research/laya_investigation.md`.

## 3. Local Installation & Model Weights Isolation
If verified and approved:
- **Local Checkpoint Path:** `<project_root>/models/weights/laya/`
- **Cache Location:** `<project_root>/models/cache/`
- **Audit Manifest:** Recorded in `models/manifest.json`.
- In mock/test mode: Requires zero downloads, executing with a deterministic rubric simulator in `packages/decision_models/laya_adapter.py`.

## 4. Hardware Footprint & Resource Impact
- **Planned Parameter Budget:** Expected to be < 1.5B parameters or quantized to 4-bit/8-bit to fit within the 4 GB VRAM GPU alongside desktop display buffers.
- **VRAM Target:** < 2.2 GB VRAM; CPU fallback if GPU memory is constrained.
- **RAM Footprint:** ~1.5 GB system RAM in PyTorch / GGUF runtime.

## 5. Architecture & Code Integration
Implemented in `packages/decision_models/laya_adapter.py`:

```python
"""
Laya decision model adapter adhering to the BaseDecisionModel contract.
"""
from typing import Dict, Any, List
from packages.common.schemas import EvidenceReference

class LayaDecisionAdapter:
    """
    Adapter interfacing with the Laya decision model or deterministic mock fixture.
    """
    def __init__(self, use_mock: bool = True):
        self.use_mock = use_mock
        self.model = None

    def evaluate_criterion(
        self,
        criterion_description: str,
        evidence: EvidenceReference,
    ) -> Dict[str, Any]:
        """
        Scores candidate evidence against a single job requirement.
        
        Returns:
            Dict containing decision ('match' | 'partial' | 'no_match'), score, and confidence.
        """
        if self.use_mock:
            # Deterministic simulation for test verification and CI
            snippet = evidence.verbatim_snippet.lower()
            criterion = criterion_description.lower()
            
            # Simple keyword overlap heuristic for mock mode
            words = set(criterion.split())
            matches = sum(1 for w in words if w in snippet)
            ratio = matches / max(len(words), 1)
            
            if ratio > 0.6:
                return {"decision": "match", "score": 1.0, "confidence": 0.9}
            elif ratio > 0.2:
                return {"decision": "partial", "score": 0.5, "confidence": 0.7}
            else:
                return {"decision": "no_match", "score": 0.0, "confidence": 0.85}

        # Real model inference code executes here upon verification
        raise NotImplementedError("Real Laya checkpoint is undergoing verification gate.")
```

## 6. Failure Modes, Fallbacks & Edge Cases
- **Verification Failure / Incompatible Checkpoint:** If the candidate checkpoint is invalid or unlicensed, the research harness records a blocked status with full evidence in `docs/research/laya_investigation.md` and seamlessly falls back to TOPSIS and Weighted Scoring.
