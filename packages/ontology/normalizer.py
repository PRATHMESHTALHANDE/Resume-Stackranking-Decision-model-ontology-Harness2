"""
Module: packages.ontology.normalizer
Description:
    Multi-stage skill string normalizer mapping candidate and job skills to
    canonical ESCO concepts:
    Stage 1: Exact case-folded match on preferred label (confidence = 1.0)
    Stage 2: Match against alternative labels / aliases (confidence = 0.95)
    Stage 3: Token-overlap fuzzy matching (confidence = 0.85)
    Stage 4: Unmapped fallback preserving verbatim string (confidence = 0.0)

Author:
    Resume Intelligence Architect
"""
import re
from typing import Dict, Any, Optional
from packages.ontology.esco_loader import ESCOLoader

class SkillNormalizer:
    """
    Normalizes arbitrary skill strings to canonical ESCO concepts with provenance.
    """
    def __init__(self, loader: Optional[ESCOLoader] = None):
        self.loader = loader or ESCOLoader()

    def normalize(self, raw_skill: str) -> Dict[str, Any]:
        """
        Executes multi-stage matching against ESCO index.

        Args:
            raw_skill: Unprocessed skill string from resume or job description.

        Returns:
            Dict containing:
            - is_matched: bool
            - concept_uri: Optional[str]
            - canonical_label: str
            - method: 'exact' | 'alias' | 'fuzzy' | 'unmapped'
            - confidence: float
        """
        clean = raw_skill.strip()
        key = clean.lower()

        # Stage 1: Exact preferred label
        if key in self.loader.exact_map:
            uri, pref = self.loader.exact_map[key]
            return {
                "is_matched": True,
                "concept_uri": uri,
                "canonical_label": pref,
                "method": "exact",
                "confidence": 1.0,
            }

        # Stage 2: Match alternative alias
        if key in self.loader.alias_map:
            uri, pref = self.loader.alias_map[key]
            return {
                "is_matched": True,
                "concept_uri": uri,
                "canonical_label": pref,
                "method": "alias",
                "confidence": 0.95,
            }

        # Stage 3: Substring / Token fuzzy heuristic
        # If raw_skill contains an exact keyword (e.g. "Python 3.11" contains "python")
        for alias_key, (uri, pref) in self.loader.alias_map.items():
            if len(alias_key) >= 3 and (alias_key in key or key in alias_key):
                return {
                    "is_matched": True,
                    "concept_uri": uri,
                    "canonical_label": pref,
                    "method": "fuzzy",
                    "confidence": 0.85,
                }

        # Stage 4: Unmapped fallback
        return {
            "is_matched": False,
            "concept_uri": None,
            "canonical_label": clean,
            "method": "unmapped",
            "confidence": 0.0,
        }
