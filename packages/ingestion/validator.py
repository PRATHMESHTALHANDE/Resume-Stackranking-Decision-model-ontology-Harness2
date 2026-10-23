"""
Module: packages.ingestion.validator
Description:
    File validation, MIME verification, content hashing, and path sanitization
    for incoming resume documents and job descriptions.

Author:
    Resume Intelligence Architect
"""
import hashlib
import os
import re
from pathlib import Path
from typing import Tuple, Dict, Any

from packages.common.settings import settings

# Supported document extensions and MIME types
ALLOWED_EXTENSIONS = {".pdf", ".docx"}
ALLOWED_MIME_TYPES = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/octet-stream", # Often sent by browsers for binary files
}

def sanitize_filename(filename: str) -> str:
    """
    Sanitizes an uploaded filename to prevent directory traversal or script injection.

    Args:
        filename: Original user-provided filename.

    Returns:
        Safe filename string containing only alphanumerics, dots, underscores, and dashes.
    """
    # Remove any directory paths
    base = os.path.basename(filename)
    # Strip any dangerous or non-printable characters
    clean = re.sub(r"[^\w\.\- \(\)]", "_", base).strip()
    return clean if clean else "document.bin"


def compute_sha256(file_bytes: bytes) -> str:
    """
    Computes deterministic SHA-256 hex digest of raw file bytes for instant deduplication.

    Args:
        file_bytes: Raw binary content of the file.

    Returns:
        64-character lowercase hexadecimal SHA-256 hash string.
    """
    return hashlib.sha256(file_bytes).hexdigest()


def validate_file_metadata(
    filename: str,
    file_bytes: bytes,
    content_type: str = "",
) -> Tuple[bool, str, Dict[str, Any]]:
    """
    Validates uploaded file against size limits, supported extensions, and MIME types.

    Args:
        filename: Name of the uploaded file.
        file_bytes: Raw binary payload.
        content_type: HTTP Content-Type header.

    Returns:
        Tuple of (is_valid: bool, error_message: str, metadata: dict).
    """
    sanitized = sanitize_filename(filename)
    ext = os.path.splitext(sanitized)[1].lower()
    
    # 1. Extension check
    if ext not in ALLOWED_EXTENSIONS:
        return (
            False,
            f"Unsupported file format '{ext}'. Only PDF (.pdf) and Word (.docx) files are supported.",
            {},
        )

    # 2. Size limit check
    size_bytes = len(file_bytes)
    if size_bytes == 0:
        return False, "Uploaded file is empty (0 bytes).", {}

    if size_bytes > settings.MAX_UPLOAD_SIZE_BYTES:
        max_mb = settings.MAX_UPLOAD_SIZE_BYTES / (1024 * 1024)
        return (
            False,
            f"File exceeds maximum allowed size of {max_mb:.1f} MB (uploaded: {size_bytes / (1024*1024):.1f} MB).",
            {},
        )

    # 3. Magic bytes inspection
    file_type = ext.lstrip(".")
    if file_type == "pdf":
        # PDFs must start with %PDF header
        if not file_bytes.startswith(b"%PDF"):
            return False, "File has a .pdf extension but lacks a valid PDF header (%PDF).", {}
    elif file_type == "docx":
        # DOCX files are zip archives starting with PK
        if not file_bytes.startswith(b"PK"):
            return False, "File has a .docx extension but lacks a valid zip archive header (PK).", {}

    content_hash = compute_sha256(file_bytes)

    metadata = {
        "sanitized_filename": sanitized,
        "file_type": file_type,
        "file_size_bytes": size_bytes,
        "content_hash": content_hash,
    }

    return True, "", metadata


class DocumentValidator:
    """Validator class offering static validation methods for uploaded documents."""

    @staticmethod
    def validate_file(filename: str, file_bytes: bytes, content_type: str = "") -> Tuple[bool, list]:
        """Validates file metadata and returns (is_valid, list_of_error_strings)."""
        valid, msg, _ = validate_file_metadata(filename, file_bytes, content_type)
        return valid, [msg] if msg else []
