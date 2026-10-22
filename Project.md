# Project.md — Open-Source Resume Intelligence, Ranking & Fairness Lab

> **Project type:** Local-first AI/ML research and engineering platform  
> **Primary purpose:** Resume-to-job-description (JD) matching, evidence-grounded ranking, model comparison, skill-ontology/graph analysis, and fairness diagnostics  
> **Target developer hardware:** Windows 11, Intel Core i7, 16 GB system RAM, NVIDIA GPU with 4 GB VRAM  
> **Operating principle:** No mandatory paid API; no resume data sent to external services by default  
> **Status:** Architecture and implementation specification. Model and dependency choices must pass the license, compatibility, and benchmark gates in this document.

---

## 1. Executive summary

Build a local web application that accepts resumes and job descriptions, parses them into validated structured records, retrieves relevant candidates, ranks candidates against explicit job criteria, explains every important score with resume evidence, and allows the user to compare different ranking and decision approaches experimentally.

This is not just a resume-matching demo. It is a reproducible research platform for answering questions such as:

- Does a hybrid of lexical and semantic retrieval outperform either method alone?
- Does an ontology/skill graph add measurable value beyond ordinary semantic matching?
- Does a dedicated decision model such as **Laya** improve criterion scoring, latency, or resource use compared with transparent scoring and supervised learning-to-rank?
- When does a cross-encoder reranker justify its additional compute?
- Which method offers the best trade-off among ranking quality, speed, memory, stability, explainability, and fairness diagnostics?
- Can the system identify uncertainty and missing evidence rather than inventing qualifications?
- Can another developer reproduce the reported results on a laptop?

The system is designed as **decision support for human review**, not an autonomous hiring decision-maker. Its output is a ranked review queue, not a determination of a person's worth, employability, or entitlement to a job.

## 2. Goals and non-goals

### 2.1 Goals

1. Parse PDF and DOCX resumes and job descriptions locally.
2. Extract normalized, evidence-linked fields using deterministic parsing plus a small local LLM where needed.
3. Support lexical retrieval, semantic retrieval, hybrid fusion, multi-criteria decision methods, supervised ranking, optional reranking, and a Laya experiment.
4. Create a skill ontology/graph using a locally stored ESCO snapshot and a lightweight graph library.
5. Compare approaches using identical datasets, splits, relevance labels, and evaluation metrics.
6. Evaluate ranking quality, extraction quality, robustness, fairness diagnostics, latency, RAM, VRAM, throughput, and cold-start cost.
7. Deliver an accessible, polished, neumorphic web UI with pagination, filters, score breakdowns, evidence, model comparisons, and graph visualization.
8. Run locally on Windows 11 with 16 GB RAM and a 4 GB NVIDIA GPU, falling back to CPU where necessary.
9. Keep all required application features available without paid APIs or external inference services.
10. Include license inventory, dependency pinning, dataset documentation, model provenance, reproducible scripts, tests, and deployment instructions.

### 2.2 Non-goals

- Automatically rejecting, hiring, or making final employment decisions.
- Inferring protected traits from names, photos, addresses, writing style, or other proxies.
- Claiming legal compliance or fairness solely because a metric looks acceptable.
- Treating semantic similarity, graph centrality, LLM confidence, or an LLM-generated score as objective truth.
- Training a large foundation model from scratch.
- Requiring Kubernetes, a remote vector database, cloud inference, or a paid SaaS service for the first release.
- Sending resumes, extracted personal data, or evaluation datasets to telemetry services by default.
- Publishing real personal resumes or sensitive audit data in the repository.

## 3. Product scope and user journeys

### 3.1 Primary user journey

1. User creates a local workspace.
2. User uploads multiple resumes (PDF/DOCX) and one or more job descriptions.
3. The application validates file types and sizes, computes content hashes, and detects duplicates.
4. Parsing produces text plus page/section provenance.
5. Extraction produces structured resume and JD records, schema validation, and warnings.
6. Skill normalization maps recognizable skill strings to canonical ESCO concepts where appropriate.
7. The system computes cached lexical/semantic features and retrieves a candidate pool.
8. A configured ranker creates a stable ordered review queue.
9. The UI displays paginated candidates, component scores, supporting evidence, missing/ambiguous evidence, and model/version metadata.
10. A reviewer can inspect evidence, export a report, and compare rankings produced by other models.
11. The research area runs controlled experiments and displays aggregate metrics without exposing sensitive candidate details unnecessarily.

### 3.2 Core screens

- **Workspace / Upload:** jobs, resume batches, processing status, errors, duplicate handling.
- **Job setup:** required/preferred criteria, weights, minimum stated requirements, and job-version history.
- **Ranked candidates:** server-side pagination, sorting, filters, candidate search, model selection, and shortlist review state.
- **Candidate detail:** anonymized candidate ID, parsed fields, evidence snippets with page/section source, score breakdown, uncertainty, and extraction warnings.
- **Model lab:** nDCG@k, Recall@k, MRR, precision, latency, peak RAM/VRAM, stability, and ablation comparisons.
- **Fairness lab:** counterfactual rank shifts, shortlist-boundary crossings, selection-rate metrics when lawful and appropriate group labels exist, and limitations.
- **Skill graph explorer:** job requirements, normalized skill concepts, candidate evidence links, and labeled relationships.
- **Settings / provenance:** active models, model hashes, licenses, offline mode, cache management, retention, and experiment configuration.

### 3.3 Neumorphic UI requirements

Use a restrained neumorphic visual system with soft raised/recessed surfaces, consistent spacing, subtle shadows, and a neutral palette. Neumorphism must not reduce accessibility:

- Provide a high-contrast mode and visible keyboard focus.
- Meet WCAG 2.2 AA contrast targets where applicable.
- Never communicate ranking or fairness status by color alone.
- Respect reduced-motion settings.
- Use semantic HTML, accessible labels, keyboard navigation, and screen-reader descriptions.
- Use charts with text summaries and data tables.
- Avoid decorative shadows that make buttons or inputs look disabled.

## 4. Target hardware and performance strategy

### 4.1 Known hardware

- OS: Windows 11
- CPU: Intel Core i7 (exact generation not yet known)
- RAM: 16 GB
- GPU: NVIDIA, 4 GB VRAM (exact GPU model not yet known)

The exact GPU model, driver, free disk space, and CPU generation must be collected at setup. A nominal 4 GB VRAM GPU cannot devote all VRAM to inference because the desktop, driver, runtime buffers, context/KV cache, and other allocations consume memory.

### 4.2 Memory budget (planning estimates, not measured guarantees)

| Consumer | Approximate system-RAM budget | Policy |
|---|---:|---|
| Windows, drivers, background apps | 4–5 GB | Close unnecessary applications during benchmarks |
| API, UI development tools, database | 1–2 GB | Avoid excessive development-server processes |
| Active local LLM | 2–4 GB, model/context-dependent | Only one generative model loaded by default |
| Parsing, embeddings, ranking | 1–2 GB | Batch and release intermediate objects |
| OS cache / headroom | 3–5 GB | Do not design around paging |

GPU planning budget:

| Consumer | Approximate VRAM budget |
|---|---:|
| Active LLM weights/layers | 1.2–2.2 GB for a small quantized model, depending on offload |
| KV cache and compute buffers | 0.4–1.0 GB, dependent on context and runtime |
| Desktop/driver/other allocations | 0.5–1.0 GB or more |
| Safety margin | Preserve headroom; CPU fallback is acceptable |

These values overlap and vary by runtime. The agent must measure actual memory use. If a model exceeds the available VRAM, reduce context length, batch size, or GPU offload layers, or use CPU inference. Never claim that a model fits just because its file size is less than 4 GB.

### 4.3 Efficiency rules

- Process each file once per content hash and parser version.
- Cache extracted text, structured records, embeddings, normalized skills, and model outputs.
- Key caches by file hash, model identifier/hash, prompt/schema version, parser version, and relevant configuration.
- Recompute only invalidated stages.
- Use batch embedding inference on CPU initially.
- Keep generation out of the interactive ranking path.
- Retrieve cheaply with BM25 and embeddings; rerank only a bounded top-N pool.
- Run research models sequentially by default; no concurrent LLM and GPU reranker on 4 GB VRAM.
- Limit context to approximately 2K–4K tokens initially and parse long resumes section by section.
- Bound concurrency and file size; use a background task queue for batch ingestion.
- Use server-side pagination and filtering. Never send all candidate records to the browser just to paginate.
- Provide cancellation, progress, retries, and actionable errors for long-running jobs.
- Use a simple SQLite + NetworkX architecture until profiling demonstrates a need for external services.
- Measure cold-start and warm-run performance separately.

## 5. Architecture

```text
                    ┌──────────────────────────────┐
                    │ React + TypeScript UI        │
                    │ Upload / review / charts     │
                    └──────────────┬───────────────┘
                                   │ HTTP / JSON
                    ┌──────────────▼───────────────┐
                    │ FastAPI + Pydantic           │
                    │ Auth boundary / validation   │
                    │ pagination / job status      │
                    └──────────────┬───────────────┘
                                   │
          ┌────────────────────────┼─────────────────────────┐
          │                        │                         │
┌─────────▼─────────┐   ┌──────────▼──────────┐   ┌──────────▼─────────┐
│ Ingestion &       │   │ Retrieval &         │   │ Research /         │
│ extraction        │   │ ranking             │   │ evaluation harness │
│ PDF/DOCX → schema │   │ BM25 + vectors + RRF│   │ metrics / fairness │
└─────────┬─────────┘   └──────────┬──────────┘   └──────────┬─────────┘
          │                        │                         │
          └────────────────────────┼─────────────────────────┘
                                   │
                    ┌──────────────▼───────────────┐
                    │ SQLite + local artifacts     │
                    │ cache / provenance / runs    │
                    └──────────────┬───────────────┘
                                   │
                    ┌──────────────▼───────────────┐
                    │ ESCO + NetworkX skill graph │
                    └──────────────────────────────┘
```

### 5.1 Recommended repository layout

```text
resume-intelligence/
├── apps/
│   ├── api/                       # FastAPI application
│   └── web/                       # React + Vite + TypeScript
├── packages/
│   ├── common/                    # shared schemas and utilities
│   ├── ingestion/                 # file validation and extraction
│   ├── extraction/                # deterministic + LLM extraction
│   ├── retrieval/                 # BM25, embeddings, RRF
│   ├── ranking/                   # weighted score, TOPSIS, LambdaMART
│   ├── decision_models/           # Laya adapter and experiments
│   ├── ontology/                  # ESCO loading and normalization
│   ├── graph/                     # NetworkX graph features
│   ├── fairness/                  # counterfactual and group metrics
│   └── evaluation/                # metrics, harness, reports
├── configs/
│   ├── app.example.yaml
│   ├── ranking.example.yaml
│   └── models.example.yaml
├── data/
│   ├── sample/                    # only redistributable samples
│   ├── benchmarks/                # labels and synthetic test fixtures
│   └── README.md                  # provenance and licensing
├── artifacts/                     # local outputs; gitignored
├── models/                         # local weights; gitignored
├── experiments/
├── scripts/
├── tests/
│   ├── unit/
│   ├── integration/
│   ├── evaluation/
│   └── e2e/
├── docs/
├── .github/workflows/
├── pyproject.toml
├── package.json or workspace manifests
├── docker-compose.yml             # optional deployment
├── THIRD_PARTY_NOTICES.md
├── MODEL_CARDS.md
├── DATASET_CARDS.md
├── LICENSE
└── README.md
```

## 6. Technology and resource selection

All dependencies and model artifacts must be checked at the time of implementation. Versions and licenses can change. The following is the intended candidate stack, not permission to skip verification.

### 6.1 Local LLM runtime and extraction models

**Runtime candidates**
- `llama.cpp` with CUDA support for GGUF quantized models.
- CPU fallback through the same runtime when GPU memory is insufficient.
- Do not add Ollama as a mandatory dependency. It may be documented as an optional convenience only if the team verifies it meets offline and licensing requirements.

**Model candidates**
- Primary initial experiment: Qwen3-1.7B in Q4_K_M GGUF if a trustworthy compatible conversion is available.
- Alternatives: Phi-4-mini-instruct in a compatible quantization; Qwen3-4B Q4_K_M as a slower/offloaded research reference.
- The project must verify the exact upstream model license, model card, supported languages, context limits, and redistribution terms before downloading or distributing weights.
- Do not treat a third-party quantization as automatically endorsed by the original model author.
- Use grammar-constrained output where the runtime supports it; otherwise validate JSON with Pydantic and retry only once with a repair prompt.
- Prompt the model to extract facts, not infer suitability or generate unsupported experience.

**Recommended initial inference configuration**
- Context: 2,048 tokens, then test 4,096.
- One active generative model.
- Small generation limit for JSON extraction.
- Process resume sections independently.
- Record inference settings and model hash for every output.
- Use CPU-only mode if CUDA build or driver compatibility fails.

### 6.2 Embeddings

Initial candidate: `sentence-transformers/all-MiniLM-L6-v2`.

- Run on CPU.
- Cache embeddings per normalized text and model revision.
- Batch multiple resumes for throughput.
- L2-normalize vectors before cosine similarity if required by the implementation.
- Store vectors in a local NumPy artifact keyed to candidate ID and model revision; for the first release, no dedicated vector database is required.
- Benchmark a stronger candidate such as BGE-M3 only if quality improvement justifies its memory, disk, and runtime cost.
- Verify model license and model card before use.

### 6.3 Lexical retrieval and fusion

- BM25: use a maintained, license-reviewed implementation such as `rank-bm25` or `bm25s`.
- Normalize text consistently; preserve important technology names, version strings, acronyms, and punctuation-sensitive skills.
- Use RRF as a robust fusion baseline rather than trying to merge incomparable raw BM25 and cosine scores directly.
- Make `k` and other fusion parameters configurable and tune them only on validation data.
- Persist retrieval results and configuration to make runs reproducible.

### 6.4 Decision and ranking models

Implement a common `Ranker` interface so every model can be swapped without modifying the UI or ingestion pipeline.

1. **Weighted feature scoring — baseline**
   - Inputs: evidence-backed criterion features.
   - Explicit normalized weights, per-criterion evidence and uncertainty.
   - Weights must be job-specific and reviewable; avoid unsupported universal weights.

2. **TOPSIS — multi-criteria experiment**
   - Use only justified criteria and documented benefit/cost direction.
   - Normalize consistently and test sensitivity to weights and correlated criteria.
   - Explain that TOPSIS results depend on normalization and the candidate set.

3. **LightGBM LambdaMART — supervised ranking**
   - Train only when enough credible graded relevance labels exist.
   - Group samples by job query; split train/validation/test by job, not randomly by candidate alone.
   - Avoid protected attributes and label leakage.
   - Save model, feature schema, training configuration, and split manifest.

4. **Cross-encoder reranker — optional**
   - Score only a small candidate pool (e.g. top 20–50) after cheap retrieval.
   - Run on CPU initially or as a separate research job.
   - Never load it alongside a GPU LLM by default.
   - Verify model-specific license and hardware behavior.

5. **Laya — explicit research experiment**
   - Laya is intended to be a compact typed-decision model; evaluate it as a criterion-scoring/choice component, not assume it replaces retrieval or ranking.
   - Identify the exact official repository, model card, checkpoint, architecture, supported decision types, input schema, context limit, license, and quantization/format before integrating.
   - Do not blindly rely on a previously mentioned URL or third-party checkpoint. Confirm the upstream repository and maintainer identity independently.
   - Build an adapter behind the `DecisionModel` interface and keep it optional.
   - Use compact evidence plus a predefined rubric; never pass protected traits or irrelevant identity fields.
   - Compare Laya with weighted scoring, TOPSIS, LambdaMART, and a local generative LLM under the same labeled evaluation.
   - Measure criterion accuracy, calibration where applicable, latency, memory, stability, and final ranking impact.
   - If model assets, license, or hardware compatibility cannot be verified, mark the experiment blocked and preserve a mock/test adapter; do not silently substitute a different model.

6. **Local LLM judge — research only**
   - Use a structured rubric and cite evidence IDs in the output.
   - Treat outputs as fallible features, not truth.
   - Test repeatability and counterfactual sensitivity.
   - Exclude from the default production ranking path unless benchmark results justify it.

### 6.5 Ontology and graph

**Ontology:** ESCO skills/occupations snapshot downloaded from its official portal. Keep the release date, URL, data license, attribution requirements, language selection, and SHA-256 hash.

**Graph:** NetworkX in process.

Suggested node types:
- `Candidate`
- `ResumeEvidence`
- `Skill`
- `Job`
- `Requirement`
- `Occupation`
- `Certification` (only when reliably extracted)

Suggested edges:
- `HAS_EVIDENCE`
- `MENTIONS_SKILL`
- `MAPS_TO_SKILL`
- `REQUIRES_SKILL`
- `RELATED_SKILL`
- `HAS_REQUIREMENT`
- `EVIDENCED_BY`

Every extracted skill should retain its original text, normalized concept ID if mapped, source evidence, confidence, and mapping method. An inferred or related skill must not be treated as equivalent to an explicit required skill.

Use graph features for skill coverage, evidence paths, synonym normalization, and exploratory analysis. Do not use generic node centrality as a direct proxy for candidate quality.

**Visualization:** Cytoscape.js. Render only the relevant subgraph for the selected candidate/job, not the entire dataset at once.

### 6.6 Backend, storage and frontend

**Backend**
- Python, FastAPI, Pydantic.
- SQLite for metadata, job records, candidates, extracted fields, experiment runs, and evaluation results.
- Use parameterized queries and explicit database migrations.
- Store large vectors and generated reports as versioned local artifacts, not huge blobs in SQLite.
- Use a background worker abstraction for ingestion/evaluation. Start with a bounded in-process queue if appropriate; do not introduce a separate broker until needed.

**Frontend**
- React, Vite, TypeScript.
- TanStack Query for API state and caching.
- TanStack Table for accessible table state and server-side pagination.
- Tailwind CSS plus custom neumorphic design tokens.
- ECharts for charts; Cytoscape.js for graph exploration.
- Use virtualized rows if profiling shows that it is needed, but preserve server-side pagination.

**Deployment**
- Native Windows setup is the primary development path.
- Docker Compose is optional for reproducible deployment if GPU support, file mounts, and Windows resource use are tested.
- No mandatory remote services.
- Bind local-only services to `127.0.0.1` by default.

## 7. Data design and data governance

### 7.1 Data sources

Use only datasets whose terms permit the intended use. Candidate sources to investigate include:
- Synthetic resumes and synthetic job descriptions authored for testing.
- Publicly licensed resume/JD matching or job-relevance datasets.
- Public job/skill taxonomies such as ESCO.
- Human-authored graded relevance labels for a small evaluation set.

Do not scrape personal resumes from job sites or professional networks. Do not assume a dataset is usable merely because it is downloadable or available on a model hub. Verify source, license, privacy terms, redistribution rights, and intended-use limitations.

### 7.2 Labeling plan

Create a relevance scale with written annotation guidance, for example:
- `0`: no meaningful evidence of meeting the stated job requirements.
- `1`: weak/limited evidence; major required criteria not evidenced.
- `2`: reasonable partial match; some required criteria supported.
- `3`: strong evidence for most stated requirements.

This scale is only an annotation aid, not a real hiring outcome. Reviewers should label evidence against explicit job criteria and be allowed to mark `insufficient_information`. For a subset, use two independent reviewers and report agreement. Do not generate all ground truth with the same LLM being evaluated.

### 7.3 Data minimization and retention

- Use random internal candidate IDs.
- Keep original files local and outside Git.
- Store only fields required for the task.
- Redact contact details from model inputs where feasible.
- Never log full resume text, names, email addresses, phone numbers, or raw protected data by default.
- Provide deletion for files, extracted records, embeddings, cached model results, and associated evaluation artifacts.
- Document retention settings and deletion behavior.
- Separate optional audit-group data from ranking features and restrict access.
- Do not use production user uploads for model training.

## 8. Evaluation and research design

### 8.1 Evaluation harness

Use Inspect AI if its abstractions fit the chosen extraction/decision tasks, plus a custom deterministic ranking harness. Keep metric calculation independent from any one LLM framework.

The harness must:
- Load immutable dataset and split manifests.
- Record dataset version/hash, job IDs, model names/revisions/hashes, prompt/schema version, hyperparameters, environment, random seeds, hardware details, and timestamps.
- Run a defined model matrix on the same cases.
- Capture errors, timeouts, peak memory, and latency.
- Write machine-readable results (JSONL or CSV/Parquet where available) and a human-readable report.
- Support resuming interrupted runs without duplicating completed cases.
- Avoid exposing resume PII in logs.
- Include unit tests for every metric and known toy examples.

### 8.2 Metrics

**Extraction**
- Field-level precision, recall, F1.
- JSON/schema validity.
- Evidence-grounding accuracy (does the cited snippet support the extracted claim?).
- Date/experience normalization accuracy.
- Failure and abstention rate.

**Ranking**
- nDCG@5 and nDCG@10.
- MRR.
- Precision@5/10 and Recall@5/10.
- Pairwise ordering accuracy where labels permit.
- Rank correlation for robustness tests.

**Efficiency**
- Cold model load time.
- Warm median and p95 latency.
- Candidates/second and resumes/minute.
- Peak process RAM and GPU VRAM.
- Disk use for weights, embeddings, and cache.
- API latency for first page and later pages.
- Cache hit rate and time saved by cache.

**Robustness and fairness diagnostics**
- Rank change after controlled changes to irrelevant identity cues.
- Kendall tau or another appropriate rank-correlation metric.
- Number/share of candidates crossing a shortlist threshold under a counterfactual.
- Selection-rate differences/ratios only when group labels are lawful, appropriate, sufficiently sized, and correctly interpreted.
- Confidence intervals or uncertainty estimates when sample size supports them.
- Report missingness, sample size, limitations, and subgroup uncertainty.

Fairness metrics can conflict and can be statistically unstable with small samples. A single metric cannot prove fairness or legal compliance.

### 8.3 Experiment matrix

At minimum, compare:
1. BM25 only.
2. Embeddings only.
3. RRF hybrid.
4. Weighted scoring.
5. TOPSIS.
6. LightGBM LambdaMART, if training labels are sufficient.
7. Cross-encoder reranking, if compatible with the hardware.
8. Laya criterion-scoring adapter, if its assets and license are verified.
9. Local LLM scoring as an optional research baseline.
10. Graph/ontology ablation: no graph, synonym normalization only, graph-derived features.

Keep retrieval constant when comparing decision layers. Also run end-to-end experiments to understand interaction effects. Tune parameters only on validation data; report the untouched test results once.

### 8.4 Acceptance criteria (initial targets)

These are proposed engineering gates, not measured claims. Revise them after establishing a baseline and document any change.

- Core app runs offline after dependencies and model assets are installed.
- No required paid API or telemetry.
- Identical inputs/configuration produce deterministic ranking results for deterministic rankers.
- No LLM inference on cached, default ranking requests.
- Every displayed criterion score can be traced to evidence or explicitly marked as unavailable/uncertain.
- Pagination and filters execute server-side.
- At least five ranking/decision approaches have reproducible benchmark results.
- Graph and ontology contributions are measured through ablation.
- RAM/VRAM and latency are recorded for every model run.
- License and provenance inventory covers all direct dependencies, model artifacts, and datasets.
- Unit, integration, and core end-to-end tests pass.
- The UI is keyboard accessible and has a high-contrast mode.
- Fairness tests include controlled counterfactuals and a limitations report.

## 9. Fairness, safety and human oversight

The system can influence access to employment, so it needs heightened care.

- Rank against job-relevant evidence only.
- Do not infer age, gender, ethnicity, religion, disability, family status, or other protected traits.
- Remove irrelevant identity cues from model inputs where possible; test whether removal affects relevant information.
- Do not use name, photo, address, prestige proxies, employment gaps, or institution brand as unexplained ranking features.
- Treat missing evidence as unknown, not proof of missing ability.
- Allow a human reviewer to inspect and challenge scores.
- Provide an appeal/correction path for parsing mistakes.
- Display model limitations and evaluation dataset coverage.
- Keep fairness-audit data separate from production scoring features.
- Require human review for every final shortlist decision.
- Do not market the system as bias-free or legally compliant.

## 10. Security and privacy

- Default host: `127.0.0.1`; do not expose the API to a LAN without an explicit secure configuration.
- Validate file extensions, MIME types, size limits, and parser errors.
- Treat uploaded files and extracted text as untrusted data; prompt injection in resume content must not control system prompts or tool execution.
- Never execute macros, scripts, or embedded file content.
- Use safe temporary directories and clean up intermediate files.
- Do not render uploaded HTML directly.
- Use parameterized database operations.
- Keep secrets out of source control.
- Apply bounded request sizes and rate limits even in local mode.
- Add audit events without PII.
- Document backup and secure deletion limitations, including SSD wear-leveling and filesystem snapshots.
- Disable external telemetry by default.

## 11. Observability and reproducibility

Each run must record:
- Run ID and UTC timestamp.
- Git commit and dependency lock version.
- Hardware, OS, Python, CUDA/driver, and runtime versions.
- Dataset and split hashes.
- Model ID, revision, file hash, quantization, context length, and inference settings.
- Ranking method, weights, fusion parameters, feature schema, and random seed.
- Metric outputs, errors, latency, memory, and cache statistics.

Use MLflow locally only if it provides value without introducing unnecessary services; a versioned JSONL results store is an acceptable first release. DVC is optional and must not upload private data to a remote by default. Git should contain code, small synthetic fixtures, configuration templates, and documentation—not real resumes or large model weights.

## 12. Setup and deployment overview

Detailed agent execution steps are specified in `Agent.md`. The expected workflow is:

1. Inspect hardware and current repository.
2. Establish license and source manifests.
3. Create the Python and frontend workspaces.
4. Implement schemas, storage, and ingestion.
5. Add extraction and caching.
6. Add retrieval and rankers.
7. Add ESCO/graph.
8. Build the evaluation/fairness harness.
9. Build the API and UI.
10. Add tests, license scanning, packaging, and documentation.
11. Run the complete benchmark and publish results.

The application should work without Docker first. Docker Compose is a reproducibility option, not a prerequisite.

## 13. Resource catalog and official entry points

The agent must confirm current URLs, versions, licenses, model cards, and maintenance status before downloading. These are starting points, not proof that every artifact is suitable.

### Models and inference
- llama.cpp: https://github.com/ggml-org/llama.cpp
- Qwen model family: https://huggingface.co/Qwen
- Microsoft Phi models: https://huggingface.co/microsoft
- Sentence Transformers: https://www.sbert.net/
- MiniLM-L6-v2 model card: https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2
- BGE models: https://huggingface.co/BAAI

### Decision models
- Laya candidate repository previously identified: https://github.com/NandhaKishorM/laya
- Laya model namespace previously identified: https://huggingface.co/convaiinnovations/laya
- LightGBM: https://github.com/microsoft/LightGBM
- scikit-learn: https://scikit-learn.org/
- TOPSIS: implement a small tested implementation or choose a maintained library after license review; do not add a dependency without need.

**Laya verification rule:** independently verify the current official repository, maintainers, model card, checkpoint, architecture, decision-task schema, license, context constraints, supported formats, and hardware performance. If the above candidate URLs are moved, stale, or cannot be authenticated, do not download an arbitrary similarly named model. Record the experiment as blocked until verified.

### Parsing and APIs
- PyMuPDF: https://pymupdf.readthedocs.io/
- Docling: https://github.com/docling-project/docling
- FastAPI: https://fastapi.tiangolo.com/
- Pydantic: https://docs.pydantic.dev/
- SQLite: https://www.sqlite.org/

### Ontology, graph, fairness and evaluation
- ESCO: https://esco.ec.europa.eu/
- NetworkX: https://networkx.org/
- Cytoscape.js: https://js.cytoscape.org/
- Fairlearn: https://fairlearn.org/
- Inspect AI: https://inspect.aisi.org.uk/
- Inspect AI source: https://github.com/UKGovernmentBEIS/inspect_ai
- ranx ranking evaluation: https://github.com/AmenRa/ranx

### Frontend and visualization
- React: https://react.dev/
- Vite: https://vite.dev/
- TypeScript: https://www.typescriptlang.org/
- Tailwind CSS: https://tailwindcss.com/
- TanStack Table: https://tanstack.com/table
- TanStack Query: https://tanstack.com/query
- Apache ECharts: https://echarts.apache.org/

### Reproducibility and security
- pytest: https://docs.pytest.org/
- Ruff: https://docs.astral.sh/ruff/
- Docker Compose: https://docs.docker.com/compose/
- Syft (SBOM): https://github.com/anchore/syft
- ScanCode Toolkit: https://github.com/nexB/scancode-toolkit

## 14. Project impact

### Technical impact
- Demonstrates a complete local AI application rather than an isolated notebook.
- Shows applied NLP, retrieval, embeddings, structured extraction, decision modeling, ranking metrics, graph analysis, and model evaluation.
- Demonstrates constrained deployment on consumer hardware.
- Produces reproducible comparisons between transparent and learned decision approaches.
- Makes the contribution of ontology and graph features measurable through ablation.

### Research impact
- Documents which methods work on the selected data, under which constraints, and with what trade-offs.
- Provides evidence about whether Laya adds value compared with simple baselines.
- Highlights uncertainty, missing information, and model limitations.
- Enables future research into counterfactual robustness and human-centered review.

### Responsible-use impact
- Gives reviewers traceable evidence instead of opaque match scores.
- Exposes instability and potential disparate outcomes for audit.
- Keeps personal data local by default.
- Emphasizes that algorithmic output is advisory and requires human judgment.

### Portfolio impact
A strong final portfolio release should contain:
- Architecture diagram.
- Working demo with synthetic or redistributable data.
- Reproducible benchmark command and machine-readable results.
- Accuracy-vs-latency-vs-memory plots.
- Ranking and fairness report with limitations.
- Example graph visualization.
- Setup guide and license/SBOM inventory.
- Short demo video or screenshots generated from safe sample data.

Do not claim improved hiring outcomes, fairness, or superiority until the evaluation provides credible evidence.

## 15. Definition of done

The project is done when a new developer can clone the repository, follow documented setup steps, download only license-approved assets, run the app locally, upload a sample batch, view evidence-backed paginated rankings, compare at least five ranking approaches, inspect the skill graph, run the fairness/robustness suite, and reproduce the published metrics without a paid API.

The final report must state the tested hardware, exact model revisions and quantizations, dataset provenance, measured resource use, model limitations, and known failure cases.
