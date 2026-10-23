"""
Unit tests for the extraction module: deterministic rules, contact parsing, and mock extractor.
"""
from packages.extraction.deterministic import DeterministicExtractor
from packages.extraction.mock_extractor import MockExtractor
from packages.extraction.llm_extractor import LLMExtractor
from packages.common.schemas import ResumeProfile

SAMPLE_RESUME_TEXT = """
Jane Doe
Email: jane.doe@example.com | Phone: (555) 123-4567
GitHub: github.com/janedoe | LinkedIn: linkedin.com/in/janedoe

PROFESSIONAL SUMMARY
Senior Machine Learning Engineer with 6 years of experience in NLP, PyTorch, and Python.

TECHNICAL SKILLS
Python, PyTorch, Docker, Kubernetes, SQL, FastAPI, Git

WORK EXPERIENCE
Lead ML Engineer | AI Innovations (2021 - Present)
- Deployed transformer models on edge devices.
ML Engineer | Data Corp (2018 - 2021)
- Built NLP parsing pipelines.

EDUCATION
M.S. in Computer Science | Stanford University (2016 - 2018)
B.S. in Software Engineering | UC Berkeley (2012 - 2016)
"""

def test_extract_contact_info():
    """Verify regex extraction of email, phone, github, and linkedin."""
    contacts = DeterministicExtractor.extract_contact_info(SAMPLE_RESUME_TEXT)
    assert contacts["email"] == "jane.doe@example.com"
    assert contacts["phone"] == "(555) 123-4567"
    assert contacts["github"] == "github.com/janedoe"
    assert contacts["linkedin"] == "linkedin.com/in/janedoe"

def test_segment_sections():
    """Verify text is correctly partitioned by standard section headers."""
    sections = DeterministicExtractor.segment_sections(SAMPLE_RESUME_TEXT)
    assert "skills" in sections
    assert "experience" in sections
    assert "education" in sections
    assert "summary" in sections
    assert "PyTorch" in sections["skills"]
    assert "Stanford" in sections["education"]

def test_parse_experience_years_merging():
    """Verify non-overlapping interval sum of employment years."""
    text_with_ranges = "Job A (2018 - 2020), Job B (2020 - 2024)"
    total_years, ranges = DeterministicExtractor.parse_experience_years(text_with_ranges)
    # 2018 to 2024 is 6 years
    assert total_years == 6.0
    assert len(ranges) == 1
    assert ranges[0] == (2018, 2024)

def test_deterministic_extract_profile():
    """Verify complete ResumeProfile assembly with skills, experience, and evidence."""
    profile = DeterministicExtractor.extract_profile(
        candidate_id="cand_test_001",
        document_id="doc_test_001",
        pages_data=[{"page_number": 1, "text": SAMPLE_RESUME_TEXT}],
        combined_text=SAMPLE_RESUME_TEXT,
    )
    assert isinstance(profile, ResumeProfile)
    assert profile.candidate_id == "cand_test_001"
    assert len(profile.skills) >= 4
    assert any(s.original_text.lower() == "python" for s in profile.skills)
    assert any(s.original_text.lower() == "pytorch" for s in profile.skills)
    
    # Check that skills have evidence citations attached
    for s in profile.skills:
        assert s.evidence is not None
        assert s.evidence.document_id == "doc_test_001"
        assert s.evidence.verbatim_snippet == s.original_text

    # Check experience duration
    assert profile.total_experience_years >= 6.0

def test_mock_extractor():
    """Verify mock extractor outputs valid profile contract with extraction_method='mock'."""
    profile = MockExtractor.extract_profile(
        candidate_id="cand_mock_002",
        document_id="doc_mock_002",
        combined_text=SAMPLE_RESUME_TEXT,
    )
    assert profile.extraction_method == "mock"
    assert profile.candidate_id == "cand_mock_002"
    assert len(profile.skills) > 0

def test_llm_extractor_fallback():
    """Verify LLM extractor gracefully falls back when GGUF weights are absent."""
    extractor = LLMExtractor("non_existent_model.gguf")
    assert extractor.is_available() is False
    
    # Should fall back cleanly without raising exceptions
    profile = extractor.extract_profile("cand_fb", "doc_fb", SAMPLE_RESUME_TEXT)
    assert isinstance(profile, ResumeProfile)
    assert len(profile.skills) > 0
