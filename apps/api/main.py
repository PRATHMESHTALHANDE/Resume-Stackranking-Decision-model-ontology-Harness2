"""
================================================================================
Open-Source Resume Intelligence, Ranking & Fairness Lab
FastAPI Master Application Entry Point
================================================================================
Configures CORS, lifespan events (database auto-migration & sample seeding),
request timing middleware, advisory safety headers, and route aggregation.
================================================================================
"""

import time
import json
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from packages.common.settings import APP_NAME, APP_VERSION, ENVIRONMENT, PROJECT_ROOT
from packages.common.database import (
    init_db,
    list_parsed_profiles,
    save_parsed_profile,
    save_resume_document,
    list_jobs,
    save_job_description,
)
from packages.common.schemas import (
    ResumeDocument,
    ResumeProfile,
    ResumeSkill,
    ExperienceItem,
    EducationItem,
    JobDescription,
    JobCriterion,
)
from apps.api.routes.system import router as system_router
from apps.api.routes.resumes import router as resumes_router
from apps.api.routes.jobs import router as jobs_router
from apps.api.routes.rankings import router as rankings_router
from apps.api.routes.graph import router as graph_router
from apps.api.routes.evaluations import router as evaluations_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifecycle management:
    1. Initializes SQLite schema and WAL journal mode.
    2. Seeds database with synthetic benchmark candidates if empty.
    3. Seeds database with a sample JobDescription if empty.
    """
    # 1. Database initialization
    init_db()

    # 2. Seed candidates if empty
    candidates = list_parsed_profiles()
    sample_file = PROJECT_ROOT / "data" / "sample" / "sample_resumes.json"
    if not candidates and sample_file.exists():
        try:
            import hashlib
            from packages.extraction.deterministic import DeterministicExtractor
            with open(sample_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            for item in data:
                cid = item["candidate_id"]
                doc_id = f"doc_{cid}"
                text = item["text"]
                content_bytes = text.encode("utf-8")
                content_hash = hashlib.sha256(content_bytes).hexdigest()

                doc = ResumeDocument(
                    document_id=doc_id,
                    content_hash=content_hash,
                    source_filename=item.get("filename", f"{cid}.pdf"),
                    file_type="pdf",
                    page_count=1,
                    file_size_bytes=len(content_bytes),
                    parser_status="success",
                )
                save_resume_document(doc)

                profile = DeterministicExtractor.extract_profile(
                    candidate_id=cid,
                    document_id=doc_id,
                    pages_data=[{"page_number": 1, "text": text}],
                    combined_text=text,
                )
                save_parsed_profile(profile)
        except Exception as e:
            print(f"Error seeding sample resumes: {e}")

    # 3. Seed default Job Description if empty
    jobs = list_jobs()
    if not jobs:
        default_job = JobDescription(
            job_id="job_senior_python_lead",
            title="Senior Python & Distributed Systems Engineer",
            description_text=(
                "We are looking for an experienced Senior Python Engineer with deep knowledge of "
                "FastAPI, Docker, SQL database architecture, and asynchronous distributed systems. "
                "PyTorch / machine learning experience is a strong plus."
            ),
            criteria=[
                JobCriterion(description="Python", is_required=True, weight=1.5),
                JobCriterion(description="FastAPI", is_required=True, weight=1.2),
                JobCriterion(description="Docker", is_required=True, weight=1.0),
                JobCriterion(description="SQL", is_required=False, weight=0.8),
                JobCriterion(description="PyTorch", is_required=False, weight=0.7),
            ],
            minimum_experience_years=3.0,
        )
        save_job_description(default_job)

    yield


# Initialize FastAPI application
app = FastAPI(
    title=f"{APP_NAME} API",
    version=APP_VERSION,
    description=(
        "Local-first, open-source stack-ranking and fairness auditing engine for resumes. "
        "Strictly designed as an evidence-grounded human-in-the-loop review aid. "
        "Does not perform autonomous hiring or rejection decisions."
    ),
    lifespan=lifespan,
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_safety_and_timing_headers(request: Request, call_next):
    """
    Attaches human-in-the-loop advisory headers and execution latency to every HTTP response.
    """
    t0 = time.perf_counter()
    response = await call_next(request)
    duration_ms = round((time.perf_counter() - t0) * 1000.0, 2)
    response.headers["X-Response-Time-Ms"] = str(duration_ms)
    response.headers["X-Decision-Support"] = (
        "Human-in-the-loop review aid only; no autonomous hiring or rejection decisions."
    )
    return response


# Mount API routers under /api/v1
app.include_router(system_router, prefix="/api/v1")
app.include_router(resumes_router, prefix="/api/v1")
app.include_router(jobs_router, prefix="/api/v1")
app.include_router(rankings_router, prefix="/api/v1")
app.include_router(graph_router, prefix="/api/v1")
app.include_router(evaluations_router, prefix="/api/v1")


@app.get("/")
def root_index():
    """Root entry point providing service metadata and documentation links."""
    return {
        "service": APP_NAME,
        "version": APP_VERSION,
        "environment": ENVIRONMENT,
        "docs_url": "/docs",
        "redoc_url": "/redoc",
        "advisory": (
            "HUMAN-IN-THE-LOOP ADVISORY: This tool is an evidence-analysis NLP system. "
            "It is not a substitute for human hiring decisions or unbiased clinical review."
        ),
    }
