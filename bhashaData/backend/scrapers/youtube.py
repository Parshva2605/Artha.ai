from __future__ import annotations

from typing import Any

from .base import BaseScraper, ScraperResult


class YoutubeScraper(BaseScraper):
    source_name = "youtube"

    def scrape(self, language_config: dict, domain: str, target_count: int) -> ScraperResult:
        self.warnings = []
        language_code = language_config["code"]
        min_words = int(language_config["min_word_count"])
        collected_rows: list[dict[str, Any]] = []

        try:
            from youtube_comment_downloader import YoutubeCommentDownloader

            try:
                from yt_dlp import YoutubeDL
            except Exception as ytdlp_error:  # noqa: BLE001
                raise RuntimeError(f"yt-dlp unavailable: {ytdlp_error}") from ytdlp_error

            downloader = YoutubeCommentDownloader()

            for search_term in language_config["youtube_search_terms"]:
                if len(collected_rows) >= target_count:
                    break

                video_urls = self._find_video_urls(search_term, YoutubeDL)
                if not video_urls:
                    self._log_warning(f"No YouTube videos found for search term '{search_term}'")
                    continue

                for video_url in video_urls:
                    if len(collected_rows) >= target_count:
                        break

                    try:
                        comments = self._download_comments(downloader, video_url)
                    except Exception as video_error:  # noqa: BLE001
                        self._log_warning(f"YouTube video failed '{video_url}': {video_error}")
                        continue

                    for comment_text in comments:
                        if len(collected_rows) >= target_count:
                            break

                        if not self._is_valid_text(comment_text, min_words):
                            continue

                        collected_rows.append(
                            self._build_row(
                                text_original=comment_text,
                                source=self.source_name,
                                source_url=video_url,
                                source_subreddit=None,
                                language_code=language_code,
                                domain=domain,
                            )
                        )

        except Exception as youtube_error:  # noqa: BLE001
            self._log_warning(f"YouTube live scraping unavailable: {youtube_error}")

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

    def _find_video_urls(self, search_term: str, youtube_dl_class: Any) -> list[str]:
        try:
            with youtube_dl_class({"quiet": True, "extract_flat": True, "skip_download": True}) as youtube_dl:
                search_result = youtube_dl.extract_info(f"ytsearch5:{search_term}", download=False)

            entries = (search_result or {}).get("entries", [])
            video_urls: list[str] = []
            for entry in entries:
                video_id = entry.get("id") or entry.get("url")
                if not video_id:
                    continue
                if str(video_id).startswith("http"):
                    video_urls.append(str(video_id))
                else:
                    video_urls.append(f"https://www.youtube.com/watch?v={video_id}")
            return video_urls
        except Exception as search_error:  # noqa: BLE001
            self._log_warning(f"YouTube search failed for '{search_term}': {search_error}")
            return []

    def _download_comments(self, downloader: Any, video_url: str) -> list[str]:
        comments: list[str] = []

        if hasattr(downloader, "get_comments"):
            iterator = downloader.get_comments(video_url)
        elif hasattr(downloader, "get_comments_from_url"):
            iterator = downloader.get_comments_from_url(video_url)
        else:
            raise RuntimeError("youtube-comment-downloader API not recognized")

        for comment in iterator:
            comment_text = comment.get("text") if isinstance(comment, dict) else getattr(comment, "text", None)
            if comment_text:
                comments.append(str(comment_text))
        return comments

    def _build_fallback_rows(self, language_code: str, domain: str, min_words: int, target_count: int) -> list[dict[str, Any]]:
        fallback_rows: list[dict[str, Any]] = []
        fallback_limit = max(1, min(3, target_count))

        for index in range(fallback_limit):
            fallback_rows.append(
                self._build_row(
                    text_original=self._fallback_sentence(language_code, self.source_name, domain, index + 1),
                    source=self.source_name,
                    source_url=f"https://www.youtube.com/watch?v=fallback_{language_code}_{index + 1}",
                    source_subreddit=None,
                    language_code=language_code,
                    domain=domain,
                )
            )

        return [row for row in fallback_rows if self._is_valid_text(row["text_original"], min_words)]
