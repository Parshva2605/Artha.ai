import os
from celery import Celery
from kombu import Queue

redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")

celery_app = Celery("artha_ai")

celery_app.conf.update(
    broker_url=redis_url,
    result_backend=redis_url,
    broker_use_ssl={"ssl_cert_reqs": None} if redis_url.startswith("rediss://") else None,
    redis_backend_use_ssl={"ssl_cert_reqs": None} if redis_url.startswith("rediss://") else None,
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    task_time_limit=3600,
    worker_max_tasks_per_child=10,
    task_default_queue="dataset_generation",
    task_queues=[
        Queue("dataset_generation"),
        Queue("celery")
    ]
)

celery_app.autodiscover_tasks(["backend.workers"])
