from scrapers.base import BaseScraper, ScrapedRow


class GooglePlayScraper(BaseScraper):
    source_name = "google_play"

    def scrape(self, language_code: str, domain: str, target_count: int) -> list[ScrapedRow]:
        return []
