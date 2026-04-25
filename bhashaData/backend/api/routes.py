from __future__ import annotations

import json
import os
import shutil
import logging
import threading
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse, RedirectResponse
from sqlalchemy.orm import Session

from backend.api.models import (
    GenerateDatasetRequest,
    GenerateDatasetResponse,
    HealthResponse,
    JobStatusResponse,
    RegisterRequest,
    LoginRequest,
    AuthResponse,
    UserResponse,
    JobResponse,
)
from backend.api.auth import (
    hash_password,
    verify_password,
    create_access_token,
    get_current_user,
    get_optional_user,
)
from backend.database.db import get_db
from backend.database.models import (
    create_job,
    get_job,
    delete_job,
    cancel_job,
    create_user,
    get_user_by_email,
    get_user_by_id,
    get_jobs_by_user,
)
from backend.workers.celery_app import celery_app
from backend.workers.dataset_job import generate_dataset_task
from backend.workers.status import get_job_status, delete_job_status


router = APIRouter()
logger = logging.getLogger(__name__)

SUPPORTED_DOWNLOAD_FORMATS = {
    "csv": "csv",
    "json": "json",
    "excel": "xlsx",
    "parquet": "parquet",
    "huggingface": "huggingface",
}
SUPPORTED_STATUSES = {
    "queued",
    "scraping",
    "cleaning",
    "labeling",
    "quality_check",
    "exporting",
    "complete",
    "failed",
    "cancelled",
}

RUNNING_STATUSES = {"queued", "scraping", "cleaning", "labeling", "quality_check", "exporting"}


def _run_dataset_job_fallback(job_id: str, request_payload: dict) -> None:
    try:
        generate_dataset_task.run(job_id, request_payload)
    except Exception as exc:  # noqa: BLE001
        logger.exception("Fallback dataset job failed for %s: %s", job_id, exc)


def _build_per_language_status(request_payload: dict[str, object]) -> dict[str, dict[str, object]]:
    return {
        str(language_code): {
            "step": "queued",
            "rows_collected": 0,
            "rows_clean": 0,
            "rows_labeled": 0,
        }
        for language_code in (request_payload.get("languages") or [])
    }


def _fallback_progress_percent(status: str) -> int:
    stage_progress = {
        "queued": 0,
        "scraping": 15,
        "cleaning": 35,
        "labeling": 60,
        "quality_check": 80,
        "exporting": 92,
        "complete": 100,
        "failed": 100,
        "cancelled": 100,
    }
    return stage_progress.get(status, 0)


def _job_to_status_response(job) -> JobStatusResponse:
    request_payload = json.loads(job.request_payload or "{}")
    status = job.status if job.status in SUPPORTED_STATUSES else "queued"
    current_step_map = {
        "queued": "Queued",
        "scraping": "Scraping",
        "cleaning": "Cleaning",
        "labeling": "Labeling",
        "quality_check": "Quality check",
        "exporting": "Exporting",
        "complete": "Complete",
        "failed": "Failed",
        "cancelled": "Cancelled",
    }
    eta_seconds = None if status in {"complete", "failed", "cancelled"} else int(job.estimated_minutes * 60)
    per_language_status = _build_per_language_status(request_payload)

    if status != "queued":
        stage_for_languages = "failed" if status in {"failed", "cancelled"} else status
        for language_status in per_language_status.values():
            language_status["step"] = stage_for_languages

    return JobStatusResponse(
        job_id=job.id,
        status=status,
        progress_percent=_fallback_progress_percent(status),
        current_step=current_step_map.get(status, "Queued"),
        per_language_status=per_language_status,
        eta_seconds=eta_seconds,
        error_message=job.error_message if status in {"failed", "cancelled"} else None,
        created_at=job.created_at.isoformat(),
        updated_at=job.updated_at.isoformat(),
    )


def _redis_status_to_response(status_dict: dict) -> JobStatusResponse:
    status = status_dict.get("status", "queued")
    return JobStatusResponse(
        job_id=str(status_dict.get("job_id", "")),
        status=status,
        progress_percent=int(status_dict.get("progress_percent", 0)),
        current_step=str(status_dict.get("current_step", "Queued")),
        per_language_status=status_dict.get("per_language_status", {}),
        eta_seconds=status_dict.get("eta_seconds"),
        error_message=status_dict.get("error_message"),
        created_at=str(status_dict.get("created_at", status_dict.get("updated_at", ""))),
        updated_at=str(status_dict.get("updated_at", status_dict.get("created_at", ""))),
    )


# ==================== Authentication Endpoints ====================


@router.post("/auth/register", response_model=AuthResponse)
def register(request: RegisterRequest, db=Depends(get_db)) -> AuthResponse:
    """Register a new user."""
    # Check if user already exists
    existing_user = get_user_by_email(db, request.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    
    # Create user
    hashed_password = hash_password(request.password)
    user = create_user(db, request.email, hashed_password, request.full_name)
    
    # Create access token
    access_token = create_access_token(data={"sub": user.email})
    
    return AuthResponse(
        user_id=user.id,
        email=user.email,
        full_name=user.full_name,
        access_token=access_token,
    )


@router.post("/auth/login", response_model=AuthResponse)
def login(request: LoginRequest, db=Depends(get_db)) -> AuthResponse:
    """Login a user."""
    # Get user by email
    user = get_user_by_email(db, request.email)
    if not user or not verify_password(request.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is disabled",
        )
    
    # Create access token
    access_token = create_access_token(data={"sub": user.email})
    
    return AuthResponse(
        user_id=user.id,
        email=user.email,
        full_name=user.full_name,
        access_token=access_token,
    )


@router.get("/auth/me", response_model=UserResponse)
async def get_me(user = Depends(get_current_user)) -> UserResponse:
    """Get current user profile."""
    return UserResponse(
        user_id=user.id,
        email=user.email,
        full_name=user.full_name,
        is_active=user.is_active,
    )


@router.post("/auth/logout")
async def logout():
    """Logout endpoint (token deletion handled by frontend)."""
    return {"message": "Logged out successfully"}


# ==================== Dataset Endpoints ====================


@router.post("/generate-dataset", response_model=GenerateDatasetResponse)
async def generate_dataset(
    request: GenerateDatasetRequest,
    db=Depends(get_db),
    current_user=Depends(get_optional_user),
) -> GenerateDatasetResponse:
    """Generate a new dataset. Authentication is optional."""
    job_id = str(uuid4())
    estimated_minutes = max(2, int((request.quantity_per_language * len(request.languages)) / 100))
    create_job(db, job_id, request.model_dump(), estimated_minutes, request.email, user_id=current_user.id if current_user else None)

    # Prefer Celery workers. If broker config is invalid in production, fall back
    # to an in-process thread so long-running work is detached from request lifecycle.
    try:
        redis_url = os.getenv("REDIS_URL", "NOT SET")
        logger.warning("[BACKEND] Sending task to Redis: %s", redis_url[:40])
        logger.warning("[BACKEND] Task queue: dataset_generation")
        generate_dataset_task.apply_async(args=[job_id, request.model_dump()], task_id=job_id)
    except Exception as exc:  # noqa: BLE001
        logger.warning("Celery queue unavailable for job %s: %s", job_id, exc)
        fallback_thread = threading.Thread(
            target=_run_dataset_job_fallback,
            args=(job_id, request.model_dump()),
            daemon=True,
        )
        fallback_thread.start()

    return GenerateDatasetResponse(
        job_id=job_id,
        estimated_minutes=estimated_minutes,
        message="Dataset generation queued successfully",
    )


@router.get("/my-jobs")
async def get_my_jobs(current_user=Depends(get_current_user), db=Depends(get_db)):
    """Get all jobs for the current user."""
    jobs = get_jobs_by_user(db, current_user.id, limit=20)
    return [
        JobResponse(
            job_id=job.id,
            status=job.status,
            created_at=job.created_at.isoformat(),
            updated_at=job.updated_at.isoformat(),
        )
        for job in jobs
    ]


@router.delete("/jobs/{job_id}")
async def delete_or_cancel_job(job_id: str, current_user=Depends(get_current_user), db=Depends(get_db)):
    """Delete old jobs and cancel active jobs."""
    job = get_job(db, job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")

    if job.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this job")

    # Cancel running jobs first; they are hidden from listing once cancelled.
    if job.status in RUNNING_STATUSES:
        cancel_job(db, job_id, error_message="Cancelled by user")
        delete_job_status(job_id)
        try:
            celery_app.control.revoke(job_id, terminate=True)
        except Exception as exc:  # noqa: BLE001
            logger.warning("Failed to revoke celery task for %s: %s", job_id, exc)
        return {"message": "Job cancellation requested", "status": "cancelled"}

    if job.output_dir:
        output_dir = Path(job.output_dir)
        if output_dir.exists() and output_dir.is_dir():
            shutil.rmtree(output_dir, ignore_errors=True)

    delete_job_status(job_id)
    delete_job(db, job_id)
    return {"message": "Job deleted", "status": "deleted"}


@router.get("/job-status/{job_id}", response_model=JobStatusResponse)
def job_status(job_id: str, db=Depends(get_db)) -> JobStatusResponse:
    redis_status = get_job_status(job_id)
    if redis_status is not None:
        return _redis_status_to_response(redis_status)

    job = get_job(db, job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return _job_to_status_response(job)


@router.get("/download/{job_id}/{format}")
def download_dataset(
    job_id: str,
    format: str,
    db: Session = Depends(get_db)
):
    valid_formats = [
        "csv", "json", "excel",
        "parquet", "huggingface"
    ]
    if format not in valid_formats:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid format: {format}"
        )

    job = get_job(db, job_id)
    if not job:
        raise HTTPException(
            status_code=404,
            detail="Job not found"
        )
    if job.status != "complete":
        raise HTTPException(
            status_code=400,
            detail=f"Job not complete: {job.status}"
        )

    import json as json_module
    try:
        formats = json_module.loads(
            job.exported_formats or "{}"
        )
    except Exception:
        formats = {}

    url = formats.get(format)
    if not url:
        raise HTTPException(
            status_code=404,
            detail=f"Format {format} not available"
        )

    from fastapi.responses import RedirectResponse
    return RedirectResponse(
        url=url,
        status_code=302
    )


@router.get("/quality-report/{job_id}")
def quality_report(job_id: str, db=Depends(get_db)):
    job = get_job(db, job_id)
    if job is None or job.status != "complete" or not job.result_summary:
        raise HTTPException(status_code=404, detail="Quality report not found")
    report_payload = json.loads(job.result_summary)

    try:
        exported_formats = json.loads(job.exported_formats or "{}")
    except Exception:
        exported_formats = {}

    report_payload["export_formats"] = list(exported_formats.keys())
    return JSONResponse(content=report_payload)


@router.get("/debug-env")
def debug_env():
    import os

    environment = os.getenv("ENVIRONMENT", "production")
    if environment == "production":
        raise HTTPException(
            status_code=404,
            detail="Not found"
        )

    return {
        "GROQ_MODEL": os.getenv("GROQ_MODEL", "NOT SET"),
        "GROQ_API_KEY_SET": bool(os.getenv("GROQ_API_KEY")),
        "OPENROUTER_API_KEY_SET": bool(os.getenv("OPENROUTER_API_KEY")),
        "OLLAMA_BASE_URL": os.getenv("OLLAMA_BASE_URL", "NOT SET"),
    }


@router.get("/health", response_model=HealthResponse)
def health_check() -> HealthResponse:
    return HealthResponse(
        status="ok",
        version="1.0.0",
        redis_connected=True,
        database_connected=True,
    )


@router.get("/version")
def get_version():
    return {
        "version": "2.2",
        "download": "supabase-redirect",
        "timestamp": "2026-04-13",
    }
