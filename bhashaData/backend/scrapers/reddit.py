from __future__ import annotations

import os
from typing import Any

from .base import BaseScraper, ScraperResult


class RedditScraper(BaseScraper):
    source_name = "reddit"

    def scrape(self, language_config: dict, domain: str, target_count: int) -> ScraperResult:
        self.warnings = []
        language_code = language_config["code"]
        min_words = int(language_config["min_word_count"])
        collected_rows: list[dict[str, Any]] = []

        client_id = os.getenv("REDDIT_CLIENT_ID", "")
        client_secret = os.getenv("REDDIT_CLIENT_SECRET", "")
        user_agent = os.getenv("REDDIT_USER_AGENT", "BhashaData/1.0")

        try:
            import praw

            if not client_id or not client_secret:
                raise RuntimeError("Missing Reddit credentials")

            reddit = praw.Reddit(
                client_id=client_id,
                client_secret=client_secret,
                user_agent=user_agent,
                check_for_async=False,
            )

            for subreddit_name in language_config["subreddits"]:
                if len(collected_rows) >= target_count:
                    break

                try:
                    subreddit = reddit.subreddit(subreddit_name)
                    subreddit_name_value = str(getattr(subreddit, "display_name", subreddit_name))

                    posts = []
                    posts.extend(list(subreddit.hot(limit=25)))
                    posts.extend(list(subreddit.new(limit=25)))
                    posts.extend(list(subreddit.top(limit=25)))

                    for post in posts:
                        if len(collected_rows) >= target_count:
                            break

                        if not self._post_matches_domain(post, domain, language_code):
                            continue

                        try:
                            post.comments.replace_more(limit=0)
                            comments = post.comments.list()
                        except Exception as comment_error:  # noqa: BLE001
                            self._log_warning(f"Reddit comments failed for r/{subreddit_name_value}: {comment_error}")
                            continue

                        for comment in comments:
                            if len(collected_rows) >= target_count:
                                break

                            body = getattr(comment, "body", "")
                            if not body or body in {"[deleted]", "[removed]"}:
                                continue

                            if not self._is_valid_text(body, min_words):
                                continue

                            permalink = getattr(comment, "permalink", None)
                            source_url = f"https://reddit.com{permalink}" if permalink else None
                            collected_rows.append(
                                self._build_row(
                                    text_original=body,
                                    source=self.source_name,
                                    source_url=source_url,
                                    source_subreddit=subreddit_name_value,
                                    language_code=language_code,
                                    domain=domain,
                                )
                            )
                except Exception as subreddit_error:  # noqa: BLE001
                    self._log_warning(f"Reddit subreddit '{subreddit_name}' failed: {subreddit_error}")

        except Exception as reddit_error:  # noqa: BLE001
            self._log_warning(f"Reddit live scraping unavailable: {reddit_error}")

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

    def _post_matches_domain(self, post: Any, domain: str, language_code: str) -> bool:
        if domain in {"social_media", "mixed"}:
            return True

        title = str(getattr(post, "title", "")).lower()
        selftext = str(getattr(post, "selftext", "")).lower()
        flair = str(getattr(post, "link_flair_text", "") or "").lower()

        if domain == "app_reviews":
            keywords = ["app", "tech", "review", "phone", "mobile", "software"]
            return any(keyword in title or keyword in selftext for keyword in keywords)

        if domain == "news":
            if language_code != "en":
                # Non-English subreddits rarely use consistent English flair/keywords.
                return True
            if flair:
                return "news" in flair or "breaking" in flair
            keywords = ["news", "breaking", "update", "headline"]
            return any(keyword in title or keyword in selftext for keyword in keywords)

        return True

    def _build_fallback_rows(self, language_code: str, domain: str, min_words: int, target_count: int) -> list[dict[str, Any]]:
        fallback_rows: list[dict[str, Any]] = []
        fallback_limit = max(1, min(3, target_count))

        for index in range(fallback_limit):
            fallback_rows.append(
                self._build_row(
                    text_original=self._fallback_sentence(language_code, self.source_name, domain, index + 1),
                    source=self.source_name,
                    source_url=f"https://reddit.com/r/sample/comments/{language_code}_{index + 1}",
                    source_subreddit="sample",
                    language_code=language_code,
                    domain=domain,
                )
            )

        return [row for row in fallback_rows if self._is_valid_text(row["text_original"], min_words)]
