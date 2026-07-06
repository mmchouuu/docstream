"""
Unit tests for ZendeskScraper class.
"""
import unittest
from unittest.mock import patch, MagicMock
from pathlib import Path
import tempfile
import shutil
import json

from src.ingestion.scraper import ZendeskScraper

class TestZendeskScraper(unittest.TestCase):

    def setUp(self) -> None:
        self.api_url = "https://example.zendesk.com/api/v2/help_center"
        self.page_url = "https://example.zendesk.com"
        self.scraper = ZendeskScraper(
            api_url=self.api_url,
            page_url=self.page_url,
            throttle_ms=0,
            max_retries=2
        )
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self) -> None:
        shutil.rmtree(self.temp_dir)

    @patch("requests.Session.get")
    def test_fetch_articles_api_success(self, mock_get) -> None:
        # Mock successful API paginated response
        mock_response_1 = MagicMock()
        mock_response_1.status_code = 200
        mock_response_1.json.return_value = {
            "articles": [
                {"id": 123, "title": "Article 1", "body": "<p>Content 1</p>", "slug": "art-1"},
                {"id": 124, "title": "Article 2", "body": "<p>Content 2</p>", "slug": "art-2"}
            ],
            "next_page": "https://example.zendesk.com/api/v2/help_center/en-us/articles.json?page=2"
        }
        
        mock_response_2 = MagicMock()
        mock_response_2.status_code = 200
        mock_response_2.json.return_value = {
            "articles": [
                {"id": 125, "title": "Article 3", "body": "<p>Content 3</p>", "slug": "art-3"}
            ],
            "next_page": None
        }
        
        mock_get.side_effect = [mock_response_1, mock_response_2]
        
        articles = self.scraper.fetch_articles_api(limit=10)
        self.assertEqual(len(articles), 3)
        self.assertEqual(articles[0]["title"], "Article 1")
        self.assertEqual(articles[2]["title"], "Article 3")

    @patch("requests.Session.get")
    def test_fetch_articles_api_rate_limiting(self, mock_get) -> None:
        # Mock 429 rate limit then success
        mock_response_429 = MagicMock()
        mock_response_429.status_code = 429
        mock_response_429.headers = {"Retry-After": "0"}
        
        mock_response_200 = MagicMock()
        mock_response_200.status_code = 200
        mock_response_200.json.return_value = {
            "articles": [{"id": 999, "title": "Post Limit Article"}]
        }
        
        mock_get.side_effect = [mock_response_429, mock_response_200]
        
        articles = self.scraper.fetch_articles_api(limit=1)
        self.assertEqual(len(articles), 1)
        self.assertEqual(articles[0]["id"], 999)

    def test_cache_raw_articles(self) -> None:
        articles = [
            {"id": 111, "title": "Test 1"},
            {"id": 222, "title": "Test 2"}
        ]
        cache_path = Path(self.temp_dir)
        self.scraper.cache_raw_articles(articles, cache_path)
        
        file1 = cache_path / "111.json"
        file2 = cache_path / "222.json"
        
        self.assertTrue(file1.exists())
        self.assertTrue(file2.exists())
        
        with open(file1, "r", encoding="utf-8") as f:
            data = json.load(f)
            self.assertEqual(data["title"], "Test 1")

if __name__ == "__main__":
    unittest.main()
