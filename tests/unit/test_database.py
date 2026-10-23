"""
Unit test suite verifying SQLite database operations, schema creation, and WAL mode.
"""
import pytest
import tempfile
from pathlib import Path
from packages.common.database import (
    init_db,
    save_resume_document,
    get_resume_by_hash,
    save_parsed_profile,
    delete_resume,
    get_connection,
)
from packages.common.schemas import ResumeDocument, ResumeProfile, ResumeSkill, EvidenceReference

@pytest.fixture
def temp_db_path(tmp_path):
    """Provides a temporary SQLite database path for isolated test execution."""
    db_file = tmp_path / "test_app.db"
    init_db(db_file)
    return db_file

def test_database_init_and_wal_mode(temp_db_path):
    """Verify tables exist and WAL journal mode is active."""
    conn = get_connection(temp_db_path)
    try:
        # Check WAL mode
        cursor = conn.execute("PRAGMA journal_mode;")
        mode = cursor.fetchone()[0]
        assert mode.lower() == "wal"

        # Check tables exist
        tables = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table';"
        ).fetchall()
        table_names = {r["name"] for r in tables}
        assert "resumes" in table_names
        assert "parsed_profiles" in table_names
        assert "jobs" in table_names
        assert "rankings" in table_names
        assert "evaluation_runs" in table_names
    finally:
        conn.close()

def test_resume_save_and_hash_deduplication(temp_db_path):
    """Verify document saving and instant SHA-256 deduplication query."""
    doc = ResumeDocument(
        document_id="doc_123",
        content_hash="abc_sha256_hash_value",
        source_filename="candidate_resume.pdf",
        file_type="pdf",
        page_count=2,
        file_size_bytes=102400,
        parser_status="success",
        warnings=[],
    )
    save_resume_document(doc, temp_db_path)

    # Lookup by hash
    existing = get_resume_by_hash("abc_sha256_hash_value", temp_db_path)
    assert existing is not None
    assert existing["document_id"] == "doc_123"
    assert existing["source_filename"] == "candidate_resume.pdf"
    assert existing["page_count"] == 2

    # Non-existent hash
    missing = get_resume_by_hash("non_existent_hash", temp_db_path)
    assert missing is None

def test_cascading_deletion(temp_db_path):
    """Verify deleting a resume cascades to remove the parsed candidate profile."""
    doc = ResumeDocument(
        document_id="doc_456",
        content_hash="hash_456",
        source_filename="test.pdf",
        file_type="pdf",
        page_count=1,
        file_size_bytes=50000,
    )
    save_resume_document(doc, temp_db_path)

    profile = ResumeProfile(
        candidate_id="cand_456",
        document_id="doc_456",
        total_experience_years=5.0,
        summary="Experienced engineer",
    )
    save_parsed_profile(profile, temp_db_path)

    # Verify profile exists
    conn = get_connection(temp_db_path)
    res = conn.execute("SELECT * FROM parsed_profiles WHERE candidate_id='cand_456';").fetchone()
    assert res is not None
    conn.close()

    # Delete resume and verify profile was cascaded
    delete_resume("doc_456", temp_db_path)

    conn = get_connection(temp_db_path)
    res_doc = conn.execute("SELECT * FROM resumes WHERE document_id='doc_456';").fetchone()
    res_prof = conn.execute("SELECT * FROM parsed_profiles WHERE candidate_id='cand_456';").fetchone()
    assert res_doc is None
    assert res_prof is None
    conn.close()
