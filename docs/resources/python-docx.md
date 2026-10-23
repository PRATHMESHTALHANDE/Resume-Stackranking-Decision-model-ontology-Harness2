# Resource Specification: python-docx

## 1. Overview & Positioning
- **Name:** python-docx
- **License:** MIT License
- **Role in Project:** Native DOCX document parsing in `packages/ingestion/parser.py`.
- **Why Selected:** Pure Python parser for Microsoft Word (.docx) documents, allowing paragraph and table extraction with zero external system dependencies (no Microsoft Office or LibreOffice required).

## 2. Ingestion & Paragraph Extraction Protocol
```python
import io
from docx import Document

doc = Document(io.BytesIO(docx_bytes))
paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
```

## 3. Operational Best Practices
- Verify magic bytes (`PK\x03\x04` zip archive signature) before parsing to prevent format mismatch errors.
- Extract both paragraphs and table cells to capture formatted technical skills matrices.
