from scrapers.base import BaseScraper, ScrapedRow


class RedditScraper(BaseScraper):
    source_name = "reddit"

    def scrape(self, language_code: str, domain: str, target_count: int) -> list[ScrapedRow]:
        return []
