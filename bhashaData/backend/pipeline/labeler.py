from __future__ import annotations

import json
import itertools
import logging
import os
import re
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
GROQ_RATE_LIMITER = _RateLimiter(max_requests_per_second=10.0)
OPENROUTER_RATE_LIMITER = _RateLimiter(max_requests_per_second=10.0)
OLLAMA_RATE_LIMITER = _RateLimiter(max_requests_per_second=10.0)

logger = logging.getLogger(__name__)


_CLAUDE_DISABLED = False
_CLAUDE_DISABLE_REASON = ""
_CLAUDE_DISABLE_LOCK = threading.Lock()

_OPENAI_DISABLED = False
_OPENAI_DISABLE_REASON = ""
_OPENAI_DISABLE_LOCK = threading.Lock()

_GROQ_DISABLED = False
_GROQ_DISABLE_REASON = ""
_GROQ_DISABLE_LOCK = threading.Lock()

_OPENROUTER_DISABLED = False
_OPENROUTER_DISABLE_REASON = ""
_OPENROUTER_DISABLE_LOCK = threading.Lock()

_OPENROUTER_MAX_CONCURRENCY = max(1, int(os.getenv("OPENROUTER_MAX_CONCURRENCY", "4")))
_OPENROUTER_SEMAPHORE = threading.Semaphore(_OPENROUTER_MAX_CONCURRENCY)

_OLLAMA_DISABLED = False
_OLLAMA_DISABLE_REASON = ""
_OLLAMA_DISABLE_LOCK = threading.Lock()

_llm_cycle = None
_groq_key_cycle = None


def _disable_claude(reason: str) -> None:
	global _CLAUDE_DISABLED, _CLAUDE_DISABLE_REASON
	with _CLAUDE_DISABLE_LOCK:
		_CLAUDE_DISABLED = True
		_CLAUDE_DISABLE_REASON = reason


def _is_claude_disabled() -> bool:
	with _CLAUDE_DISABLE_LOCK:
		return _CLAUDE_DISABLED


def _disable_openai(reason: str) -> None:
	global _OPENAI_DISABLED, _OPENAI_DISABLE_REASON
	with _OPENAI_DISABLE_LOCK:
		_OPENAI_DISABLED = True
		_OPENAI_DISABLE_REASON = reason


def _is_openai_disabled() -> bool:
	with _OPENAI_DISABLE_LOCK:
		return _OPENAI_DISABLED


def _disable_groq(reason: str) -> None:
	global _GROQ_DISABLED, _GROQ_DISABLE_REASON
	with _GROQ_DISABLE_LOCK:
		_GROQ_DISABLED = True
		_GROQ_DISABLE_REASON = reason


def _is_groq_disabled() -> bool:
	with _GROQ_DISABLE_LOCK:
		return _GROQ_DISABLED


def _disable_openrouter(reason: str) -> None:
	global _OPENROUTER_DISABLED, _OPENROUTER_DISABLE_REASON
	with _OPENROUTER_DISABLE_LOCK:
		_OPENROUTER_DISABLED = True
		_OPENROUTER_DISABLE_REASON = reason


def _is_openrouter_disabled() -> bool:
	with _OPENROUTER_DISABLE_LOCK:
		return _OPENROUTER_DISABLED


def _disable_ollama(reason: str) -> None:
	global _OLLAMA_DISABLED, _OLLAMA_DISABLE_REASON
	with _OLLAMA_DISABLE_LOCK:
		_OLLAMA_DISABLED = True
		_OLLAMA_DISABLE_REASON = reason


def _is_ollama_disabled() -> bool:
	with _OLLAMA_DISABLE_LOCK:
		return _OLLAMA_DISABLED


def get_next_llm() -> str:
	global _llm_cycle
	available: list[str] = []
	if os.getenv("GROQ_API_KEY"):
		available.append("groq")
	if os.getenv("OPENROUTER_API_KEY"):
		available.append("openrouter")
	if os.getenv("OLLAMA_API_KEY"):
		available.append("ollama")
	if not available:
		available = ["groq"]
	if _llm_cycle is None:
		_llm_cycle = itertools.cycle(available)
	return str(next(_llm_cycle))


def get_groq_keys() -> list[str]:
	keys: list[str] = []
	key1 = (os.getenv("GROQ_API_KEY") or "").strip()
	if key1:
		keys.append(key1)
	key2 = (os.getenv("GROQ_API_KEY_2") or "").strip()
	if key2:
		keys.append(key2)
	key3 = (os.getenv("GROQ_API_KEY_3") or "").strip()
	if key3:
		keys.append(key3)
	legacy_key = (os.getenv("groq") or "").strip()
	if legacy_key and legacy_key not in keys:
		keys.append(legacy_key)
	return keys


def get_next_groq_key() -> str | None:
	global _groq_key_cycle
	keys = get_groq_keys()
	if not keys:
		return None
	if _groq_key_cycle is None:
		_groq_key_cycle = itertools.cycle(keys)
	return str(next(_groq_key_cycle))


def _is_non_retryable_ollama_error(status_code: int, payload_text: str) -> bool:
	lowered = (payload_text or "").lower()
	if status_code in {401, 402, 403, 404}:
		return True
	return any(
		token in lowered
		for token in (
			"insufficient",
			"quota",
			"credit",
			"payment required",
			"unauthorized",
			"forbidden",
			"invalid api key",
			"model not found",
		)
	)


def _is_non_retryable_openrouter_error(status_code: int, payload_text: str) -> bool:
	if status_code in {401, 402, 403, 404, 429}:
		return True
	return _looks_like_non_retryable_provider_error(payload_text)


def _looks_like_non_retryable_provider_error(message: str) -> bool:
	lowered = (message or "").lower()
	return any(
		token in lowered
		for token in (
			"insufficient",
			"quota",
			"credit",
			"payment required",
			"unauthorized",
			"forbidden",
			"invalid api key",
			"incorrect api key",
			"authentication",
		)
	)


def _exception_status_code(exc: Exception) -> int | None:
	response = getattr(exc, "response", None)
	if response is not None:
		status_code = getattr(response, "status_code", None)
		if isinstance(status_code, int):
			return status_code
	status_code = getattr(exc, "status_code", None)
	if isinstance(status_code, int):
		return status_code
	return None


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
	groq_count: int = 0
	claude_count: int = 0
	openai_count: int = 0
	openrouter_count: int = 0
	ollama_count: int = 0
	needs_review_count: int = 0
	total_input: int = 0
	total_output: int = 0


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
		if _is_claude_disabled():
			return None

		api_key = os.getenv("ANTHROPIC_API_KEY", "")
		if not api_key:
			return None
		timeout = min(15.0, float(os.getenv("CLAUDE_TIMEOUT", "15")))

		prompt = build_prompt(label_type, text, language_name)

		from anthropic import Anthropic

		CLAUDE_RATE_LIMITER.wait()
		client = Anthropic(api_key=api_key, timeout=timeout)
		response = client.messages.create(
			model="claude-sonnet-4-20250514",
			max_tokens=200,
			messages=[{"role": "user", "content": prompt}],
			timeout=timeout,
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
	except Exception as exc:  # noqa: BLE001
		status_code = _exception_status_code(exc)
		if status_code in {401, 402, 403, 404, 429} or _looks_like_non_retryable_provider_error(str(exc)):
			_disable_claude(str(exc)[:400])
		return None


def label_with_openai(text: str, label_type: str, language_name: str) -> LabelResult | None:
	try:
		if _is_openai_disabled():
			return None

		api_key = os.getenv("OPENAI_API_KEY", "")
		if not api_key:
			return None
		timeout = min(15.0, float(os.getenv("OPENAI_TIMEOUT", "15")))

		prompt = build_prompt(label_type, text, language_name)

		from openai import OpenAI

		OPENAI_RATE_LIMITER.wait()
		client = OpenAI(api_key=api_key, timeout=timeout)
		response = client.chat.completions.create(
			model="gpt-4o",
			max_tokens=200,
			messages=[{"role": "user", "content": prompt}],
			response_format={"type": "json_object"},
			timeout=timeout,
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
	except Exception as exc:  # noqa: BLE001
		status_code = _exception_status_code(exc)
		if status_code in {401, 402, 403, 404, 429} or _looks_like_non_retryable_provider_error(str(exc)):
			_disable_openai(str(exc)[:400])
		return None


def label_with_groq(text: str, label_type: str, language_name: str) -> LabelResult | None:
	import requests
	from requests.exceptions import Timeout, ConnectionError

	try:
		if _is_groq_disabled():
			return None

		api_key = get_next_groq_key()
		if not api_key:
			return None
		model = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant").strip() or "llama-3.1-8b-instant"
		timeout = 10

		prompt = build_prompt(label_type, text, language_name)
		# Truncate text to max 500 characters to avoid 413 errors.
		text = text[:500] if len(text) > 500 else text
		prompt = build_prompt(label_type, text, language_name)

		GROQ_RATE_LIMITER.wait()
		time.sleep(2.0)
		response = requests.post(
			"https://api.groq.com/openai/v1/chat/completions",
			headers={
				"Authorization": f"Bearer {api_key}",
				"Content-Type": "application/json",
			},
			json={
				"model": model,
				"messages": [{"role": "user", "content": prompt}],
				"max_tokens": 200,
				"temperature": 0.1,
			},
			timeout=timeout,
		)

		if response.status_code == 429:
			print("[GROQ] Key rate limited, will rotate next call")
			return None
		if response.status_code != 200:
			print(f"[GROQ] Status {response.status_code}")
			return None

		response.raise_for_status()
		payload = response.json()
		response_text = str(payload["choices"][0]["message"]["content"])
		parsed = parse_llm_response(response_text, label_type)
		if parsed is None:
			return None
		if parsed.confidence < 0.75:
			return None

		parsed.llm_used = "groq"
		parsed.needs_review = False
		return parsed
	except Timeout:
		print("[GROQ] Request timed out")
		return None
	except ConnectionError as e:
		print(f"[GROQ] Connection error: {e}")
		return None
	except Exception as e:  # noqa: BLE001
		print(f"[GROQ ERROR] {e}")
		return None


def label_with_openrouter(text: str, label_type: str, language_name: str) -> LabelResult | None:
	import os
	import requests

	try:
		if _is_openrouter_disabled():
			return None

		with _OPENROUTER_SEMAPHORE:
			if _is_openrouter_disabled():
				return None

			api_key = os.getenv("OPENROUTER_API_KEY")
			model = os.getenv(
				"OPENROUTER_MODEL",
				"mistralai/mistral-7b-instruct:free"
			)

			if not api_key:
				return None

			prompt = build_prompt(label_type, text, language_name)
			OPENROUTER_RATE_LIMITER.wait()

			response = requests.post(
				"https://openrouter.ai/api/v1/chat/completions",
				headers={
					"Authorization": f"Bearer {api_key}",
					"Content-Type": "application/json",
					"HTTP-Referer": "https://arthaai.com",
					"X-Title": "Artha AI",
				},
				json={
					"model": model,
					"messages": [{"role": "user", "content": prompt}],
					"max_tokens": 200,
					"temperature": 0.1,
				},
				timeout=15,
			)

			if response.status_code >= 400:
				payload_text = response.text[:500]
				if response.status_code == 429:
					logger.warning("OpenRouter rate limited, skipping")
					return None
				if _is_non_retryable_openrouter_error(response.status_code, payload_text):
					_disable_openrouter(payload_text)
				return None

			response.raise_for_status()
			data = response.json()
			response_text = str(data["choices"][0]["message"]["content"])

		parsed = parse_llm_response(response_text, label_type)
		if parsed is None:
			return None
		if parsed.confidence < 0.75:
			return None

		parsed.llm_used = "openrouter"
		parsed.needs_review = False
		return parsed
	except Exception as exc:  # noqa: BLE001
		status_code = _exception_status_code(exc)
		message = str(exc)
		if status_code is not None and _is_non_retryable_openrouter_error(status_code, message):
			_disable_openrouter(message[:400])
		elif _looks_like_non_retryable_provider_error(message):
			_disable_openrouter(message[:400])
		return None


def label_with_ollama(text: str, label_type: str, language_name: str) -> LabelResult | None:
	import requests

	try:
		if _is_ollama_disabled():
			return None

		base_url = os.getenv("OLLAMA_ENDPOINT", os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")).rstrip("/")
		model = os.getenv("OLLAMA_MODEL", "llama3.1:8b")
		api_key = os.getenv("OLLAMA_API_KEY", "").strip()
		timeout = min(15, int(os.getenv("OLLAMA_TIMEOUT", "15")))

		prompt = build_prompt(label_type, text, language_name)
		OLLAMA_RATE_LIMITER.wait()

		headers = {"Content-Type": "application/json"}
		if api_key:
			headers["Authorization"] = f"Bearer {api_key}"

		response = requests.post(
			f"{base_url}/chat/completions",
			headers=headers,
			json={
				"model": model,
				"messages": [{"role": "user", "content": prompt}],
				"max_tokens": 200,
				"temperature": 0.1,
			},
			timeout=timeout,
		)

		if response.status_code >= 400:
			payload_text = response.text[:500]
			if _is_non_retryable_ollama_error(response.status_code, payload_text):
				_disable_ollama(payload_text)
			return None

		response.raise_for_status()
		data = response.json()
		response_text = str(data["choices"][0]["message"]["content"])

		parsed = parse_llm_response(response_text, label_type)
		if parsed is None:
			return None
		if parsed.confidence < 0.75:
			return None

		parsed.llm_used = "ollama"
		parsed.needs_review = False
		return parsed
	except requests.Timeout:
		return None
	except Exception as exc:  # noqa: BLE001
		status_code = _exception_status_code(exc)
		message = str(exc)
		if status_code is not None and _is_non_retryable_ollama_error(status_code, message):
			_disable_ollama(message[:400])
		elif _looks_like_non_retryable_provider_error(message):
			_disable_ollama(message[:400])
		return None


def label_text(text: str, label_type: str, language_name: str) -> LabelResult:
	try:
		primary = get_next_llm()

		if primary == "groq":
			result = label_with_groq(text, label_type, language_name)
			if result is not None:
				return result
			result = label_with_openrouter(text, label_type, language_name)
			if result is not None:
				return result
			result = label_with_ollama(text, label_type, language_name)
			if result is not None:
				return result

		elif primary == "openrouter":
			result = label_with_openrouter(text, label_type, language_name)
			if result is not None:
				return result
			result = label_with_groq(text, label_type, language_name)
			if result is not None:
				return result
			result = label_with_ollama(text, label_type, language_name)
			if result is not None:
				return result

		elif primary == "ollama":
			result = label_with_ollama(text, label_type, language_name)
			if result is not None:
				return result
			result = label_with_groq(text, label_type, language_name)
			if result is not None:
				return result
			result = label_with_openrouter(text, label_type, language_name)
			if result is not None:
				return result
	except Exception:  # noqa: BLE001
		pass

	return LabelResult(
		label="unknown",
		confidence=0.0,
		reason="All LLMs failed",
		llm_used="needs_review",
		needs_review=True,
		label_type=(label_type or "").lower(),
		raw_response="",
	)


def _rule_based_label(text: str, label_type: str) -> LabelResult | None:
	normalized = (label_type or "").lower().strip()
	text_lower = (text or "").lower()

	if normalized == "sentiment":
		positive_terms = {
			"good", "great", "excellent", "love", "awesome", "amazing", "happy", "best",
			"nice", "liked", "like", "fantastic", "wonderful", "super", "satisfied",
		}
		negative_terms = {
			"bad", "worst", "hate", "awful", "terrible", "poor", "angry", "disappointed",
			"bug", "issue", "problem", "slow", "crash", "broken", "useless",
		}
		pos_hits = sum(1 for token in positive_terms if token in text_lower)
		neg_hits = sum(1 for token in negative_terms if token in text_lower)

		if pos_hits > neg_hits:
			label = "positive"
		elif neg_hits > pos_hits:
			label = "negative"
		else:
			label = "neutral"

		return LabelResult(
			label=label,
			confidence=0.84,
			reason="Rule-based fallback used because external LLM providers were unavailable",
			llm_used="rule_fallback",
			needs_review=False,
			label_type="sentiment",
			raw_response="",
		)

	if normalized == "topic":
		topic_rules = {
			"sports": {"match", "cricket", "football", "soccer", "tournament", "player", "team", "score"},
			"technology": {"app", "software", "ai", "tech", "phone", "mobile", "internet", "code", "update"},
			"food": {"food", "restaurant", "taste", "eat", "dish", "meal", "recipe"},
			"health": {"health", "hospital", "doctor", "medicine", "fitness", "disease"},
			"finance": {"money", "bank", "loan", "price", "market", "stock", "payment", "budget"},
			"education": {"school", "college", "student", "teacher", "exam", "class", "course"},
			"politics": {"election", "government", "minister", "policy", "party", "vote"},
			"entertainment": {"movie", "music", "song", "show", "actor", "series", "video"},
		}

		best_topic = "other"
		best_hits = 0
		for topic, terms in topic_rules.items():
			hits = sum(1 for token in terms if token in text_lower)
			if hits > best_hits:
				best_hits = hits
				best_topic = topic

		return LabelResult(
			label=best_topic,
			confidence=0.82,
			reason="Rule-based fallback used because external LLM providers were unavailable",
			llm_used="rule_fallback",
			needs_review=False,
			label_type="topic",
			raw_response="",
		)

	if normalized == "ner":
		if re.search(r"\b\d{1,2}[-/]\d{1,2}[-/]\d{2,4}\b", text) or re.search(r"\b\d{4}\b", text):
			label = "DATE"
		elif any(symbol in text for symbol in ("$", "₹", "€", "£")):
			label = "CURRENCY"
		elif any(keyword in text_lower for keyword in ("inc", "ltd", "corp", "company", "university", "bank")):
			label = "ORGANIZATION"
		elif any(keyword in text_lower for keyword in ("city", "village", "state", "country", "street", "road")):
			label = "LOCATION"
		else:
			label = "OTHER"

		return LabelResult(
			label=label,
			confidence=0.81,
			reason="Rule-based fallback used because external LLM providers were unavailable",
			llm_used="rule_fallback",
			needs_review=False,
			label_type="ner",
			raw_response="",
		)

	return None


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
	groq_count = 0
	claude_count = 0
	openai_count = 0
	openrouter_count = 0
	ollama_count = 0
	needs_review_count = 0

	total = len(rows)
	all_llms_unavailable_logged = False
	batch_size = 5

	for i in range(0, total, batch_size):
		batch = rows[i:i + batch_size]
		for offset, row in enumerate(batch, start=1):
			index = i + offset
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
					updated_row["confidence_reason"] = "All LLMs failed or returned low confidence"
					updated_row["llm_used"] = "needs_review"
					updated_row["needs_review"] = True
					break

			if updated_row is None:
				updated_row = dict(row)
				updated_row["label_sentiment"] = None
				updated_row["label_topic"] = None
				updated_row["label_ner"] = None
				updated_row["confidence"] = 0.0
				updated_row["confidence_reason"] = "All LLMs failed or returned low confidence"
				updated_row["llm_used"] = "needs_review"
				updated_row["needs_review"] = True

			if bool(updated_row.get("needs_review", False)):
				needs_review_rows.append(updated_row)
				needs_review_count += 1
				logger.warning(
					"Labeling failed for row %s/%s: %s",
					index,
					total,
					str(updated_row.get("confidence_reason", "LLM unavailable")),
				)
			elif float(updated_row.get("confidence", 0.0)) < 0.80:
				rejected_low_confidence += 1
			else:
				labeled_rows.append(updated_row)
				llm_used = str(updated_row.get("llm_used", ""))
				if llm_used == "claude":
					claude_count += 1
				elif llm_used == "groq":
					groq_count += 1
				elif llm_used == "openrouter":
					openrouter_count += 1
				elif llm_used == "openai":
					openai_count += 1
				elif llm_used == "ollama":
					ollama_count += 1

			if index == 3 and needs_review_count == 3 and not all_llms_unavailable_logged:
				logger.warning("All LLMs appear to be unavailable. Check API keys.")
				all_llms_unavailable_logged = True

		if i + batch_size < total:
			time.sleep(3.0)

		if progress_callback is not None:
			progress_callback(min(i + batch_size, total), total)

	return LabelingResult(
		labeled_rows=labeled_rows,
		needs_review_rows=needs_review_rows,
		rejected_low_confidence=rejected_low_confidence,
		groq_count=groq_count,
		claude_count=claude_count,
		openai_count=openai_count,
		openrouter_count=openrouter_count,
		ollama_count=ollama_count,
		needs_review_count=needs_review_count,
		total_input=len(rows),
		total_output=len(labeled_rows),
	)
