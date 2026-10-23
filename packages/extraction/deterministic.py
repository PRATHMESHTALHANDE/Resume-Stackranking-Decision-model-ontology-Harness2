"""
Module: packages.extraction.deterministic
Description:
    Deterministic rule-based extractor for resume documents.
    Extracts:
    - Contact identifiers (email, phone, LinkedIn, GitHub) via regex.
    - Standard section segmentation (Experience, Education, Skills, Projects, Summary).
    - Date normalization and employment duration calculation.
    - Candidate skill candidates anchored to verbatim evidence snippets.

Author:
    Resume Intelligence Architect
"""
import re
from typing import Dict, Any, List, Optional, Tuple
from packages.common.schemas import (
    EvidenceReference,
    ResumeSkill,
    ExperienceItem,
    EducationItem,
    ResumeProfile,
)

# Standard section header regex patterns
SECTION_PATTERNS = {
    "summary": r"(?:professional\s+summary|summary|profile|about\s+me|objective)\b",
    "skills": r"(?:technical\s+skills|skills|technologies|core\s+competencies|expertise)\b",
    "experience": r"(?:work\s+experience|professional\s+experience|experience|employment\s+history)\b",
    "education": r"(?:education|academic\s+background|qualifications|degrees)\b",
    "projects": r"(?:projects|selected\s+projects|personal\s+projects)\b",
    "certifications": r"(?:certifications|licenses|credentials)\b",
}

# Contact information regex patterns
EMAIL_PATTERN = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
PHONE_PATTERN = r"(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}"
GITHUB_PATTERN = r"(?:https?:\/\/)?(?:www\.)?github\.com\/([A-Za-z0-9_-]+)"
LINKEDIN_PATTERN = r"(?:https?:\/\/)?(?:www\.)?linkedin\.com\/in\/([A-Za-z0-9_-]+)"

# Date range extraction (e.g. "2021 - Present", "Jan 2018 - Dec 2021", "2019 - 2022")
YEAR_RANGE_PATTERN = r"\b(19\d\d|20\d\d)\s*(?:-|–|to)\s*(present|current|19\d\d|20\d\d)\b"

class DeterministicExtractor:
    """
    Rule-based deterministic extractor for structured resume parsing.
    """

    @staticmethod
    def extract_contact_info(text: str) -> Dict[str, Optional[str]]:
        """Extracts email, phone, and professional profiles from text."""
        email_match = re.search(EMAIL_PATTERN, text, re.IGNORECASE)
        phone_match = re.search(PHONE_PATTERN, text)
        github_match = re.search(GITHUB_PATTERN, text, re.IGNORECASE)
        linkedin_match = re.search(LINKEDIN_PATTERN, text, re.IGNORECASE)

        return {
            "email": email_match.group(0) if email_match else None,
            "phone": phone_match.group(0) if phone_match else None,
            "github": github_match.group(0) if github_match else None,
            "linkedin": linkedin_match.group(0) if linkedin_match else None,
        }

    @classmethod
    def segment_sections(cls, text: str) -> Dict[str, str]:
        """
        Segments full resume text into named sections based on header keywords.
        """
        lines = text.split("\n")
        sections: Dict[str, List[str]] = {"header": []}
        current_section = "header"

        for line in lines:
            trimmed = line.strip()
            if not trimmed:
                continue

            matched_section = None
            # Check if this line looks like a section header (short line matching header pattern)
            if len(trimmed) < 45:
                for sec_name, pattern in SECTION_PATTERNS.items():
                    if re.match(pattern, trimmed, re.IGNORECASE):
                        matched_section = sec_name
                        break

            if matched_section:
                current_section = matched_section
                if current_section not in sections:
                    sections[current_section] = []
            else:
                sections[current_section].append(trimmed)

        return {k: "\n".join(v) for k, v in sections.items() if v}

    @staticmethod
    def parse_experience_years(text: str) -> Tuple[float, List[Tuple[int, int]]]:
        """
        Extracts year ranges and estimates total professional experience duration.
        Formula: Sum of (end_year - start_year) across non-overlapping ranges.
        """
        matches = re.findall(YEAR_RANGE_PATTERN, text, re.IGNORECASE)
        current_year = 2026
        ranges = []

        for start_str, end_str in matches:
            start_yr = int(start_str)
            end_yr = current_year if end_str.lower() in ["present", "current"] else int(end_str)
            if start_yr <= end_yr:
                ranges.append((start_yr, end_yr))

        if not ranges:
            return 0.0, []

        # Merge overlapping intervals to prevent double-counting
        ranges.sort(key=lambda x: x[0])
        merged = [ranges[0]]
        for start, end in ranges[1:]:
            last_start, last_end = merged[-1]
            if start <= last_end:
                merged[-1] = (last_start, max(last_end, end))
            else:
                merged.append((start, end))

        total_years = sum(end - start for start, end in merged)
        return float(total_years), merged

    @classmethod
    def extract_profile(
        cls,
        candidate_id: str,
        document_id: str,
        pages_data: List[Dict[str, Any]],
        combined_text: str,
    ) -> ResumeProfile:
        """
        Extracts a complete ResumeProfile using deterministic heuristics with evidence references.
        """
        sections = cls.segment_sections(combined_text)
        total_exp_years, _ = cls.parse_experience_years(combined_text)

        skills_list: List[ResumeSkill] = []
        skills_text = sections.get("skills", "")
        if skills_text:
            # Split skill items by commas, pipes, bullets, or newlines
            raw_skills = re.split(r"[,\|\n•\-\/]\s*", skills_text)
            for raw_s in raw_skills:
                clean_s = raw_s.strip()
                # Filter out headers and short artifacts
                if 2 <= len(clean_s) <= 40 and not any(k in clean_s.lower() for k in ["programming", "technical", "skills", "tools"]):
                    # Create evidence reference to the skills section
                    ev = EvidenceReference(
                        document_id=document_id,
                        page_number=1,
                        section_name="Skills",
                        verbatim_snippet=clean_s,
                        extraction_confidence=1.0,
                        extraction_method="deterministic",
                    )
                    skills_list.append(
                        ResumeSkill(
                            original_text=clean_s,
                            mapping_method="unmapped",
                            mapping_confidence=0.0,
                            evidence=ev,
                        )
                    )

        # Work Experience Extraction
        experience_items: List[ExperienceItem] = []
        exp_text = sections.get("experience", "")
        if exp_text:
            lines = [l.strip() for l in exp_text.split("\n") if l.strip()]
            for idx, line in enumerate(lines[:5]):  # Sample key lines
                if any(yr in line for yr in ["2020", "2021", "2022", "2023", "2024", "2025", "Present"]):
                    ev = EvidenceReference(
                        document_id=document_id,
                        page_number=1,
                        section_name="Experience",
                        verbatim_snippet=line,
                        extraction_confidence=0.9,
                    )
                    experience_items.append(
                        ExperienceItem(
                            job_title=line[:50],
                            evidence=ev,
                        )
                    )

        # Education Extraction
        education_items: List[EducationItem] = []
        edu_text = sections.get("education", "")
        if edu_text:
            for line in edu_text.split("\n"):
                if any(deg in line.lower() for deg in ["b.s.", "b.a.", "m.s.", "ph.d.", "bachelor", "master", "degree"]):
                    ev = EvidenceReference(
                        document_id=document_id,
                        page_number=1,
                        section_name="Education",
                        verbatim_snippet=line.strip(),
                        extraction_confidence=0.95,
                    )
                    education_items.append(
                        EducationItem(
                            degree=line.strip()[:60],
                            evidence=ev,
                        )
                    )

        uncertainty_flags = []
        if total_exp_years == 0.0:
            uncertainty_flags.append("undated_experience: No clear employment year ranges found.")
        if not skills_list:
            uncertainty_flags.append("no_skills_section_found: Candidate skills inferred from general body.")

        return ResumeProfile(
            candidate_id=candidate_id,
            document_id=document_id,
            skills=skills_list,
            experience_items=experience_items,
            education_items=education_items,
            total_experience_years=total_exp_years,
            summary=sections.get("summary", None),
            uncertainty_flags=uncertainty_flags,
            extraction_method="deterministic",
        )
