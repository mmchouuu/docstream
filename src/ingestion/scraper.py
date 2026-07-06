"""
Zendesk Help Center API Scraper / HTML Crawler
"""
import os
import json
import time
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

class ZendeskScraper:
    """Scraper client to connect to Zendesk Help Center and retrieve articles."""

    def __init__(
        self,
        api_url: str,
        page_url: str,
        token: Optional[str] = None,
        throttle_ms: int = 500,
        max_retries: int = 3
    ) -> None:
        self.api_url = api_url.rstrip("/")
        self.page_url = page_url.rstrip("/")
        self.token = token
        self.throttle_ms = throttle_ms
        self.max_retries = max_retries
        self.session = requests.Session()
        
        # Setup headers
        self.session.headers.update({
            "User-Agent": "DocStream-Bot/1.0",
            "Accept": "application/json"
        })
        if self.token:
            self.session.headers.update({
                "Authorization": f"Bearer {self.token}"
            })

    def fetch_articles_api(self, limit: int = 40) -> List[Dict[str, Any]]:
        """
        Fetch articles via the Zendesk Help Center REST API.
        Attempts to read from the articles endpoint with pagination support.
        """
        articles: List[Dict[str, Any]] = []
        # API URL usually points to .../api/v2/help_center/en-us/articles.json or .../api/v2/help_center/articles.json
        # Zendesk API defaults to 30 articles per page.
        next_url = f"{self.api_url}/en-us/articles.json"
        if not next_url.startswith("http"):
            # Fallback if api_url is just a relative path or domain
            next_url = f"{self.page_url}/api/v2/help_center/en-us/articles.json"

        logger.info(f"Starting API ingestion from {next_url}")
        
        while next_url and len(articles) < limit:
            response_data = self._make_request_with_retry(next_url)
            if not response_data:
                logger.warning("Failed to fetch page data, terminating API ingest.")
                break
            
            page_articles = response_data.get("articles", [])
            if not page_articles:
                break
                
            articles.extend(page_articles)
            logger.info(f"Retrieved {len(page_articles)} articles. Total: {len(articles)}")
            
            # Pagination
            next_url = response_data.get("next_page")
            
            # Throttling
            if next_url and self.throttle_ms > 0:
                time.sleep(self.throttle_ms / 1000.0)
                
        return articles[:limit]

    def crawl_articles_html(self, limit: int = 40) -> List[Dict[str, Any]]:
        """
        Fallback HTML crawler using BeautifulSoup to discover and parse articles
        directly from the public help center webpage.
        """
        logger.info(f"Starting fallback HTML crawler at {self.page_url}")
        articles: List[Dict[str, Any]] = []
        visited_urls = set()
        to_visit = [f"{self.page_url}/hc/en-us"]
        
        headers = {"User-Agent": "DocStream-Bot/1.0"}
        
        while to_visit and len(articles) < limit:
            current_url = to_visit.pop(0)
            if current_url in visited_urls:
                continue
            visited_urls.add(current_url)
            
            try:
                time.sleep(self.throttle_ms / 1000.0)
                response = self.session.get(current_url, headers=headers, timeout=10)
                if response.status_code != 200:
                    continue
                    
                soup = BeautifulSoup(response.text, "html.parser")
                
                # Check if it is an article page (has article content wrapper)
                # Zendesk article body usually has class 'article-body' or 'article-container'
                article_body_div = soup.find(class_="article-body") or soup.find(class_="article-container")
                if article_body_div:
                    title_h1 = soup.find("h1", class_="article-title")
                    title = title_h1.get_text(strip=True) if title_h1 else "Untitled Article"
                    
                    # Generate a pseudo ID from URL or hash
                    slug = current_url.split("/")[-1].split("-")[0]
                    article_id = slug if slug.isdigit() else str(hash(current_url))
                    
                    articles.append({
                        "id": int(article_id) if article_id.isdigit() else article_id,
                        "title": title,
                        "body": str(article_body_div),
                        "html_url": current_url,
                        "updated_at": response.headers.get("Last-Modified", time.strftime("%Y-%m-%dT%H:%M:%SZ")),
                        "slug": current_url.split("/")[-1]
                    })
                    logger.info(f"Crawled article {len(articles)}: {title}")
                    
                # Discover links
                for link in soup.find_all("a", href=True):
                    href = link["href"]
                    if href.startswith("/"):
                        href = self.page_url + href
                    
                    # Only follow English help center links
                    if "/hc/en-us" in href and "#" not in href:
                        if href not in visited_urls and href not in to_visit:
                            # Prioritize article links (usually contains /articles/)
                            if "/articles/" in href:
                                to_visit.insert(0, href)
                            else:
                                to_visit.append(href)
                                
            except Exception as e:
                logger.error(f"Error crawling URL {current_url}: {e}")
                
        return articles[:limit]

    def cache_raw_articles(self, articles: List[Dict[str, Any]], cache_dir: Path) -> None:
        """
        Cache raw article JSON payloads to data/raw/<id>.json.
        """
        cache_dir.mkdir(parents=True, exist_ok=True)
        for article in articles:
            article_id = article.get("id")
            if not article_id:
                continue
            file_path = cache_dir / f"{article_id}.json"
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(article, f, indent=2, ensure_ascii=False)
            except Exception as e:
                logger.error(f"Failed to cache raw article {article_id}: {e}")

    def _make_request_with_retry(self, url: str) -> Optional[Dict[str, Any]]:
        """Helper to make HTTP GET request with retries and exponential backoff."""
        for attempt in range(self.max_retries):
            try:
                response = self.session.get(url, timeout=10)
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 429:
                    retry_after = int(response.headers.get("Retry-After", 2))
                    logger.warning(f"Rate limited (429). Retrying after {retry_after}s.")
                    time.sleep(retry_after)
                else:
                    logger.warning(f"Request failed with status {response.status_code}. Attempt {attempt + 1}/{self.max_retries}")
            except Exception as e:
                logger.warning(f"Request exception: {e}. Attempt {attempt + 1}/{self.max_retries}")
            
            # Exponential backoff
            if attempt < self.max_retries - 1:
                time.sleep(2 ** attempt)
                
        return None
