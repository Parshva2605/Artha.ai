from scrapers.base import BaseScraper, ScrapedRow


class NewsScraper(BaseScraper):
    source_name = "news"

    def scrape(self, language_code: str, domain: str, target_count: int) -> list[ScrapedRow]:
        return []
