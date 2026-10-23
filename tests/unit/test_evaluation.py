"""
================================================================================
Open-Source Resume Intelligence, Ranking & Fairness Lab
Phase 7 Unit Tests: Evaluation & Fairness Harness
================================================================================
Tests information retrieval metrics (nDCG@k, MRR, Precision@k, Recall@k),
CounterfactualAuditor (identity perturbation stability & Kendall's Tau),
ParityAuditor (Four-Fifths Rule / Adverse Impact Ratio),
and end-to-end multi-ranker EvaluationHarness execution.
================================================================================
"""

import pytest
from packages.common.schemas import (
    JobDescription,
    ResumeProfile,
    ResumeSkill,
    JobCriterion,
    EvaluationRun,
)
from packages.evaluation.metrics import MetricsCalculator
from packages.fairness.counterfactual import CounterfactualAuditor
from packages.fairness.parity import ParityAuditor
from packages.evaluation.harness import EvaluationHarness
from packages.ranking.bm25_ranker import BM25Ranker


def test_ndcg_computation():
    """
    Test normalized Discounted Cumulative Gain (nDCG@k).
    A perfect ranking should yield nDCG = 1.0.
    """
    # Relevance scores in ranked order: 3, 2, 1, 0
    pred_rels = [3.0, 2.0, 1.0, 0.0]
    golden_rels = [3.0, 2.0, 1.0, 0.0]

    score_perfect = MetricsCalculator.ndcg_at_k(pred_rels, golden_rels, k=4)
    assert pytest.approx(score_perfect, 0.001) == 1.0

    # Reversed ranking should be strictly less than 1.0
    reversed_rels = [0.0, 1.0, 2.0, 3.0]
    score_reversed = MetricsCalculator.ndcg_at_k(reversed_rels, golden_rels, k=4)
    assert score_reversed < 1.0
    assert score_reversed > 0.0


def test_reciprocal_rank():
    """
    Test Mean Reciprocal Rank (MRR).
    First relevant item at rank 1 gives 1.0; at rank 2 gives 0.5.
    """
    ranked_ids = ["cand_1", "cand_2", "cand_3"]
    relevant_ids = ["cand_2", "cand_3"]

    # First relevant item is at index 1 (rank 2) -> 1 / 2 = 0.5
    rr = MetricsCalculator.reciprocal_rank(ranked_ids, relevant_ids)
    assert pytest.approx(rr, 0.001) == 0.5

    # If first item is relevant -> 1.0
    assert pytest.approx(MetricsCalculator.reciprocal_rank(["cand_2", "cand_1"], relevant_ids), 0.001) == 1.0

    # If no relevant items -> 0.0
    assert MetricsCalculator.reciprocal_rank(["cand_99"], relevant_ids) == 0.0


def test_precision_and_recall_at_k():
    """
    Test Precision@k and Recall@k.
    """
    ranked_ids = ["c1", "c2", "c3", "c4"]
    relevant_ids = ["c1", "c3", "c5"]

    # At k=2: ranked has [c1, c2]. Relevant in top 2 is {c1} (1 item).
    # Precision@2 = 1 / 2 = 0.5
    # Recall@2 = 1 / 3 = 0.3333...
    p2 = MetricsCalculator.precision_at_k(ranked_ids, relevant_ids, k=2)
    r2 = MetricsCalculator.recall_at_k(ranked_ids, relevant_ids, k=2)
    assert pytest.approx(p2, 0.01) == 0.5
    assert pytest.approx(r2, 0.01) == 0.3333


def test_resource_measurement():
    """
    Test system telemetry measurement.
    """
    res = MetricsCalculator.measure_system_resources()
    assert "ram_mb" in res
    assert res["ram_mb"] > 0
    assert "vram_mb" in res


def test_counterfactual_auditor_perturbation():
    """
    Test perturb_profile identity swapping.
    """
    profile = ResumeProfile(
        candidate_id="cand_test_1",
        document_id="doc_1",
        summary="John is an exceptional engineer. He has built scalable systems for his team.",
        skills=[ResumeSkill(original_text="Python")],
    )

    perturbed = CounterfactualAuditor.perturb_profile(profile)
    assert perturbed.candidate_id == "cand_test_1_cf"
    # John -> Jane, He -> She, his -> her
    assert "jane" in perturbed.summary.lower()
    assert "she" in perturbed.summary.lower()


def test_counterfactual_auditor_ranker_audit():
    """
    Test auditing a ranker with CounterfactualAuditor.audit_ranker.
    """
    ranker = BM25Ranker()
    job = JobDescription(
        job_id="job_dev",
        title="Senior Python Backend Engineer",
        description_text="Looking for a Python and FastAPI backend engineer with database experience.",
        criteria=[JobCriterion(description="Python", is_required=True, weight=1.0)],
    )
    candidates = [
        ResumeProfile(
            candidate_id="c1",
            document_id="d1",
            summary="John is a Senior Python Developer with 8 years of FastAPI experience.",
            skills=[ResumeSkill(original_text="Python"), ResumeSkill(original_text="FastAPI")],
        ),
        ResumeProfile(
            candidate_id="c2",
            document_id="d2",
            summary="David is a frontend engineer with React and CSS skills.",
            skills=[ResumeSkill(original_text="React"), ResumeSkill(original_text="CSS")],
        ),
    ]

    audit_res = CounterfactualAuditor.audit_ranker(ranker, job, candidates, top_k=2)
    assert "kendall_tau" in audit_res
    assert "shortlist_crossings" in audit_res
    # Stable ranking under name swap: tau should be 1.0 and crossings 0
    assert pytest.approx(audit_res["kendall_tau"], 0.01) == 1.0
    assert audit_res["shortlist_crossings"] == 0


def test_parity_auditor():
    """
    Test ParityAuditor.evaluate_shortlist_disparity with synthetic demographic groups.
    """
    # 4 candidates: 2 group_a, 2 group_b
    y_true = [1, 1, 1, 0]
    y_pred = [1, 1, 0, 0]  # Both selected are from group_a
    sensitive = ["group_a", "group_a", "group_b", "group_b"]

    disparity = ParityAuditor.evaluate_shortlist_disparity(y_true, y_pred, sensitive)
    assert "selection_rates_by_group" in disparity
    assert "demographic_parity_ratio" in disparity
    # Selection rate group_a = 1.0, group_b = 0.0 -> disparate impact ratio = 0.0
    assert pytest.approx(disparity["demographic_parity_ratio"], 0.01) == 0.0
    assert disparity["demographic_parity_ratio"] < 0.8
    assert disparity["is_statistically_constrained"] is True


def test_evaluation_harness_benchmark(tmp_path):
    """
    Test full evaluation harness execution with mock golden labels and markdown export.
    """
    harness = EvaluationHarness(output_dir=tmp_path)
    job = JobDescription(
        job_id="job_py",
        title="Python Engineer",
        description_text="Python backend developer with SQL and FastAPI skills.",
        criteria=[
            JobCriterion(description="Python", is_required=True, weight=1.0),
            JobCriterion(description="FastAPI", is_required=True, weight=1.0),
        ],
    )
    candidates = [
        ResumeProfile(
            candidate_id="c1",
            document_id="d1",
            summary="Experienced Python and FastAPI backend architect.",
            skills=[ResumeSkill(original_text="Python"), ResumeSkill(original_text="FastAPI")],
            total_experience_years=5.0,
        ),
        ResumeProfile(
            candidate_id="c2",
            document_id="d2",
            summary="Frontend engineer working with TypeScript and Vue.",
            skills=[ResumeSkill(original_text="TypeScript"), ResumeSkill(original_text="Vue")],
            total_experience_years=2.0,
        ),
    ]
    golden_relevance = {"c1": 3.0, "c2": 0.0}

    runs = harness.run_benchmark(
        job=job,
        candidates=candidates,
        golden_relevance=golden_relevance,
        split_name="test_split_v1",
    )

    assert len(runs) >= 4
    for r in runs:
        assert isinstance(r, EvaluationRun)
        assert r.dataset_split == "test_split_v1"
        assert r.ndcg_at_5 >= 0.0

    # Verify markdown report generation
    report_file = tmp_path / "latest_evaluation_report.md"
    assert report_file.exists()
    content = report_file.read_text(encoding="utf-8")
    assert "Model Evaluation & Benchmark Comparison Report" in content
    assert "bm25" in content
