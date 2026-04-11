from __future__ import annotations

import json
import logging
import os
import shutil
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd
import requests

try:
	from backend.config.languages import get_config_by_code, is_supported_language
except ModuleNotFoundError:
	from config.languages import get_config_by_code, is_supported_language


logger = logging.getLogger(__name__)


EXPORT_COLUMNS = [
	"id",
	"text_original",
	"text_clean",
	"language",
	"language_name",
	"script",
	"domain",
	"source",
	"source_url",
	"source_subreddit",
	"label_sentiment",
	"label_topic",
	"label_ner",
	"confidence",
	"confidence_reason",
	"llm_used",
	"needs_review",
	"app_id",
	"star_rating",
	"rating_hint",
	"created_at",
	"job_id",
]

REQUIRED_COLUMNS = {
	"id",
	"text_original",
	"text_clean",
	"language",
	"language_name",
	"script",
	"domain",
	"source",
	"confidence",
	"llm_used",
	"needs_review",
	"created_at",
	"job_id",
}

_STRING_COLUMNS = [
	column
	for column in EXPORT_COLUMNS
	if column not in {"id", "confidence", "needs_review", "star_rating"}
]


@dataclass
class ExportResult:
	job_id: str
	output_dir: str
	exported_files: dict[str, str]
	metadata_path: str
	formats_succeeded: list[str]
	formats_failed: list[str]
	total_rows_exported: int


def _now_iso() -> str:
	return datetime.now(timezone.utc).isoformat()


def _unique_preserving_order(values: list[str]) -> list[str]:
	seen: set[str] = set()
	ordered: list[str] = []
	for value in values:
		if value in seen:
			continue
		seen.add(value)
		ordered.append(value)
	return ordered


def _get_language_code(row: dict[str, Any]) -> str:
	return str(row.get("language") or row.get("language_code") or "").strip()


def _derive_language_fields(row: dict[str, Any]) -> tuple[str | None, str | None]:
	language_code = _get_language_code(row)
	if not language_code:
		return None, None

	if not is_supported_language(language_code):
		return language_code, None

	config = get_config_by_code(language_code)
	return language_code, config["name"]


def _normalise_created_at(value: Any | None) -> str:
	if value:
		return str(value)
	return _now_iso()


def _is_missing_required_value(value: Any) -> bool:
	if value is None:
		return True
	if isinstance(value, str) and not value.strip():
		return True
	return False


def prepare_rows_for_export(rows: list[dict], job_id: str) -> list[dict]:
	prepared_rows: list[dict] = []
	exported_at = _now_iso()

	for index, row in enumerate(rows, start=1):
		prepared_row = dict(row)
		language_code = _get_language_code(prepared_row)
		language_name = prepared_row.get("language_name")
		script = prepared_row.get("script")

		if (not language_name or not str(language_name).strip() or not script or not str(script).strip()) and language_code:
			resolved_language, resolved_name = _derive_language_fields(prepared_row)
			if not prepared_row.get("language") and resolved_language is not None:
				prepared_row["language"] = resolved_language
			if not language_name and resolved_name is not None:
				prepared_row["language_name"] = resolved_name
			if not script and resolved_language is not None and is_supported_language(resolved_language):
				prepared_row["script"] = get_config_by_code(resolved_language)["script"]

		if not prepared_row.get("language") and language_code:
			prepared_row["language"] = language_code
		if not prepared_row.get("language_name") and language_code and is_supported_language(language_code):
			prepared_row["language_name"] = get_config_by_code(language_code)["name"]
		if not prepared_row.get("script") and language_code and is_supported_language(language_code):
			prepared_row["script"] = get_config_by_code(language_code)["script"]

		prepared_row["id"] = index
		prepared_row["job_id"] = job_id
		prepared_row["created_at"] = _normalise_created_at(prepared_row.get("created_at") or exported_at)

		for column in EXPORT_COLUMNS:
			if column not in prepared_row:
				prepared_row[column] = None

		missing_required_columns = [
			column for column in REQUIRED_COLUMNS if _is_missing_required_value(prepared_row.get(column))
		]
		if missing_required_columns:
			raise ValueError(
				f"Row {index} is missing required export columns: {', '.join(sorted(missing_required_columns))}"
			)

		ordered_row = {column: prepared_row.get(column) for column in EXPORT_COLUMNS}
		prepared_rows.append(ordered_row)

	return prepared_rows


def _ensure_output_path(output_path: str) -> Path:
	path = Path(output_path)
	path.parent.mkdir(parents=True, exist_ok=True)
	return path


def _build_export_dataframe(rows: list[dict]) -> pd.DataFrame:
	df = pd.DataFrame(rows)
	for column in EXPORT_COLUMNS:
		if column not in df.columns:
			df[column] = None
	return df[EXPORT_COLUMNS]


def export_csv(rows: list[dict], output_path: str) -> str:
	path = _ensure_output_path(output_path)
	df = _build_export_dataframe(rows)
	df.to_csv(path, index=False, encoding="utf-8-sig")
	return str(path)


def export_json(rows: list[dict], output_path: str) -> str:
	path = _ensure_output_path(output_path)
	ordered_rows = [{column: row.get(column) for column in EXPORT_COLUMNS} for row in rows]
	with path.open("w", encoding="utf-8") as file_handle:
		json.dump(ordered_rows, file_handle, ensure_ascii=False, indent=2)
	return str(path)


def export_excel(rows: list[dict], output_path: str) -> str:
	if len(rows) > 100000:
		logger.warning("Exporting %s rows to Excel may be slow and memory intensive.", len(rows))

	path = _ensure_output_path(output_path)
	df = _build_export_dataframe(rows)
	generated_at = _now_iso()

	with pd.ExcelWriter(path, engine="openpyxl") as writer:
		df.to_excel(writer, index=False, sheet_name="Dataset")
		workbook = writer.book
		if "Sheet" in workbook.sheetnames:
			default_sheet = workbook["Sheet"]
			workbook.remove(default_sheet)
		quality_sheet = workbook.create_sheet("Quality_Info")
		quality_sheet["A1"] = "Generated by Artha AI"
		quality_sheet["A2"] = f"Total rows: {len(rows)}"
		quality_sheet["A3"] = f"Export date: {generated_at}"

	return str(path)


def export_parquet(rows: list[dict], output_path: str) -> str:
	path = _ensure_output_path(output_path)
	df = _build_export_dataframe(rows)
	df["id"] = pd.to_numeric(df["id"], errors="raise").astype("int64")
	df["confidence"] = pd.to_numeric(df["confidence"], errors="raise").astype("float64")
	df["needs_review"] = df["needs_review"].fillna(False).astype(bool)
	df["star_rating"] = pd.to_numeric(df["star_rating"], errors="coerce").astype("Int64")
	for column in _STRING_COLUMNS:
		df[column] = df[column].astype("object")
	df.to_parquet(path, engine="pyarrow", index=False)
	return str(path)


def export_huggingface(rows: list[dict], output_path: str) -> str:
	path = Path(output_path)
	path.mkdir(parents=True, exist_ok=True)

	from datasets import Dataset, Features, Value

	ordered_rows = [{column: row.get(column) for column in EXPORT_COLUMNS} for row in rows]
	dataset = Dataset.from_list(ordered_rows)
	features = Features(
		{
			"id": Value("int64"),
			"text_original": Value("string"),
			"text_clean": Value("string"),
			"language": Value("string"),
			"language_name": Value("string"),
			"script": Value("string"),
			"domain": Value("string"),
			"source": Value("string"),
			"source_url": Value("string"),
			"source_subreddit": Value("string"),
			"label_sentiment": Value("string"),
			"label_topic": Value("string"),
			"label_ner": Value("string"),
			"confidence": Value("float64"),
			"confidence_reason": Value("string"),
			"llm_used": Value("string"),
			"needs_review": Value("bool"),
			"app_id": Value("string"),
			"star_rating": Value("int64"),
			"rating_hint": Value("string"),
			"created_at": Value("string"),
			"job_id": Value("string"),
		}
	)
	dataset = dataset.cast(features)
	dataset.save_to_disk(str(path))
	return str(path)


def generate_metadata(
	job_id: str,
	rows: list[dict],
	quality_report,
	requested_per_language: dict,
	label_type: str,
	export_formats: list[str],
	domain: str,
) -> dict:
	languages = _unique_preserving_order([
		str(row.get("language") or row.get("language_code") or "").strip()
		for row in rows
		if str(row.get("language") or row.get("language_code") or "").strip()
	])
	label_types = ["sentiment", "topic", "ner"] if (label_type or "").lower() == "all" else [label_type]
	delivered_by_language: dict[str, int] = {}
	needs_review_by_language: dict[str, int] = {}
	for language_code in languages:
		language_rows = [
			row for row in rows if str(row.get("language") or row.get("language_code") or "").strip() == language_code
		]
		delivered_by_language[language_code] = len(language_rows)
		needs_review_by_language[language_code] = len([row for row in language_rows if bool(row.get("needs_review"))])

	per_language = {
		language_code: {
			"requested": int(requested_per_language.get(language_code, 0)),
			"delivered": delivered_by_language.get(language_code, 0),
			"needs_review": needs_review_by_language.get(language_code, 0),
		}
		for language_code in languages
	}

	quality_scores = dict(getattr(quality_report, "per_language_quality", {}))
	quality_scores["overall"] = float(getattr(quality_report, "overall_quality_score", 0.0))

	sources_used = _unique_preserving_order(
		[str(row.get("source", "")).strip() for row in rows if str(row.get("source", "")).strip()]
	)

	return {
		"dataset_id": job_id,
		"job_id": job_id,
		"created_at": _now_iso(),
		"platform": "Artha AI v1.0",
		"languages": languages,
		"label_types": label_types,
		"domain": domain,
		"total_rows": len(rows),
		"per_language": per_language,
		"quality_scores": quality_scores,
		"label_distribution": getattr(quality_report, "label_distribution", {}),
		"per_language_distribution": getattr(quality_report, "per_language_distribution", {}),
		"is_balanced": getattr(getattr(quality_report, "balance_result", None), "is_balanced", False),
		"sources_used": sources_used,
		"export_formats": export_formats,
		"llm_usage": {
			"claude": getattr(quality_report, "claude_count", 0),
			"openai": getattr(quality_report, "openai_count", 0),
			"openrouter": getattr(quality_report, "openrouter_count", getattr(quality_report, "ollama_count", 0)),
			"ollama": getattr(quality_report, "ollama_count", 0),
			"needs_review": getattr(quality_report, "needs_review_count", 0),
		},
		"english_benchmark_note": getattr(getattr(quality_report, "benchmark_comparison", None), "benchmark_note", ""),
		"shortfall_warnings": getattr(quality_report, "shortfall_warnings", []),
		"low_quality_warning": getattr(quality_report, "low_quality_warning", None),
	}


def save_metadata(metadata: dict, output_path: str) -> str:
	path = _ensure_output_path(output_path)
	with path.open("w", encoding="utf-8") as file_handle:
		json.dump(metadata, file_handle, ensure_ascii=False, indent=2)
	return str(path)


def upload_to_supabase(
	local_path: str,
	job_id: str,
	filename: str,
) -> str | None:
	print(f"[UPLOAD] SUPABASE_URL: {bool(os.getenv('SUPABASE_URL'))}")
	print(f"[UPLOAD] SUPABASE_SERVICE_KEY: {bool(os.getenv('SUPABASE_SERVICE_KEY'))}")
	supabase_url = os.getenv("SUPABASE_URL")
	service_key = os.getenv("SUPABASE_SERVICE_KEY")

	if not supabase_url or not service_key:
		return None

	try:
		path = Path(local_path)
		if path.is_dir():
			archive_base = path.parent / path.name
			local_path = shutil.make_archive(str(archive_base), "zip", root_dir=str(path))
			path = Path(local_path)
			if not filename.lower().endswith(".zip"):
				filename = f"{Path(filename).stem}.zip"

		print(f"[UPLOAD] Uploading {filename} to Supabase...")
		with path.open("rb") as file_handle:
			file_data = file_handle.read()

		upload_path = f"{job_id}/{filename}"
		url = f"{supabase_url}/storage/v1/object/datasets/{upload_path}"

		response = requests.post(
			url,
			headers={
				"Authorization": f"Bearer {service_key}",
				"Content-Type": "application/octet-stream",
				"x-upsert": "true",
			},
			data=file_data,
			timeout=60,
		)
		print(f"[UPLOAD] Status: {response.status_code}")
		print(f"[UPLOAD] Response: {response.text[:200]}")

		if response.status_code in [200, 201]:
			public_url = f"{supabase_url}/storage/v1/object/public/datasets/{upload_path}"
			print(f"[UPLOAD] Success: {public_url}")
			return public_url
		print(f"[UPLOAD] Failed: {response.text}")
		return None
	except Exception as e:
		print(f"[UPLOAD ERROR] {e}")
		return None


def _export_with_format(format_name: str, rows: list[dict], output_path: str) -> str:
	if format_name == "csv":
		return export_csv(rows, output_path)
	if format_name == "json":
		return export_json(rows, output_path)
	if format_name == "excel":
		return export_excel(rows, output_path)
	if format_name == "parquet":
		return export_parquet(rows, output_path)
	if format_name == "huggingface":
		return export_huggingface(rows, output_path)
	raise ValueError(f"Unsupported export format: {format_name}")


def run_export_pipeline(
	rows: list[dict],
	job_id: str,
	export_formats: list[str],
	quality_report,
	requested_per_language: dict,
	label_type: str,
	domain: str,
	base_output_dir: str = "./datasets",
) -> ExportResult:
	if not export_formats:
		raise ValueError("At least one export format must be selected")

	output_dir = Path(base_output_dir) / job_id
	output_dir.mkdir(parents=True, exist_ok=True)

	prepared_rows = prepare_rows_for_export(rows, job_id)
	metadata = generate_metadata(
		job_id=job_id,
		rows=prepared_rows,
		quality_report=quality_report,
		requested_per_language=requested_per_language,
		label_type=label_type,
		export_formats=export_formats,
		domain=domain,
	)
	metadata_path = save_metadata(metadata, str(output_dir / "metadata.json"))

	format_paths: dict[str, str] = {
		"csv": str(output_dir / "data.csv"),
		"json": str(output_dir / "data.json"),
		"excel": str(output_dir / "data.xlsx"),
		"parquet": str(output_dir / "data.parquet"),
		"huggingface": str(output_dir / "huggingface"),
	}

	selected_formats = [format_name for format_name in export_formats if format_name in format_paths]
	unknown_formats = [format_name for format_name in export_formats if format_name not in format_paths]

	for format_name in unknown_formats:
		logger.warning("Unsupported export format requested: %s", format_name)

	exported_files: dict[str, str] = {format_name: format_paths[format_name] for format_name in selected_formats}
	formats_succeeded: list[str] = []
	formats_failed: list[str] = []

	if selected_formats:
		with ThreadPoolExecutor(max_workers=min(5, len(selected_formats))) as executor:
			futures = {
				executor.submit(_export_with_format, format_name, prepared_rows, format_paths[format_name]): format_name
				for format_name in selected_formats
			}
			for future in as_completed(futures):
				format_name = futures[future]
				try:
					result_path = future.result()
					filename = Path(result_path).name
					if Path(result_path).is_dir():
						filename = f"{Path(result_path).name}.zip"
					public_url = upload_to_supabase(result_path, job_id, filename)
					exported_files[format_name] = public_url or result_path
					formats_succeeded.append(format_name)
				except Exception as exc:  # noqa: BLE001
					logger.warning("Failed to export %s format for job %s: %s", format_name, job_id, exc)
					formats_failed.append(format_name)

	formats_failed.extend(unknown_formats)

	return ExportResult(
		job_id=job_id,
		output_dir=str(output_dir),
		exported_files=exported_files,
		metadata_path=metadata_path,
		formats_succeeded=formats_succeeded,
		formats_failed=formats_failed,
		total_rows_exported=len(prepared_rows),
	)
