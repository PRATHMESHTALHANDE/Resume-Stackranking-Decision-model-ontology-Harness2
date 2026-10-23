"""
================================================================================
Open-Source Resume Intelligence, Ranking & Fairness Lab
FastAPI System Routes: Health, Diagnostics & Telemetry
================================================================================
Provides endpoints for system health verification, database readiness,
hardware specs (CPU, RAM, GPU/CUDA, VRAM), and advisory safety banners.
================================================================================
"""

import os
import psutil
from fastapi import APIRouter
from typing import Dict, Any

from packages.common.settings import APP_NAME, APP_VERSION, ENVIRONMENT, DATABASE_PATH, WEIGHTS_DIR
from packages.common.database import list_parsed_profiles, list_jobs

router = APIRouter(prefix="/system", tags=["System & Diagnostics"])

@router.get("/health")
def health_check() -> Dict[str, Any]:
    """
    Returns operational health status, database connectivity, and hardware telemetry.
    """
    # 1. Database check
    db_ok = False
    candidate_count = 0
    job_count = 0
    try:
        candidate_count = len(list_parsed_profiles())
        job_count = len(list_jobs())
        db_ok = True
    except Exception as exc:
        db_error = str(exc)

    # 2. Memory & Hardware telemetry
    vm = psutil.virtual_memory()
    ram_total_gb = round(vm.total / (1024 ** 3), 2)
    ram_available_gb = round(vm.available / (1024 ** 3), 2)

    # 3. PyTorch / CUDA detection (safely guarded)
    cuda_available = False
    device_name = "CPU Only"
    vram_total_mb = 0.0
    try:
        import torch
        cuda_available = torch.cuda.is_available()
        if cuda_available:
            device_name = torch.cuda.get_device_name(0)
            vram_total_mb = round(torch.cuda.get_device_properties(0).total_memory / (1024 ** 2), 1)
    except (ImportError, OSError, Exception):
        pass

    return {
        "status": "healthy" if db_ok else "degraded",
        "app_name": APP_NAME,
        "version": APP_VERSION,
        "environment": ENVIRONMENT,
        "advisory_disclaimer": (
            "HUMAN-IN-THE-LOOP ADVISORY: This tool is a decision-support and audit system. "
            "It does not make autonomous employment or rejection decisions."
        ),
        "database": {
            "status": "connected" if db_ok else "disconnected",
            "path": str(DATABASE_PATH),
            "total_candidates": candidate_count,
            "total_jobs": job_count,
        },
        "hardware": {
            "cpu_cores": psutil.cpu_count(logical=True),
            "ram_total_gb": ram_total_gb,
            "ram_available_gb": ram_available_gb,
            "cuda_available": cuda_available,
            "gpu_device": device_name,
            "vram_total_mb": vram_total_mb,
        },
        "storage": {
            "weights_dir": str(WEIGHTS_DIR),
            "weights_dir_exists": WEIGHTS_DIR.exists(),
        },
    }
