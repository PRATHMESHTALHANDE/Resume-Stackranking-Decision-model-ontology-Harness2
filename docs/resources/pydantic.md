# Resource: Pydantic (v2.9+)

## 1. Overview & Purpose
**Pydantic** is the most widely-used data validation and settings management library for Python, powered by a high-performance Rust core (`pydantic-core`).

In the **Resume Intelligence, Ranking & Fairness Lab**, Pydantic serves as the canonical contract boundary:
- Validates all parsed resume records, job descriptions, and structured evidence citations.
- Enforces strict data types, non-null guarantees, and allowed value constraints (e.g. scores between 0.0 and 1.0).
- Automatically repairs or safely rejects LLM-generated JSON during structured extraction.
- Ensures zero data leakage between sensitive audit demographic data and production ranking feature vectors.

## 2. Upstream Provenance & License
- **Official Documentation:** https://docs.pydantic.dev/latest/
- **GitHub Repository:** https://github.com/pydantic/pydantic
- **License:** MIT License (Permissive open source).
- **Maintainers:** Pydantic Services Inc. / Samuel Colvin.

## 3. Local Installation & Storage Location
Pydantic is installed via `pyproject.toml` using `uv`:
```powershell
uv add pydantic pydantic-settings
```
Runs entirely in-process using compiled CPython/Rust extensions.

## 4. Hardware Footprint & Resource Impact
- **System RAM:** Negligible (< 15 MB module footprint).
- **Processing Speed:** Pydantic v2 is up to 20x faster than v1 due to the Rust validation core, validating thousands of candidate records in milliseconds.
- **VRAM:** 0 MB.

## 5. Architecture & Code Integration
Pydantic models define the core schemas in `packages/common/schemas.py`:

```python
"""
Pydantic v2 data contract definitions for evidence references and candidate records.
"""
from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
from datetime import datetime

class EvidenceReference(BaseModel):
    """
    Verbatim provenance snippet extracted directly from a source resume document.
    """
    document_id: str = Field(..., description="Foreign key of source resume")
    page_number: Optional[int] = Field(None, ge=1, description="1-indexed page number")
    section_name: Optional[str] = Field(None, description="Resume section header (e.g. Experience)")
    verbatim_snippet: str = Field(..., min_length=5, description="Exact text citation from document")
    extraction_confidence: float = Field(..., ge=0.0, le=1.0, description="Heuristic or model confidence")

class ResumeSkill(BaseModel):
    """
    Individual skill identified within candidate evidence, mapped to ESCO concepts.
    """
    original_text: str = Field(..., min_length=1, description="Raw text string in resume")
    esco_concept_uri: Optional[str] = Field(None, description="Canonical ESCO concept identifier")
    mapping_method: str = Field(..., description="exact | alias | fuzzy | semantic | unmapped")
    mapping_confidence: float = Field(..., ge=0.0, le=1.0)
    evidence: EvidenceReference = Field(..., description="Mandatory source grounding")

    @field_validator("original_text")
    @classmethod
    def clean_skill_string(cls, v: str) -> str:
        """Strip surrounding punctuation and whitespace."""
        return v.strip().title()
```

## 6. Failure Modes, Fallbacks & Edge Cases
- **Validation Errors on LLM Output:** When a local LLM returns malformed JSON or invalid types, Pydantic's `ValidationError` captures the exact field name, allowing a single-attempt targeted repair prompt before falling back to regex extraction.
- **Partial Records:** Optional fields default to `None` with explicit uncertainty flags rather than fabricating default data.
