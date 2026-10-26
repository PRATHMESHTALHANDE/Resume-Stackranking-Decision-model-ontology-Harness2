"""
Unit tests for LayaDecisionAdapter (convaiinnovations/laya integration & resilient fallback).
"""
import pytest
from packages.common.schemas import JobDescription, JobCriterion, ResumeProfile, ResumeSkill, EvidenceReference
from packages.decision_models.laya_adapter import LayaDecisionAdapter


@pytest.fixture
def sample_job():
    return JobDescription(
        job_id="job_test_laya",
        title="Senior Python & FastAPI Engineer",
        description_text="Must have strong Python, FastAPI, and PostgreSQL skills.",
        criteria=[
            JobCriterion(criterion_id="c1", description="Python", is_required=True, weight=2.0),
            JobCriterion(criterion_id="c2", description="FastAPI", is_required=True, weight=1.5),
            JobCriterion(criterion_id="c3", description="PostgreSQL", is_required=False, weight=1.0),
        ],
        minimum_experience_years=3.0,
    )


@pytest.fixture
def sample_candidates():
    c1 = ResumeProfile(
        candidate_id="cand_strong",
        document_id="doc_1",
        skills=[
            ResumeSkill(
                original_text="Python",
                evidence=EvidenceReference(
                    document_id="doc_1",
                    verbatim_snippet="Over 6 years of Python development and microservices architecture.",
                    page_number=1,
                    extraction_confidence=0.95,
                ),
            ),
            ResumeSkill(
                original_text="FastAPI",
                evidence=EvidenceReference(
                    document_id="doc_1",
                    verbatim_snippet="Built high-throughput REST APIs using FastAPI and Pydantic.",
                    page_number=1,
                    extraction_confidence=0.90,
                ),
            ),
            ResumeSkill(
                original_text="PostgreSQL",
                evidence=EvidenceReference(
                    document_id="doc_1",
                    verbatim_snippet="Designed relational schemas in PostgreSQL.",
                    page_number=2,
                    extraction_confidence=0.88,
                ),
            ),
        ],
        total_experience_years=6.0,
    )

    c2 = ResumeProfile(
        candidate_id="cand_partial",
        document_id="doc_2",
        skills=[
            ResumeSkill(
                original_text="Python",
                evidence=EvidenceReference(
                    document_id="doc_2",
                    verbatim_snippet="Basic scripting with Python for data pipelines.",
                    page_number=1,
                    extraction_confidence=0.80,
                ),
            ),
        ],
        total_experience_years=2.0,
    )

    c3 = ResumeProfile(
        candidate_id="cand_none",
        document_id="doc_3",
        skills=[
            ResumeSkill(
                original_text="Java",
                evidence=EvidenceReference(
                    document_id="doc_3",
                    verbatim_snippet="5 years developing Spring Boot applications in Java.",
                    page_number=1,
                    extraction_confidence=0.90,
                ),
            ),
        ],
        total_experience_years=5.0,
    )

    return [c1, c2, c3]


def test_laya_adapter_mock_mode(sample_job, sample_candidates):
    """Verify deterministic rubric in LayaDecisionAdapter."""
    adapter = LayaDecisionAdapter(use_mock=True)
    results = adapter.rank(sample_job, sample_candidates, run_id="run_test_mock")

    assert len(results) == 3
    # Candidate 1 should rank #1 because they match all requirements
    assert results[0].candidate_id == "cand_strong"
    assert results[0].rank == 1
    assert results[0].score > results[1].score
    assert "crit_c1" in results[0].component_scores
    assert results[0].component_scores["crit_c1"] == 1.0


def test_laya_adapter_resilient_mode(sample_job, sample_candidates):
    """Verify LayaDecisionAdapter initializes with use_mock=False and produces valid rankings."""
    adapter = LayaDecisionAdapter(use_mock=False)
    results = adapter.rank(sample_job, sample_candidates, run_id="run_test_neural")

    assert len(results) == 3
    assert results[0].rank == 1
    assert 0.0 <= results[0].score <= 1.0
    assert "avg_confidence" in results[0].component_scores
    assert any("laya" in m.lower() for m in results[0].uncertainty_markers)
