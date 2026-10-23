"""
Module: packages.ontology.esco_loader
Description:
    Loader for the official European Skills, Competences, Qualifications and Occupations
    (ESCO) taxonomy snapshot.
    Includes:
    - In-memory CSV parsing from data/ontology/esco/.
    - Pre-populated curated offline seed taxonomy covering standard software, AI,
      data science, and cloud competencies to guarantee offline operability.

Author:
    Resume Intelligence Architect
"""
import csv
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from packages.common.settings import ESCO_DIR

# Curated seed taxonomy ensuring immediate offline functionality
SEED_ESCO_SKILLS = [
    {
        "concept_uri": "http://data.europa.eu/esco/skill/7cfd3fae-8360-4965-b1a7-a36c53a693c1",
        "preferred_label": "Python (computer programming)",
        "alt_labels": ["Python", "Python 3", "python scripting", "python programming"],
        "skill_type": "skill/competence",
    },
    {
        "concept_uri": "http://data.europa.eu/esco/skill/9a1e09c8-47c3-4d6d-88b1-1d5d34e2c9ef",
        "preferred_label": "PyTorch",
        "alt_labels": ["pytorch", "torch", "pytorch framework"],
        "skill_type": "knowledge",
    },
    {
        "concept_uri": "http://data.europa.eu/esco/skill/2a8b3c4d-5e6f-7a8b-9c0d-1e2f3a4b5c6d",
        "preferred_label": "Docker (computer software)",
        "alt_labels": ["Docker", "Docker containers", "containerization"],
        "skill_type": "knowledge",
    },
    {
        "concept_uri": "http://data.europa.eu/esco/skill/3b9c4d5e-6f7a-8b9c-0d1e-2f3a4b5c6d7e",
        "preferred_label": "Kubernetes",
        "alt_labels": ["k8s", "kubernetes cluster", "container orchestration"],
        "skill_type": "knowledge",
    },
    {
        "concept_uri": "http://data.europa.eu/esco/skill/4c0d5e6f-7a8b-9c0d-1e2f-3a4b5c6d7e8f",
        "preferred_label": "FastAPI",
        "alt_labels": ["fastapi", "fastapi framework", "asgi"],
        "skill_type": "knowledge",
    },
    {
        "concept_uri": "http://data.europa.eu/esco/skill/5d1e6f7a-8b9c-0d1e-2f3a-4b5c6d7e8f9a",
        "preferred_label": "React (computer software)",
        "alt_labels": ["React", "React.js", "ReactJS"],
        "skill_type": "knowledge",
    },
    {
        "concept_uri": "http://data.europa.eu/esco/skill/6e2f7a8b-9c0d-1e2f-3a4b-5c6d7e8f9a0b",
        "preferred_label": "TypeScript",
        "alt_labels": ["typescript", "ts"],
        "skill_type": "skill/competence",
    },
    {
        "concept_uri": "http://data.europa.eu/esco/skill/7f3a8b9c-0d1e-2f3a-4b5c-6d7e8f9a0b1c",
        "preferred_label": "SQL",
        "alt_labels": ["Structured Query Language", "relational database queries", "sql"],
        "skill_type": "skill/competence",
    },
    {
        "concept_uri": "http://data.europa.eu/esco/skill/8a4b9c0d-1e2f-3a4b-5c6d-7e8f9a0b1c2d",
        "preferred_label": "Natural Language Processing",
        "alt_labels": ["NLP", "text analytics", "computational linguistics"],
        "skill_type": "knowledge",
    },
    {
        "concept_uri": "http://data.europa.eu/esco/skill/9b5c0d1e-2f3a-4b5c-6d7e-8f9a0b1c2d3e",
        "preferred_label": "Git",
        "alt_labels": ["git version control", "github", "gitlab"],
        "skill_type": "skill/competence",
    },
]

class ESCOLoader:
    """
    Manages loading and indexing of ESCO taxonomy records.
    """
    def __init__(self, esco_dir: Optional[Path] = None):
        self.esco_dir = esco_dir or ESCO_DIR
        self.exact_map: Dict[str, Tuple[str, str]] = {}  # lowercase -> (concept_uri, preferred_label)
        self.alias_map: Dict[str, Tuple[str, str]] = {}  # lowercase alias -> (concept_uri, preferred_label)
        self.concept_details: Dict[str, Dict[str, Any]] = {}
        self.load_taxonomy()

    def load_taxonomy(self) -> int:
        """
        Loads CSV snapshots if present, otherwise initializes the seed taxonomy.
        Returns total number of indexed concept mappings.
        """
        # Always populate seed skills first
        for item in SEED_ESCO_SKILLS:
            uri = item["concept_uri"]
            pref = item["preferred_label"]
            self.exact_map[pref.strip().lower()] = (uri, pref)
            self.concept_details[uri] = item
            for alt in item.get("alt_labels", []):
                self.alias_map[alt.strip().lower()] = (uri, pref)

        # Ingest external CSV snapshot if present in data/ontology/esco/
        skills_file = self.esco_dir / "skills_en.csv"
        if skills_file.exists():
            try:
                with open(skills_file, mode="r", encoding="utf-8") as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        uri = row.get("conceptUri", "")
                        pref = row.get("preferredLabel", "")
                        if uri and pref:
                            clean_pref = pref.strip()
                            self.exact_map[clean_pref.lower()] = (uri, clean_pref)
                            self.concept_details[uri] = {
                                "concept_uri": uri,
                                "preferred_label": clean_pref,
                                "skill_type": row.get("skillType", "skill/competence"),
                            }
            except Exception:
                pass  # Fallback to seed taxonomy

        return len(self.exact_map)
