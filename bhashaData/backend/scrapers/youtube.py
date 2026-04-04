from scrapers.base import BaseScraper, ScrapedRow


class YouTubeScraper(BaseScraper):
    source_name = "youtube"

    def scrape(self, language_code: str, domain: str, target_count: int) -> list[ScrapedRow]:
        return []
