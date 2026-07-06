"""
Zendesk Help Center API Scraper / HTML Crawler
"""
class ZendeskScraper:
    """Scraper client to connect to Zendesk Help Center and retrieve articles."""
    def __init__(self, api_url: str, token: str = None) -> None:
        self.api_url = api_url
        self.token = token
