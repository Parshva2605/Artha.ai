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
