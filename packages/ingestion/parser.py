"""
Module: packages.ingestion.parser
Description:
    Local document text extraction engine supporting PDF and DOCX files.
    Extracts verbatim text while strictly preserving page-level provenance,
    paragraph offsets, and section coordinates to guarantee evidence traceability.

Author:
    Resume Intelligence Architect
"""
import io
from pathlib import Path
from typing import List, Dict, Any, Tuple

try:
    import fitz  # PyMuPDF
except ImportError:
    fitz = None

try:
    from docx import Document as DocxDocument
except ImportError:
    DocxDocument = None

class DocumentParserError(Exception):
    """Custom exception raised when document parsing fails."""
    pass

class DocumentParser:
    """
    Parses PDF and DOCX resume documents and extracts text with page provenance.
    """

    @staticmethod
    def parse_pdf_bytes(pdf_bytes: bytes) -> Tuple[List[Dict[str, Any]], List[str]]:
        """
        Extracts text and page-level metadata from raw PDF bytes using PyMuPDF.

        Args:
            pdf_bytes: Binary content of the PDF.

        Returns:
            Tuple of (pages_data: list of dicts, warnings: list of strings).

        Raises:
            DocumentParserError: If PDF is encrypted, corrupted, or cannot be opened.
        """
        if fitz is None:
            raise DocumentParserError("PyMuPDF (fitz) is not installed in the environment.")

        warnings: List[str] = []
        pages_data: List[Dict[str, Any]] = []

        try:
            doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        except Exception as e:
            raise DocumentParserError(f"Corrupted or invalid PDF structure: {str(e)}") from e

        with doc:
            if doc.is_encrypted:
                raise DocumentParserError("Document is password protected and cannot be processed.")

            total_pages = len(doc)
            total_characters = 0

            for page_idx in range(total_pages):
                page = doc[page_idx]
                page_num = page_idx + 1

                # Extract plain text
                raw_text = page.get_text("text").strip()
                total_characters += len(raw_text)

                # Extract detailed text blocks with coordinates (x0, y0, x1, y1, text, block_no)
                # Useful for UI bounding box highlighting
                raw_blocks = page.get_text("blocks")
                blocks = []
                for b in raw_blocks:
                    # PyMuPDF blocks format: (x0, y0, x1, y1, "text", block_no, block_type)
                    if len(b) >= 5 and isinstance(b[4], str) and b[4].strip():
                        blocks.append({
                            "bbox": (b[0], b[1], b[2], b[3]),
                            "text": b[4].strip(),
                            "block_number": b[5] if len(b) > 5 else 0,
                        })

                pages_data.append({
                    "page_number": page_num,
                    "text": raw_text,
                    "char_count": len(raw_text),
                    "blocks": blocks,
                })

            # Check for scanned or low-density PDF (e.g. fewer than 50 chars in multi-page doc)
            if total_characters < 50:
                warnings.append("scanned_pdf_detected: Very low character count; document may be scanned.")

        return pages_data, warnings

    @staticmethod
    def parse_docx_bytes(docx_bytes: bytes) -> Tuple[List[Dict[str, Any]], List[str]]:
        """
        Extracts text from raw DOCX bytes using python-docx.

        Args:
            docx_bytes: Binary content of the DOCX file.

        Returns:
            Tuple of (pages_data: list of dicts, warnings: list of strings).
        """
        if DocxDocument is None:
            raise DocumentParserError("python-docx is not installed in the environment.")

        warnings: List[str] = []
        try:
            doc_file = io.BytesIO(docx_bytes)
            doc = DocxDocument(doc_file)
        except Exception as e:
            raise DocumentParserError(f"Corrupted or invalid DOCX document: {str(e)}") from e

        paragraphs_text = []
        for p in doc.paragraphs:
            clean_p = p.text.strip()
            if clean_p:
                paragraphs_text.append(clean_p)

        # Also extract table text cells if present in resume
        for table in doc.tables:
            for row in table.rows:
                row_cells = [cell.text.strip() for cell in row.cells if cell.text.strip()]
                if row_cells:
                    paragraphs_text.append(" | ".join(row_cells))

        full_text = "\n\n".join(paragraphs_text)
        if len(full_text.strip()) < 50:
            warnings.append("low_text_density: Document has very few text characters.")

        # DOCX files do not have explicit page delimiters; treat as a single structured page
        pages_data = [{
            "page_number": 1,
            "text": full_text,
            "char_count": len(full_text),
            "blocks": [{"bbox": (0, 0, 0, 0), "text": p, "block_number": idx} for idx, p in enumerate(paragraphs_text)],
        }]

        return pages_data, warnings

    @classmethod
    def parse_document(
        cls,
        file_bytes: bytes,
        file_type: str,
    ) -> Tuple[List[Dict[str, Any]], List[str], str]:
        """
        Unified document parsing dispatcher.

        Args:
            file_bytes: Raw binary file content.
            file_type: 'pdf' or 'docx'.

        Returns:
            Tuple of (pages_data, warnings, combined_full_text).
        """
        if file_type == "pdf":
            pages_data, warnings = cls.parse_pdf_bytes(file_bytes)
        elif file_type == "docx":
            pages_data, warnings = cls.parse_docx_bytes(file_bytes)
        else:
            raise DocumentParserError(f"Unsupported file type '{file_type}' for parsing.")

        combined_text = "\n\n--- Page Break ---\n\n".join(
            p["text"] for p in pages_data if p["text"]
        )

        return pages_data, warnings, combined_text
