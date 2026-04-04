from dataclasses import dataclass
from typing import Any


@dataclass
class ScrapedRow:
    text_original: str
    source: str
    source_url: str | None
    source_subreddit: str | None
    extra: dict[str, Any]


class BaseScraper:
    source_name: str = "base"

    def scrape(self, language_code: str, domain: str, target_count: int) -> list[ScrapedRow]:
        raise NotImplementedError
