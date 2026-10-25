"""
Unit tests for EnsembleSymbiosisRanker and custom WeightedScorer percentages.
"""
import pytest
from packages.common.schemas import JobDescription, JobCriterion, ResumeProfile, ResumeSkill, ExperienceItem
from packages.ranking.ensemble_ranker import EnsembleSymbiosisRanker
from packages.ranking.weighted_ranker import WeightedScorer


@pytest.fixture
def sample_job():
    return JobDescription(
        job_id="job_test_ensemble",
        requisition_id="REQ-ENG-001",
        title="Senior Python Backend Architect",
        description_text="Must have Python, FastAPI, Docker, and PostgreSQL expertise.",
        criteria=[
            JobCriterion(description="Python", is_required=True, weight=2.0),
            JobCriterion(description="FastAPI", is_required=True, weight=1.5),
            JobCriterion(description="Docker", is_required=False, weight=1.0),
            JobCriterion(description="PostgreSQL", is_required=True, weight=1.5),
        ],
        minimum_experience_years=5.0,
    )


@pytest.fixture
def sample_candidates():
    c1 = ResumeProfile(
        candidate_id="cand_expert_python",
        document_id="doc_1",
        requisition_id="REQ-ENG-001",
        skills=[
            ResumeSkill(original_text="Python"),
            ResumeSkill(original_text="FastAPI"),
            ResumeSkill(original_text="Docker"),
            ResumeSkill(original_text="PostgreSQL"),
        ],
        experience_items=[
            ExperienceItem(job_title="Lead Architect", organization="Acme", duration_months=72.0)
        ],
        total_experience_years=6.0,
    )
    c2 = ResumeProfile(
        candidate_id="cand_junior_python",
        document_id="doc_2",
        requisition_id="REQ-ENG-001",
        skills=[
            ResumeSkill(original_text="Python"),
        ],
        experience_items=[
            ExperienceItem(job_title="Junior Dev", organization="Startup", duration_months=12.0)
        ],
        total_experience_years=1.0,
    )
    return [c1, c2]


def test_ensemble_symbiosis_ranking(sample_job, sample_candidates):
    ranker = EnsembleSymbiosisRanker()
    results = ranker.rank(sample_job, sample_candidates, run_id="run_symbiosis_test")

    assert len(results) == 2
    top = results[0]
    assert top.candidate_id == "cand_expert_python"
    assert top.rank == 1
    assert top.model_name == "ensemble_symbiosis"
    assert top.score > results[1].score

    # Check component scores attribution
    comp = top.component_scores
    assert "topsis_score" in comp
    assert "laya_score" in comp
    assert "weighted_score" in comp
    assert "rrf_score" in comp
    assert "dense_score" in comp
    assert "bm25_score" in comp
    assert "model_agreement_rate" in comp
    assert comp["model_agreement_rate"] >= 0.0


def test_weighted_custom_percentage_weights(sample_job, sample_candidates):
    ranker = WeightedScorer()

    # Case A: Heavy skills weight (90% criteria, 10% experience)
    res_skills_heavy = ranker.rank(
        sample_job,
        sample_candidates,
        run_id="run_skills_heavy",
        config={"criteria_weight_pct": 90.0, "experience_weight_pct": 10.0},
    )
    top_comp_a = res_skills_heavy[0].component_scores
    assert top_comp_a["criteria_weight_pct"] == 90.0
    assert top_comp_a["experience_weight_pct"] == 10.0

    # Case B: Heavy experience weight (30% criteria, 70% experience)
    res_exp_heavy = ranker.rank(
        sample_job,
        sample_candidates,
        run_id="run_exp_heavy",
        config={"criteria_weight_pct": 30.0, "experience_weight_pct": 70.0},
    )
    top_comp_b = res_exp_heavy[0].component_scores
    assert top_comp_b["criteria_weight_pct"] == 30.0
    assert top_comp_b["experience_weight_pct"] == 70.0
