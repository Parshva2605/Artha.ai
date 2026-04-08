from celery import Celery

from backend.config.settings import settings

celery_app = Celery(
    "artha_ai",
    broker=settings.redis_url,
    backend=settings.redis_url,
)

# Configure SSL for Upstash (rediss:// protocol)
broker_use_ssl = {}
redis_backend_use_ssl = {}

if settings.redis_url.startswith("rediss://"):
    broker_use_ssl = {
        "ssl_cert_reqs": None,
    }
    redis_backend_use_ssl = {
        "ssl_cert_reqs": None,
    }

celery_app.conf.update(
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
    broker_use_ssl=broker_use_ssl,
    redis_backend_use_ssl=redis_backend_use_ssl,
)

celery_app.autodiscover_tasks(["backend.workers"])

from backend.workers import dataset_job  # noqa: F401,E402
