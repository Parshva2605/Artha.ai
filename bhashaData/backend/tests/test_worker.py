from __future__ import annotations

from dataclasses import is_dataclass
from unittest.mock import MagicMock, patch

try:
	from backend.workers.celery_app import celery_app
	from backend.workers.dataset_job import (
		LanguageResult,
		generate_dataset_task,
		process_language,
		report_progress,
	)
except ModuleNotFoundError:
	from workers.celery_app import celery_app
	from workers.dataset_job import (
		LanguageResult,
		generate_dataset_task,
		process_language,
		report_progress,
	)


def test_generate_dataset_task_is_registered_celery_task() -> None:
	assert hasattr(generate_dataset_task, "delay")


def test_language_result_dataclass_has_required_fields() -> None:
	result = LanguageResult(
		language_code="hi",
		scrape_result=None,
		clean_result=None,
		label_result=None,
		success=True,
		error_message=None,
	)
	assert is_dataclass(result)
	assert result.language_code == "hi"
	assert result.success is True


def test_report_progress_calls_update_job_progress() -> None:
	with patch("backend.workers.dataset_job.update_job_progress") as mock_update:
		report_progress(
			job_id="test-job",
			status="scraping",
			percent=25,
			step_name="Scraping Reddit",
			per_language_status={},
		)
		mock_update.assert_called_once()


def test_process_language_returns_failure_on_scraper_exception() -> None:
	with patch(
		"backend.workers.dataset_job.run_scrapers_for_language",
		side_effect=Exception("Scraper failed"),
	):
		result = process_language(
			language_code="hi",
			domain="social_media",
			label_type="sentiment",
			quantity=100,
			deduplicator=MagicMock(),
			job_id="test-job",
		)
		assert result.success is False
		assert "Scraper failed" in str(result.error_message)


def test_celery_app_has_correct_task_time_limit() -> None:
	config = celery_app.conf
	assert config.task_time_limit == 3600


def test_generate_dataset_task_marks_failed_on_exception() -> None:
	mock_session = MagicMock()
	request_payload = {
		"languages": ["hi"],
		"domain": "social_media",
		"label_type": "sentiment",
		"quantity_per_language": 10,
		"export_formats": ["csv", "json"],
		"email": None,
	}
	with patch("backend.workers.dataset_job.SessionLocal", return_value=mock_session), \
		patch("backend.workers.dataset_job.run_scrapers_for_language", side_effect=Exception("boom")), \
		patch("backend.workers.dataset_job.run_cleaning_pipeline"), \
		patch("backend.workers.dataset_job.run_labeling_pipeline"), \
		patch("backend.workers.dataset_job.generate_quality_report"), \
		patch("backend.workers.dataset_job.run_export_pipeline"), \
		patch("backend.workers.dataset_job.set_job_status") as mock_set_status, \
		patch("backend.workers.dataset_job.update_job_status"):
		try:
			generate_dataset_task(job_id="job-123", request=request_payload)
		except Exception:
			pass

	assert mock_set_status.called
	assert mock_set_status.call_args.args[1]["status"] == "failed"
