from workers.celery_app import celery_app


@celery_app.task(name="workers.dataset_job.generate_dataset_job")
def generate_dataset_job(job_id: str) -> dict[str, str]:
    # Full pipeline will be implemented in later phases.
    return {"job_id": job_id, "status": "queued"}
