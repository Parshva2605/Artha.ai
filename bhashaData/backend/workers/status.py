from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from typing import Any

try:
	import redis
except ModuleNotFoundError:  # pragma: no cover
	redis = None


redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
redis_client = None

if redis is not None:
	if redis_url.startswith("rediss://"):
		redis_client = redis.from_url(
			redis_url,
			ssl_cert_reqs=None,
			decode_responses=True,
		)
	else:
		redis_client = redis.from_url(
			redis_url,
			decode_responses=True,
		)


_STATUS_TTL_SECONDS = 24 * 60 * 60


def _get_redis_client():
	return redis_client


def set_job_status(job_id, status_dict) -> None:
	client = _get_redis_client()
	if client is None:
		return
	try:
		client.setex(f"job:{job_id}:status", _STATUS_TTL_SECONDS, json.dumps(status_dict, ensure_ascii=False))
	except Exception:  # noqa: BLE001
		return


def get_job_status(job_id) -> dict | None:
	client = _get_redis_client()
	if client is None:
		return None
	try:
		payload = client.get(f"job:{job_id}:status")
		if not payload:
			return None
		return json.loads(payload)
	except Exception:  # noqa: BLE001
		return None


def delete_job_status(job_id) -> None:
	client = _get_redis_client()
	if client is None:
		return
	try:
		client.delete(f"job:{job_id}:status")
	except Exception:  # noqa: BLE001
		return


def update_job_progress(
	job_id,
	status,
	progress_percent,
	current_step,
	per_language_status=None,
	eta_seconds=None,
) -> None:
	status_dict: dict[str, Any] = {
		"job_id": job_id,
		"status": status,
		"progress_percent": int(progress_percent),
		"current_step": current_step,
		"per_language_status": per_language_status or {},
		"eta_seconds": eta_seconds,
		"updated_at": datetime.now(timezone.utc).isoformat(),
	}
	set_job_status(job_id, status_dict)