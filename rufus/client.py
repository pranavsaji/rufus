# rufus/client.py

import asyncio
import logging
from urllib.parse import urljoin, urlparse
from typing import List, Dict, Set, Optional
from playwright.async_api import async_playwright, Page, Browser
from bs4 import BeautifulSoup
from .utils import compute_similarity, extract_keywords
import os

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,  
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class RufusClient:
    def __init__(
        self,
        api_key: str,
        instructions: str,
        keywords: Optional[List[str]] = None,
        max_depth: int = 2,
        max_pages: int = 50,
        similarity_threshold: float = 0.5
    ):
        """
        Initializes the RufusClient.

        :param api_key: API key for authentication.
        :param instructions: Instructions defining what content to extract.
        :param keywords: Optional list of keywords for filtering.
        :param max_depth: Maximum depth to crawl.
        :param max_pages: Maximum number of pages to crawl.
        :param similarity_threshold: Threshold for content relevance.
        """
        self.api_key = api_key
        self.instructions = instructions
        self.keywords = keywords
        self.max_depth = max_depth
        self.max_pages = max_pages
        self.similarity_threshold = similarity_threshold
        self.logger = logging.getLogger(self.__class__.__name__)
        self.browser: Browser = None

        # If keywords are not provided, extract them from instructions
        if not self.keywords:
            self.keywords = extract_keywords(self.instructions)
            if self.keywords:
                self.logger.info(f"Automatically extracted keywords: {self.keywords}")
            else:
                self.logger.warning("No keywords extracted from instructions.")

        # Authenticate the API key
        if not self._authenticate():
            self.logger.error("Invalid API Key provided.")
            raise ValueError("Invalid API Key.")

    def _authenticate(self) -> bool:
        """
        Authenticates the provided API key.
        Placeholder for actual authentication mechanism.

        :return: True if authentication is successful, False otherwise.
        """
        # TODO: Implement actual authentication logic (e.g., verify against a database)
        expected_api_key = os.getenv('RUFUS_API_KEY')
        if self.api_key == expected_api_key:
            self.logger.debug("API Key authentication successful.")
            return True
        else:
            self.logger.debug("API Key authentication failed.")
            return False

    async def scrape(self, base_url: str) -> List[Dict[str, str]]:
        """
        Public method to initiate scraping. Resets internal state before crawling.

        :param base_url: The base URL to start crawling from.
        :return: A list of extracted documents.
        """
        # Reset internal state
        self.visited_urls: Set[str] = set()
        self.results: List[Dict[str, str]] = []
        self.logger.debug("Internal state reset for new scrape operation.")

        # Run the crawler
        results = await self.run(base_url)
        return results

    async def run(self, base_url: str) -> List[Dict[str, str]]:
        """
        Runs the crawler.

        :param base_url: The base URL to start crawling from.
        :return: A list of extracted documents.
        """
        self.logger.debug(f"Initializing Playwright.")
        async with async_playwright() as p:
            self.browser = await p.chromium.launch(headless=True)
            self.logger.debug(f"Browser launched.")
            await self._crawl(base_url, depth=0)
            await self.browser.close()
            self.logger.debug(f"Browser closed.")
        return self.results

    async def _crawl(self, url: str, depth: int):
        """
        Recursively crawls the website.

        :param url: The URL to crawl.
        :param depth: The current depth of crawling.
        """
        if depth > self.max_depth:
            self.logger.debug(f"Max depth {self.max_depth} reached at URL: {url}")
            return
        if url in self.visited_urls:
            self.logger.debug(f"Already visited URL: {url}")
            return
        if len(self.visited_urls) >= self.max_pages:
            self.logger.debug(f"Max pages {self.max_pages} reached.")
            return

        # **Removed robots.txt compliance check**

        self.visited_urls.add(url)
        self.logger.info(f"Crawling URL: {url} at depth {depth}")

        try:
            html = await self._render_page(url)
            content = self._extract_content(html)
            if content:
                is_relevant = compute_similarity(
                    content,
                    self.instructions,
                    self.keywords,
                    self.similarity_threshold
                )
                self.logger.debug(f"Similarity score for URL {url}: {is_relevant}")
                if is_relevant:
                    self.results.append({
                        "url": url,
                        "content": content
                    })
                    self.logger.info(f"Relevant content found at URL: {url}")
        except Exception as e:
            self.logger.error(f"Error processing URL {url}: {e}")

        # Find and crawl links
        links = self._extract_links(html, url)
        self.logger.debug(f"Found {len(links)} links on URL: {url}")

        # Introduce a delay to respect the target server
        await asyncio.sleep(1)  # 1-second delay; adjust as needed

        tasks = []
        for link in links:
            if len(self.visited_urls) >= self.max_pages:
                self.logger.debug(f"Max pages {self.max_pages} reached during link extraction.")
                break
            tasks.append(self._crawl(link, depth + 1))
        
        if tasks:
            await asyncio.gather(*tasks)

    async def _render_page(self, url: str) -> str:
        """
        Renders the page using Playwright and retrieves the HTML content.

        :param url: The URL to render.
        :return: The HTML content of the page.
        """
        if not self.browser:
            self.logger.error("Browser is not initialized.")
            return ""
        page: Page = await self.browser.new_page()
        # Set a custom User-Agent
        await page.set_extra_http_headers({
            "User-Agent": "RufusCrawler/1.0 (+https://github.com/yourusername/rufus)"
        })
        self.logger.debug(f"Navigating to URL: {url}")
        try:
            await page.goto(url, timeout=60000)  # 60 seconds timeout
            await page.wait_for_load_state('networkidle')  # Wait until network is idle
            html = await page.content()
            self.logger.debug(f"Page content retrieved for URL: {url}")
        except Exception as e:
            self.logger.error(f"Error rendering page {url}: {e}")
            html = ""
        await page.close()
        return html

    def _extract_content(self, html: str) -> str:
        """
        Extracts and cleans text content from HTML.

        :param html: The HTML content of the page.
        :return: The extracted text content.
        """
        soup = BeautifulSoup(html, 'html.parser')
        content = soup.get_text(separator=' ', strip=True)
        if content:
            self.logger.debug(f"Extracted content length: {len(content)} characters")
            # Add a snippet of the content for verification
            snippet = content[:200] + '...' if len(content) > 200 else content
            self.logger.debug(f"Content snippet: {snippet}")
            print(f"Extracted content from URL: {snippet}")  # Added print statement for immediate verification
            return content
        else:
            self.logger.warning("No content extracted from the page.")
            return ""

    def _extract_links(self, html: str, current_url: str) -> List[str]:
        """
        Extracts all valid links from the HTML content.

        :param html: The HTML content of the page.
        :param current_url: The URL of the current page.
        :return: A list of valid URLs to crawl.
        """
        soup = BeautifulSoup(html, 'html.parser')
        links = set()
        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href']
            parsed_href = urlparse(href)
            if parsed_href.scheme in ['http', 'https']:
                full_url = href
            else:
                full_url = urljoin(current_url, href)
            if self._is_valid_url(full_url):
                links.add(full_url)
        self.logger.debug(f"Total valid links extracted: {len(links)}")
        return list(links)

    def _is_valid_url(self, url: str) -> bool:
        """
        Checks if the URL is valid (i.e., uses HTTP or HTTPS scheme).

        :param url: The URL to check.
        :return: True if valid, False otherwise.
        """
        parsed_url = urlparse(url)
        is_valid = parsed_url.scheme in ['http', 'https']
        if not is_valid:
            self.logger.debug(f"Ignored invalid URL scheme: {url}")
        return is_valid

   