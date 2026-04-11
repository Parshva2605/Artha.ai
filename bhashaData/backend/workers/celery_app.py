import os

from celery import Celery
from kombu import Queue


redis_url = os.getenv("REDIS_URL", "")

# Fix SSL for Upstash rediss:// URLs
ssl_options = {}
if redis_url.startswith("rediss://"):
    ssl_options = {
        "ssl_cert_reqs": "CERT_NONE",
        "ssl_ca_certs": None,
        "ssl_certfile": None,
        "ssl_keyfile": None,
    }

celery_app = Celery("artha_ai")

celery_app.conf.update(
    broker_url=redis_url,
    result_backend=redis_url,
    broker_use_ssl=ssl_options if ssl_options else None,
    redis_backend_use_ssl=ssl_options if ssl_options else None,
    task_track_started=True,
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    task_time_limit=3600,
    task_soft_time_limit=3300,
    worker_max_tasks_per_child=10,
    task_default_queue="dataset_generation",
    task_routes={"generate_dataset": {"queue": "dataset_generation"}},
    task_queues=[
        Queue("dataset_generation"),
        Queue("celery"),
    ],
)

celery_app.autodiscover_tasks(["backend.workers"])

from backend.workers import dataset_job  # noqa: F401,E402
