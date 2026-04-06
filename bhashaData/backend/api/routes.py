from __future__ import annotations

import json
import shutil
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from sqlalchemy import text

from backend.api.models import GenerateDatasetRequest, GenerateDatasetResponse, HealthResponse, JobStatusResponse
from backend.database.db import get_db
from backend.database.models import create_job, get_job
from backend.workers.dataset_job import generate_dataset_task
from backend.workers.status import get_job_status, _get_redis_client


router = APIRouter()

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
}


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
    }
    eta_seconds = None if status in {"complete", "failed"} else int(job.estimated_minutes * 60)
    return JobStatusResponse(
        job_id=job.id,
        status=status,
        progress_percent=100 if status == "complete" else 0,
        current_step=current_step_map.get(status, "Queued"),
        per_language_status=_build_per_language_status(request_payload),
        eta_seconds=eta_seconds,
        error_message=job.error_message if status == "failed" else None,
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


@router.post("/generate-dataset", response_model=GenerateDatasetResponse)
def generate_dataset(request: GenerateDatasetRequest, db=Depends(get_db)) -> GenerateDatasetResponse:
    job_id = str(uuid4())
    estimated_minutes = max(2, int((request.quantity_per_language * len(request.languages)) / 100))
    create_job(db, job_id, request.model_dump(), estimated_minutes, request.email)
    generate_dataset_task.delay(job_id, request.model_dump())
    return GenerateDatasetResponse(
        job_id=job_id,
        estimated_minutes=estimated_minutes,
        message="Dataset generation queued successfully",
    )


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
def download_dataset(job_id: str, format: str, db=Depends(get_db)):
    if format not in SUPPORTED_DOWNLOAD_FORMATS:
        raise HTTPException(status_code=400, detail="Unsupported download format")

    job = get_job(db, job_id)
    if job is None or job.status != "complete" or not job.output_dir:
        raise HTTPException(status_code=404, detail="Dataset not available")

    output_dir = Path(job.output_dir)
    if format == "huggingface":
        hf_dir = output_dir / "huggingface"
        if not hf_dir.exists() or not hf_dir.is_dir():
            raise HTTPException(status_code=404, detail="HuggingFace dataset not found")
        archive_base = output_dir / "huggingface_export"
        archive_path = Path(f"{archive_base}.zip")
        if not archive_path.exists():
            shutil.make_archive(str(archive_base), "zip", root_dir=hf_dir)
        return FileResponse(str(archive_path), filename=f"{job_id}-huggingface.zip")

    file_path = output_dir / f"data.{SUPPORTED_DOWNLOAD_FORMATS[format]}"
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Export file not found")
    return FileResponse(str(file_path), filename=file_path.name)


@router.get("/quality-report/{job_id}")
def quality_report(job_id: str, db=Depends(get_db)):
    job = get_job(db, job_id)
    if job is None or job.status != "complete" or not job.result_summary:
        raise HTTPException(status_code=404, detail="Quality report not found")
    return JSONResponse(content=json.loads(job.result_summary))


@router.get("/health", response_model=HealthResponse)
def health_check(db=Depends(get_db)) -> HealthResponse:
    redis_connected = False
    try:
        client = _get_redis_client()
        if client is not None:
            client.ping()
            redis_connected = True
    except Exception:  # noqa: BLE001
        redis_connected = False

    database_connected = False
    try:
        db.execute(text("SELECT 1"))
        database_connected = True
    except Exception:  # noqa: BLE001
        database_connected = False

    return HealthResponse(
        status="ok",
        version="1.0.0",
        redis_connected=redis_connected,
        database_connected=database_connected,
    )
