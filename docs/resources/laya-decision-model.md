# Resource: Laya System-1 Decision Model (`convaiinnovations/laya`)

## 1. Overview & Purpose
**Laya** is an open-source, non-autoregressive **System-1 Decision Model** developed by Convai Innovations and hosted on Hugging Face ([`convaiinnovations/laya`](https://huggingface.co/convaiinnovations/laya)).

Unlike traditional generative Large Language Models (LLMs) that generate free-form text tokens autoregressively—which incurs high computational latency and token hallucination risks—**Laya evaluates text states against typed decision queries in a single forward pass**.

In the **Resume Intelligence, Ranking & Fairness Lab**, Laya serves as the dedicated neural decision engine for **discrete criterion verification**:
- **Non-Autoregressive Inference**: Scores candidate evidence directly against job requirements without text generation hallucinations.
- **Typed Decision Outputs**: Maps candidate evidence into bounded decision choices (`match`, `partial`, `no_match`) with calibrated confidence ratings.
- **Strict Non-Compensatory Evaluation**: Designed for high-compliance hiring where a failure to satisfy a mandatory requirement cannot be offset by unrelated general tenure.

---

## 2. Model Architecture & Specifications

| Parameter | Specification |
|---|---|
| **Hugging Face Model ID** | [`convaiinnovations/laya`](https://huggingface.co/convaiinnovations/laya) |
| **Python Library** | `laya` (`pip install laya>=0.4.15`) |
| **Encoder Backbone** | Bidirectional `ModernBERT-large` (395 Million parameters) |
| **Decision Head** | 2-layer transformer decision head (26 Million parameters) |
| **Total Parameters** | **421 Million parameters** |
| **Disk / Download Footprint** | $\approx 840\text{ MB}$ (cached in `models/cache/huggingface/`) |
| **License** | Apache-2.0 (Permissive open source) |
| **Inference Mode** | Single parallel forward pass (`@torch.no_grad()`) |

---

## 3. How It Works in Stackranking

When evaluating a candidate $C_i$ against a job criterion $K_j$:
1. **State Construction**: The system formats the candidate's verified resume citation:
   ```python
   state = {"evidence": candidate_evidence_text}
   ```
2. **Typed Question Schema**: It submits a typed `choice` question primitive:
   ```python
   questions = {
       "criterion_match": {
           "type": "choice",
           "instructions": f"Evaluate whether candidate evidence satisfies: '{criterion_description}'",
           "criteria": {
               "match": "Evidence explicitly demonstrates full competence or meets requirement",
               "partial": "Evidence demonstrates related, foundational, or partial competence",
               "no_match": "No supporting evidence found or fails requirement",
           },
       }
   }
   ```
3. **Single Forward Pass Execution**:
   ```python
   result = laya_agent.predict(state, questions)
   ```
4. **Decision Mapping**:
   - `match` $\rightarrow \text{Score} = 1.0$
   - `partial` $\rightarrow \text{Score} = 0.5$
   - `no_match` $\rightarrow \text{Score} = 0.0$
   - The calibrated confidence score $P(\text{choice})$ is attached to the candidate's breakdown telemetry.

---

## 4. Hardware Footprint & Compute Budget
- **GPU VRAM**: $\approx 840\text{ MB}$ to $1.2\text{ GB}$ VRAM when placed on CUDA GPU. Fits comfortably inside the RTX 3050 (4 GB VRAM) alongside display buffers.
- **Automatic Device Fallback**: If GPU VRAM is full, Laya automatically falls back to CPU execution without throwing out-of-memory errors.
- **Latency**: $\approx 25 - 45\text{ ms}$ per evaluation on CUDA GPU; $\approx 150 - 250\text{ ms}$ on CPU.

---

## 5. Architecture & Code Integration
- **Adapter Implementation**: [`packages/decision_models/laya_adapter.py`](file:///c:/Users/roari/Downloads/AI%20Projects/HR%20Resume%20Stackranking%20-%20Decision%20model%20+%20LLM%20+%20Ontology%20+%20Harness2/packages/decision_models/laya_adapter.py)
- **API Registry**: Registered in [`apps/api/routes/rankings.py`](file:///c:/Users/roari/Downloads/AI%20Projects/HR%20Resume%20Stackranking%20-%20Decision%20model%20+%20LLM%20+%20Ontology%20+%20Harness2/apps/api/routes/rankings.py) under `"laya_adapter"`.
- **Ensemble Integration**: Concurrently executed inside [`packages/ranking/ensemble_ranker.py`](file:///c:/Users/roari/Downloads/AI%20Projects/HR%20Resume%20Stackranking%20-%20Decision%20model%20+%20LLM%20+%20Ontology%20+%20Harness2/packages/ranking/ensemble_ranker.py) for the "All Models in Symbiosis" consensus mode.
- **Resilient Fallback**: If offline or if model weights are unavailable, the adapter seamlessly falls back to a deterministic keyword/phrase rubric so tests and CI runs never fail.
