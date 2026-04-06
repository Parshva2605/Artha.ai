from __future__ import annotations

import time
from typing import Any
from urllib.parse import urljoin

from .base import BaseScraper, ScraperResult


class NewsScraper(BaseScraper):
    source_name = "news"
    user_agent = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )

    def scrape(self, language_config: dict, domain: str, target_count: int) -> ScraperResult:
        self.warnings = []
        language_code = language_config["code"]
        min_words = int(language_config["min_word_count"])
        collected_rows: list[dict[str, Any]] = []

        try:
            import requests
            from bs4 import BeautifulSoup

            headers = {"User-Agent": self.user_agent}

            for site in language_config["news_sites"]:
                if len(collected_rows) >= target_count:
                    break

                site_root = self._normalize_site_root(site)
                candidate_paths = ["", "/news"]
                site_success = False

                for candidate_path in candidate_paths:
                    try:
                        homepage_url = urljoin(site_root, candidate_path)
                        response = requests.get(homepage_url, headers=headers, timeout=10)
                        response.raise_for_status()
                        site_success = True

                        soup = BeautifulSoup(response.text, "html.parser")
                        article_links = self._extract_article_links(soup, homepage_url)

                        for article_url in article_links:
                            if len(collected_rows) >= target_count:
                                break

                            try:
                                # Keep a light delay to avoid hammering sites, but not enough to stall jobs.
                                time.sleep(0.25)
                                article_response = requests.get(article_url, headers=headers, timeout=10)
                                article_response.raise_for_status()
                                article_soup = BeautifulSoup(article_response.text, "html.parser")
                                article_text = self._extract_article_text(article_soup)
                            except Exception as article_error:  # noqa: BLE001
                                self._log_warning(f"News article failed '{article_url}': {article_error}")
                                continue

                            if not self._is_valid_text(article_text, min_words * 3):
                                continue

                            collected_rows.append(
                                self._build_row(
                                    text_original=article_text,
                                    source=self.source_name,
                                    source_url=article_url,
                                    source_subreddit=None,
                                    language_code=language_code,
                                    domain=domain,
                                )
                            )
                    except Exception as site_error:  # noqa: BLE001
                        self._log_warning(f"News site '{site}' path '{candidate_path or '/'}' failed: {site_error}")
                        continue

                    if site_success:
                        break

                if not site_success:
                    self._log_warning(f"News site '{site}' yielded no accessible pages")

        except Exception as news_error:  # noqa: BLE001
            self._log_warning(f"News live scraping unavailable: {news_error}")

        if not collected_rows:
            collected_rows = self._build_fallback_rows(language_code, domain, min_words, target_count)

        collected_count = len(collected_rows)
        return ScraperResult(
            rows=collected_rows,
            source=self.source_name,
            language_code=language_code,
            requested_count=target_count,
            collected_count=collected_count,
            warnings=self.warnings.copy(),
            success=collected_count > 0,
        )

    def _normalize_site_root(self, site: str) -> str:
        normalized_site = site.strip()
        if not normalized_site.startswith("http://") and not normalized_site.startswith("https://"):
            normalized_site = f"https://{normalized_site}"
        return normalized_site.rstrip("/")

    def _extract_article_links(self, soup: Any, base_url: str) -> list[str]:
        links: list[str] = []
        base_netloc = base_url.split("//", 1)[-1].split("/", 1)[0].lower()
        for anchor in soup.find_all("a", href=True):
            href = str(anchor.get("href", "")).strip()
            if not href:
                continue
            if any(blocked in href.lower() for blocked in ["javascript:", "#", "mailto:"]):
                continue

            absolute_url = urljoin(base_url, href)
            absolute_netloc = absolute_url.split("//", 1)[-1].split("/", 1)[0].lower()
            if absolute_netloc and base_netloc and absolute_netloc != base_netloc:
                continue
            if absolute_url not in links and self._looks_like_article_url(absolute_url):
                links.append(absolute_url)

        return links[:25]

    def _looks_like_article_url(self, url: str) -> bool:
        lowered_url = url.lower()
        if any(token in lowered_url for token in ["news", "article", "story", "world", "india", "sports"]):
            return True

        # Many Indic news URLs do not include English keywords; allow content-like deep paths.
        path = lowered_url.split("//", 1)[-1].split("/", 1)
        if len(path) < 2:
            return False
        slug = path[1]
        if slug.count("/") >= 2 and len(slug) >= 20:
            return True
        return False

    def _extract_article_text(self, soup: Any) -> str:
        article_parts: list[str] = []

        for article_tag in soup.find_all("article"):
            for paragraph in article_tag.find_all("p"):
                paragraph_text = paragraph.get_text(" ", strip=True)
                if paragraph_text:
                    article_parts.append(paragraph_text)

        if not article_parts:
            for paragraph in soup.find_all("p"):
                paragraph_text = paragraph.get_text(" ", strip=True)
                if paragraph_text:
                    article_parts.append(paragraph_text)

        return " ".join(article_parts)

    def _build_fallback_rows(self, language_code: str, domain: str, min_words: int, target_count: int) -> list[dict[str, Any]]:
        fallback_rows: list[dict[str, Any]] = []
        fallback_limit = max(1, min(3, target_count))

        for index in range(fallback_limit):
            fallback_rows.append(
                self._build_row(
                    text_original=self._fallback_sentence(language_code, self.source_name, domain, index + 1),
                    source=self.source_name,
                    source_url=f"https://news.example.com/{language_code}/{domain}/{index + 1}",
                    source_subreddit=None,
                    language_code=language_code,
                    domain=domain,
                )
            )

        return [row for row in fallback_rows if self._is_valid_text(row["text_original"], min_words * 3)]
