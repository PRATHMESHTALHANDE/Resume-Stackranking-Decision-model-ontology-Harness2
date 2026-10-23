"""
Module: packages.extraction.mock_extractor
Description:
    Deterministic offline mock extractor used for testing, CI pipelines, and demo
    modes when local GGUF models are not yet downloaded. Generates valid ResumeProfile
    contracts grounded in source document text.

Author:
    Resume Intelligence Architect
"""
from typing import Dict, Any, List
from packages.common.schemas import (
    ResumeProfile,
    ResumeSkill,
    ExperienceItem,
    EducationItem,
    EvidenceReference,
)
from packages.extraction.deterministic import DeterministicExtractor

class MockExtractor:
    """
    Offline mock extractor generating verified Pydantic contracts from text.
    """

    @classmethod
    def extract_profile(
        cls,
        candidate_id: str,
        document_id: str,
        combined_text: str,
    ) -> ResumeProfile:
        """
        Uses deterministic rule-based segmentation to produce a valid profile.
        """
        # Run deterministic extractor as foundation
        profile = DeterministicExtractor.extract_profile(
            candidate_id=candidate_id,
            document_id=document_id,
            pages_data=[{"page_number": 1, "text": combined_text}],
            combined_text=combined_text,
        )

        # Mark extraction method explicitly as mock
        return profile.model_copy(update={"extraction_method": "mock"})
