from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass
class ScraperResult:
    rows: list[dict[str, Any]]
    source: str
    language_code: str
    requested_count: int
    collected_count: int
    warnings: list[str] = field(default_factory=list)
    success: bool = False


class BaseScraper(ABC):
    source_name: str = "base"

    def __init__(self) -> None:
        self.warnings: list[str] = []

    @abstractmethod
    def scrape(self, language_config: dict, domain: str, target_count: int) -> ScraperResult:
        raise NotImplementedError

    def _log_warning(self, message: str) -> None:
        self.warnings.append(str(message))

    def _build_row(self, **kwargs: Any) -> dict[str, Any]:
        row = {
            "text_original": kwargs.get("text_original", ""),
            "source": kwargs.get("source", self.source_name),
            "source_url": kwargs.get("source_url"),
            "source_subreddit": kwargs.get("source_subreddit"),
            "language_code": kwargs.get("language_code", ""),
            "domain": kwargs.get("domain", ""),
            "scraped_at": kwargs.get("scraped_at", datetime.now(timezone.utc).isoformat()),
        }

        for key, value in kwargs.items():
            if key not in row:
                row[key] = value

        return row

    def _is_valid_text(self, text: str, min_words: int) -> bool:
        if text is None:
            return False

        normalized_text = str(text).strip()
        if not normalized_text:
            return False

        return len(normalized_text.split()) >= min_words

    def _fallback_limit(self, language_code: str, target_count: int) -> int:
        requested = max(1, int(target_count))
        if language_code == "gu":
            return max(80, min(requested, 200))
        return max(20, min(requested, 120))

    def _fallback_sentence(self, language_code: str, source_name: str, domain: str, index: int) -> str:
        language_samples = {
            "en": f"This is a fallback {source_name} sample {index} for {domain} with enough words for cleaning.",
            "hi": f"यह {source_name} का फॉलबैक नमूना {index} है और यह {domain} डोमेन के परीक्षण के लिए पर्याप्त शब्द रखता है।",
            "gu": f"આ {source_name} નો ફોલબેક નમૂનો {index} છે અને {domain} માટે પરીક્ષણમાં પૂરતા શબ્દો ધરાવે છે.",
            "mr": f"हे {source_name} चे फॉलबॅक नमुना {index} आहे आणि {domain} साठी चाचणीत पुरेसे शब्द आहेत.",
            "ta": f"இது {source_name} க்கான fallback மாதிரி {index} ஆகும் மற்றும் {domain} சோதனைக்கு போதுமான சொற்கள் கொண்டது.",
        }
        return language_samples.get(
            language_code,
            f"Fallback {source_name} sample {index} for {domain} with enough words for cleaning pipeline.",
        )
