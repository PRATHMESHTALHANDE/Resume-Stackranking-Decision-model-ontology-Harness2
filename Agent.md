# Agent.md — Master Autonomous Execution Specification: Resume Intelligence, Ranking & Fairness Lab

> **Role:** You are the Lead Software Architect, ML Engineer, Full-Stack Frontend Engineer, QA Specialist, and Technical Writer responsible for implementing the open-source platform described in `Project.md` and `Plan.md`.  
> **Master Reference:** [Project.md](file:///c:/Users/roari/Downloads/AI%20Projects/HR%20Resume%20Stackranking%20-%20Decision%20model%20+%20LLM%20+%20Ontology%20+%20Harness2/Project.md) | [Plan.md](file:///c:/Users/roari/Downloads/AI%20Projects/HR%20Resume%20Stackranking%20-%20Decision%20model%20+%20LLM%20+%20Ontology%20+%20Harness2/Plan.md)  
> **Target Hardware:** Windows 11, Intel Core i7-12650H (10 Cores, 16 Logical Processors), 16 GB Physical RAM, NVIDIA GeForce RTX 3050 Laptop GPU (4 GB VRAM, Driver 561.17, CUDA 12.6).  
> **Core Operating Principles:** 100% Open-Source; Local-First; Zero Unmonitored Global Disk Caching; Human-in-the-Loop Review Aid; Comprehensive Code Commenting; Accessible Neumorphic UI; Deep Testing & Evaluation; Ready for GitHub Publication.

---

## 1. Mandatory Core Engineering Principles & Constraints

Antigravity must adhere strictly to these principles across every single task:

1. **Evidence Before Ranking:** Never generate a candidate score or ranking without explicit, traceable evidence snippets extracted verbatim from the parsed resume document. Every score must link to a document page, paragraph, or section.
2. **Zero Fact Fabrication / Hallucination:** Never infer unstated degrees, certifications, job titles, or skills. Missing evidence must be explicitly labeled as `insufficient_information` or `uncertain`, never penalized as an unstated negative without documented policy.
3. **100% Open Source & Zero Mandatory Paid APIs:** The entire system must run completely local and offline after initial package installation. No external LLM APIs (OpenAI, Anthropic, Google Cloud Vertex, etc.) may be required for core functionality.
4. **Local Model Weight Isolation (`models/weights/` & `models/cache/`):**
   - **CRITICAL DISK INTEGRITY RULE:** Model weights, tokenizers, checkpoints, and GGUF files must NEVER be silently written to global user profile caches (such as `C:\Users\<user>\.cache\huggingface`).
   - All runtime environments and scripts must explicitly route cache and model directories inside the project workspace:
     - `HF_HOME = <project_root>/models/cache/huggingface`
     - `TRANSFORMERS_CACHE = <project_root>/models/cache/huggingface`
     - `SENTENCE_TRANSFORMERS_HOME = <project_root>/models/cache/sentence_transformers`
     - `LLAMA_CPP_MODELS_DIR = <project_root>/models/weights/llm`
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
11. **GitHub Repository Cleanliness & Release Quality:**
    - The codebase will be published as a clean, brand-new GitHub repository.
    - Zero secrets, API tokens, personal resumes, model weights, or local database blobs (`*.db`) may ever be committed.
    - Full GitHub Actions CI workflow must pass all linters, type checks, and tests on a pristine clone.

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

The master index must be maintained in [`docs/resources/README.md`](file:///c:/Users/roari/Downloads/AI%20Projects/HR%20Resume%20Stackranking%20-%20Decision%20model%20+%20LLM%20+%20Ontology%20+%20Harness2/docs/resources/README.md).

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
"""
Central configuration enforcer isolating model weights and caches to the project workspace.
"""
import os
from pathlib import Path

# Resolve absolute project root directory
PROJECT_ROOT = Path(__file__).resolve().parents[2]
MODELS_DIR = PROJECT_ROOT / "models"
WEIGHTS_DIR = MODELS_DIR / "weights"
CACHE_DIR = MODELS_DIR / "cache"
ARTIFACTS_DIR = PROJECT_ROOT / "artifacts"
DATA_DIR = PROJECT_ROOT / "data"

# Guarantee directories exist
for p in [WEIGHTS_DIR / "llm", WEIGHTS_DIR / "embeddings", WEIGHTS_DIR / "reranker", 
          CACHE_DIR / "huggingface", CACHE_DIR / "sentence_transformers", 
          ARTIFACTS_DIR / "data", ARTIFACTS_DIR / "indices", DATA_DIR / "ontology" / "esco"]:
    p.mkdir(parents=True, exist_ok=True)

# Force environment overrides to isolate disk usage strictly to project workspace
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
   - Include equations in comments:
     - TOPSIS: Euclidean distance $S_i^+ = \sqrt{\sum (v_{ij} - v_j^+)^2}$ and relative closeness $C_i = \frac{S_i^-}{S_i^+ + S_i^-}$.
     - RRF: Score decay $\text{RRF}(d) = \sum_{m \in M} \frac{1}{k + r_m(d)}$ with $k=60$.
     - Cosine: $\cos(\theta) = \frac{\mathbf{u} \cdot \mathbf{v}}{\|\mathbf{u}\| \|\mathbf{v}\|}$.
     - BM25: Saturation $\text{IDF}(q_i) \cdot \frac{f(q_i, D) \cdot (k_1 + 1)}{f(q_i, D) + k_1 \cdot (1 - b + b \cdot \frac{|D|}{\text{avgdl}})}$.
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

## 7. Core Data Contracts (`packages/common/schemas.py`)

All ingested resumes, job postings, evidence snippets, and rankings must strictly normalize into typed Pydantic v2 schemas:

### 7.1 `EvidenceReference`
```python
class EvidenceReference(BaseModel):
    document_id: str = Field(..., description="Foreign key of source resume")
    page_number: Optional[int] = Field(None, ge=1, description="1-indexed source page")
    section_name: Optional[str] = Field(None, description="Experience | Education | Skills")
    verbatim_snippet: str = Field(..., min_length=5, description="Exact text excerpt")
    extraction_confidence: float = Field(..., ge=0.0, le=1.0)
```

### 7.2 `ResumeProfile`
```python
class ResumeProfile(BaseModel):
    candidate_id: str = Field(..., description="Anonymized candidate identifier")
    experience_items: List[ExperienceItem] = Field(default_factory=list)
    skills: List[ResumeSkill] = Field(default_factory=list)
    education_items: List[EducationItem] = Field(default_factory=list)
    uncertainty_flags: List[str] = Field(default_factory=list)
    summary: Optional[str] = None
    extraction_method: str = Field(..., description="deterministic | llm_gguf | mock")
```

### 7.3 `JobDescription`
```python
class JobDescription(BaseModel):
    job_id: str
    title: str
    requirements: List[JobCriterion]
    minimum_experience_years: Optional[float] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
```

### 7.4 `RankingResult`
```python
class RankingResult(BaseModel):
    candidate_id: str
    job_id: str
    rank: int = Field(..., ge=1)
    score: float = Field(..., ge=0.0, le=1.0)
    model_name: str
    component_scores: Dict[str, float] = Field(default_factory=dict)
    evidence_citations: List[EvidenceReference] = Field(default_factory=list)
    uncertainty_markers: List[str] = Field(default_factory=list)
    run_id: str
```

### 7.5 `EvaluationRun`
```python
class EvaluationRun(BaseModel):
    run_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    model_name: str
    dataset_split: str
    ndcg_at_5: float
    ndcg_at_10: float
    mrr: float
    precision_at_5: float
    recall_at_10: float
    latency_p50_ms: float
    latency_p95_ms: float
    peak_ram_mb: float
    peak_vram_mb: float
```

---

## 8. Multi-Tiered Testing & Deep Edge-Case Architecture

Before any code is approved or pushed to GitHub, Antigravity must execute and verify tests across 5 distinct tiers:

### 8.1 Tier 1: Unit & Mathematical Correctness Tests (`tests/unit/`)
- **TOPSIS Verification:** Test against Hwang & Yoon (1981) textbook toy example. Validate that Euclidean distances and relative closeness match hand-calculated numbers to within $10^{-6}$.
- **RRF Verification:** Test rank fusion on known 2-system rankings. Verify that $\sum \frac{1}{60 + r_m}$ produces exact predictable ordering.
- **BM25 Tokenization:** Verify that technical terms (`C++`, `C#`, `.NET`, `Node.js`, `Vue.js`) are preserved as single tokens and not stripped.
- **MiniLM Cosine Similarity:** Test orthogonal vectors ($\cos = 0$), identical vectors ($\cos = 1$), and opposite vectors ($\cos = -1$).
- **NetworkX Graph Traversal:** Test ego-graph extraction, path discovery, and exact skill coverage ratio.

### 8.2 Tier 2: Document Ingestion & Parsing Edge Cases (`tests/integration/test_ingestion_edge_cases.py`)
- **Corrupted PDF/DOCX:** Ensure malformed files return structured HTTP 422 errors with clean logs without crashing workers.
- **Scanned (Image-Only) PDF:** Ensure PDF with zero selectable text triggers an explicit `scanned_pdf_detected` warning without failing.
- **Unicode & Non-Latin Scripts:** Test resumes containing accented characters, umlauts, Cyrillic, and unusual symbols.
- **File Size Limits:** Test rejection of files $> 10\text{ MB}$.
- **Duplicate Resumes:** Verify SHA-256 deduplication: uploading the same file with a different filename must return existing cached parsed records immediately.

### 8.3 Tier 3: Model & Hardware Fallbacks (`tests/integration/test_fallbacks.py`)
- **Missing GGUF Weights:** Ensure system functions 100% in deterministic mock mode when `models/weights/llm/` is empty.
- **CUDA Unavailable Fallback:** Force `CUDA_VISIBLE_DEVICES=""` and confirm all vector and LLM components cleanly fall back to Intel CPU.
- **Context Truncation:** Pass 5,000-word resumes and verify section-level chunking prevents context overflow.

### 8.4 Tier 4: Fairness & Counterfactual Diagnostics (`tests/evaluation/test_counterfactual.py`)
- **Identity Perturbation Suite:** Create synthetic resume pairs where only names, pronouns, and cultural markers differ (e.g. "John Smith" vs. "Jane Smith").
- Verify that rank shifts ($\Delta \text{rank}$) and Kendall's $\tau$ correlation are tracked and that shortlist boundary crossings are highlighted.

### 8.5 Tier 5: API & End-to-End Contract Tests (`tests/api/test_api.py`)
- Test complete flow: Upload Resume ➔ Create Job ➔ Trigger Ranking ➔ Fetch Paginated Candidates ➔ Inspect Evidence ➔ Download Markdown Evaluation Report.

---

## 9. GitHub Repository Publication & Release Protocol

When all phases and tests pass, Antigravity must execute the following release protocol:

1. **Security & Secret Audit:**
   - Execute a regex scan across the entire workspace ensuring zero `.env` files, API keys, passwords, or personal credentials exist.
   - Verify that `models/weights/` and `models/cache/` contain zero git-tracked binary blobs.
2. **License & Attribution Inventory (`THIRD_PARTY_NOTICES.md`):**
   - Generate a complete software bill of materials (SBOM) and license inventory verifying that all direct and transitive dependencies use permissive open-source licenses (MIT, Apache-2.0, BSD-3-Clause, AGPLv3 for PyMuPDF).
3. **Model & Dataset Cards (`MODEL_CARDS.md` & `DATASET_CARDS.md`):**
   - Document upstream repositories, revisions, file hashes, context limits, and usage disclaimers.
4. **GitHub Actions CI Workflow (`.github/workflows/ci.yml`):**
   - Automated workflow running on `ubuntu-latest` and `windows-latest`:
     - Python 3.11 setup via `uv`.
     - Code linting and formatting via `ruff check` and `ruff format --check`.
     - Full test suite via `pytest tests/ -v`.
     - Frontend lint and production build via `npm run build`.
5. **Master `README.md`:**
   - Features, architecture diagram, quickstart guide, Neumorphic UI screenshots/walkthrough, and human-in-the-loop ethical disclaimer.
6. **Git Remote Push:**
   - Connect to the user's new GitHub repository and push main branch with clean initial history.
