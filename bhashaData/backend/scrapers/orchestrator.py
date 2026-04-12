from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from typing import Callable, Any

from .base import ScraperResult
from .google_play import GooglePlayScraper
from .news import NewsScraper
from .youtube import YoutubeScraper


@dataclass
class OrchestratorResult:
    rows: list[dict[str, Any]]
    language_code: str
    total_collected: int
    per_scraper_counts: dict[str, int]
    warnings: list[str] = field(default_factory=list)
    scrapers_failed: list[str] = field(default_factory=list)


def run_scrapers_for_language(
    language_config: dict,
    domain: str,
    target_count: int,
    progress_callback: Callable[[int, int], None] | None = None,
) -> OrchestratorResult:
    if language_config["code"] == "gu":
        effective_target = target_count * 8
    else:
        effective_target = target_count * 5

    scrapers = [
        YoutubeScraper(),
        GooglePlayScraper(),
        NewsScraper(),
    ]
    total_scrapers = len(scrapers)
    completed_scrapers = 0
    rows: list[dict[str, Any]] = []
    warnings: list[str] = []
    scrapers_failed: list[str] = []
    per_scraper_counts: dict[str, int] = {
        scraper.source_name: 0 for scraper in scrapers
    }

    with ThreadPoolExecutor(max_workers=4) as executor:
        future_map = {
            executor.submit(scraper.scrape, language_config, domain, effective_target): scraper
            for scraper in scrapers
        }

        for future in as_completed(future_map):
            scraper = future_map[future]
            completed_scrapers += 1

            try:
                result = future.result()
                if not isinstance(result, ScraperResult):
                    raise RuntimeError(f"{scraper.source_name} returned an invalid result")

                rows.extend(result.rows)
                per_scraper_counts[scraper.source_name] = result.collected_count
                warnings.extend(result.warnings)
                if result.collected_count == 0:
                    scrapers_failed.append(scraper.source_name)
            except Exception as scraper_error:  # noqa: BLE001
                error_message = f"{scraper.source_name} failed: {scraper_error}"
                warnings.append(error_message)
                scrapers_failed.append(scraper.source_name)

            if progress_callback is not None:
                progress_callback(completed_scrapers, total_scrapers)

    total_collected = len(rows)
    if total_collected == 0:
        raise RuntimeError(f"No data collected for {language_config['code']}")

    return OrchestratorResult(
        rows=rows,
        language_code=language_config["code"],
        total_collected=total_collected,
        per_scraper_counts=per_scraper_counts,
        warnings=warnings,
        scrapers_failed=scrapers_failed,
    )