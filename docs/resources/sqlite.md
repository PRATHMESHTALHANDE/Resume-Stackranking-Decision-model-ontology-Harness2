# Resource: SQLite & SQLModel/Alembic (Local Persistence Engine)

## 1. Overview & Purpose
**SQLite** is a C-language library that implements a small, fast, self-contained, high-reliability, full-featured, SQL database engine.

In our **Resume Intelligence, Ranking & Fairness Lab**, SQLite acts as the complete local metadata and run registry:
- Stores `jobs`, `resumes`, `parsed_profiles`, `criteria_weights`, and `evaluation_runs`.
- Operates zero-configuration directly from a single local file (`artifacts/data/app.db`).
- Guarantees ACID transactions with Write-Ahead Logging (WAL mode enabled) for safe concurrent reads during background parsing.
- Requires zero background daemons, network ports, or Docker containers.

## 2. Upstream Provenance & License
- **Official Documentation:** https://www.sqlite.org/
- **License:** Public Domain (Unrestricted free use in any context).
- **Author:** D. Richard Hipp.

## 3. Local Installation & Configuration
Built directly into the standard Python runtime (`sqlite3` module). Enhanced with Python ORM bindings via:
```powershell
uv add sqlmodel aiosqlite
```

### Database Connection & PRAGMA Settings (`packages/common/database.py`):
```python
"""
SQLite database connection initialization with WAL mode for concurrency.
"""
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parents[2] / "artifacts" / "data" / "app.db"

def get_connection() -> sqlite3.Connection:
    """Returns a SQLite connection with Write-Ahead Logging enabled."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.execute("PRAGMA journal_mode = WAL;")  # Non-blocking concurrent reads
    conn.execute("PRAGMA synchronous = NORMAL;") # Fast, crash-safe on SSDs
    conn.execute("PRAGMA foreign_keys = ON;")   # Strict referential integrity
    conn.row_factory = sqlite3.Row
    return conn
```

## 4. Hardware Footprint & Resource Impact
- **Disk Footprint:** Extremely compact (< 10 MB for typical database with 500 resumes).
- **Memory Footprint:** In-process caching consumes < 15 MB system RAM.
- **Query Latency:** Sub-millisecond indexed lookups on primary keys (`candidate_id`, `job_id`).

## 5. Schema & Architecture
Key Tables:
- `resumes`: `id`, `content_hash`, `filename`, `file_type`, `page_count`, `created_at`
- `parsed_profiles`: `candidate_id`, `structured_json`, `uncertainty_flags`, `updated_at`
- `jobs`: `id`, `title`, `description_text`, `criteria_json`, `version`
- `rankings`: `run_id`, `job_id`, `candidate_id`, `rank`, `score`, `model_name`, `created_at`
- `evaluation_runs`: `run_id`, `config_hash`, `metrics_json`, `latency_ms`, `ram_mb`, `vram_mb`

## 6. Failure Modes, Fallbacks & Edge Cases
- **Database Locks:** Avoided entirely by using WAL mode (`PRAGMA journal_mode = WAL;`) and short parameterized write transactions. Large vector arrays are kept out of SQLite and stored as dedicated NumPy binary files (`artifacts/embeddings/*.npy`).
