from __future__ import annotations

import json
import logging
import threading
import traceback
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import asdict, dataclass, is_dataclass
from datetime import datetime, timezone
from typing import Any
from unittest.mock import Mock

from backend.config.languages import get_config_by_code
from backend.config.settings import settings
from backend.database.db import SessionLocal
from backend.database.models import get_job, update_job_status
from backend.pipeline.cleaner import Deduplicator, run_cleaning_pipeline
from backend.pipeline.exporter import run_export_pipeline
from backend.pipeline.labeler import balance_dataset, run_labeling_pipeline
from backend.pipeline.quality import generate_quality_report
from backend.scrapers.orchestrator import run_scrapers_for_language
from backend.workers.celery_app import celery_app
from backend.workers.status import get_job_status, set_job_status, update_job_progress


logger = logging.getLogger(__name__)

_JOB_START_TIMES: dict[str, float] = {}


class JobCancelledError(RuntimeError):
    pass


def _ensure_not_cancelled(db, job_id: str) -> None:
    job = get_job(db, job_id)
    if job is None or job.status == "cancelled":
        raise JobCancelledError("Job cancelled")


@dataclass
class LanguageResult:
    language_code: str
    scrape_result: object | None
    clean_result: object | None
    label_result: object | None
    success: bool
    error_message: str | None


def _build_per_language_status(language_codes: list[str]) -> dict[str, dict[str, Any]]:
    return {
        language_code: {"step": "queued", "rows_collected": 0, "rows_clean": 0, "rows_labeled": 0}
        for language_code in language_codes
    }


def report_progress(
    job_id: str,
    status: str,
    percent: int,
    step_name: str,
    per_language_status: dict,
    eta_seconds: int | None = None,
) -> None:
    if eta_seconds is None:
        start_time = _JOB_START_TIMES.get(job_id)
        if start_time is not None and percent > 0:
            elapsed_seconds = max(0.0, datetime.now(timezone.utc).timestamp() - start_time)
            eta_seconds = int(elapsed_seconds * (100 - percent) / max(percent, 1))

    logger.info(
        "Job %s | status=%s | progress=%s | step=%s | eta=%s",
        job_id,
        status,
        percent,
        step_name,
        eta_seconds,
    )
    update_job_progress(
        job_id=job_id,
        status=status,
        progress_percent=percent,
        current_step=step_name,
        per_language_status=per_language_status,
        eta_seconds=eta_seconds,
    )


def process_language(
    language_code: str,
    domain: str,
    label_type: str,
    quantity: int,
    deduplicator,
    job_id: str,
) -> LanguageResult:
    scrape_result = None
    clean_result = None
    label_result = None
    try:
        language_config = get_config_by_code(language_code)
        scrape_result = run_scrapers_for_language(
            language_config=language_config,
            domain=domain,
            target_count=quantity,
        )
        clean_result = run_cleaning_pipeline(
            rows=getattr(scrape_result, "rows", []),
            language_config=language_config,
            deduplicator=deduplicator,
        )
        label_result = run_labeling_pipeline(
            rows=getattr(clean_result, "clean_rows", [])[: quantity * 3],
            label_type=label_type,
            language_config=language_config,
        )
        return LanguageResult(
            language_code=language_code,
            scrape_result=scrape_result,
            clean_result=clean_result,
            label_result=label_result,
            success=True,
            error_message=None,
        )
    except Exception as exc:  # noqa: BLE001
        logger.exception("Language processing failed for job %s language %s", job_id, language_code)
        return LanguageResult(
            language_code=language_code,
            scrape_result=scrape_result,
            clean_result=clean_result,
            label_result=label_result,
            success=False,
            error_message=str(exc),
        )


def _run_parallel_with_progress(
    job_id: str,
    language_codes: list[str],
    stage_status: str,
    step_name_prefix: str,
    progress_offset: int,
    progress_span: int,
    task_factory,
    per_language_status: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    results: dict[str, Any] = {}
    done_count = 0
    with ThreadPoolExecutor(max_workers=max(1, len(language_codes))) as executor:
        future_to_language = {executor.submit(task_factory, language_code): language_code for language_code in language_codes}
        for future in as_completed(future_to_language):
            language_code = future_to_language[future]
            result = future.result()
            results[language_code] = result
            done_count += 1
            progress_percent = int(progress_offset + (done_count / max(1, len(language_codes))) * progress_span)
            per_language_status[language_code]["step"] = step_name_prefix

            if step_name_prefix == "scraped":
                per_language_status[language_code]["rows_collected"] = len(getattr(result, "rows", []))
            elif step_name_prefix == "cleaned":
                per_language_status[language_code]["rows_clean"] = len(getattr(result, "clean_rows", []))
            elif step_name_prefix == "labeled":
                per_language_status[language_code]["rows_labeled"] = len(getattr(result, "labeled_rows", []))

            report_progress(
                job_id=job_id,
                status=stage_status,
                percent=progress_percent,
                step_name=f"{step_name_prefix.title()} {language_code}",
                per_language_status=per_language_status,
            )
    return results


def _nested_to_dict(value: Any) -> Any:
    if is_dataclass(value):
        return asdict(value)
    if isinstance(value, Mock):
        data = {}
        for key in (
            "is_balanced",
            "dominant_label",
            "dominant_percentage",
            "warning_message",
            "english_score",
            "other_scores",
            "differences",
            "benchmark_note",
        ):
            if key in value.__dict__:
                data[key] = _nested_to_dict(value.__dict__[key])
        return data or None
    return value


def _quality_report_to_dict(quality_report: Any) -> dict[str, Any]:
    fields = [
        "job_id",
        "overall_quality_score",
        "per_language_quality",
        "label_distribution",
        "per_language_distribution",
        "total_labeled",
        "total_needs_review",
        "total_rejected_low_confidence",
        "claude_count",
        "openai_count",
        "openrouter_count",
        "ollama_count",
        "needs_review_count",
        "shortfall_warnings",
        "low_quality_warning",
        "is_low_quality",
        "generated_at",
    ]
    payload = {field: getattr(quality_report, field, None) for field in fields}
    payload["balance_result"] = _nested_to_dict(getattr(quality_report, "balance_result", None))
    payload["benchmark_comparison"] = _nested_to_dict(getattr(quality_report, "benchmark_comparison", None))
    return payload


@celery_app.task(name="generate_dataset")
def generate_dataset_task(job_id: str, request: dict):
    db = SessionLocal()
    request_payload = dict(request or {})
    languages = [str(language_code) for language_code in request_payload.get("languages", [])]
    domain = str(request_payload.get("domain", ""))
    label_type = str(request_payload.get("label_type", "sentiment"))
    quantity_per_language = int(request_payload.get("quantity_per_language", 100))
    export_formats = list(request_payload.get("export_formats", []))
    email = request_payload.get("email")
    custom_labels = request_payload.get("custom_labels", None)
    per_language_status = _build_per_language_status(languages)
    _JOB_START_TIMES[job_id] = datetime.now(timezone.utc).timestamp()

    try:
        logger.info("Starting dataset generation job %s with request=%s", job_id, request_payload)
        _ensure_not_cancelled(db, job_id)
        update_job_status(db, job_id, "scraping")
        report_progress(job_id, "scraping", 0, "Initializing job", per_language_status)

        scrape_results: dict[str, Any] = {}

        def scrape_language(language_code: str):
            language_config = get_config_by_code(language_code)
            return run_scrapers_for_language(
                language_config=language_config,
                domain=domain,
                target_count=quantity_per_language * 8,
            )

        scrape_results = _run_parallel_with_progress(
            job_id=job_id,
            language_codes=languages,
            stage_status="scraping",
            step_name_prefix="scraped",
            progress_offset=10,
            progress_span=20,
            task_factory=scrape_language,
            per_language_status=per_language_status,
        )

        total_scraped_rows = sum(len(getattr(result, "rows", [])) for result in scrape_results.values())
        if total_scraped_rows == 0:
            raise RuntimeError("No data collected")

        _ensure_not_cancelled(db, job_id)
        update_job_status(db, job_id, "cleaning")
        report_progress(job_id, "cleaning", 30, "Starting cleaning", per_language_status)

        deduplicator = Deduplicator()

        def clean_language(language_code: str):
            language_config = get_config_by_code(language_code)
            scrape_result = scrape_results[language_code]
            return run_cleaning_pipeline(
                rows=getattr(scrape_result, "rows", []),
                language_config=language_config,
                deduplicator=deduplicator,
            )

        clean_results = _run_parallel_with_progress(
            job_id=job_id,
            language_codes=languages,
            stage_status="cleaning",
            step_name_prefix="cleaned",
            progress_offset=30,
            progress_span=20,
            task_factory=clean_language,
            per_language_status=per_language_status,
        )

        _ensure_not_cancelled(db, job_id)
        update_job_status(db, job_id, "labeling")
        report_progress(job_id, "labeling", 50, "Starting labeling", per_language_status)

        label_progress_lock = threading.Lock()
        label_stage_progress: dict[str, dict[str, int]] = {
            language_code: {"current": 0, "total": 1}
            for language_code in languages
        }

        def _label_stage_percent() -> int:
            if not languages:
                return 75
            done_ratio = 0.0
            for language_code in languages:
                progress = label_stage_progress.get(language_code, {"current": 0, "total": 1})
                total = max(1, int(progress.get("total", 1)))
                current = min(total, max(0, int(progress.get("current", 0))))
                done_ratio += current / total
            return int(50 + (done_ratio / len(languages)) * 25)

        def _make_label_progress_callback(language_code: str, total_rows: int):
            threshold = max(5, total_rows // 20) if total_rows > 0 else 1
            last_reported = {"rows": 0}

            def _callback(current: int, total: int) -> None:
                should_report = False
                with label_progress_lock:
                    label_stage_progress[language_code] = {
                        "current": int(current),
                        "total": max(1, int(total)),
                    }
                    per_language_status[language_code]["step"] = "labeling"
                    per_language_status[language_code]["rows_labeled"] = int(current)

                    if current >= total or (current - last_reported["rows"]) >= threshold:
                        last_reported["rows"] = int(current)
                        should_report = True

                    progress_percent = _label_stage_percent()

                if should_report:
                    report_progress(
                        job_id,
                        "labeling",
                        progress_percent,
                        f"Labeling {language_code}: {current}/{total}",
                        per_language_status,
                    )

            return _callback

        def label_language(language_code: str):
            language_config = get_config_by_code(language_code)
            clean_result = clean_results[language_code]
            oversample_target = int(quantity_per_language * 4)
            rows_for_labeling = getattr(clean_result, "clean_rows", [])[:oversample_target]

            with label_progress_lock:
                label_stage_progress[language_code] = {
                    "current": 0,
                    "total": max(1, len(rows_for_labeling)),
                }

            logger.info(f"label_type={label_type}, custom_labels={custom_labels}")
            return run_labeling_pipeline(
                rows=rows_for_labeling,
                label_type=label_type,
                language_config=language_config,
                progress_callback=_make_label_progress_callback(language_code, len(rows_for_labeling)),
                custom_labels=custom_labels,
            )

        label_results = _run_parallel_with_progress(
            job_id=job_id,
            language_codes=languages,
            stage_status="labeling",
            step_name_prefix="labeled",
            progress_offset=50,
            progress_span=25,
            task_factory=label_language,
            per_language_status=per_language_status,
        )

        for language_code, result in label_results.items():
            processed_rows = int(getattr(result, "total_input", 0))
            if processed_rows > 0:
                per_language_status[language_code]["rows_labeled"] = processed_rows
                per_language_status[language_code]["step"] = "labeled"

        report_progress(job_id, "labeling", 75, "Labeling complete", per_language_status)

        _ensure_not_cancelled(db, job_id)
        update_job_status(db, job_id, "balancing")
        report_progress(job_id, "balancing", 76, "Balancing dataset...", per_language_status)

        # Balance per language first, then merge
        balanced_rows = []
        for lang_code in languages:
            lang_labeled = getattr(label_results[lang_code], "labeled_rows", [])
            
            # Balance this language to target quantity
            lang_balanced = balance_dataset(
                rows=lang_labeled,
                target_count=quantity_per_language,
                label_type=label_type
            )
            
            logger.info(
                "[BALANCE] %s: %d → %d rows after balance",
                lang_code,
                len(lang_labeled),
                len(lang_balanced)
            )
            
            per_language_status[lang_code]["rows_labeled"] = len(lang_balanced)
            balanced_rows.extend(lang_balanced)

        report_progress(job_id, "balancing", 80, "Balance complete", per_language_status)

        _ensure_not_cancelled(db, job_id)
        update_job_status(db, job_id, "quality_check")
        report_progress(job_id, "quality_check", 80, "Quality check", per_language_status)

        # Use balanced rows for quality check and export
        merged_labeled_rows = balanced_rows
        merged_needs_review_rows: list[dict[str, Any]] = []
        for label_result in label_results.values():
            merged_needs_review_rows.extend(getattr(label_result, "needs_review_rows", []))

        requested_per_language = {language_code: quantity_per_language for language_code in languages}
        quality_report = generate_quality_report(
            labeled_rows=merged_labeled_rows,
            needs_review_rows=merged_needs_review_rows,
            labeling_result=type("LabelingSummary", (), {
                "rejected_low_confidence": sum(getattr(result, "rejected_low_confidence", 0) for result in label_results.values()),
                "claude_count": sum(getattr(result, "claude_count", 0) for result in label_results.values()),
                "openai_count": sum(getattr(result, "openai_count", 0) for result in label_results.values()),
                "openrouter_count": sum(getattr(result, "openrouter_count", getattr(result, "ollama_count", 0)) for result in label_results.values()),
                "ollama_count": sum(getattr(result, "ollama_count", 0) for result in label_results.values()),
                "needs_review_count": sum(getattr(result, "needs_review_count", 0) for result in label_results.values()),
            })(),
            language_codes=languages,
            label_type=label_type,
            custom_labels=custom_labels,
            requested_per_language=requested_per_language,
            job_id=job_id,
        )

        report_progress(job_id, "quality_check", 85, "Quality check complete", per_language_status)

        _ensure_not_cancelled(db, job_id)
        update_job_status(db, job_id, "exporting")
        report_progress(job_id, "exporting", 85, "Starting export", per_language_status)

        export_result = run_export_pipeline(
            rows=merged_labeled_rows,
            job_id=job_id,
            export_formats=export_formats,
            quality_report=quality_report,
            requested_per_language=requested_per_language,
            label_type=label_type,
            domain=domain,
            base_output_dir=settings.datasets_storage_path,
        )

        report_progress(job_id, "exporting", 95, "Export complete", per_language_status)

        _ensure_not_cancelled(db, job_id)
        update_job_status(
            db,
            job_id,
            "complete",
            result_summary={
                **_quality_report_to_dict(quality_report),
                "custom_labels": custom_labels,
            },
            output_dir=export_result.output_dir,
            exported_formats=export_result.exported_files,
        )
        report_progress(job_id, "complete", 100, "Complete", per_language_status, eta_seconds=0)
        logger.info(
            "Job %s complete | languages=%s | rows=%s | exported=%s",
            job_id,
            languages,
            len(merged_labeled_rows),
            export_result.formats_succeeded,
        )
        return {"job_id": job_id, "status": "complete"}
    except JobCancelledError:
        logger.info("Job %s cancelled by user", job_id)
        set_job_status(
            job_id,
            {
                "job_id": job_id,
                "status": "cancelled",
                "progress_percent": 100,
                "current_step": "Cancelled",
                "per_language_status": per_language_status,
                "eta_seconds": None,
                "error_message": "Cancelled by user",
                "updated_at": datetime.now(timezone.utc).isoformat(),
            },
        )
        return {"job_id": job_id, "status": "cancelled"}
    except Exception as exc:  # noqa: BLE001
        error_message = str(exc)
        logger.error("Job %s failed: %s", job_id, traceback.format_exc())
        try:
            set_job_status(
                job_id,
                {
                    "job_id": job_id,
                    "status": "failed",
                    "progress_percent": 100,
                    "current_step": "Failed",
                    "per_language_status": per_language_status,
                    "eta_seconds": None,
                    "error_message": error_message,
                    "updated_at": datetime.now(timezone.utc).isoformat(),
                },
            )
        finally:
            try:
                update_job_status(db, job_id, "failed", error_message=error_message)
            except Exception:  # noqa: BLE001
                logger.exception("Failed to persist failure state for job %s", job_id)
        raise
    finally:
        _JOB_START_TIMES.pop(job_id, None)
        db.close()


generate_dataset_job = generate_dataset_task
