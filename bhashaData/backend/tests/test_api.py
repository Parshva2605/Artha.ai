from __future__ import annotations

from unittest.mock import patch

from fastapi.testclient import TestClient

from backend.main import app


client = TestClient(app)


def test_health_endpoint_returns_200() -> None:
	response = client.get("/api/health")
	assert response.status_code == 200
	data = response.json()
	assert data["status"] == "ok"
	assert data["version"] == "1.0.0"


def test_generate_dataset_validates_language_codes() -> None:
	response = client.post(
		"/api/generate-dataset",
		json={
			"languages": ["xx"],
			"domain": "social_media",
			"label_type": "sentiment",
			"quantity_per_language": 100,
			"export_formats": ["csv"],
		},
	)
	assert response.status_code == 422


def test_generate_dataset_validates_quantity_minimum() -> None:
	response = client.post(
		"/api/generate-dataset",
		json={
			"languages": ["hi"],
			"domain": "social_media",
			"label_type": "sentiment",
			"quantity_per_language": 50,
			"export_formats": ["csv"],
		},
	)
	assert response.status_code == 422


def test_generate_dataset_validates_empty_export_formats() -> None:
	response = client.post(
		"/api/generate-dataset",
		json={
			"languages": ["hi"],
			"domain": "social_media",
			"label_type": "sentiment",
			"quantity_per_language": 100,
			"export_formats": [],
		},
	)
	assert response.status_code == 422


def test_generate_dataset_returns_job_id_for_valid_request() -> None:
	with patch("backend.api.routes.generate_dataset_task.delay"):
		response = client.post(
			"/api/generate-dataset",
			json={
				"languages": ["hi"],
				"domain": "social_media",
				"label_type": "sentiment",
				"quantity_per_language": 100,
				"export_formats": ["csv"],
			},
		)
	assert response.status_code == 200
	data = response.json()
	assert "job_id" in data
	assert "estimated_minutes" in data


def test_job_status_unknown_job_returns_404() -> None:
	response = client.get("/api/job-status/nonexistent-job")
	assert response.status_code == 404


def test_download_invalid_format_returns_400() -> None:
	response = client.get("/api/download/any-job/invalid")
	assert response.status_code == 400
