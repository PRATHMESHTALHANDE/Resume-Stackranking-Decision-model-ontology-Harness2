"""
Module: packages.common.database
Description:
    SQLite database management for the Resume Intelligence Lab.
    Implements:
    - Thread-safe SQLite connection factory with Write-Ahead Logging (WAL mode).
    - Automated schema migrations creating tables for resumes, profiles, jobs, rankings, and runs.
    - Parameterized database operations preventing SQL injection.
    - Clean cascading deletion for candidate data minimization.

Author:
    Resume Intelligence Architect
"""
import sqlite3
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

from packages.common.settings import SQLITE_DB_PATH
from packages.common.schemas import (
    ResumeDocument,
    ResumeProfile,
    JobDescription,
    RankingResult,
    EvaluationRun,
)

# ==============================================================================
# 1. Connection Factory (WAL Mode Enabled)
# ==============================================================================
def get_connection(db_path: Optional[Path] = None) -> sqlite3.Connection:
    """
    Returns an open SQLite database connection configured with WAL journal mode
    for safe concurrent readers during background document ingestion.

    Args:
        db_path: Optional custom path (used in unit tests for temporary DBs).

    Returns:
        sqlite3.Connection with Row row_factory for dict-like column access.
    """
    target_path = db_path or SQLITE_DB_PATH
    target_path.parent.mkdir(parents=True, exist_ok=True)
    
    conn = sqlite3.connect(str(target_path), timeout=30.0)
    conn.execute("PRAGMA journal_mode = WAL;")     # Non-blocking concurrent reads
    conn.execute("PRAGMA synchronous = NORMAL;")    # High performance, crash-safe on SSDs
    conn.execute("PRAGMA foreign_keys = ON;")      # Enforce referential integrity
    conn.row_factory = sqlite3.Row
    return conn


# ==============================================================================
# 2. Database Schema Initialization & Migrations
# ==============================================================================
SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS resumes (
    document_id TEXT PRIMARY KEY,
    content_hash TEXT NOT NULL UNIQUE,
    source_filename TEXT NOT NULL,
    file_type TEXT NOT NULL,
    page_count INTEGER NOT NULL DEFAULT 1,
    file_size_bytes INTEGER NOT NULL,
    parser_status TEXT NOT NULL DEFAULT 'pending',
    warnings_json TEXT NOT NULL DEFAULT '[]',
    requisition_id TEXT,
    created_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_resumes_hash ON resumes(content_hash);

CREATE TABLE IF NOT EXISTS parsed_profiles (
    candidate_id TEXT PRIMARY KEY,
    document_id TEXT NOT NULL UNIQUE,
    requisition_id TEXT,
    skills_json TEXT NOT NULL DEFAULT '[]',
    experience_json TEXT NOT NULL DEFAULT '[]',
    education_json TEXT NOT NULL DEFAULT '[]',
    total_experience_years REAL NOT NULL DEFAULT 0.0,
    summary TEXT,
    uncertainty_json TEXT NOT NULL DEFAULT '[]',
    extraction_method TEXT NOT NULL,
    created_at TEXT NOT NULL,
    FOREIGN KEY (document_id) REFERENCES resumes(document_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS jobs (
    job_id TEXT PRIMARY KEY,
    requisition_id TEXT,
    title TEXT NOT NULL,
    description_text TEXT NOT NULL,
    criteria_json TEXT NOT NULL DEFAULT '[]',
    minimum_experience_years REAL,
    version INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS rankings (
    ranking_id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id TEXT NOT NULL,
    job_id TEXT NOT NULL,
    candidate_id TEXT NOT NULL,
    rank INTEGER NOT NULL,
    score REAL NOT NULL,
    model_name TEXT NOT NULL,
    component_scores_json TEXT NOT NULL DEFAULT '{}',
    evidence_json TEXT NOT NULL DEFAULT '[]',
    uncertainty_json TEXT NOT NULL DEFAULT '[]',
    decision_summary TEXT,
    llm_summary TEXT,
    created_at TEXT NOT NULL,
    FOREIGN KEY (job_id) REFERENCES jobs(job_id) ON DELETE CASCADE,
    FOREIGN KEY (candidate_id) REFERENCES parsed_profiles(candidate_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_rankings_job_model ON rankings(job_id, model_name);
CREATE INDEX IF NOT EXISTS idx_rankings_run ON rankings(run_id);

CREATE TABLE IF NOT EXISTS evaluation_runs (
    run_id TEXT PRIMARY KEY,
    timestamp TEXT NOT NULL,
    model_name TEXT NOT NULL,
    dataset_split TEXT NOT NULL,
    split_hash TEXT NOT NULL,
    candidate_count INTEGER NOT NULL,
    query_count INTEGER NOT NULL,
    ndcg_at_5 REAL NOT NULL,
    ndcg_at_10 REAL NOT NULL,
    mrr REAL NOT NULL,
    precision_at_5 REAL NOT NULL,
    recall_at_10 REAL NOT NULL,
    latency_median_ms REAL NOT NULL,
    latency_p95_ms REAL NOT NULL,
    candidates_per_second REAL NOT NULL,
    peak_ram_mb REAL NOT NULL,
    peak_vram_mb REAL NOT NULL,
    counterfactual_tau REAL,
    shortlist_crossings INTEGER
);
"""

def init_db(db_path: Optional[Path] = None) -> None:
    """
    Initializes all database tables and indexes if they do not exist,
    and applies backwards-compatible column migrations.
    """
    conn = get_connection(db_path)
    try:
        with conn:
            # 1. Base table creation
            conn.executescript(SCHEMA_SQL)

            # 2. Safe backwards-compatible column migrations for existing databases
            for tbl in ["jobs", "resumes", "parsed_profiles"]:
                try:
                    conn.execute(f"ALTER TABLE {tbl} ADD COLUMN requisition_id TEXT;")
                except Exception:
                    pass  # Column already exists

            for col in ["decision_summary", "llm_summary"]:
                try:
                    conn.execute(f"ALTER TABLE rankings ADD COLUMN {col} TEXT;")
                except Exception:
                    pass  # Column already exists

            # 3. Create indexes safely after ensuring columns exist
            for idx_stmt in [
                "CREATE INDEX IF NOT EXISTS idx_resumes_req ON resumes(requisition_id);",
                "CREATE INDEX IF NOT EXISTS idx_profiles_req ON parsed_profiles(requisition_id);",
                "CREATE INDEX IF NOT EXISTS idx_jobs_req ON jobs(requisition_id);",
            ]:
                try:
                    conn.execute(idx_stmt)
                except Exception:
                    pass
    finally:
        conn.close()


# ==============================================================================
# 3. Parameterized CRUD Data Operations
# ==============================================================================
def save_resume_document(doc: ResumeDocument, db_path: Optional[Path] = None) -> None:
    """Inserts or updates a ResumeDocument record using parameterized SQL."""
    conn = get_connection(db_path)
    try:
        with conn:
            conn.execute(
                """
                INSERT INTO resumes (
                    document_id, content_hash, source_filename, file_type,
                    page_count, file_size_bytes, parser_status, warnings_json,
                    requisition_id, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(document_id) DO UPDATE SET
                    parser_status=excluded.parser_status,
                    warnings_json=excluded.warnings_json,
                    requisition_id=excluded.requisition_id;
                """,
                (
                    doc.document_id,
                    doc.content_hash,
                    doc.source_filename,
                    doc.file_type,
                    doc.page_count,
                    doc.file_size_bytes,
                    doc.parser_status,
                    json.dumps(doc.warnings),
                    doc.requisition_id,
                    doc.created_at.isoformat(),
                ),
            )
    finally:
        conn.close()


def get_resume_by_hash(content_hash: str, db_path: Optional[Path] = None) -> Optional[Dict[str, Any]]:
    """Checks for existing document by SHA-256 content hash (instant deduplication)."""
    conn = get_connection(db_path)
    try:
        cursor = conn.execute("SELECT * FROM resumes WHERE content_hash = ?;", (content_hash,))
        row = cursor.fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def save_parsed_profile(profile: ResumeProfile, db_path: Optional[Path] = None) -> None:
    """Saves structured candidate profile with JSON serialization of nested collections."""
    conn = get_connection(db_path)
    try:
        with conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO parsed_profiles (
                    candidate_id, document_id, requisition_id, skills_json, experience_json,
                    education_json, total_experience_years, summary, uncertainty_json,
                    extraction_method, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                """,
                (
                    profile.candidate_id,
                    profile.document_id,
                    profile.requisition_id,
                    json.dumps([s.model_dump() for s in profile.skills]),
                    json.dumps([e.model_dump() for e in profile.experience_items]),
                    json.dumps([ed.model_dump() for ed in profile.education_items]),
                    profile.total_experience_years,
                    profile.summary,
                    json.dumps(profile.uncertainty_flags),
                    profile.extraction_method,
                    profile.created_at.isoformat(),
                ),
            )
    finally:
        conn.close()


def save_job_description(job: JobDescription, db_path: Optional[Path] = None) -> None:
    """Saves or updates a Job Description and its review criteria."""
    conn = get_connection(db_path)
    try:
        with conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO jobs (
                    job_id, requisition_id, title, description_text, criteria_json,
                    minimum_experience_years, version, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?);
                """,
                (
                    job.job_id,
                    job.requisition_id,
                    job.title,
                    job.description_text,
                    json.dumps([c.model_dump() for c in job.criteria]),
                    job.minimum_experience_years,
                    job.version,
                    job.created_at.isoformat(),
                ),
            )
    finally:
        conn.close()


def delete_resume(document_id: str, db_path: Optional[Path] = None) -> None:
    """Cascading deletion of resume, extracted profile, and rankings."""
    conn = get_connection(db_path)
    try:
        with conn:
            conn.execute("DELETE FROM resumes WHERE document_id = ?;", (document_id,))
    finally:
        conn.close()


def delete_all_resumes(db_path: Optional[Path] = None) -> None:
    """Cascading deletion of all uploaded resumes, candidate profiles, and candidate rankings."""
    conn = get_connection(db_path)
    try:
        with conn:
            conn.execute("DELETE FROM rankings;")
            conn.execute("DELETE FROM parsed_profiles;")
            conn.execute("DELETE FROM resumes;")
    finally:
        conn.close()


def list_resumes(db_path: Optional[Path] = None, requisition_id: Optional[str] = None) -> List[ResumeDocument]:
    """Retrieves all ingested resume documents, optionally filtered by requisition_id."""
    conn = get_connection(db_path)
    try:
        if requisition_id:
            cursor = conn.execute("SELECT * FROM resumes WHERE requisition_id = ? ORDER BY created_at DESC;", (requisition_id,))
        else:
            cursor = conn.execute("SELECT * FROM resumes ORDER BY created_at DESC;")
        rows = cursor.fetchall()
        docs = []
        for r in rows:
            req_id = r["requisition_id"] if "requisition_id" in r.keys() else None
            docs.append(
                ResumeDocument(
                    document_id=r["document_id"],
                    content_hash=r["content_hash"],
                    source_filename=r["source_filename"],
                    file_type=r["file_type"],
                    page_count=r["page_count"],
                    file_size_bytes=r["file_size_bytes"],
                    parser_status=r["parser_status"],
                    warnings=json.loads(r["warnings_json"]),
                    requisition_id=req_id,
                    created_at=datetime.fromisoformat(r["created_at"]),
                )
            )
        return docs
    finally:
        conn.close()


def get_resume(document_id: str, db_path: Optional[Path] = None) -> Optional[ResumeDocument]:
    """Retrieves a single ResumeDocument by ID."""
    conn = get_connection(db_path)
    try:
        cursor = conn.execute("SELECT * FROM resumes WHERE document_id = ?;", (document_id,))
        r = cursor.fetchone()
        if not r:
            return None
        req_id = r["requisition_id"] if "requisition_id" in r.keys() else None
        return ResumeDocument(
            document_id=r["document_id"],
            content_hash=r["content_hash"],
            source_filename=r["source_filename"],
            file_type=r["file_type"],
            page_count=r["page_count"],
            file_size_bytes=r["file_size_bytes"],
            parser_status=r["parser_status"],
            warnings=json.loads(r["warnings_json"]),
            requisition_id=req_id,
            created_at=datetime.fromisoformat(r["created_at"]),
        )
    finally:
        conn.close()


def list_parsed_profiles(db_path: Optional[Path] = None, requisition_id: Optional[str] = None) -> List[ResumeProfile]:
    """Retrieves parsed candidate profiles, optionally filtered by requisition_id."""
    conn = get_connection(db_path)
    try:
        if requisition_id:
            cursor = conn.execute("SELECT * FROM parsed_profiles WHERE requisition_id = ? ORDER BY created_at DESC;", (requisition_id,))
        else:
            cursor = conn.execute("SELECT * FROM parsed_profiles ORDER BY created_at DESC;")
        rows = cursor.fetchall()
        profiles = []
        for r in rows:
            req_id = r["requisition_id"] if "requisition_id" in r.keys() else None
            profiles.append(
                ResumeProfile(
                    candidate_id=r["candidate_id"],
                    document_id=r["document_id"],
                    requisition_id=req_id,
                    skills=json.loads(r["skills_json"]),
                    experience_items=json.loads(r["experience_json"]),
                    education_items=json.loads(r["education_json"]),
                    total_experience_years=r["total_experience_years"],
                    summary=r["summary"],
                    uncertainty_flags=json.loads(r["uncertainty_json"]),
                    extraction_method=r["extraction_method"],
                    created_at=datetime.fromisoformat(r["created_at"]),
                )
            )
        return profiles
    finally:
        conn.close()


def get_parsed_profile(candidate_id: str, db_path: Optional[Path] = None) -> Optional[ResumeProfile]:
    """Retrieves a single candidate profile by ID."""
    conn = get_connection(db_path)
    try:
        cursor = conn.execute("SELECT * FROM parsed_profiles WHERE candidate_id = ?;", (candidate_id,))
        r = cursor.fetchone()
        if not r:
            return None
        req_id = r["requisition_id"] if "requisition_id" in r.keys() else None
        return ResumeProfile(
            candidate_id=r["candidate_id"],
            document_id=r["document_id"],
            requisition_id=req_id,
            skills=json.loads(r["skills_json"]),
            experience_items=json.loads(r["experience_json"]),
            education_items=json.loads(r["education_json"]),
            total_experience_years=r["total_experience_years"],
            summary=r["summary"],
            uncertainty_flags=json.loads(r["uncertainty_json"]),
            extraction_method=r["extraction_method"],
            created_at=datetime.fromisoformat(r["created_at"]),
        )
    finally:
        conn.close()


def list_jobs(db_path: Optional[Path] = None) -> List[JobDescription]:
    """Retrieves all job descriptions."""
    conn = get_connection(db_path)
    try:
        cursor = conn.execute("SELECT * FROM jobs ORDER BY created_at DESC;")
        rows = cursor.fetchall()
        jobs = []
        for r in rows:
            req_id = r["requisition_id"] if ("requisition_id" in r.keys() and r["requisition_id"]) else f"REQ-{r['job_id'][:6].upper()}"
            jobs.append(
                JobDescription(
                    job_id=r["job_id"],
                    requisition_id=req_id,
                    title=r["title"],
                    description_text=r["description_text"],
                    criteria=json.loads(r["criteria_json"]),
                    minimum_experience_years=r["minimum_experience_years"],
                    version=r["version"],
                    created_at=datetime.fromisoformat(r["created_at"]),
                )
            )
        return jobs
    finally:
        conn.close()


def get_job(job_id: str, db_path: Optional[Path] = None) -> Optional[JobDescription]:
    """Retrieves a job description by ID."""
    conn = get_connection(db_path)
    try:
        cursor = conn.execute("SELECT * FROM jobs WHERE job_id = ?;", (job_id,))
        r = cursor.fetchone()
        if not r:
            return None
        req_id = r["requisition_id"] if ("requisition_id" in r.keys() and r["requisition_id"]) else f"REQ-{r['job_id'][:6].upper()}"
        return JobDescription(
            job_id=r["job_id"],
            requisition_id=req_id,
            title=r["title"],
            description_text=r["description_text"],
            criteria=json.loads(r["criteria_json"]),
            minimum_experience_years=r["minimum_experience_years"],
            version=r["version"],
            created_at=datetime.fromisoformat(r["created_at"]),
        )
    finally:
        conn.close()


def delete_job(job_id: str, db_path: Optional[Path] = None) -> None:
    """Deletes a job description and its associated rankings."""
    conn = get_connection(db_path)
    try:
        with conn:
            conn.execute("DELETE FROM jobs WHERE job_id = ?;", (job_id,))
    finally:
        conn.close()


def save_ranking_results(results: List[RankingResult], db_path: Optional[Path] = None) -> None:
    """Saves a batch of ranking results for a run, including decision and LLM summaries."""
    conn = get_connection(db_path)
    try:
        with conn:
            conn.executemany(
                """
                INSERT INTO rankings (
                    run_id, job_id, candidate_id, rank, score, model_name,
                    component_scores_json, evidence_json, uncertainty_json,
                    decision_summary, llm_summary, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                """,
                [
                    (
                        res.run_id,
                        res.job_id,
                        res.candidate_id,
                        res.rank,
                        res.score,
                        res.model_name,
                        json.dumps(res.component_scores),
                        json.dumps([e.model_dump() for e in res.evidence_citations]),
                        json.dumps(res.uncertainty_markers),
                        res.decision_summary,
                        res.llm_summary,
                        res.created_at.isoformat(),
                    )
                    for res in results
                ],
            )
    finally:
        conn.close()


def get_rankings_by_run(run_id: str, db_path: Optional[Path] = None) -> List[RankingResult]:
    """Retrieves ranking results for a specific run ID."""
    conn = get_connection(db_path)
    try:
        cursor = conn.execute(
            "SELECT * FROM rankings WHERE run_id = ? ORDER BY rank ASC;",
            (run_id,),
        )
        rows = cursor.fetchall()
        results = []
        for r in rows:
            keys = r.keys()
            results.append(
                RankingResult(
                    candidate_id=r["candidate_id"],
                    job_id=r["job_id"],
                    rank=r["rank"],
                    score=r["score"],
                    model_name=r["model_name"],
                    component_scores=json.loads(r["component_scores_json"]),
                    evidence_citations=json.loads(r["evidence_json"]),
                    uncertainty_markers=json.loads(r["uncertainty_json"]),
                    decision_summary=r["decision_summary"] if "decision_summary" in keys else None,
                    llm_summary=r["llm_summary"] if "llm_summary" in keys else None,
                    run_id=r["run_id"],
                    created_at=datetime.fromisoformat(r["created_at"]),
                )
            )
        return results
    finally:
        conn.close()


def get_latest_rankings_for_job(job_id: str, db_path: Optional[Path] = None) -> List[RankingResult]:
    """Retrieves the most recent ranking run results for a specific job."""
    conn = get_connection(db_path)
    try:
        cursor = conn.execute(
            "SELECT run_id FROM rankings WHERE job_id = ? ORDER BY created_at DESC LIMIT 1;",
            (job_id,),
        )
        row = cursor.fetchone()
        if not row:
            return []
        return get_rankings_by_run(row["run_id"], db_path)
    finally:
        conn.close()


def delete_rankings_for_job(job_id: str, db_path: Optional[Path] = None) -> None:
    """Clears all ranking results for a specific job without deleting the job itself."""
    conn = get_connection(db_path)
    try:
        with conn:
            conn.execute("DELETE FROM rankings WHERE job_id = ?;", (job_id,))
    finally:
        conn.close()


def save_evaluation_run(run: EvaluationRun, db_path: Optional[Path] = None) -> None:
    """Saves an evaluation run record."""
    conn = get_connection(db_path)
    try:
        with conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO evaluation_runs (
                    run_id, timestamp, model_name, dataset_split, split_hash,
                    candidate_count, query_count, ndcg_at_5, ndcg_at_10, mrr,
                    precision_at_5, recall_at_10, latency_median_ms, latency_p95_ms,
                    candidates_per_second, peak_ram_mb, peak_vram_mb,
                    counterfactual_tau, shortlist_crossings
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                """,
                (
                    run.run_id,
                    run.timestamp.isoformat(),
                    run.model_name,
                    run.dataset_split,
                    run.split_hash,
                    run.candidate_count,
                    run.query_count,
                    run.ndcg_at_5,
                    run.ndcg_at_10,
                    run.mrr,
                    run.precision_at_5,
                    run.recall_at_10,
                    run.latency_median_ms,
                    run.latency_p95_ms,
                    run.candidates_per_second,
                    run.peak_ram_mb,
                    run.peak_vram_mb,
                    run.counterfactual_tau,
                    run.shortlist_crossings,
                ),
            )
    finally:
        conn.close()


def list_evaluation_runs(db_path: Optional[Path] = None) -> List[EvaluationRun]:
    """Retrieves all evaluation runs."""
    conn = get_connection(db_path)
    try:
        cursor = conn.execute("SELECT * FROM evaluation_runs ORDER BY timestamp DESC;")
        rows = cursor.fetchall()
        runs = []
        for r in rows:
            runs.append(
                EvaluationRun(
                    run_id=r["run_id"],
                    timestamp=datetime.fromisoformat(r["timestamp"]),
                    model_name=r["model_name"],
                    dataset_split=r["dataset_split"],
                    split_hash=r["split_hash"],
                    candidate_count=r["candidate_count"],
                    query_count=r["query_count"],
                    ndcg_at_5=r["ndcg_at_5"],
                    ndcg_at_10=r["ndcg_at_10"],
                    mrr=r["mrr"],
                    precision_at_5=r["precision_at_5"],
                    recall_at_10=r["recall_at_10"],
                    latency_median_ms=r["latency_median_ms"],
                    latency_p95_ms=r["latency_p95_ms"],
                    candidates_per_second=r["candidates_per_second"],
                    peak_ram_mb=r["peak_ram_mb"],
                    peak_vram_mb=r["peak_vram_mb"],
                    counterfactual_tau=r["counterfactual_tau"],
                    shortlist_crossings=r["shortlist_crossings"],
                )
            )
        return runs
    finally:
        conn.close()
