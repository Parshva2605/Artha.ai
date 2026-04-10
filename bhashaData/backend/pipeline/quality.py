from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from backend.config.languages import get_config_by_code


@dataclass
class BalanceResult:
	is_balanced: bool
	dominant_label: str | None
	dominant_percentage: float
	warning_message: str | None


@dataclass
class BenchmarkComparison:
	english_score: float | None
	other_scores: dict[str, float]
	differences: dict[str, float]
	benchmark_note: str


@dataclass
class QualityReport:
	job_id: str
	overall_quality_score: float
	per_language_quality: dict[str, float]
	label_distribution: dict[str, int]
	per_language_distribution: dict[str, dict[str, int]]
	balance_result: BalanceResult
	benchmark_comparison: BenchmarkComparison
	total_labeled: int
	total_needs_review: int
	total_rejected_low_confidence: int
	claude_count: int
	openai_count: int
	openrouter_count: int
	ollama_count: int
	needs_review_count: int
	shortfall_warnings: list[str]
	low_quality_warning: str | None
	is_low_quality: bool
	generated_at: str


def _get_language_field(row: dict[str, Any]) -> str:
	return str(row.get("language") or row.get("language_code") or "")


def calculate_confidence_score(rows: list[dict]) -> float:
	if not rows:
		return 0.0
	confidences = [float(row.get("confidence", 0.0)) for row in rows]
	if not confidences:
		return 0.0
	return round(sum(confidences) / len(confidences), 4)


def calculate_quality_score(rows: list[dict]) -> float:
	return round(calculate_confidence_score(rows) * 100, 1)


def calculate_per_language_quality(rows: list[dict], language_codes: list[str]) -> dict:
	quality_by_language: dict[str, float] = {code: 0.0 for code in language_codes}
	for language_code in language_codes:
		language_rows = [row for row in rows if _get_language_field(row).lower() == language_code.lower()]
		quality_by_language[language_code] = calculate_quality_score(language_rows)
	return quality_by_language


def calculate_label_distribution(rows: list[dict], label_type: str) -> dict:
	field_map = {
		"sentiment": "label_sentiment",
		"topic": "label_topic",
		"ner": "label_ner",
	}
	if label_type not in field_map:
		raise ValueError(f"Unknown label_type: {label_type}")
	field_name = field_map[label_type]
	distribution: dict[str, int] = {}
	for row in rows:
		label_value = row.get(field_name)
		if label_value is None:
			continue
		label_key = str(label_value)
		distribution[label_key] = distribution.get(label_key, 0) + 1
	return distribution


def calculate_per_language_distribution(rows: list[dict], language_codes: list[str], label_type: str) -> dict:
	per_language: dict[str, dict[str, int]] = {}
	for language_code in language_codes:
		language_rows = [row for row in rows if _get_language_field(row).lower() == language_code.lower()]
		per_language[language_code] = calculate_label_distribution(language_rows, label_type)
	return per_language


def check_label_balance(distribution: dict, total_rows: int) -> BalanceResult:
	if total_rows == 0:
		return BalanceResult(
			is_balanced=True,
			dominant_label=None,
			dominant_percentage=0.0,
			warning_message=None,
		)

	dominant_label: str | None = None
	dominant_percentage = 0.0
	for label, count in distribution.items():
		percentage = round((count / total_rows) * 100, 1)
		if percentage > dominant_percentage:
			dominant_percentage = percentage
			dominant_label = label

	if dominant_percentage > 60.0 and dominant_label is not None:
		return BalanceResult(
			is_balanced=False,
			dominant_label=dominant_label,
			dominant_percentage=dominant_percentage,
			warning_message=(
				f"Label '{dominant_label}' dominates {dominant_percentage}% of rows, exceeding the 60% threshold."
			),
		)

	return BalanceResult(
		is_balanced=True,
		dominant_label=None,
		dominant_percentage=dominant_percentage,
		warning_message=None,
	)


def get_benchmark_comparison(per_language_quality: dict) -> BenchmarkComparison:
	english_score_value = per_language_quality.get("en")
	english_score = float(english_score_value) if english_score_value is not None else None
	other_scores: dict[str, float] = {}
	differences: dict[str, float] = {}

	if english_score is None:
		return BenchmarkComparison(
			english_score=None,
			other_scores={lang: float(score) for lang, score in per_language_quality.items() if lang != "en"},
			differences={},
			benchmark_note="English not included in this dataset. Benchmark comparison unavailable.",
		)

	for language_code, score in per_language_quality.items():
		if language_code == "en":
			continue
		score_value = float(score)
		other_scores[language_code] = score_value
		differences[language_code] = round(score_value - english_score, 1)

	parts = [f"English benchmark score: {english_score}."]
	for language_code, diff in differences.items():
		language_name = language_code.capitalize() if language_code != "hi" else "Hindi"
		if diff < 0:
			parts.append(f"{language_name} is {abs(diff)} points below benchmark.")
		elif diff > 0:
			parts.append(f"{language_name} is {diff} points above benchmark.")
		else:
			parts.append(f"{language_name} matches the benchmark.")

	return BenchmarkComparison(
		english_score=english_score,
		other_scores=other_scores,
		differences=differences,
		benchmark_note=" ".join(parts),
	)


def check_shortfall(delivered_per_language: dict, requested_per_language: dict) -> list[str]:
	warnings: list[str] = []
	for language_code, requested in requested_per_language.items():
		delivered = int(delivered_per_language.get(language_code, 0))
		requested_value = int(requested)
		if requested_value <= 0:
			continue
		percentage = round((delivered / requested_value) * 100, 1)
		if delivered < requested_value * 0.80:
			warnings.append(
				f"{language_code} delivered {delivered} rows but {requested_value} were requested ({percentage}% of target). Consider rerunning with expanded sources."
			)
	return warnings


def check_low_quality(quality_score: float) -> str | None:
	if quality_score < 78:
		return (
			f"Overall quality score is {quality_score} which is below the minimum threshold of 78. "
			"Dataset may not be suitable for production model training. Consider requesting a larger dataset or reviewing needs_review rows manually."
		)
	return None


def generate_quality_report(
	labeled_rows: list[dict],
	needs_review_rows: list[dict],
	labeling_result,
	language_codes: list[str],
	label_type: str,
	requested_per_language: dict,
	job_id: str,
) -> QualityReport:
	overall_quality_score = calculate_quality_score(labeled_rows)
	per_language_quality = calculate_per_language_quality(labeled_rows, language_codes)
	label_distribution = calculate_label_distribution(labeled_rows, label_type)
	per_language_distribution = calculate_per_language_distribution(labeled_rows, language_codes, label_type)
	balance_result = check_label_balance(label_distribution, len(labeled_rows))
	benchmark_comparison = get_benchmark_comparison(per_language_quality)
	delivered_per_language = {
		language_code: len([row for row in labeled_rows if _get_language_field(row).lower() == language_code.lower()])
		for language_code in language_codes
	}
	shortfall_warnings = check_shortfall(delivered_per_language, requested_per_language)

	for language_code, requested in requested_per_language.items():
		delivered = int(delivered_per_language.get(language_code, 0))
		requested_value = int(requested)
		if requested_value <= 0:
			continue

		minimum_acceptable = int(requested_value * 0.80)
		if delivered < minimum_acceptable:
			pct = round((delivered / requested_value) * 100, 1)
			try:
				language_name = str(get_config_by_code(str(language_code))["name"])
			except Exception:  # noqa: BLE001
				language_name = str(language_code)
			shortfall_warnings.append(
				f"{language_name} delivered only {delivered} rows ({pct}% of {requested_value} requested). "
				f"Minimum acceptable is {minimum_acceptable}. Consider increasing scrape target_count "
				f"for {language_name} sources."
			)

	low_quality_warning = check_low_quality(overall_quality_score)
	return QualityReport(
		job_id=job_id,
		overall_quality_score=overall_quality_score,
		per_language_quality=per_language_quality,
		label_distribution=label_distribution,
		per_language_distribution=per_language_distribution,
		balance_result=balance_result,
		benchmark_comparison=benchmark_comparison,
		total_labeled=len(labeled_rows),
		total_needs_review=len(needs_review_rows),
		total_rejected_low_confidence=getattr(labeling_result, "rejected_low_confidence", 0),
		claude_count=getattr(labeling_result, "claude_count", 0),
		openai_count=getattr(labeling_result, "openai_count", 0),
		openrouter_count=getattr(labeling_result, "openrouter_count", getattr(labeling_result, "ollama_count", 0)),
		ollama_count=getattr(labeling_result, "ollama_count", 0),
		needs_review_count=getattr(labeling_result, "needs_review_count", 0),
		shortfall_warnings=shortfall_warnings,
		low_quality_warning=low_quality_warning,
		is_low_quality=overall_quality_score < 78,
		generated_at=datetime.now(timezone.utc).isoformat(),
	)
