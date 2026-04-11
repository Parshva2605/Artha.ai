# Clean version - no SSL needed for Railway Redis
import os
from celery import Celery
from kombu import Queue

redis_url = os.getenv(
    "REDIS_URL",
    "redis://localhost:6379"
)

celery_app = Celery("artha_ai")

celery_app.conf.update(
    broker_url=redis_url,
    result_backend=redis_url,
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    task_time_limit=3600,
    worker_max_tasks_per_child=10,
    task_default_queue="dataset_generation",
    task_queues=[
        Queue("dataset_generation"),
        Queue("celery")
    ],
    broker_connection_retry_on_startup=True,
)

celery_app.autodiscover_tasks(["backend.workers"])
