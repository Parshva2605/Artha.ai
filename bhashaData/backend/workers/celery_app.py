# Redis SSL fix - final version
import os
import ssl
from celery import Celery
from kombu import Queue

redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")

celery_app = Celery("artha_ai")

if redis_url.startswith("rediss://"):
    broker_ssl = {
        "ssl_cert_reqs": ssl.CERT_NONE,
        "ssl_ca_certs": None,
        "ssl_certfile": None,
        "ssl_keyfile": None,
    }
    celery_app.conf.broker_use_ssl = broker_ssl
    celery_app.conf.redis_backend_use_ssl = broker_ssl

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
