from __future__ import annotations

import json
import os
import threading
import time
from dataclasses import dataclass, field
from typing import Any, Callable


LABEL_PROMPTS: dict[str, str] = {
	"sentiment": (
		"You are a sentiment analysis expert.\n"
		"Language: {language_name}\n"
		"Task: Classify the sentiment of the following text.\n"
		"Valid labels: positive, negative, neutral\n"
		"Text: {text}\n\n"
		"Respond ONLY with valid JSON, no other text:\n"
		"{{\n"
		"  \"label\": \"positive or negative or neutral\",\n"
		"  \"confidence\": 0.0,\n"
		"  \"reason\": \"one sentence explanation\"\n"
		"}}"
	),
	"topic": (
		"You are a topic classification expert.\n"
		"Language: {language_name}\n"
		"Task: Classify the topic of the following text.\n"
		"Valid labels: politics, sports, entertainment, technology, food, health, finance, education, other\n"
		"Text: {text}\n\n"
		"Respond ONLY with valid JSON, no other text:\n"
		"{{\n"
		"  \"label\": \"one of the valid labels above\",\n"
		"  \"confidence\": 0.0,\n"
		"  \"reason\": \"one sentence explanation\"\n"
		"}}"
	),
	"ner": (
		"You are a named entity recognition expert.\n"
		"Language: {language_name}\n"
		"Task: Identify the primary named entity type in the following text.\n"
		"Valid labels: PERSON, ORGANIZATION, LOCATION, DATE, CURRENCY, OTHER\n"
		"Text: {text}\n\n"
		"Respond ONLY with valid JSON, no other text:\n"
		"{{\n"
		"  \"label\": \"one of the valid labels above\",\n"
		"  \"confidence\": 0.0,\n"
		"  \"reason\": \"one sentence explanation\"\n"
		"}}"
	),
}


VALID_LABELS: dict[str, set[str]] = {
	"sentiment": {"positive", "negative", "neutral"},
	"topic": {"politics", "sports", "entertainment", "technology", "food", "health", "finance", "education", "other"},
	"ner": {"PERSON", "ORGANIZATION", "LOCATION", "DATE", "CURRENCY", "OTHER"},
}


class _RateLimiter:
	def __init__(self, max_requests_per_second: float) -> None:
		self._interval = 1.0 / max_requests_per_second
		self._lock = threading.Lock()
		self._last_call = 0.0

	def wait(self) -> None:
		with self._lock:
			now = time.time()
			elapsed = now - self._last_call
			if elapsed < self._interval:
				time.sleep(self._interval - elapsed)
			self._last_call = time.time()


CLAUDE_RATE_LIMITER = _RateLimiter(max_requests_per_second=10.0)
OPENAI_RATE_LIMITER = _RateLimiter(max_requests_per_second=10.0)
OLLAMA_RATE_LIMITER = _RateLimiter(max_requests_per_second=10.0)


@dataclass
class LabelResult:
	label: str
	confidence: float
	reason: str
	llm_used: str
	needs_review: bool
	label_type: str
	raw_response: str


@dataclass
class LabelingResult:
	labeled_rows: list[dict[str, Any]]
	needs_review_rows: list[dict[str, Any]]
	rejected_low_confidence: int
	claude_count: int
	openai_count: int
	ollama_count: int
	needs_review_count: int
	total_input: int
	total_output: int


def build_prompt(label_type: str, text: str, language_name: str) -> str:
	normalized_type = (label_type or "").strip().lower()
	if normalized_type not in LABEL_PROMPTS:
		raise ValueError(f"Unknown label_type: {label_type}")
	return LABEL_PROMPTS[normalized_type].format(text=text, language_name=language_name)


def _strip_code_fences(response_text: str) -> str:
	cleaned = (response_text or "").strip()
	if cleaned.startswith("```"):
		lines = cleaned.splitlines()
		if lines and lines[0].startswith("```"):
			lines = lines[1:]
		if lines and lines[-1].strip() == "```":
			lines = lines[:-1]
		cleaned = "\n".join(lines).strip()
	return cleaned


def parse_llm_response(response_text: str, label_type: str) -> LabelResult | None:
	try:
		normalized_type = (label_type or "").strip().lower()
		if normalized_type not in VALID_LABELS:
			return None

		raw = response_text or ""
		payload_text = _strip_code_fences(raw)
		payload = json.loads(payload_text)

		if not isinstance(payload, dict):
			return None

		if "label" not in payload or "confidence" not in payload or "reason" not in payload:
			return None

		label = str(payload["label"]).strip()
		reason = str(payload["reason"]).strip()
		confidence = float(payload["confidence"])

		if normalized_type == "ner":
			if label not in VALID_LABELS[normalized_type]:
				return None
		else:
			if label.lower() not in VALID_LABELS[normalized_type]:
				return None
			label = label.lower()

		if not (0.0 <= confidence <= 1.0):
			return None

		if not reason:
			return None

		return LabelResult(
			label=label,
			confidence=confidence,
			reason=reason,
			llm_used="unknown",
			needs_review=False,
			label_type=normalized_type,
			raw_response=raw,
		)
	except Exception:  # noqa: BLE001
		return None


def label_with_claude(text: str, label_type: str, language_name: str) -> LabelResult | None:
	try:
		api_key = os.getenv("ANTHROPIC_API_KEY", "")
		if not api_key:
			return None

		prompt = build_prompt(label_type, text, language_name)

		from anthropic import Anthropic

		CLAUDE_RATE_LIMITER.wait()
		client = Anthropic(api_key=api_key)
		response = client.messages.create(
			model="claude-sonnet-4-20250514",
			max_tokens=200,
			messages=[{"role": "user", "content": prompt}],
		)

		response_text = ""
		if getattr(response, "content", None):
			response_text = str(response.content[0].text)

		parsed = parse_llm_response(response_text, label_type)
		if parsed is None:
			return None
		if parsed.confidence < 0.75:
			return None

		parsed.llm_used = "claude"
		parsed.needs_review = False
		return parsed
	except Exception:  # noqa: BLE001
		return None


def label_with_openai(text: str, label_type: str, language_name: str) -> LabelResult | None:
	try:
		api_key = os.getenv("OPENAI_API_KEY", "")
		if not api_key:
			return None

		prompt = build_prompt(label_type, text, language_name)

		from openai import OpenAI

		OPENAI_RATE_LIMITER.wait()
		client = OpenAI(api_key=api_key)
		response = client.chat.completions.create(
			model="gpt-4o",
			max_tokens=200,
			messages=[{"role": "user", "content": prompt}],
			response_format={"type": "json_object"},
		)

		response_text = str(response.choices[0].message.content or "")
		parsed = parse_llm_response(response_text, label_type)
		if parsed is None:
			return None
		if parsed.confidence < 0.75:
			return None

		parsed.llm_used = "openai"
		parsed.needs_review = False
		return parsed
	except Exception:  # noqa: BLE001
		return None


def label_with_ollama(text: str, label_type: str, language_name: str) -> LabelResult | None:
	try:
		base_url = (
			os.getenv("OLLAMA_ENDPOINT", "").strip()
			or os.getenv("OLLAMA_BASE_URL", "").strip()
		).rstrip("/")
		model = os.getenv("OLLAMA_MODEL", "").strip()
		api_key = os.getenv("OLLAMA_API_KEY", "").strip()
		timeout = int(os.getenv("OLLAMA_TIMEOUT", "60"))
		auth_header_name = os.getenv("OLLAMA_AUTH_HEADER", "Authorization").strip() or "Authorization"

		if not base_url or not model:
			return None

		prompt = build_prompt(label_type, text, language_name)
		OLLAMA_RATE_LIMITER.wait()

		import requests

		response = requests.post(
			f"{base_url}/api/chat",
			headers={
				auth_header_name: f"Bearer {api_key}",
				"Content-Type": "application/json",
			},
			json={
				"model": model,
				"messages": [{"role": "user", "content": prompt}],
				"stream": False,
				"options": {
					"temperature": 0.1,
				},
			},
			timeout=timeout,
		)
		response.raise_for_status()
		payload = response.json()
		response_text = ""
		if isinstance(payload, dict) and isinstance(payload.get("message"), dict):
			response_text = str(payload["message"].get("content", ""))

		parsed = parse_llm_response(response_text, label_type)
		if parsed is None:
			return None
		if parsed.confidence < 0.75:
			return None

		parsed.llm_used = "ollama"
		parsed.needs_review = False
		return parsed
	except Exception:  # noqa: BLE001
		return None


def label_text(text: str, label_type: str, language_name: str) -> LabelResult:
	try:
		claude_result = label_with_claude(text, label_type, language_name)
		if claude_result is not None:
			return claude_result

		openai_result = label_with_openai(text, label_type, language_name)
		if openai_result is not None:
			return openai_result

		ollama_result = label_with_ollama(text, label_type, language_name)
		if ollama_result is not None:
			return ollama_result
	except Exception:  # noqa: BLE001
		pass

	return LabelResult(
		label="unknown",
		confidence=0.0,
		reason="Both LLMs failed or returned low confidence",
		llm_used="needs_review",
		needs_review=True,
		label_type=(label_type or "").lower(),
		raw_response="",
	)


def label_row(row: dict, label_type: str, language_config: dict) -> dict:
	updated_row = dict(row)
	language_name = str(language_config["name"])
	text = str(updated_row.get("text_clean", ""))
	normalized_label_type = (label_type or "").lower()

	if normalized_label_type == "all":
		sentiment_result = label_text(text, "sentiment", language_name)
		topic_result = label_text(text, "topic", language_name)
		ner_result = label_text(text, "ner", language_name)

		updated_row["label_sentiment"] = sentiment_result.label
		updated_row["label_topic"] = topic_result.label
		updated_row["label_ner"] = ner_result.label
		updated_row["confidence"] = (
			sentiment_result.confidence + topic_result.confidence + ner_result.confidence
		) / 3.0
		updated_row["confidence_reason"] = " | ".join(
			[sentiment_result.reason, topic_result.reason, ner_result.reason]
		)
		updated_row["llm_used"] = "/".join(
			[sentiment_result.llm_used, topic_result.llm_used, ner_result.llm_used]
		)
		updated_row["needs_review"] = (
			sentiment_result.needs_review or topic_result.needs_review or ner_result.needs_review
		)
		return updated_row

	single_result = label_text(text, normalized_label_type, language_name)
	updated_row["label_sentiment"] = None
	updated_row["label_topic"] = None
	updated_row["label_ner"] = None

	if normalized_label_type == "sentiment":
		updated_row["label_sentiment"] = single_result.label
	elif normalized_label_type == "topic":
		updated_row["label_topic"] = single_result.label
	elif normalized_label_type == "ner":
		updated_row["label_ner"] = single_result.label
	else:
		raise ValueError(f"Unknown label_type: {label_type}")

	updated_row["confidence"] = single_result.confidence
	updated_row["confidence_reason"] = single_result.reason
	updated_row["llm_used"] = single_result.llm_used
	updated_row["needs_review"] = single_result.needs_review
	return updated_row


def _looks_like_rate_limit_error(message: str) -> bool:
	lowered = (message or "").lower()
	return "rate limit" in lowered or "429" in lowered or "too many requests" in lowered


def run_labeling_pipeline(
	rows: list[dict],
	label_type: str,
	language_config: dict,
	progress_callback: Callable[[int, int], None] | None = None,
) -> LabelingResult:
	labeled_rows: list[dict[str, Any]] = []
	needs_review_rows: list[dict[str, Any]] = []

	rejected_low_confidence = 0
	claude_count = 0
	openai_count = 0
	ollama_count = 0
	needs_review_count = 0

	total = len(rows)
	for index, row in enumerate(rows, start=1):
		updated_row: dict[str, Any] | None = None

		backoffs = [2, 4, 8]
		for attempt in range(0, len(backoffs) + 1):
			try:
				updated_row = label_row(row, label_type, language_config)
				break
			except Exception as labeling_error:  # noqa: BLE001
				if _looks_like_rate_limit_error(str(labeling_error)) and attempt < len(backoffs):
					time.sleep(backoffs[attempt])
					continue
				updated_row = dict(row)
				updated_row["label_sentiment"] = None
				updated_row["label_topic"] = None
				updated_row["label_ner"] = None
				updated_row["confidence"] = 0.0
				updated_row["confidence_reason"] = "Both LLMs failed or returned low confidence"
				updated_row["llm_used"] = "needs_review"
				updated_row["needs_review"] = True
				break

		if updated_row is None:
			updated_row = dict(row)
			updated_row["label_sentiment"] = None
			updated_row["label_topic"] = None
			updated_row["label_ner"] = None
			updated_row["confidence"] = 0.0
			updated_row["confidence_reason"] = "Both LLMs failed or returned low confidence"
			updated_row["llm_used"] = "needs_review"
			updated_row["needs_review"] = True

		if bool(updated_row.get("needs_review", False)):
			needs_review_rows.append(updated_row)
			needs_review_count += 1
		elif float(updated_row.get("confidence", 0.0)) < 0.80:
			rejected_low_confidence += 1
		else:
			labeled_rows.append(updated_row)
			llm_used = str(updated_row.get("llm_used", ""))
			if llm_used == "claude":
				claude_count += 1
			elif llm_used == "openai":
				openai_count += 1
			elif llm_used == "ollama":
				ollama_count += 1

		if progress_callback is not None:
			progress_callback(index, total)

	return LabelingResult(
		labeled_rows=labeled_rows,
		needs_review_rows=needs_review_rows,
		rejected_low_confidence=rejected_low_confidence,
		claude_count=claude_count,
		openai_count=openai_count,
		ollama_count=ollama_count,
		needs_review_count=needs_review_count,
		total_input=len(rows),
		total_output=len(labeled_rows),
	)
