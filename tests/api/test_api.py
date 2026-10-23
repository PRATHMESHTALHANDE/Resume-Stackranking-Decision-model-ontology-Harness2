"""
================================================================================
Open-Source Resume Intelligence, Ranking & Fairness Lab
FastAPI Test Suite: End-to-End API Routes
================================================================================
Tests system health, resume ingestion, job criteria specification,
multi-model stack ranking, Cytoscape graph export, and fairness audits.
================================================================================
"""

import pytest
from fastapi.testclient import TestClient
from apps.api.main import app


@pytest.fixture(scope="module")
def client():
    """Context manager to ensure lifespan startup (database init & seed) runs."""
    with TestClient(app) as test_client:
        yield test_client


def test_root_endpoint(client):
    """Verify root index and mandatory advisory headers."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "service" in data
    assert "advisory" in data
    assert "X-Decision-Support" in response.headers
    assert "X-Response-Time-Ms" in response.headers


def test_system_health(client):
    """Verify /api/v1/system/health telemetry."""
    response = client.get("/api/v1/system/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ["healthy", "degraded"]
    assert "hardware" in data
    assert "database" in data


def test_jobs_crud(client):
    """Verify creating, listing, and retrieving job descriptions."""
    # List jobs (should contain seeded job)
    res_list = client.get("/api/v1/jobs/")
    assert res_list.status_code == 200
    jobs = res_list.json()
    assert len(jobs) >= 1

    # Create new job
    new_job = {
        "job_id": "job_frontend_lead",
        "title": "Lead Frontend React Architect",
        "description_text": "Seeking an expert in React, TypeScript, Tailwind CSS, and Web Vitals.",
        "criteria": [
            {"description": "React", "is_required": True, "weight": 1.5},
            {"description": "TypeScript", "is_required": True, "weight": 1.2},
            {"description": "Tailwind", "is_required": False, "weight": 0.8},
        ],
        "minimum_experience_years": 4.0,
    }
    res_create = client.post("/api/v1/jobs/", json=new_job)
    assert res_create.status_code == 201
    created = res_create.json()
    assert created["job_id"] == "job_frontend_lead"

    # Get single job
    res_get = client.get("/api/v1/jobs/job_frontend_lead")
    assert res_get.status_code == 200
    assert res_get.json()["title"] == "Lead Frontend React Architect"


def test_resumes_crud(client):
    """Verify creating and retrieving candidate profiles."""
    res_list = client.get("/api/v1/resumes/")
    assert res_list.status_code == 200
    candidates = res_list.json()
    assert len(candidates) >= 1

    # Get single candidate
    first_cid = candidates[0]["candidate_id"]
    res_single = client.get(f"/api/v1/resumes/{first_cid}")
    assert res_single.status_code == 200
    cand = res_single.json()
    assert cand["candidate_id"] == first_cid
    assert "skills" in cand


def test_ranking_execution(client):
    """Verify executing ranking with BM25 and RRF Hybrid models."""
    # 1. Rank with BM25
    payload = {"model_name": "bm25"}
    res = client.post("/api/v1/rankings/job_senior_python_lead/rank", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["model_name"] == "bm25"
    assert len(data["rankings"]) >= 1
    assert data["rankings"][0]["rank"] == 1
    assert "advisory_disclaimer" in data

    # 2. Rank with RRF Hybrid
    payload_rrf = {"model_name": "rrf_hybrid"}
    res_rrf = client.post("/api/v1/rankings/job_senior_python_lead/rank", json=payload_rrf)
    assert res_rrf.status_code == 200
    assert res_rrf.json()["model_name"] == "rrf_hybrid"

    # 3. Retrieve run by run_id
    run_id = data["run_id"]
    res_run = client.get(f"/api/v1/rankings/runs/{run_id}")
    assert res_run.status_code == 200
    assert len(res_run.json()) == len(data["rankings"])


def test_graph_visualization(client):
    """Verify Cytoscape.js graph generation."""
    res = client.get("/api/v1/graph/job_senior_python_lead/cytoscape")
    assert res.status_code == 200
    graph = res.json()
    assert "elements" in graph
    assert graph["element_count"] > 0


def test_evaluations_and_fairness(client):
    """Verify evaluation benchmark and fairness audit endpoints."""
    # 1. Run benchmark
    bench_payload = {
        "job_id": "job_senior_python_lead",
        "split_name": "api_test_split",
    }
    res_bench = client.post("/api/v1/evaluations/benchmark", json=bench_payload)
    assert res_bench.status_code == 200
    runs = res_bench.json()
    assert len(runs) >= 4

    # 2. Fairness audit
    audit_payload = {
        "job_id": "job_senior_python_lead",
        "ranker_name": "rrf_hybrid",
        "top_k": 3,
    }
    res_audit = client.post("/api/v1/evaluations/fairness/audit", json=audit_payload)
    assert res_audit.status_code == 200
    audit_data = res_audit.json()
    assert "counterfactual_stability" in audit_data
    assert "demographic_parity" in audit_data
    assert "advisory_notice" in audit_data
