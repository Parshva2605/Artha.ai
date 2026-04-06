from __future__ import annotations

from typing import Any

from backend.workers.celery_app import celery_app
from backend.workers.status import update_job_progress


@celery_app.task(name="workers.dataset_job.generate_dataset_task")
def generate_dataset_task(job_id: str, request_payload: dict[str, Any]) -> dict[str, Any]:
    update_job_progress(
        job_id=job_id,
        status="queued",
        progress_percent=0,
        current_step="Queued",
        per_language_status={
            str(language_code): {"step": "queued", "rows_collected": 0, "rows_clean": 0, "rows_labeled": 0}
            for language_code in request_payload.get("languages", [])
        },
        eta_seconds=None,
    )
    return {"job_id": job_id, "status": "queued"}


generate_dataset_job = generate_dataset_task
