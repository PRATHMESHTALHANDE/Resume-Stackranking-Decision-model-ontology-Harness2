"""
Unit tests for packages.decision_models.explanation (ExplanationEngine).
"""

from packages.common.schemas import JobDescription, JobCriterion, ResumeProfile, ResumeSkill
from packages.decision_models.explanation import ExplanationEngine

def test_explanation_engine_decision_summaries():
    job = JobDescription(
        job_id="job_test_ai",
        title="AI Engineer",
        description_text="Seeking an AI engineer with Python and PyTorch.",
        criteria=[
            JobCriterion(criterion_id="c1", description="Python", is_required=True, weight=1.5),
            JobCriterion(criterion_id="c2", description="PyTorch", is_required=True, weight=1.2),
            JobCriterion(criterion_id="c3", description="Docker", is_required=False, weight=0.8),
        ],
        minimum_experience_years=3.0,
    )

    cand = ResumeProfile(
        candidate_id="cand_test_01",
        document_id="doc_test_01",
        skills=[
            ResumeSkill(original_text="Python"),
            ResumeSkill(original_text="PyTorch"),
            ResumeSkill(original_text="Git"),
        ],
        total_experience_years=4.5,
        uncertainty_flags=[],
    )

    # 1. Test TOPSIS
    comp_scores = {"topsis_closeness": 0.88, "dist_to_ideal": 0.12, "dist_to_anti_ideal": 0.85}
    top_summary = ExplanationEngine.generate_decision_summary(
        model_name="topsis",
        rank=1,
        score=0.88,
        component_scores=comp_scores,
        candidate=cand,
        job=job,
    )
    assert "TOPSIS Ideal-Point Analysis" in top_summary
    assert "88.0%" in top_summary

    # 2. Test Weighted
    weighted_summary = ExplanationEngine.generate_decision_summary(
        model_name="weighted",
        rank=1,
        score=0.85,
        component_scores={"req_coverage": 1.0, "pref_coverage": 0.0, "exp_score": 1.0},
        candidate=cand,
        job=job,
    )
    assert "Multi-Criteria Linear Weighted Scorer" in weighted_summary

    # 3. Test Laya
    laya_summary = ExplanationEngine.generate_decision_summary(
        model_name="laya_adapter",
        rank=1,
        score=0.90,
        component_scores={"crit_c1": 1.0, "crit_c2": 1.0, "crit_c3": 0.0},
        candidate=cand,
        job=job,
    )
    assert "LAYA Discrete Criterion Decision Adapter" in laya_summary

    # 4. Test LambdaMART
    lmart_summary = ExplanationEngine.generate_decision_summary(
        model_name="lambdamart",
        rank=1,
        score=0.76,
        component_scores={},
        candidate=cand,
        job=job,
    )
    assert "LambdaMART Learning-to-Rank Decision Forest" in lmart_summary

    # 5. Test LLM Summary
    llm_summary = ExplanationEngine.generate_llm_summary(
        rank=1,
        score=0.88,
        candidate=cand,
        job=job,
        decision_summary=top_summary,
    )
    assert "Candidate cand_test_01" in llm_summary
    assert "TOP RANK" in llm_summary
    assert "Python" in llm_summary
