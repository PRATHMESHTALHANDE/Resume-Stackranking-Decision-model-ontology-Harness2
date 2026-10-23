# Resume Intelligence, Ranking & Fairness Lab

> An open-source, local-first platform for evidence-grounded resume-to-job matching, multi-criteria decision modeling, skill ontology graph analysis, and diagnostic fairness benchmarking.

[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Local-First](https://img.shields.io/badge/Architecture-Local--First-green.svg)](#)
[![Zero-Paid-API](https://img.shields.io/badge/APIs-100%25%20Open--Source-brightgreen.svg)](#)

---

## ⚠️ Important Advisory Disclaimer
**This application is a decision-support aid designed exclusively for human recruiters and researchers. It does NOT make autonomous hiring, rejection, or candidate disqualification decisions.** All match scores represent specific multi-criteria alignment signals and must be verified against source evidence citations by a human reviewer.

---

## 🌟 Key Features

1. **Evidence-Grounded Ingestion & Parsing:**
   - Supports PDF and DOCX formats locally via PyMuPDF (`fitz`) and `python-docx`.
   - Every qualification claim anchors to verbatim citations with exact page numbers and section provenance.
   - Instant SHA-256 deduplication and parser caching.

2. **Multi-Model Retrieval & Decision Engine:**
   - **BM25 Lexical Search:** Accurate technical keyword and exact acronym matching (`C++`, `.NET`, `AWS`).
   - **Dense Semantic Vector Search:** `sentence-transformers/all-MiniLM-L6-v2` cosine similarity.
   - **RRF (Reciprocal Rank Fusion):** Robust hybrid fusion combining lexical and semantic signals.
   - **Weighted Criterion Scoring:** Transparent recruiter-controlled requirement weights.
   - **TOPSIS Decision Analysis:** Mathematical multi-criteria distance to Positive/Negative Ideal Solutions.
   - **LightGBM LambdaMART:** Supervised Learning-to-Rank optimizing listwise nDCG.
   - **Laya Decision Model:** Experimental investigation and typed adapter.

3. **ESCO Skill Taxonomy & Knowledge Graph:**
   - Canonical concept mapping against the official European Skills/Competences classification.
   - Multi-stage normalizer (Exact ➔ Alias ➔ Fuzzy ➔ Semantic).
   - In-memory heterogeneous graph (NetworkX) visualized interactively via Cytoscape.js.

4. **Robustness & Fairness Diagnostics:**
   - Counterfactual identity perturbation suite auditing rank shifts under name/pronoun swaps.
   - Selection rate disparity and demographic parity metrics via Fairlearn.

5. **Accessible Neumorphic (Soft UI) Dashboard:**
   - Custom soft-UI dual-shadow aesthetic built with React, Vite, TypeScript, and Tailwind CSS.
   - Full light (`#E8ECF2`) and dark (`#181B20`) themes meeting WCAG 2.2 AA accessibility standards.
   - Interactive Pareto frontier plots (Quality vs. Latency vs. Memory) powered by Apache ECharts.

6. **100% Local-First & Zero Global Disk Pollution:**
   - All model weights and caches reside strictly within `<project_root>/models/weights/` and `models/cache/`.
   - Zero unmonitored disk caching (`~/.cache/huggingface` is completely disabled).
   - Audited via `models/manifest.json`.

---

## 🛠️ Quickstart

### Prerequisites
- Windows 11 (or Linux/macOS)
- Python 3.11 (`uv` recommended)
- Node.js v20+ / v24+

### Installation

1. **Clone the repository:**
   ```bash
   git clone <repo-url>
   cd "HR Resume Stackranking - Decision model + LLM + Ontology + Harness2"
   ```

2. **Set up Python environment with `uv`:**
   ```powershell
   uv venv --python 3.11
   uv sync --extra dev
   ```

3. **Run automated test suite:**
   ```powershell
   uv run pytest tests/ -v
   ```

4. **Launch the FastAPI backend:**
   ```powershell
   uv run uvicorn apps.api.main:app --reload --host 127.0.0.1 --port 8001
   ```

5. **Launch the Neumorphic web interface:**
   ```powershell
   cd apps/web
   npm install
   npm run dev
   ```

---

## 📚 Documentation Catalog

Comprehensive standalone documentation for every tool and model used is maintained in [`docs/resources/`](docs/resources/README.md):
- [FastAPI](docs/resources/fastapi.md) | [Pydantic](docs/resources/pydantic.md) | [PyMuPDF](docs/resources/pymupdf.md)
- [MiniLM Embeddings](docs/resources/sentence-transformers-all-minilm-l6-v2.md) | [BM25](docs/resources/rank-bm25.md) | [ESCO Ontology](docs/resources/esco-ontology.md)
- [TOPSIS Ranker](docs/resources/topsis.md) | [LightGBM LambdaMART](docs/resources/lightgbm.md) | [Laya Decision Model](docs/resources/laya-decision-model.md)
- [NetworkX](docs/resources/networkx.md) | [ranx Benchmark](docs/resources/ranx.md) | [Fairlearn](docs/resources/fairlearn.md)
- [Tailwind Neumorphism](docs/resources/tailwind-css-neumorphism.md) | [Cytoscape.js](docs/resources/cytoscape-js.md) | [ECharts](docs/resources/apache-echarts.md)

---

## 📄 License
This project is licensed under the [MIT License](LICENSE).
Third-party component notices and licenses are inventoried in [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).
