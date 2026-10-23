# Resource Specification: uv (Extremely Fast Python Package Manager)

## 1. Overview & Positioning
- **Name:** uv
- **Creator / Maintainer:** Astral
- **License:** Apache-2.0 / MIT
- **Role in Project:** Primary environment manager, package installer, and dependency resolution lockfile engine (`uv venv`, `uv sync`, `uv run`).
- **Why Selected:** 10x-100x faster than pip/poetry, written in Rust, built-in virtual environment orchestration, native Windows support with zero global cache pollution.

## 2. Configuration & Usage
```bash
# Initialize virtual environment with Python 3.11
uv venv --python 3.11

# Install and lock all workspace dependencies
uv sync --extra dev

# Run tools within the isolated environment
uv run pytest tests/ -v
uv run uvicorn apps.api.main:app --reload
```

## 3. Operational Best Practices
- Always prefix execution with `uv run` to guarantee that the local `.venv/` site-packages are utilized without needing manual shell activation.
- All dependencies are deterministically pinned in `uv.lock`.
