"""
================================================================================
Open-Source Resume Intelligence, Ranking & Fairness Lab
FastAPI Routes: Job Descriptions & Requirements
================================================================================
Endpoints for creating, listing, inspecting, and deleting job descriptions
with explicit required and preferred criteria.
================================================================================
"""

from typing import List
from fastapi import APIRouter, HTTPException, status

from packages.common.schemas import JobDescription
from packages.common.database import (
    save_job_description,
    list_jobs,
    get_job,
    delete_job,
)

router = APIRouter(prefix="/jobs", tags=["Job Descriptions"])


@router.post("/", response_model=JobDescription, status_code=status.HTTP_201_CREATED)
def create_job(job: JobDescription):
    """
    Creates or updates a JobDescription specification with criteria weights.
    """
    save_job_description(job)
    return job


@router.get("/", response_model=List[JobDescription])
def get_all_jobs():
    """
    Lists all job descriptions stored in the database.
    """
    return list_jobs()


@router.get("/{job_id}", response_model=JobDescription)
def get_single_job(job_id: str):
    """
    Retrieves a single JobDescription by ID.
    """
    job = get_job(job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job description '{job_id}' not found.",
        )
    return job


@router.delete("/{job_id}", status_code=status.HTTP_200_OK)
def remove_job(job_id: str):
    """
    Deletes a JobDescription and its associated ranking runs.
    """
    job = get_job(job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job description '{job_id}' not found.",
        )
    delete_job(job_id)
    return {"status": "deleted", "job_id": job_id}
