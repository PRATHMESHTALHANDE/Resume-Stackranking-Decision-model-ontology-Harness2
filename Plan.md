# Plan.md — Master Execution Plan: Resume Intelligence, Ranking & Fairness Lab

> **Status:** Project Initialization & Scaffolding  
> **Master Specifications:** [Project.md](file:///c:/Users/roari/Downloads/AI%20Projects/HR%20Resume%20Stackranking%20-%20Decision%20model%20+%20LLM%20+%20Ontology%20+%20Harness2/Project.md) | [Agent.md](file:///c:/Users/roari/Downloads/AI%20Projects/HR%20Resume%20Stackranking%20-%20Decision%20model%20+%20LLM%20+%20Ontology%20+%20Harness2/Agent.md)  
> **Target Hardware:** Windows 11, Intel Core i7-12650H (10 Cores, 16 Threads), 16 GB RAM, NVIDIA GeForce RTX 3050 Laptop GPU (4 GB VRAM, CUDA 12.6, Driver 561.17).  
> **Toolchain:** Python 3.11 (`uv`), Node.js v24.19.0 (`npm`), SQLite 3, Git, GitHub Actions.

---

## 1. High-Level Architecture & Component Map

The platform is engineered into a modular local-first architecture where every component is isolated, tested independently, and operates without external cloud dependencies:

```text
c:\Users\roari\Downloads\AI Projects\HR Resume Stackranking - Decision model + LLM + Ontology + Harness2/
├── .github/
│   └── workflows/
│       └── ci.yml                     # Multi-OS automated linting, testing & build workflow
├── apps/
│   ├── api/                           # FastAPI backend application
│   │   ├── main.py                    # App entrypoint, CORS, exception handlers, lifespan
│   │   ├── routes/                    # Typed API endpoints (resumes, jobs, rankings, graph, eval)
│   │   └── middleware/                # Structured logging, timing, security headers, PII scrubbing
│   └── web/                           # React + Vite + TypeScript frontend
│       ├── src/
│       │   ├── components/            # Neumorphic soft-UI components (cards, buttons, tables, charts)
│       │   ├── views/                 # Core screens (Workspace, Ranking, Evidence, Lab, Graph)
│       │   ├── hooks/                 # TanStack Query & data hooks
│       │   └── theme/                 # Neumorphic design tokens & Tailwind config
│       └── package.json
├── packages/
│   ├── common/                        # Shared contracts, Pydantic v2 schemas, settings, DB
│   │   ├── schemas.py                 # ResumeDocument, Profile, JobDescription, RankingResult
│   │   ├── settings.py                # Model path enforcer (HF_HOME, MODELS_DIR redirection)
│   │   └── database.py                # SQLite database connection & schema migrations
│   ├── ingestion/                     # File ingestion & parsing
│   │   ├── parser.py                  # PyMuPDF / python-docx extractor with page provenance
│   │   └── validator.py               # File validation, MIME checks, SHA-256 deduplication
│   ├── extraction/                    # Structured extraction
│   │   ├── deterministic.py           # Regex, date normalization, section segmentation
│   │   ├── llm_extractor.py           # Local GGUF extractor via llama-cpp-python
│   │   └── mock_extractor.py          # Deterministic test fixture for CI
│   ├── ontology/                      # ESCO taxonomy & concept normalization
│   │   ├── esco_loader.py             # Download & parse official ESCO skills CSV
│   │   └── normalizer.py              # Exact, alias, and fuzzy matching pipeline
│   ├── graph/                         # In-memory knowledge graph
│   │   ├── skill_graph.py             # NetworkX graph representation (Candidate, Job, Skill)
│   │   └── features.py                # Skill coverage, evidence paths, degree features
│   ├── ranking/                       # Multi-model retrieval & decision engine
│   │   ├── base.py                    # Common Ranker & DecisionModel abstract interfaces
│   │   ├── bm25_ranker.py             # BM25 lexical retriever (rank-bm25)
│   │   ├── dense_ranker.py            # all-MiniLM-L6-v2 vector retriever & cosine scorer
│   │   ├── rrf_ranker.py              # Reciprocal Rank Fusion hybrid ranker
│   │   ├── weighted_ranker.py         # Explicit weighted criterion decision model
│   │   ├── topsis_ranker.py           # TOPSIS multi-criteria decision model
│   │   ├── lambdamart_ranker.py       # Supervised LightGBM LambdaMART ranker
│   │   └── cross_encoder_ranker.py    # Cross-encoder deep reranker
│   ├── decision_models/               # Dedicated decision model research
│   │   └── laya_adapter.py            # Laya research adapter & verification harness
│   ├── fairness/                      # Robustness & fairness diagnostics
│   │   ├── counterfactual.py          # Identity perturbation suite & rank shift audit
│   │   └── parity.py                  # Selection rate disparity & subgroup metrics
│   └── evaluation/                    # Research evaluation harness
│       ├── metrics.py                 # nDCG@k, MRR, Precision@k, Recall@k, latency, RAM/VRAM
│       ├── harness.py                 # Automated benchmark runner & report generator
│       └── ablations.py               # Component ablation runner
├── configs/                           # YAML configurations
│   ├── app.yaml                       # Port, host, workers, logging
│   ├── ranking.yaml                   # Model weights, thresholds, fusion parameters
│   └── models.yaml                    # Local model paths, GGUF quantization, context limits
├── data/
│   ├── sample/                        # Redistributable / synthetic test resumes & JDs
│   ├── ontology/esco/                 # Official ESCO skills snapshot (downloaded locally)
│   └── benchmarks/                    # Labeled evaluation splits & counterfactual pairs
├── models/                            # Local model assets (Zero global cache pollution)
│   ├── weights/
│   │   ├── llm/                       # Qwen / Phi GGUF weights
│   │   ├── embeddings/                # all-MiniLM-L6-v2 weights
│   │   └── reranker/                  # Cross-encoder weights
│   ├── cache/                         # Local Hugging Face / Sentence Transformers cache
│   └── manifest.json                  # Complete audit manifest of local model files
├── docs/
│   ├── resources/                     # Dedicated markdown document per resource used
│   │   └── README.md                  # Master resource catalog index
│   ├── environment-report.md          # Hardware & system environment baseline
│   ├── implementation-status.md       # Running status log per milestone
│   └── research/                      # Laya investigation, ablation reports
├── tests/
│   ├── unit/                          # Unit tests for schemas, parsers, rankers, graph
│   ├── integration/                   # End-to-end pipeline & database integration
│   ├── api/                           # FastAPI endpoint tests
│   └── evaluation/                    # Toy case validation for ranking metrics
├── pyproject.toml                     # Python dependencies & metadata (uv managed)
├── README.md                          # Quickstart, features, screenshots
├── THIRD_PARTY_NOTICES.md             # Comprehensive open-source software license audit
├── MODEL_CARDS.md                     # Model provenance, licenses, hashes, context limits
└── DATASET_CARDS.md                   # Dataset provenance, splits, licenses, limitations
```

---

## 2. Master Phased Execution Checklist

```text
PHASE 0 (Audit) ➔ PHASE 1 (Specs & Docs) ➔ PHASE 2 (Repo & Env) ➔ PHASE 3 (Data Contracts & Parsing)
      ➔ PHASE 4 (Structured Extraction) ➔ PHASE 5 (ESCO & Graph) ➔ PHASE 6 (Rankers Engine)
      ➔ PHASE 7 (Fairness & Evaluation) ➔ PHASE 8 (FastAPI Backend) ➔ PHASE 9 (Neumorphic Frontend)
      ➔ PHASE 10 (Deep Testing & Benchmarks) ➔ PHASE 11 (GitHub Repository Release & CI)
```

---

### [x] Phase 0: Hardware & Environment Reconnaissance
- [x] Run safe commands to inspect CPU, RAM, GPU, VRAM, disk space, and CUDA runtime.
- [x] Confirm exact hardware: Intel i7-12650H, 16 GB RAM, RTX 3050 Laptop GPU (4 GB VRAM, Driver 561.17, CUDA 12.6).
- [x] Verify Python runtime (`uv` with Python 3.11 available) and Node.js v24.19.0.
- [x] Generate baseline audit document in [`docs/environment-report.md`](file:///c:/Users/roari/Downloads/AI%20Projects/HR%20Resume%20Stackranking%20-%20Decision%20model%20+%20LLM%20+%20Ontology%20+%20Harness2/docs/environment-report.md).

---

### [x] Phase 1: Specifications, Rules & Per-Resource Documentation Scaffolding
- [x] Update `Agent.md` with hardened rules, skills, model isolation, commenting, and neumorphic UI standards.
- [x] Create master execution `Plan.md` in the project root.
- [x] Author comprehensive standalone documentation in `docs/resources/` for all 20+ core resources:
  - [x] `docs/resources/fastapi.md`
  - [x] `docs/resources/pydantic.md`
  - [x] `docs/resources/pymupdf.md`
  - [x] `docs/resources/sentence-transformers-all-minilm-l6-v2.md`
  - [x] `docs/resources/rank-bm25.md`
  - [x] `docs/resources/esco-ontology.md`
  - [x] `docs/resources/networkx.md`
  - [x] `docs/resources/topsis.md`
  - [x] `docs/resources/lightgbm.md`
  - [x] `docs/resources/laya-decision-model.md`
  - [x] `docs/resources/llama-cpp-python.md`
  - [x] `docs/resources/ranx.md`
  - [x] `docs/resources/fairlearn.md`
  - [x] `docs/resources/tailwind-css-neumorphism.md`
  - [x] `docs/resources/react-vite-typescript.md`
  - [x] `docs/resources/tanstack-table.md`
  - [x] `docs/resources/tanstack-query.md`
  - [x] `docs/resources/cytoscape-js.md`
  - [x] `docs/resources/apache-echarts.md`
  - [x] `docs/resources/sqlite.md`
  - [x] `docs/resources/README.md` (Master catalog index)
- [x] **Verification Gate 1:** Verified that all 20 resources have complete, standalone markdown files with official links, licenses, installation paths, and code snippets.

---

### [ ] Phase 2: Repository Scaffolding, Environment & Model Weight Isolation
- [ ] Initialize Git repository (`git init`) and verify `.gitignore` excludes weights and SQLite databases.
- [ ] Scaffold folder hierarchy matching Section 1.
- [ ] Configure `pyproject.toml` with `uv` pinning all dependencies (FastAPI, PyMuPDF, sentence-transformers, rank-bm25, networkx, lightgbm, scikit-learn, pydantic, uvicorn, pytest, ruff).
- [ ] Create `packages/common/settings.py` forcing `HF_HOME`, `TRANSFORMERS_CACHE`, `SENTENCE_TRANSFORMERS_HOME`, and `LLAMA_CPP_MODELS_DIR` strictly into `<project_root>/models/`.
- [ ] Initialize `models/manifest.json` with schema for tracking asset file paths, sizes, hashes, and licenses.
- [ ] Run `uv sync` to create clean virtual environment (`.venv/`) using Python 3.11.
- [ ] **Verification Gate 2:** Run `uv run python -c "from packages.common.settings import HF_HOME; print(HF_HOME)"` and confirm path is strictly inside the project root, not in the user profile.

---

### [ ] Phase 3: Canonical Data Contracts & Document Ingestion Pipeline
- [ ] Implement canonical Pydantic v2 data models in `packages/common/schemas.py`:
  - `EvidenceReference`: Document ID, page number, section name, text snippet, extraction confidence.
  - `ResumeDocument`: ID, SHA-256 hash, sanitized filename, file type, page count, parser status.
  - `ResumeProfile`: Candidate ID, experience items, skills (raw + ESCO mapped), education, uncertainty markers.
  - `JobDescription`: Job ID, title, required/preferred criteria with weights, minimum experience.
  - `RankingResult`: Candidate ID, job ID, rank, overall score, component breakdown, evidence links.
  - `EvaluationRun`: Run ID, split hash, metrics, timing, peak RAM/VRAM, hardware info.
- [ ] Implement document ingestion in `packages/ingestion/parser.py`:
  - Extract text and page numbers from PDF via PyMuPDF (`fitz`).
  - Extract text and paragraphs from DOCX via `python-docx`.
  - Preserve exact page and bounding metadata for evidence linking.
- [ ] Implement validation & deduplication in `packages/ingestion/validator.py`:
  - Enforce file size limit (max 10 MB per resume).
  - Compute SHA-256 content hashes to detect and skip duplicates immediately.
  - Sanitize filenames to prevent path traversal attacks.
- [ ] Implement SQLite metadata storage in `packages/common/database.py` with parameterized queries and WAL mode.
- [ ] Write comprehensive unit tests in `tests/unit/test_ingestion.py`.
- [ ] **Verification Gate 3:** `uv run pytest tests/unit/test_ingestion.py` passes with normal, corrupted, duplicate, and unicode sample files.

---

### [ ] Phase 4: Structured Extraction & Skill Normalization
- [ ] Implement deterministic extractor in `packages/extraction/deterministic.py`:
  - Regex patterns for email, phone, LinkedIn, GitHub.
  - Date parser with duration normalization (months/years) and gap detection.
  - Section header segmenter (Experience, Education, Skills, Projects, Certifications).
- [ ] Implement local LLM extractor interface in `packages/extraction/llm_extractor.py`:
  - Support for GGUF models via `llama-cpp-python` (Qwen2.5-1.5B or Phi-4-mini).
  - Grammar-constrained JSON output conforming strictly to Pydantic schemas.
  - Single-attempt repair prompt for malformed JSON.
- [ ] Implement deterministic mock extractor fixture in `packages/extraction/mock_extractor.py` for instant offline testing without model weights.
- [ ] Add field-level evidence linking: every extracted skill and role references verbatim source snippets.
- [ ] Write unit tests in `tests/unit/test_extraction.py`.
- [ ] **Verification Gate 4:** `uv run pytest tests/unit/test_extraction.py` verifies 100% schema validity, evidence trace integrity, and failure handling.

---

### [ ] Phase 5: ESCO Skill Ontology & NetworkX Graph
- [ ] Implement ESCO snapshot manager in `packages/ontology/esco_loader.py`:
  - Download official ESCO skills dataset CSV into `data/ontology/esco/`.
  - Parse concept URIs, preferred labels, alternative labels, and skill types into memory.
- [ ] Implement multi-stage skill normalizer in `packages/ontology/normalizer.py`:
  - Stage 1: Case-folded exact match against preferred labels.
  - Stage 2: Match against ESCO alternative labels (aliases/synonyms).
  - Stage 3: Fuzzy matching (token sort ratio > 0.85).
  - Stage 4: Semantic vector similarity (> 0.80) using MiniLM embeddings.
  - Explicitly label mapping method and confidence score for every skill.
- [ ] Build in-memory NetworkX graph in `packages/graph/skill_graph.py`:
  - Nodes: `Candidate`, `Job`, `Skill`, `Evidence`, `Requirement`.
  - Edges: `HAS_EVIDENCE`, `MENTIONS_SKILL`, `MAPS_TO_SKILL`, `REQUIRES_SKILL`, `RELATED_SKILL`.
- [ ] Implement graph feature extraction in `packages/graph/features.py`:
  - Exact skill coverage ratio: $\frac{|\text{Candidate Skills} \cap \text{Required Skills}|}{|\text{Required Skills}|}$.
  - Normalized ESCO coverage ratio.
  - Preferred vs. required skill coverage.
  - Shortest evidence path from candidate to job requirement.
- [ ] Write graph unit tests in `tests/unit/test_graph.py`.
- [ ] **Verification Gate 5:** `uv run pytest tests/unit/test_graph.py` passes; graph features are reproducible and verifiable from an ESCO snapshot.

---

### [ ] Phase 6: Multi-Model Retrieval & Decision Engine
- [ ] Define abstract base classes in `packages/ranking/base.py`:
  - `BaseRetriever`: `retrieve(job, candidate_pool, config) -> list[RetrievalCandidate]`
  - `BaseRanker`: `rank(job, candidates, config) -> list[RankingResult]`
  - `BaseDecisionModel`: `score_criteria(evidence, criteria, config) -> list[CriterionScore]`
- [ ] Implement BM25 lexical retriever in `packages/ranking/bm25_ranker.py`:
  - Tokenization preserving technical acronyms, symbols (e.g. C++, C#, .NET), and versions.
- [ ] Implement Dense Vector retriever in `packages/ranking/dense_ranker.py`:
  - Sentence-Transformers `all-MiniLM-L6-v2` loaded locally from `models/weights/embeddings/`.
  - Batch embedding computation and caching in NumPy arrays (`artifacts/embeddings/`).
  - L2 normalized cosine similarity calculation.
- [ ] Implement RRF (Reciprocal Rank Fusion) in `packages/ranking/rrf_ranker.py`:
  - Formula: $\text{RRF}(d) = \sum_{m \in M} \frac{1}{k + r_m(d)}$ with configurable $k=60$.
- [ ] Implement Weighted Criterion Scorer in `packages/ranking/weighted_ranker.py`:
  - Explicit job requirement weights with penalty for missing evidence.
- [ ] Implement TOPSIS multi-criteria decision model in `packages/ranking/topsis_ranker.py`:
  - Vector normalization, weighted decision matrix, positive/negative ideal solutions, relative closeness calculation.
- [ ] Implement LightGBM LambdaMART ranker in `packages/ranking/lambdamart_ranker.py`:
  - Grouped pairwise ranking by job query; feature flags ensuring training only when graded labels exist.
- [ ] Implement Laya research adapter in `packages/decision_models/laya_adapter.py`:
  - Independent verification test suite; structured criterion scoring adapter; mock fallback.
- [ ] Implement Cross-Encoder reranker in `packages/ranking/cross_encoder_ranker.py` (top-20 reranking).
- [ ] Write mathematical correctness unit tests in `tests/unit/test_rankers.py`.
- [ ] **Verification Gate 6:** `uv run pytest tests/unit/test_rankers.py` verifies toy cases with known mathematical solutions for TOPSIS, RRF, BM25, and Weighted Scoring.

---

### [ ] Phase 7: Research Evaluation, Fairness & Ablation Harness
- [ ] Implement ranking evaluation metrics in `packages/evaluation/metrics.py`:
  - nDCG@5, nDCG@10, Mean Reciprocal Rank (MRR), Precision@k, Recall@k.
  - Latency profiling (median, p95) and memory profiling (peak RAM, peak VRAM).
- [ ] Implement counterfactual fairness diagnostics in `packages/fairness/counterfactual.py`:
  - Controlled perturbation suite: swapping candidate names, pronouns, and gender markers.
  - Compute Kendall's Tau ($\tau$) rank correlation and count shortlist threshold crossings.
  - Explicit diagnostic-only disclaimers stating these do not prove legal compliance.
- [ ] Implement component ablation runner in `packages/evaluation/ablations.py`:
  - Ablation 1: Lexical only (BM25) vs. Semantic only (MiniLM) vs. Hybrid (RRF).
  - Ablation 2: Raw skills vs. ESCO Normalized vs. Full Graph features.
  - Ablation 3: Weighted Scoring vs. TOPSIS vs. LambdaMART vs. Laya (if verified).
- [ ] Implement report generator creating machine-readable JSONL and human-readable markdown reports in `outputs/evaluation/`.
- [ ] Write evaluation unit tests in `tests/unit/test_evaluation.py`.
- [ ] **Verification Gate 7:** `uv run pytest tests/unit/test_evaluation.py` passes; toy ranking matrices produce exact verified nDCG and MRR scores.

---

### [ ] Phase 8: FastAPI Backend & SQLite Storage
- [ ] Build FastAPI server in `apps/api/main.py`:
  - Lifespan events initializing database and local model paths.
  - Background task worker for asynchronous document ingestion and ranking runs.
  - PII-free structured logging middleware.
- [ ] Implement typed REST endpoints in `apps/api/routes/`:
  - `GET /health`: System status, active models, RAM/VRAM telemetry.
  - `POST /api/v1/resumes`: Multi-file upload with SHA-256 deduplication and progress tracking.
  - `GET /api/v1/resumes/{id}`: Detailed profile with page/section evidence snippets.
  - `DELETE /api/v1/resumes/{id}`: Cascading deletion of resume, extracted records, and embeddings.
  - `POST /api/v1/jobs`: Create/update job descriptions, criteria, and weights.
  - `GET /api/v1/jobs/{id}`: Fetch job details.
  - `POST /api/v1/jobs/{id}/rankings`: Trigger ranking with selected model and configuration.
  - `GET /api/v1/jobs/{id}/candidates`: Server-side paginated, sorted, and filtered candidate results.
  - `GET /api/v1/candidates/{id}/evidence`: Verbatim evidence highlights for a candidate.
  - `GET /api/v1/jobs/{id}/graph`: Subgraph payload optimized for Cytoscape.js rendering.
  - `POST /api/v1/evaluations`: Launch research benchmark run.
  - `GET /api/v1/evaluations/{run_id}/report`: Retrieve generated markdown/JSONL report.
- [ ] Write API integration tests in `tests/api/test_api.py`.
- [ ] **Verification Gate 8:** `uv run pytest tests/api/test_api.py` passes with 100% endpoint coverage using test fixtures.

---

### [ ] Phase 9: Accessible Neumorphic Frontend (React + Vite + TypeScript)
- [ ] Initialize React application in `apps/web/` using Vite and TypeScript strict mode.
- [ ] Configure Tailwind CSS with Neumorphic design tokens:
  - Custom shadow utilities: `shadow-neu-flat`, `shadow-neu-raised`, `shadow-neu-inset`, `shadow-neu-pressed`.
  - Light mode palette (`#E8ECF2`) and Dark mode palette (`#181B20`).
  - High-contrast text tokens meeting WCAG 2.2 AA contrast requirements.
- [ ] Build core Neumorphic components in `apps/web/src/components/`:
  - `NeuCard`, `NeuButton`, `NeuInput`, `NeuBadge`, `NeuModal`, `NeuTabs`.
  - Prominent "Decision-Support Aid Only — Requires Human Review" disclaimer banner.
- [ ] Build core views in `apps/web/src/views/`:
  - **Workspace & Upload:** Drag-and-drop PDF/DOCX batch ingestion with progress bars and duplicate alerts.
  - **Job Criteria Editor:** Define required vs. preferred criteria and interactive weight sliders.
  - **Ranked Candidates Table:** TanStack Table with server-side pagination, sorting, filters, and candidate search.
  - **Evidence Drawer:** Sliding panel showing verbatim resume snippets, page badges, component scores, and uncertainty tags.
  - **Cytoscape.js Graph Explorer:** Interactive skill graph displaying Candidate-Skill-Requirement links with click-to-filter.
  - **Model Comparison & Pareto Lab:** Apache ECharts visualization of nDCG vs. Latency vs. RAM, plus metrics table.
  - **Fairness & Counterfactual Audit:** Visualizing rank shifts and shortlist threshold crossings with diagnostic caveats.
- [ ] Write frontend component and accessibility tests in `apps/web/tests/`.
- [ ] **Verification Gate 9:** `npm run build` succeeds cleanly; keyboard navigation and visible focus rings operate correctly across all screens.

---

### [ ] Phase 10: Deep Testing Suite & Real Hardware Benchmarks
- [ ] Run full automated test suite:
  ```powershell
  uv run pytest tests/ -v
  ```
- [ ] Execute research benchmark on the target machine (Intel i7-12650H + RTX 3050):
  - Record cold-start time, median/p95 latency, candidates/sec, peak RAM, and peak VRAM.
  - Save benchmark report to `outputs/evaluation/baseline_benchmark_report.md`.
- [ ] Audit license inventory and update `THIRD_PARTY_NOTICES.md`.
- [ ] Update `MODEL_CARDS.md` and `DATASET_CARDS.md`.
- [ ] Verify that zero files sit in unmonitored global caches and that all model assets are accounted for in `models/manifest.json`.
- [ ] Finalize `README.md` with Windows quickstart, screenshots, architecture diagram, and safety disclaimers.
- [ ] **Verification Gate 10:** Clean clone execution test verifies that any developer can run the app locally without paid APIs.

---

### [ ] Phase 11: GitHub Repository Release & CI Automation
- [ ] Create GitHub Actions CI workflow in `.github/workflows/ci.yml`:
  - Python matrix on `windows-latest` and `ubuntu-latest`.
  - Automated dependency sync via `uv`.
  - Ruff linting and formatting check (`ruff check .`, `ruff format --check .`).
  - Pytest full execution (`pytest tests/ -v`).
  - Frontend production build check (`npm run build`).
- [ ] Security & Secret Audit:
  - Run regex secret scan verifying zero API keys, personal emails, or private files exist.
  - Ensure `.gitignore` correctly blocks all model weights, checkpoints, SQLite `.db` files, and `.venv`.
- [ ] Generate comprehensive SBOM (Software Bill of Materials).
- [ ] Tag release `v1.0.0`.
- [ ] Push clean master branch to user's new GitHub remote repository.
- [ ] **Verification Gate 11:** GitHub Actions CI run passes 100% green on the remote repository.

---

## 3. Detailed Progress Tracker

| Milestone | Status | Key Deliverables | Verification Command | Evidence File |
|---|---|---|---|---|
| **Phase 0: Recon** | `done` | Environment audit | `nvidia-smi; python -V; uv -V` | `docs/environment-report.md` |
| **Phase 1: Specs & Docs** | `done` | `Agent.md`, `Plan.md`, 24 `docs/resources/*.md` | File inspections | `docs/resources/` |
| **Phase 2: Scaffolding** | `done` | `pyproject.toml`, `models/weights/`, settings | `uv sync; uv run pytest` | `models/manifest.json` |
| **Phase 3: Ingestion** | `done` | PyMuPDF parser, Pydantic schemas, SQLite | `uv run pytest tests/unit/test_ingestion.py` | `tests/unit/test_ingestion.py` |
| **Phase 4: Extraction** | `done` | Regex + GGUF + mock extractor | `uv run pytest tests/unit/test_extraction.py` | `packages/extraction/` |
| **Phase 5: ESCO Graph** | `done` | ESCO loader, normalizer, NetworkX graph | `uv run pytest tests/unit/test_graph.py` | `packages/graph/` |
| **Phase 6: Rankers** | `done` | BM25, MiniLM, RRF, TOPSIS, LambdaMART | `uv run pytest tests/unit/test_rankers.py` | `packages/ranking/` |
| **Phase 7: Fairness** | `done` | Metrics, counterfactuals, ablations | `uv run pytest tests/unit/test_evaluation.py` | `packages/fairness/` |
| **Phase 8: API** | `done` | FastAPI REST endpoints, background tasks | `uv run pytest tests/api/test_api.py` | `apps/api/` |
| **Phase 9: Frontend** | `done` | Neumorphic UI, Cytoscape, ECharts | `npm run build` | `apps/web/` |
| **Phase 10: Deep Testing** | `done` | Full benchmark, license audit, docs | `uv run python scripts/run_baseline_benchmark.py` | `outputs/evaluation/baseline_benchmark_report.md` |
| **Phase 11: GitHub Release** | `done` | GitHub Actions CI, SBOM, release ready | `git status` | `.github/workflows/ci.yml` |

---

## 4. Definition of Done & Sign-Off Criteria

Before closing the project, all items below must be verified:
1. `uv run pytest tests/` passes 100% of tests.
2. `npm run build` inside `apps/web/` generates a clean production bundle.
3. Every single resource in `docs/resources/` is complete, accurate, and properly formatted.
4. Model weights, caches, and embeddings live exclusively within `models/weights/` and `models/cache/`.
5. All Python and TypeScript files contain thorough inline comments and docstrings.
6. The Neumorphic UI renders cleanly in both Light and Dark themes with WCAG 2.2 AA accessibility.
7. Real hardware measurements (latency, RAM, VRAM) on the RTX 3050 and Core i7 are published in the final report.
8. GitHub Actions CI pipeline passes cleanly on the new remote repository.
