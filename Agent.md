# Agent.md — Master Autonomous Execution Specification: Resume Intelligence, Ranking & Fairness Lab

> **Role:** You are the Lead Software Architect, ML Engineer, Full-Stack Frontend Engineer, QA Specialist, and Technical Writer responsible for implementing the open-source platform described in `Project.md` and `Plan.md`.  
> **Master Reference:** [Project.md](file:///c:/Users/roari/Downloads/AI%20Projects/HR%20Resume%20Stackranking%20-%20Decision%20model%20+%20LLM%20+%20Ontology%20+%20Harness2/Project.md) | [Plan.md](file:///c:/Users/roari/Downloads/AI%20Projects/HR%20Resume%20Stackranking%20-%20Decision%20model%20+%20LLM%20+%20Ontology%20+%20Harness2/Plan.md)  
> **Target Hardware:** Windows 11, Intel Core i7-12650H (10 Cores, 16 Logical Processors), 16 GB Physical RAM, NVIDIA GeForce RTX 3050 Laptop GPU (4 GB VRAM, Driver 561.17, CUDA 12.6).  
> **Core Operating Principles:** 100% Open-Source; Local-First; Zero Unmonitored Global Disk Caching; Human-in-the-Loop Review Aid; Comprehensive Code Commenting; Accessible Neumorphic UI.

---

## 1. Mandatory Core Engineering Principles & Constraints

Antigravity must adhere strictly to these principles across every single task:

1. **Evidence Before Ranking:** Never generate a candidate score or ranking without explicit, traceable evidence snippets extracted verbatim from the parsed resume document.
2. **Zero Fact Fabrication / Hallucination:** Never infer unstated degrees, certifications, job titles, or skills. Missing evidence must be explicitly labeled as `insufficient_information` or `uncertain`, never penalized as a negative fact without policy.
3. **100% Open Source & Zero Mandatory Paid APIs:** The entire system must run completely local and offline after initial package installation. No external LLM APIs (OpenAI, Anthropic, Google Cloud Vertex, etc.) may be required for core functionality.
4. **Local Model Weight Isolation (`models/weights/` & `models/cache/`):**
   - **CRITICAL DISK INTEGRITY RULE:** Model weights, tokenizers, checkpoints, and GGUF files must NEVER be silently written to global user profile caches (such as `C:\Users\<user>\.cache\huggingface`).
   - All runtime environments and scripts must explicitly route cache and model directories inside the project workspace:
     - `HF_HOME = <project_root>/models/cache/huggingface`
     - `TRANSFORMERS_CACHE = <project_root>/models/cache/huggingface`
     - `SENTENCE_TRANSFORMERS_HOME = <project_root>/models/cache/sentence_transformers`
     - `LLAMA_CPP_MODELS_DIR = <project_root>/models/weights/gguf`
     - `ESCO_DIR = <project_root>/data/ontology/esco`
   - Every downloaded or converted model asset must be registered in `<project_root>/models/manifest.json` with its relative path, exact byte size, SHA-256 checksum, upstream URL, and license.
5. **Separate Markdown Documentation for Every Resource (`docs/resources/*.md`):**
   - For **every single** third-party library, ML model, ontology, dataset, framework, and runtime used in this project, there must be an individual, dedicated, well-formatted markdown document in `docs/resources/<resource-name>.md`.
   - The user must be able to open `docs/resources/` and inspect how each component works, its license, installation, and code examples.
6. **Exhaustive Code Commenting Standard:**
   - Every file, class, method, function, data schema, mathematical formula (TOPSIS distances, RRF rank decay, cosine similarity, BM25 scoring), and React component/hook must contain comprehensive docstrings and inline explanatory comments.
   - When a user reads any line of code, the purpose, algorithmic logic, and error handling must be immediately evident.
7. **Accessible Neumorphic (Soft UI) Visual Design:**
   - The user interface must employ a clean, modern Neumorphic design system with soft raised/recessed surfaces, dual-light box shadows, smooth transitions, and distinct light/dark themes.
   - Neumorphism must strictly maintain WCAG 2.2 AA accessibility: visible focus rings (`outline: 2px solid #3b82f6; outline-offset: 2px;`), high-contrast typography, screen-reader semantics, and accessible charts.
8. **Deterministic & Reproducible Evaluation:**
   - Benchmark claims must be backed by exact numbers (nDCG@5/10, MRR, Precision@k, Recall@k, latency in ms, peak RAM in MB, peak VRAM in MB) on explicitly versioned, immutable evaluation splits.
9. **Human-in-the-Loop Employment Boundary:**
   - The system is an evidence-analysis and ranking decision-support aid for human HR recruiters. It must NEVER execute autonomous hiring, rejection, or candidate disqualification. Every output must display an advisory review banner.
10. **Laya Decision Model Research Gate:**
    - Laya must be investigated as a formal research task. If the official upstream repository/checkpoint (`convaiinnovations/laya` or `NandhaKishorM/laya`) is verified and runs within 4 GB VRAM, implement the real adapter. If unavailable, blocked, or unlicensed, maintain a typed adapter interface and fixture mock, and generate a transparent blocker report in `docs/research/laya_investigation.md`. Never silently fake model outputs.

---

## 2. Applicable Skills & Plugins Guidelines

When implementing components, Antigravity should leverage relevant established skills and plugins:

| Domain | Recommended Skill / Plugin | Application in this Project |
|---|---|---|
| **Frontend UI** | `frontend-development` & `modern-web-guidance` | React 18/19, Vite, TypeScript, Tailwind CSS Neumorphic tokens, dual-shadow CSS, accessible form controls, keyboard navigation. |
| **Backend API** | `backend-fastapi` | FastAPI asynchronous endpoints, Pydantic v2 schemas, SQLite parameterization, streaming responses (SSE), error middleware. |
| **Machine Learning** | `ml-best-practices` | Evaluation metrics (nDCG, MRR), fair splits, counterfactual evaluation, cross-validation, hyperparameter discipline. |
| **Dependency Mgmt** | `managing-python-dependencies` | `uv` lock file management, clean virtual environments, avoiding global pollution. |
| **Safety & Audit** | `accidental-data-loss-prevention` | Safe database migrations, non-destructive file updates, local artifact isolation. |

---

## 3. Dedicated Resource Documentation Specification (`docs/resources/`)

Whenever a resource is introduced into `pyproject.toml`, `package.json`, or the runtime stack, Antigravity must create or update its dedicated markdown file in `docs/resources/`.

Each resource document must strictly follow this structure:
```markdown
# Resource: <Resource Name> (<Official Identifier / Version>)

## 1. Overview & Purpose
- What this tool/library/model does.
- Specific role in the Resume Intelligence & Ranking platform.

## 2. Upstream Provenance & License
- Official Website / Repository URL.
- License Type (e.g. MIT, Apache-2.0, BSD-3-Clause, OpenRAIL).
- Permitted Commercial / Research Uses & Attribution Requirements.

## 3. Local Installation & Storage Location
- Installation command (`uv add <pkg>` or `npm install <pkg>`).
- If model weights: Exact local path (`models/weights/...`), file size, SHA-256 hash.

## 4. Hardware Footprint & Resource Impact
- RAM usage (Idle vs. Peak).
- VRAM allocation (if GPU-accelerated).
- Latency profile (p50 / p95).

## 5. Architecture & Code Integration
- Code snippet demonstrating exact usage in our codebase with full comments.
- Key classes, functions, or hooks utilized.

## 6. Failure Modes, Fallbacks & Edge Cases
- Known limitations, CPU fallbacks, error handling strategy.
```

### Initial Required Resource Catalog:
1. `docs/resources/fastapi.md`
2. `docs/resources/pydantic.md`
3. `docs/resources/pymupdf.md`
4. `docs/resources/docling.md`
5. `docs/resources/sqlite.md`
6. `docs/resources/rank-bm25.md`
7. `docs/resources/sentence-transformers-all-minilm-l6-v2.md`
8. `docs/resources/esco-ontology.md`
9. `docs/resources/networkx.md`
10. `docs/resources/topsis.md`
11. `docs/resources/lightgbm.md`
12. `docs/resources/laya-decision-model.md`
13. `docs/resources/llama-cpp-python.md`
14. `docs/resources/qwen-gguf.md`
15. `docs/resources/phi-4-mini-gguf.md`
16. `docs/resources/cross-encoder-ms-marco.md`
17. `docs/resources/ranx.md`
18. `docs/resources/fairlearn.md`
19. `docs/resources/react-vite-typescript.md`
20. `docs/resources/tailwind-css-neumorphism.md`
21. `docs/resources/tanstack-query.md`
22. `docs/resources/tanstack-table.md`
23. `docs/resources/cytoscape-js.md`
24. `docs/resources/apache-echarts.md`

---

## 4. Model Weights Management & Isolation (`models/`)

### 4.1 Directory Structure
```text
models/
├── weights/
│   ├── llm/                 # Quantized GGUF models (e.g. Qwen2.5-1.5B-Instruct-Q4_K_M.gguf)
│   ├── embeddings/          # sentence-transformers/all-MiniLM-L6-v2
│   ├── reranker/            # cross-encoder/ms-marco-MiniLM-L-6-v2
│   └── laya/                # Laya checkpoint if verified
├── cache/
│   ├── huggingface/         # Explicitly isolated HF cache
│   └── sentence_transformers/ # Explicitly isolated ST cache
├── manifest.json            # Machine-readable registry of all downloaded assets
└── README.md                # Human-readable download guide and checksum verification
```

### 4.2 Central Settings Enforcer (`packages/common/settings.py`)
All backend scripts and workers must import from `packages.common.settings` before loading any Hugging Face, PyTorch, or llama.cpp modules:
```python
import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
MODELS_DIR = PROJECT_ROOT / "models"
WEIGHTS_DIR = MODELS_DIR / "weights"
CACHE_DIR = MODELS_DIR / "cache"

# Force environment overrides to isolate disk usage to project workspace
os.environ["HF_HOME"] = str(CACHE_DIR / "huggingface")
os.environ["TRANSFORMERS_CACHE"] = str(CACHE_DIR / "huggingface")
os.environ["SENTENCE_TRANSFORMERS_HOME"] = str(CACHE_DIR / "sentence_transformers")
os.environ["LLAMA_CPP_MODELS_DIR"] = str(WEIGHTS_DIR / "llm")
```

---

## 5. Code Commenting Standards

Every line of code written in this project must adhere to strict commenting rules:

1. **Module-Level Docstrings:**
   Each Python file must begin with a comprehensive header explaining:
   - Module Purpose.
   - Algorithms or Mathematical Foundations implemented.
   - Input contracts and Output guarantees.
   - Edge case and failure handling behaviors.

2. **Function & Method Docstrings (Google Style):**
   - Summary of operation.
   - `Args:` each argument with expected type, unit, and validation boundary.
   - `Returns:` return value description and schema.
   - `Raises:` possible exceptions and mitigation.
   - `Algorithm / Formula:` mathematical or heuristic formulation.

3. **Inline Comments for Math & Complex Logic:**
   - Explain *why* an operation is performed, not just *what* the syntax does.
   - Include equations in comments (e.g., `# TOPSIS Euclidean Distance: d_i^+ = sqrt(sum((v_ij - v_j^+)^2))`).
   - Detail regular expressions, data transformations, and normalization logic.

4. **Frontend Component Comments:**
   - Explain component hierarchy, state flow, accessibility ARIA roles, and Neumorphic design token mappings.

---

## 6. Neumorphic (Soft UI) Design System

### 6.1 Visual Philosophy
Neumorphism relies on subtle, soft dual-light shadows that simulate physical surfaces protruding from or recessed into the background plane.

### 6.2 Design Tokens (Tailwind CSS Integration)
- **Light Theme:**
  - Background Base: `#E8ECF2` (Soft cool grey-blue)
  - Surface Raised: `#E8ECF2` with `box-shadow: 6px 6px 14px #c2c8d2, -6px -6px 14px #ffffff`
  - Surface Inset (pressed/sunken): `box-shadow: inset 4px 4px 8px #c2c8d2, inset -4px -4px 8px #ffffff`
  - Border: `1px solid rgba(255, 255, 255, 0.6)`
  - Accent Colors: `#3B82F6` (Electric Blue), `#10B981` (Emerald), `#F59E0B` (Amber), `#EF4444` (Rose)
  - Primary Text: `#1E293B` (Slate-800, contrast ratio > 7:1 against base)
  - Secondary Text: `#475569` (Slate-600, contrast ratio > 4.5:1 against base)

- **Dark Theme:**
  - Background Base: `#181B20` (Deep obsidian slate)
  - Surface Raised: `#181B20` with `box-shadow: 5px 5px 12px #0c0e10, -5px -5px 12px #242830`
  - Surface Inset: `box-shadow: inset 3px 3px 6px #0c0e10, inset -3px -3px 6px #242830`
  - Border: `1px solid rgba(255, 255, 255, 0.08)`
  - Primary Text: `#F1F5F9` (Slate-100)
  - Secondary Text: `#94A3B8` (Slate-400)

### 6.3 Accessibility Safeguards (WCAG 2.2 AA)
- Never rely on shadows alone to indicate interactive states.
- All buttons, inputs, and toggles must have visible focus indicators (`ring-2 ring-blue-500 ring-offset-2`).
- Charts and graphs must provide tabular data equivalents or text summaries.
- Reduced-motion media query (`prefers-reduced-motion: reduce`) disables smooth shadow transformations.

---

## 7. Master Phased Execution Roadmap

Antigravity executes in discrete milestones. Each milestone must satisfy its verification gate before proceeding:

```text
PHASE 0 (Audit & Recon) ➔ PHASE 1 (Specs, Rules & Resources) ➔ PHASE 2 (Repo & Env Setup)
     ➔ PHASE 3 (Data Contracts & Ingestion) ➔ PHASE 4 (Structured Extraction)
     ➔ PHASE 5 (ESCO Ontology & NetworkX Graph) ➔ PHASE 6 (Retrieval & Rankers)
     ➔ PHASE 7 (Evaluation & Fairness Harness) ➔ PHASE 8 (FastAPI Backend)
     ➔ PHASE 9 (Neumorphic Frontend) ➔ PHASE 10 (Verification & Release)
```

### [x] Phase 0: Hardware & Environment Reconnaissance
- [x] Measure CPU, RAM, GPU, VRAM, disk space, and CUDA runtime.
- [x] Record exact hardware: Intel i7-12650H, 16 GB RAM, RTX 3050 Laptop GPU (4 GB VRAM), Windows 11.
- [x] Verify `uv` CLI and Python 3.11 availability.

### [ ] Phase 1: Specifications, Rules & Resource Documentation
- [x] Update `Agent.md` with hardened guidelines, resource rules, model weights isolation, commenting, and neumorphic UI.
- [ ] Generate master execution `Plan.md` in the project root.
- [ ] Initialize `docs/resources/` with comprehensive markdown files for all 24+ core resources.

### [ ] Phase 2: Repository Scaffolding & Isolated Environment Setup
- [ ] Scaffold project layout (`apps/`, `packages/`, `configs/`, `data/`, `models/`, `docs/`, `tests/`).
- [ ] Initialize `pyproject.toml` with `uv` and pin all dependencies.
- [ ] Configure `models/weights/` and `models/cache/` environment redirection in `packages/common/settings.py`.
- [ ] Create `models/manifest.json`.

### [ ] Phase 3: Core Data Contracts & Document Ingestion
- [ ] Implement Pydantic v2 schemas in `packages/common/schemas.py` (`ResumeDocument`, `ResumeProfile`, `JobDescription`, `EvidenceReference`, `RankingResult`, `EvaluationRun`).
- [ ] Implement PDF and DOCX text extraction with page/section provenance in `packages/ingestion/`.
- [ ] Add SHA-256 deduplication and parser caching.
- [ ] Write unit tests in `tests/unit/test_ingestion.py`.

### [ ] Phase 4: Structured Extraction & Skill Normalization
- [ ] Implement deterministic section parsing (regex, date normalizer).
- [ ] Implement local LLM semantic extractor interface with GGUF support (`llama-cpp-python`).
- [ ] Implement offline deterministic mock extractor fixture for CI.
- [ ] Write schema validation and extraction tests in `tests/unit/test_extraction.py`.

### [ ] Phase 5: ESCO Skill Ontology & NetworkX Graph
- [ ] Implement ESCO snapshot loader in `packages/ontology/esco_loader.py`.
- [ ] Implement multi-stage skill alias normalizer (exact, normalized, alias, fuzzy).
- [ ] Build in-memory NetworkX graph in `packages/graph/skill_graph.py`.
- [ ] Implement graph features (coverage, related skills, shortest evidence paths).
- [ ] Write graph unit tests in `tests/unit/test_graph.py`.

### [ ] Phase 6: Multi-Model Retrieval & Decision Engine
- [ ] Implement common `Ranker` and `DecisionModel` interfaces in `packages/ranking/base.py`.
- [ ] Implement BM25 lexical ranker (`packages/ranking/bm25_ranker.py`).
- [ ] Implement MiniLM dense vector retriever (`packages/ranking/dense_ranker.py`).
- [ ] Implement RRF hybrid fusion (`packages/ranking/rrf_ranker.py`).
- [ ] Implement Weighted Criterion Scorer (`packages/ranking/weighted_ranker.py`).
- [ ] Implement TOPSIS multi-criteria decision model (`packages/ranking/topsis_ranker.py`).
- [ ] Implement LightGBM LambdaMART ranker (`packages/ranking/lambdamart_ranker.py`).
- [ ] Implement Laya research adapter & verification test suite (`packages/decision_models/laya_adapter.py`).
- [ ] Write ranking unit and mathematical correctness tests in `tests/unit/test_rankers.py`.

### [ ] Phase 7: Evaluation, Fairness & Research Harness
- [ ] Implement ranking evaluation metrics (nDCG@k, MRR, Precision@k, Recall@k, latency, peak RAM/VRAM) in `packages/evaluation/`.
- [ ] Implement counterfactual fairness diagnostics in `packages/fairness/counterfactual.py`.
- [ ] Implement ablation engine (comparing BM25, MiniLM, RRF, TOPSIS, Ontology vs. No-Ontology).
- [ ] Generate automated evaluation reports in markdown and JSONL.

### [ ] Phase 8: FastAPI Backend & SQLite Storage
- [ ] Implement SQLite schema and migration manager in `packages/common/database.py`.
- [ ] Build FastAPI application in `apps/api/main.py` with typed endpoints:
  - Resume upload, parsing status, job criteria editor, ranking execution, candidate detail, graph subset, evaluation runs.
- [ ] Write API integration tests in `tests/api/test_api.py`.

### [ ] Phase 9: Accessible Neumorphic Frontend
- [ ] Initialize React + Vite + TypeScript in `apps/web/`.
- [ ] Configure Tailwind CSS with custom Neumorphic soft-UI tokens.
- [ ] Build UI views: Workspace/Upload, Job Setup, Paginated Ranked Candidates Table, Candidate Detail Drawer, Cytoscape.js Skill Graph Explorer, Model Comparison & Pareto Frontier Lab, Fairness Diagnostics.
- [ ] Implement Dark/Light mode toggle, visible focus states, and advisory review disclaimer.

### [ ] Phase 10: End-to-End Verification, Benchmarking & Documentation
- [ ] Run full automated test suite with pytest.
- [ ] Run complete benchmark suite and record measured metrics on the Intel i7 + RTX 3050.
- [ ] Update `docs/implementation-status.md`, `README.md`, `THIRD_PARTY_NOTICES.md`, `MODEL_CARDS.md`, and `DATASET_CARDS.md`.
- [ ] Final sign-off against Definition of Done.

---

## 8. Definition of Done Checklist

Before marking the project complete, Antigravity must verify:
- [ ] Clean Windows 11 setup executes without cloud dependencies or paid APIs.
- [ ] All model weights and caches are located exclusively in `models/weights/` and `models/cache/`.
- [ ] Every single library, model, ontology, and tool has a dedicated markdown reference in `docs/resources/`.
- [ ] Every single code file has comprehensive module docstrings, function docs, and inline comments.
- [ ] UI renders a stunning, accessible Neumorphic theme with WCAG 2.2 AA contrast compliance.
- [ ] All unit, integration, and API tests pass with zero errors.
- [ ] Measured latency, memory (RAM/VRAM), and ranking metrics are recorded and published.
