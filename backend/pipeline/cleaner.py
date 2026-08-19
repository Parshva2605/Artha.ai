from __future__ import annotations

import hashlib
import re
import unicodedata
from dataclasses import dataclass
from typing import Any


URL_PATTERN = re.compile(r"(?:https?://\S+|www\.\S+)", re.IGNORECASE)
MENTION_PATTERN = re.compile(r"@\w+")
HASHTAG_PATTERN = re.compile(r"#\w+")
WHITESPACE_PATTERN = re.compile(r"\s+")

DEVANAGARI_PATTERN = re.compile(r"[\u0900-\u097F]")
GUJARATI_PATTERN = re.compile(r"[\u0A80-\u0AFF]")
TAMIL_PATTERN = re.compile(r"[\u0B80-\u0BFF]")


@dataclass
class CleaningResult:
	clean_rows: list[dict[str, Any]]
	rejected_language: int
	rejected_too_short: int
	rejected_high_noise: int
	rejected_duplicate: int
	total_input: int
	total_output: int


def detect_language(text: str) -> str | None:
	try:
		from langdetect import detect

		detected = detect(text)
		return str(detected).lower() if detected else None
	except Exception:  # noqa: BLE001
		return None


def _script_char_ratio(text: str, script: str) -> float:
	if not text:
		return 0.0

	if script == "devanagari":
		matches = DEVANAGARI_PATTERN.findall(text)
	elif script == "gujarati":
		matches = GUJARATI_PATTERN.findall(text)
	elif script == "tamil":
		matches = TAMIL_PATTERN.findall(text)
	else:
		matches = []

	letter_count = sum(1 for char in text if char.isalpha())
	if letter_count == 0:
		return 0.0
	return len(matches) / letter_count


def is_correct_language(text: str, expected_code: str, script: str) -> bool:
	expected_code_normalized = (expected_code or "").lower()
	script_normalized = (script or "").lower()

	# Prefer script-aware checks for Indic scripts to avoid over-rejection from langdetect.
	if script_normalized in {"devanagari", "gujarati", "tamil"}:
		ratio = _script_char_ratio(text, script_normalized)
		if ratio >= 0.25:
			return True

	detected_code = detect_language(text)
	if not detected_code:
		# For Latin/English, accept when text does not look Indic-script heavy.
		if script_normalized == "latin":
			indic_ratio = max(
				_script_char_ratio(text, "devanagari"),
				_script_char_ratio(text, "gujarati"),
				_script_char_ratio(text, "tamil"),
			)
			return indic_ratio < 0.10
		return False

	detected_code_normalized = detected_code.lower()

	if script_normalized == "devanagari" and expected_code_normalized in {"hi", "mr"}:
		return detected_code_normalized in {"hi", "mr", "ne", "mai", "kok"}

	if script_normalized == "tamil":
		return detected_code_normalized == "ta"

	if script_normalized == "gujarati":
		return detected_code_normalized == "gu"

	if script_normalized == "latin":
		indic_ratio = max(
			_script_char_ratio(text, "devanagari"),
			_script_char_ratio(text, "gujarati"),
			_script_char_ratio(text, "tamil"),
		)
		if indic_ratio >= 0.15:
			return False
		return detected_code_normalized == "en"

	return detected_code_normalized == expected_code_normalized


def _non_alnum_non_space_ratio(text: str) -> float:
	if not text:
		return 0.0
	total_chars = len(text)
	noisy_chars = sum(1 for char in text if not char.isalnum() and not char.isspace())
	return noisy_chars / total_chars if total_chars else 0.0


def _url_mention_ratio(text: str) -> float:
	if not text:
		return 0.0

	tokens = text.split()
	if not tokens:
		return 0.0

	noisy_tokens = 0
	for token in tokens:
		if URL_PATTERN.fullmatch(token) or MENTION_PATTERN.fullmatch(token):
			noisy_tokens += 1

	return noisy_tokens / len(tokens)


def _clean_text_with_reason(text: str, min_word_count: int = 4) -> tuple[str | None, str | None]:
	if text is None:
		return None, "too_short"

	original_text = str(text)

	if _url_mention_ratio(original_text) > 0.30:
		return None, "high_noise"

	# Step 1: Strip leading and trailing whitespace
	cleaned = original_text.strip()
	# Step 2: Remove all URLs (http/https/www patterns)
	cleaned = URL_PATTERN.sub(" ", cleaned)
	# Step 3: Remove @username mentions
	cleaned = MENTION_PATTERN.sub(" ", cleaned)
	# Step 4: Remove #hashtags
	cleaned = HASHTAG_PATTERN.sub(" ", cleaned)
	# Step 5: Normalize unicode (NFC normalization)
	cleaned = unicodedata.normalize("NFC", cleaned)
	# Step 6: Collapse multiple spaces/newlines into single space
	cleaned = WHITESPACE_PATTERN.sub(" ", cleaned)
	# Step 7: Strip again after transforms
	cleaned = cleaned.strip()

	if cleaned == "":
		return None, "too_short"

	if len(cleaned.split()) < min_word_count:
		return None, "too_short"

	if _non_alnum_non_space_ratio(cleaned) > 0.40:
		return None, "high_noise"

	return cleaned, None


def clean_text(text: str, min_word_count: int = 4) -> str | None:
	cleaned, _reason = _clean_text_with_reason(text, min_word_count=min_word_count)
	return cleaned


def generate_text_hash(text: str) -> str:
	normalized = (text or "").lower().encode("utf-8")
	return hashlib.md5(normalized).hexdigest()


class Deduplicator:
	def __init__(self) -> None:
		self._seen_hashes: set[str] = set()

	def is_duplicate(self, text: str) -> bool:
		text_hash = generate_text_hash(text)
		if text_hash in self._seen_hashes:
			return True
		self._seen_hashes.add(text_hash)
		return False

	def reset(self) -> None:
		self._seen_hashes.clear()

	def seen_count(self) -> int:
		return len(self._seen_hashes)


def run_cleaning_pipeline(
	rows: list[dict],
	language_config: dict,
	deduplicator: Deduplicator,
) -> CleaningResult:
	clean_rows: list[dict[str, Any]] = []
	rejected_language = 0
	rejected_too_short = 0
	rejected_high_noise = 0
	rejected_duplicate = 0

	expected_code = str(language_config["code"]).lower()
	script = str(language_config.get("script", "")).lower()
	min_word_count = int(language_config["min_word_count"])

	for row in rows:
		text_original = str(row.get("text_original", ""))

		if not is_correct_language(text_original, expected_code, script):
			rejected_language += 1
			continue

		text_clean, rejection_reason = _clean_text_with_reason(text_original, min_word_count=min_word_count)
		if text_clean is None:
			if rejection_reason == "high_noise":
				rejected_high_noise += 1
			else:
				rejected_too_short += 1
			continue

		if deduplicator.is_duplicate(text_clean):
			rejected_duplicate += 1
			continue

		cleaned_row = dict(row)
		cleaned_row["text_clean"] = text_clean
		clean_rows.append(cleaned_row)

	total_input = len(rows)
	total_output = len(clean_rows)

	return CleaningResult(
		clean_rows=clean_rows,
		rejected_language=rejected_language,
		rejected_too_short=rejected_too_short,
		rejected_high_noise=rejected_high_noise,
		rejected_duplicate=rejected_duplicate,
		total_input=total_input,
		total_output=total_output,
	)
