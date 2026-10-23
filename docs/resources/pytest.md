# Resource Specification: pytest & Multi-Tier Testing Suite

## 1. Overview & Positioning
- **Name:** pytest
- **Ecosystem:** `pytest`, `pytest-asyncio`, `pytest-cov`, `anyio`
- **License:** MIT License
- **Role in Project:** Comprehensive multi-tier automated testing covering unit tests (`tests/unit/`) and end-to-end API tests (`tests/api/`).

## 2. Test Execution Commands
```bash
# Execute entire test suite
uv run pytest tests/ -v

# Execute unit tests with timing and coverage
uv run pytest tests/unit/ -v --cov=packages

# Execute API integration tests
uv run pytest tests/api/test_api.py -v
```

## 3. Test Suites Implemented
- `test_settings.py`: Path resolution, directory existence, environment variable redirection.
- `test_database.py`: SQLite WAL mode, schema initialization, parameterized CRUD operations.
- `test_ingestion.py`: MIME type inspection, SHA-256 deduplication, PyMuPDF and DOCX extraction.
- `test_extraction.py`: Contact parsing, section segmentation, date normalization, mock extraction.
- `test_graph.py`: NetworkX heterogeneous graph modeling, Cytoscape subgraph extraction.
- `test_rankers.py`: BM25, Dense MiniLM, RRF, Weighted, TOPSIS, LambdaMART, LAYA adapter.
- `test_evaluation.py`: nDCG@k, MRR, Precision, Recall, CounterfactualAuditor, ParityAuditor.
- `test_api.py`: FastAPI endpoints for health, jobs, resumes, rankings, graph, and evaluations.
