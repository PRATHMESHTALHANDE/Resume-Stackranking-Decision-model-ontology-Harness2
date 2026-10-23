"""
================================================================================
Open-Source Resume Intelligence, Ranking & Fairness Lab
Benchmark Execution Script: Multi-Model Evaluation & Report Export
================================================================================
Runs BM25, Dense MiniLM, RRF Hybrid, Weighted Scorer, TOPSIS, and LAYA Adapter
over the golden benchmark candidate dataset, generating the comprehensive
baseline report at outputs/evaluation/baseline_benchmark_report.md.
================================================================================
"""

import json
from pathlib import Path
from packages.common.settings import PROJECT_ROOT, EVALUATION_OUTPUTS_DIR
from packages.common.schemas import JobDescription, JobCriterion
from packages.common.database import init_db, list_parsed_profiles, list_jobs
from packages.evaluation.harness import EvaluationHarness


def main():
    init_db()
    EVALUATION_OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)

    candidates = list_parsed_profiles()
    jobs = list_jobs()

    if not jobs or not candidates:
        print("[!] No jobs or candidates found. Please ensure database is initialized.")
        return

    job = jobs[0]
    print(f"[*] Running benchmark for Job: '{job.title}' (ID: {job.job_id})")
    print(f"[*] Candidate pool size: {len(candidates)}")

    # Ground truth relevance based on criteria overlap
    golden_relevance = {}
    job_skills = {c.description.lower() for c in job.criteria}
    for cand in candidates:
        cand_skills = {s.original_text.lower() for s in cand.skills}
        overlap = len(job_skills.intersection(cand_skills))
        golden_relevance[cand.candidate_id] = min(3.0, float(overlap))

    harness = EvaluationHarness(output_dir=EVALUATION_OUTPUTS_DIR)
    runs = harness.run_benchmark(
        job=job,
        candidates=candidates,
        golden_relevance=golden_relevance,
        split_name="golden_sample_v1",
    )

    # Save dedicated baseline benchmark report
    target_report = EVALUATION_OUTPUTS_DIR / "baseline_benchmark_report.md"
    src_report = EVALUATION_OUTPUTS_DIR / "latest_evaluation_report.md"
    if src_report.exists():
        target_report.write_text(src_report.read_text(encoding="utf-8"), encoding="utf-8")
        print(f"[+] Benchmark report successfully generated at: {target_report}")

    for r in runs:
        print(f"  - {r.model_name:<15} | nDCG@5: {r.ndcg_at_5:.3f} | MRR: {r.mrr:.3f} | Latency: {r.latency_median_ms:.1f}ms | Tau: {r.counterfactual_tau:.3f}")


if __name__ == "__main__":
    main()
