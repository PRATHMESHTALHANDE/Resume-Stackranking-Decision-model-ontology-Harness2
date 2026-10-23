"""
Unit tests for the ingestion module: parser and validator.
"""
import io
import pytest
import fitz
from docx import Document as DocxDocument

from packages.ingestion.validator import (
    sanitize_filename,
    compute_sha256,
    validate_file_metadata,
)
from packages.ingestion.parser import (
    DocumentParser,
    DocumentParserError,
)

# ==============================================================================
# Helper Fixtures: Programmatically Generating Test PDFs and DOCXs
# ==============================================================================
def create_test_pdf_bytes(text: str = "Candidate Name\nSoftware Engineer with Python and PyTorch experience.") -> bytes:
    """Creates a valid in-memory PDF document using PyMuPDF."""
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((50, 50), text)
    pdf_bytes = doc.tobytes()
    doc.close()
    return pdf_bytes

def create_test_docx_bytes(paragraphs: list[str] = None) -> bytes:
    """Creates a valid in-memory DOCX document using python-docx."""
    if paragraphs is None:
        paragraphs = ["Candidate Name", "Skills: Python, FastAPI, Docker", "Experience: 5 years in AI development."]
    doc = DocxDocument()
    for p in paragraphs:
        doc.add_paragraph(p)
    buf = io.BytesIO()
    doc.save(buf)
    return buf.getvalue()

# ==============================================================================
# 1. Validator Tests
# ==============================================================================
def test_sanitize_filename():
    """Verify directory traversal and dangerous characters are sanitized."""
    assert sanitize_filename("../../../etc/passwd") == "passwd"
    assert sanitize_filename("my resume (1).pdf") == "my resume (1).pdf"
    assert sanitize_filename("resume<script>.pdf") == "resume_script_.pdf"
    assert sanitize_filename("") == "document.bin"

def test_validate_file_metadata_valid_pdf():
    """Verify valid PDF metadata extraction and SHA-256 generation."""
    pdf_bytes = create_test_pdf_bytes("Valid resume content.")
    is_valid, err, meta = validate_file_metadata("resume.pdf", pdf_bytes, "application/pdf")
    
    assert is_valid is True
    assert err == ""
    assert meta["file_type"] == "pdf"
    assert meta["sanitized_filename"] == "resume.pdf"
    assert meta["content_hash"] == compute_sha256(pdf_bytes)

def test_validate_file_metadata_unsupported_ext():
    """Verify rejection of unsupported extensions (e.g. .exe, .txt)."""
    is_valid, err, _ = validate_file_metadata("malicious.exe", b"MZ...", "application/x-dosexec")
    assert is_valid is False
    assert "Unsupported file format" in err

def test_validate_file_metadata_empty_file():
    """Verify rejection of empty files."""
    is_valid, err, _ = validate_file_metadata("empty.pdf", b"")
    assert is_valid is False
    assert "empty" in err.lower()

def test_validate_file_metadata_fake_header():
    """Verify rejection of file with .pdf extension but invalid header bytes."""
    is_valid, err, _ = validate_file_metadata("fake.pdf", b"This is not a PDF")
    assert is_valid is False
    assert "%PDF" in err

# ==============================================================================
# 2. Parser Tests
# ==============================================================================
def test_parse_valid_pdf():
    """Verify PyMuPDF extracts text, blocks, and page provenance."""
    sample_text = "Jane Doe\nMachine Learning Engineer\nExtensive experience in NLP and Transformers."
    pdf_bytes = create_test_pdf_bytes(sample_text)
    
    pages_data, warnings, combined = DocumentParser.parse_document(pdf_bytes, "pdf")
    
    assert len(pages_data) == 1
    assert pages_data[0]["page_number"] == 1
    assert "Jane Doe" in pages_data[0]["text"]
    assert "Machine Learning Engineer" in combined
    assert len(warnings) == 0

def test_parse_valid_docx():
    """Verify python-docx extracts paragraphs and text blocks."""
    docx_bytes = create_test_docx_bytes(["Alex Smith", "Senior Backend Developer", "Expertise in FastAPI and SQLite"])
    
    pages_data, warnings, combined = DocumentParser.parse_document(docx_bytes, "docx")
    
    assert len(pages_data) == 1
    assert "Alex Smith" in combined
    assert "Senior Backend Developer" in combined

def test_parse_corrupted_pdf_error():
    """Verify corrupted PDF triggers structured DocumentParserError."""
    corrupted_bytes = b"%PDF-1.4\nCorrupted content without valid xref or trailer."
    with pytest.raises(DocumentParserError) as exc_info:
        DocumentParser.parse_pdf_bytes(corrupted_bytes)
    assert "Corrupted or invalid" in str(exc_info.value)

def test_parse_scanned_pdf_warning():
    """Verify nearly blank / scanned PDF generates scanned_pdf_detected warning."""
    blank_pdf = create_test_pdf_bytes("A")  # Only 1 character
    pages, warnings = DocumentParser.parse_pdf_bytes(blank_pdf)
    assert any("scanned_pdf_detected" in w for w in warnings)
