"""
================================================================================
Open-Source Resume Intelligence, Ranking & Fairness Lab
FastAPI Routes: Resumes & Candidate Profiles
================================================================================
Handles document uploading, content validation, text extraction (PyMuPDF / Docx),
deterministic entity normalization, profile persistence, and data minimization.
================================================================================
"""

import uuid
from pathlib import Path
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, UploadFile, File, HTTPException, status

from packages.common.schemas import ResumeDocument, ResumeProfile
from packages.common.database import (
    save_resume_document,
    save_parsed_profile,
    list_parsed_profiles,
    get_parsed_profile,
    delete_resume,
    delete_all_resumes,
    get_resume,
    list_resumes,
)
from packages.ingestion.validator import DocumentValidator, compute_sha256
from packages.ingestion.parser import DocumentParser
from packages.extraction.deterministic import DeterministicExtractor

router = APIRouter(prefix="/resumes", tags=["Resumes & Candidates"])


@router.post("/upload", response_model=Dict[str, Any], status_code=status.HTTP_201_CREATED)
async def upload_resume(file: UploadFile = File(...)):
    """
    Ingests an uploaded PDF or DOCX file:
    1. Validates magic bytes, size limits, and extension.
    2. Parses text content using PyMuPDF or DocxParser.
    3. Deterministically extracts skills, experience, education, and verbatim evidence citations.
    4. Persists the document metadata and structured candidate profile to SQLite.
    """
    filename = file.filename or "unknown.pdf"
    content_bytes = await file.read()

    # 1. Validation
    is_valid, validation_errors = DocumentValidator.validate_file(filename, content_bytes)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "Document validation failed", "reasons": validation_errors},
        )

    # 2. Parsing text
    ext = Path(filename).suffix.lower()
    doc_id = f"doc_{uuid.uuid4().hex[:8]}"
    content_hash = compute_sha256(content_bytes)

    if ext == ".pdf":
        pages, warnings = DocumentParser.parse_pdf_bytes(content_bytes)
    else:
        pages, warnings = DocumentParser.parse_docx_bytes(content_bytes)

    full_text = "\n".join([page.get("text", "") for page in pages])

    # 3. Deterministic Extraction
    candidate_id = f"cand_{doc_id[4:]}"
    profile = DeterministicExtractor.extract_profile(
        candidate_id=candidate_id,
        document_id=doc_id,
        pages_data=pages,
        combined_text=full_text,
    )

    # 4. Persistence
    doc_record = ResumeDocument(
        document_id=doc_id,
        content_hash=content_hash,
        source_filename=filename,
        file_type=ext.lstrip("."),
        page_count=len(pages),
        file_size_bytes=len(content_bytes),
        parser_status="success",
        warnings=warnings,
    )
    save_resume_document(doc_record)
    save_parsed_profile(profile)

    return {
        "status": "success",
        "document": doc_record.model_dump(),
        "profile": profile.model_dump(),
    }


@router.post("/", response_model=ResumeProfile, status_code=status.HTTP_201_CREATED)
def create_profile(profile: ResumeProfile):
    """
    Directly persists a pre-structured ResumeProfile (e.g. for synthetic benchmarks).
    """
    save_parsed_profile(profile)
    return profile


@router.get("/", response_model=List[ResumeProfile])
def get_all_candidates():
    """
    Retrieves all candidate profiles stored in the local SQLite database.
    """
    return list_parsed_profiles()


@router.get("/{candidate_id}", response_model=ResumeProfile)
def get_candidate(candidate_id: str):
    """
    Retrieves a single candidate profile with skills, experience, and evidence citations.
    """
    profile = get_parsed_profile(candidate_id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Candidate profile '{candidate_id}' not found.",
        )
    return profile


@router.delete("/", status_code=status.HTTP_200_OK)
def remove_all_candidates():
    """
    Cascading deletion of all candidate profiles, source resumes, and ranking history.
    """
    delete_all_resumes()
    return {"status": "all_resumes_deleted"}


@router.delete("/{candidate_id}", status_code=status.HTTP_200_OK)
def remove_candidate(candidate_id: str):
    """
    Cascading deletion of a candidate profile and its source resume document.
    """
    profile = get_parsed_profile(candidate_id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Candidate profile '{candidate_id}' not found.",
        )
    delete_resume(profile.document_id)
    return {"status": "deleted", "candidate_id": candidate_id}
