import os

from celery import Celery
from kombu import Queue


redis_url = os.getenv(
    "REDIS_URL",
    "redis://localhost:6379",
)

celery_app = Celery("artha_ai")

if redis_url.startswith("rediss://"):
    broker_url = redis_url
    result_backend = redis_url
    broker_ssl = {
        "ssl_cert_reqs": None,
    }
    backend_ssl = {
        "ssl_cert_reqs": None,
    }
    celery_app.conf.update(
        broker_url=broker_url,
        result_backend=result_backend,
        broker_use_ssl=broker_ssl,
        redis_backend_use_ssl=backend_ssl,
    )
else:
    celery_app.conf.update(
        broker_url=redis_url,
        result_backend=redis_url,
    )

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    task_time_limit=3600,
    worker_max_tasks_per_child=10,
    task_default_queue="dataset_generation",
    task_queues=[
        Queue("dataset_generation"),
        Queue("celery"),
    ],
)

celery_app.autodiscover_tasks(["backend.workers"])

from backend.workers import dataset_job  # noqa: F401,E402
