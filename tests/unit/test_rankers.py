"""
Unit test suite for the ranking and decision model engines:
- BM25
- Dense Vector Retrieval (MiniLM)
- RRF Hybrid Fusion
- Weighted Criterion Scorer
- TOPSIS Multi-Criteria Decision Model
- LightGBM LambdaMART
- Laya Decision Adapter
"""
import pytest
import numpy as np
from packages.common.schemas import JobDescription, JobCriterion, ResumeProfile, ResumeSkill, EvidenceReference
from packages.ranking.bm25_ranker import BM25Ranker
from packages.ranking.dense_ranker import DenseRanker
from packages.ranking.rrf_ranker import RRFRanker
from packages.ranking.weighted_ranker import WeightedScorer
from packages.ranking.topsis_ranker import TOPSISRanker
from packages.ranking.lambdamart_ranker import LambdaMARTRanker
from packages.decision_models.laya_adapter import LayaDecisionAdapter

# ==============================================================================
# Test Fixtures: Query and Candidate Pool
# ==============================================================================
@pytest.fixture
def sample_job():
    """Sample job description for Senior Python & PyTorch Engineer."""
    return JobDescription(
        job_id="job_test_ml",
        title="Senior Python & PyTorch Engineer",
        description_text="We need an expert in Python, PyTorch, Docker, and NLP.",
        criteria=[
            JobCriterion(criterion_id="c1", description="Python", is_required=True, weight=1.5),
            JobCriterion(criterion_id="c2", description="PyTorch", is_required=True, weight=1.5),
            JobCriterion(criterion_id="c3", description="Docker", is_required=False, weight=1.0),
        ],
        minimum_experience_years=4.0,
    )

@pytest.fixture
def candidate_pool():
    """Three candidates with distinct qualification levels."""
    ev1 = EvidenceReference(document_id="d1", verbatim_snippet="6 years of Python and PyTorch experience.")
    ev2 = EvidenceReference(document_id="d2", verbatim_snippet="Python developer with Docker skills.")
    ev3 = EvidenceReference(document_id="d3", verbatim_snippet="Frontend JavaScript and CSS developer.")

    c1 = ResumeProfile(
        candidate_id="cand_strong_ml",
        document_id="d1",
        skills=[
            ResumeSkill(original_text="Python", evidence=ev1),
            ResumeSkill(original_text="PyTorch", evidence=ev1),
            ResumeSkill(original_text="Docker", evidence=ev1),
        ],
        total_experience_years=6.0,
        summary="Senior ML Engineer",
    )
    c2 = ResumeProfile(
        candidate_id="cand_mid_backend",
        document_id="d2",
        skills=[
            ResumeSkill(original_text="Python", evidence=ev2),
            ResumeSkill(original_text="Docker", evidence=ev2),
        ],
        total_experience_years=3.0,
        summary="Backend Developer",
    )
    c3 = ResumeProfile(
        candidate_id="cand_frontend_unrelated",
        document_id="d3",
        skills=[
            ResumeSkill(original_text="JavaScript", evidence=ev3),
            ResumeSkill(original_text="CSS", evidence=ev3),
        ],
        total_experience_years=2.0,
        summary="Web Developer",
    )
    return [c1, c2, c3]

# ==============================================================================
# Ranker Tests
# ==============================================================================
def test_bm25_ranking(sample_job, candidate_pool):
    """Verify BM25 ranks strong ML candidate highest due to term overlap."""
    ranker = BM25Ranker()
    results = ranker.rank(sample_job, candidate_pool, run_id="run_bm25_test")

    assert len(results) == 3
    assert results[0].candidate_id == "cand_strong_ml"
    assert results[0].rank == 1
    assert results[0].score >= results[1].score

def test_dense_vector_ranking(sample_job, candidate_pool):
    """Verify DenseRanker computes valid cosine similarity."""
    ranker = DenseRanker()
    results = ranker.rank(sample_job, candidate_pool, run_id="run_dense_test")

    assert len(results) == 3
    assert 0.0 <= results[0].score <= 1.0
    assert results[0].rank == 1

def test_rrf_hybrid_fusion(sample_job, candidate_pool):
    """Verify RRF fusion merges lexical and dense rankings."""
    rrf = RRFRanker(k=60)
    results = rrf.rank(sample_job, candidate_pool, run_id="run_rrf_test")

    assert len(results) == 3
    assert results[0].model_name == "rrf_hybrid"
    assert "bm25_rank" in results[0].component_scores
    assert "dense_rank" in results[0].component_scores
    assert results[0].candidate_id == "cand_strong_ml"

def test_weighted_scoring(sample_job, candidate_pool):
    """Verify WeightedScorer computes criterion sum and catches missing criteria."""
    scorer = WeightedScorer()
    results = scorer.rank(sample_job, candidate_pool, run_id="run_weighted_test")

    assert len(results) == 3
    assert results[0].candidate_id == "cand_strong_ml"
    
    # Unrelated candidate should have missing required criteria warnings
    c3_res = next(r for r in results if r.candidate_id == "cand_frontend_unrelated")
    assert any("missing_required" in m for m in c3_res.uncertainty_markers)

def test_topsis_mathematical_ranking(sample_job, candidate_pool):
    """Verify TOPSIS computes relative closeness to ideal solution."""
    topsis = TOPSISRanker()
    results = topsis.rank(sample_job, candidate_pool, run_id="run_topsis_test")

    assert len(results) == 3
    assert results[0].candidate_id == "cand_strong_ml"
    # Relative closeness must be in [0.0, 1.0]
    for r in results:
        assert 0.0 <= r.score <= 1.0
        assert "topsis_closeness" in r.component_scores

def test_lambdamart_untrained_fallback(sample_job, candidate_pool):
    """Verify LambdaMART gracefully uses TOPSIS fallback when untrained."""
    lmart = LambdaMARTRanker("non_existent_lambdamart.txt")
    results = lmart.rank(sample_job, candidate_pool, run_id="run_lmart_test")

    assert len(results) == 3
    assert "fallback: topsis" in results[0].model_name

def test_laya_decision_adapter(sample_job, candidate_pool):
    """Verify Laya decision adapter evaluates criteria and ranks candidates."""
    adapter = LayaDecisionAdapter(use_mock=True)
    decision = adapter.evaluate_criterion("Python", "6 years of Python experience")
    assert decision["decision"] in ["match", "partial", "no_match"]

    results = adapter.rank(sample_job, candidate_pool, run_id="run_laya_test")
    assert len(results) == 3
    assert results[0].candidate_id == "cand_strong_ml"
