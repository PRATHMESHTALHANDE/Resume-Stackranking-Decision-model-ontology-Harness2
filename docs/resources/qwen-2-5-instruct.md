# Resource: Qwen2.5-1.5B-Instruct Local Language Model

## 1. Overview & Purpose
**Qwen2.5-1.5B-Instruct** is an advanced open-weights large language model released by Alibaba Cloud, known for strong performance in instruction following, structured data extraction, and factual reasoning relative to its compact parameter footprint.

In the **Resume Intelligence, Ranking & Fairness Lab**, Qwen2.5-1.5B is quantized to **4-bit `Q4_K_M` GGUF** and deployed entirely offline on local hardware:
- **Zero Cloud Leakage**: Candidate resumes and sensitive PII never leave the local machine.
- **Dual Role**:
  1. **Resume Entity Extraction**: Parses raw OCR/PDF text into structured JSON schemas (skills, job titles, degrees, dates).
  2. **LLM Qualification Summaries**: Synthesizes 2–3 sentence natural language hiring narratives in the UI explaining *why the candidate is on top* and highlighting verified resume citations.

---

## 2. Technical Specifications

| Parameter | Specification |
|---|---|
| **Base Model** | Qwen/Qwen2.5-1.5B-Instruct |
| **Quantization** | GGUF Q4_K_M (4-bit medium k-quant) |
| **Model Size on Disk** | $\approx 1.12\text{ GB}$ |
| **Parameters** | 1.54 Billion |
| **Context Window** | 2,048 tokens (configured locally for speed) |
| **Decoding Policy** | Greedy (`temperature = 0.0`) for strict deterministic extraction |
| **Execution Engine** | `llama-cpp-python` with CUDA GPU layer offload |

---

## 3. Real-World HR Purpose & Benefits
- **Structured Parsing**: Transforms messy, multi-column resume PDFs into standardized Pydantic data schemas without brittle regex rules alone.
- **Auditable Summaries**: Rather than giving a raw number (e.g., "Score: 89%"), the LLM generates a human-readable review for hiring managers:
  > *"Candidate 101 holds the #1 TOP RANK for 'Senior Python Lead' with an 89.2% match score. They demonstrate verified competencies in Python, FastAPI, and Kubernetes, backed by 5 verbatim resume citations. The candidate exceeds the minimum experience requirement (7.0 yrs vs 5.0 yrs required)."*
- **Offline / Enterprise Air-Gapped Deployment**: Complies with GDPR, CCPA, and enterprise privacy standards because no external API keys (OpenAI, Anthropic, Gemini) are required.

---

## 4. Hardware Footprint & Resource Impact
- **GPU VRAM Usage**: $\approx 1.2\text{ GB}$ VRAM when fully offloaded (28 layers on NVIDIA RTX 3050).
- **CPU Fallback**: Can execute on CPU with 4 threads in $\approx 2.5\text{ GB}$ system RAM if no GPU is available.
- **Inference Latency**:
  - Summary Generation: $\approx 250 - 450\text{ ms}$ on local GPU.
  - Profile Extraction: $\approx 800 - 1,200\text{ ms}$ per candidate page.

---

## 5. Architecture & Code Integration
- **Extractor Engine**: [`packages/extraction/llm_extractor.py`](file:///c:/Users/roari/Downloads/AI%20Projects/HR%20Resume%20Stackranking%20-%20Decision%20model%20+%20LLM%20+%20Ontology%20+%20Harness2/packages/extraction/llm_extractor.py)
- **Explanation Synthesizer**: [`packages/decision_models/explanation.py`](file:///c:/Users/roari/Downloads/AI%20Projects/HR%20Resume%20Stackranking%20-%20Decision%20model%20+%20LLM%20+%20Ontology%20+%20Harness2/packages/decision_models/explanation.py)
- **Designated Weights Directory**: `models/weights/llm/Qwen2.5-1.5B-Instruct-Q4_K_M.gguf`
- **Graceful Deterministic Fallback**: If the `.gguf` file is absent, the system seamlessly transitions to [`DeterministicExtractor`](file:///c:/Users/roari/Downloads/AI%20Projects/HR%20Resume%20Stackranking%20-%20Decision%20model%20+%20LLM%20+%20Ontology%20+%20Harness2/packages/extraction/deterministic.py) with zero runtime crash.
