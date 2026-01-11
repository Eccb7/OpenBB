"""Web scraping utilities for Kenya data sources."""

import asyncio
from typing import Any, Dict, List, Optional
from urllib.parse import urljoin

import aiohttp
from bs4 import BeautifulSoup

# Default headers to appear as a normal browser
DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate",
    "Connection": "keep-alive",
}


class ScraperError(Exception):
    """Base exception for scraping errors."""

    pass


class HTTPError(ScraperError):
    """HTTP request failed."""

    def __init__(self, status: int, message: str):
        self.status = status
        self.message = message
        super().__init__(f"HTTP {status}: {message}")


class ParseError(ScraperError):
    """Failed to parse HTML content."""

    pass


class RateLimiter:
    """Rate limiter for API/scraping requests."""

    def __init__(self, max_requests_per_second: float = 1.0):
        self.max_requests_per_second = max_requests_per_second
        self.min_interval = 1.0 / max_requests_per_second
        self.last_request_time = 0.0

    async def wait(self):
        """Wait if necessary to respect rate limit."""
        now = asyncio.get_event_loop().time()
        time_since_last = now - self.last_request_time

        if time_since_last < self.min_interval:
            await asyncio.sleep(self.min_interval - time_since_last)

        self.last_request_time = asyncio.get_event_loop().time()


class BaseScraper:
    """Base class for web scrapers with retry and rate limiting."""

    def __init__(
        self,
        base_url: str,
        rate_limit: float = 1.0,  # requests per second
        max_retries: int = 3,
        timeout: int = 30,
    ):
        self.base_url = base_url
        self.rate_limiter = RateLimiter(rate_limit)
        self.max_retries = max_retries
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self.session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self):
        """Context manager entry."""
        self.session = aiohttp.ClientSession(
            headers=DEFAULT_HEADERS,
            timeout=self.timeout,
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        if self.session:
            await self.session.close()

    async def fetch(
        self,
        url: str,
        params: Optional[Dict] = None,
        headers: Optional[Dict] = None,
    ) -> str:
        """
        Fetch URL with retry logic and rate limiting.

        Args:
            url: URL to fetch (absolute or relative to base_url)
            params: Query parameters
            headers: Additional headers

        Returns:
            Response text

        Raises:
            HTTPError: If request fails after retries
        """
        if not url.startswith("http"):
            url = urljoin(self.base_url, url)

        request_headers = DEFAULT_HEADERS.copy()
        if headers:
            request_headers.update(headers)

        last_exception = None

        for attempt in range(self.max_retries):
            try:
                # Rate limiting
                await self.rate_limiter.wait()

                # Make request
                async with self.session.get(
                    url,
                    params=params,
                    headers=request_headers,
                ) as response:
                    if response.status == 200:
                        return await response.text()
                    elif response.status == 404:
                        raise HTTPError(404, "Resource not found")
                    elif response.status == 503:
                        # Service unavailable - retry
                        if attempt < self.max_retries - 1:
                            await asyncio.sleep(2 ** attempt)  # Exponential backoff
                            continue
                        raise HTTPError(503, "Service temporarily unavailable")
                    else:
                        raise HTTPError(response.status, f"Request failed: {response.reason}")

            except aiohttp.ClientError as e:
                last_exception = e
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(2 ** attempt)
                    continue
                raise HTTPError(500, f"Network error: {str(e)}")

        # If we get here, all retries failed
        if last_exception:
            raise HTTPError(500, f"Failed after {self.max_retries} attempts: {str(last_exception)}")

    def parse_html(self, html: str) -> BeautifulSoup:
        """
        Parse HTML string into BeautifulSoup object.

        Args:
            html: HTML string

        Returns:
            BeautifulSoup object
        """
        return BeautifulSoup(html, "lxml")

    async def fetch_json(
        self,
        url: str,
        params: Optional[Dict] = None,
        headers: Optional[Dict] = None,
    ) -> Dict | List:
        """
        Fetch JSON API endpoint.

        Args:
            url: URL to fetch
            params: Query parameters
            headers: Additional headers

        Returns:
            Parsed JSON response
        """
        html = await self.fetch(url, params, headers)
        try:
            import json

            return json.loads(html)
        except json.JSONDecodeError as e:
            raise ParseError(f"Failed to parse JSON: {str(e)}")


class NSEScraper(BaseScraper):
    """Scraper for Nairobi Securities Exchange website."""

    NSE_BASE_URL = "https://www.nse.co.ke"

    def __init__(self, rate_limit: float = 0.5):  # 0.5 req/sec = 1 req per 2 seconds
        super().__init__(
            base_url=self.NSE_BASE_URL,
            rate_limit=rate_limit,
        )

    async def fetch_equity_data(self, symbol: str) -> Dict[str, Any]:
        """
        Fetch equity data for a symbol.

        Note: This is a placeholder. Actual implementation depends on NSE website structure.

        Args:
            symbol: Stock symbol

        Returns:
            Dictionary of equity data
        """
        # TODO: Implement based on actual NSE website structure
        raise NotImplementedError("NSE equity scraping not yet implemented")

    async def fetch_index_data(self, index_symbol: str) -> Dict[str, Any]:
        """
        Fetch index data.

        Args:
            index_symbol: Index symbol (e.g., "NSE20")

        Returns:
            Dictionary of index data
        """
        # TODO: Implement based on actual NSE website structure
        raise NotImplementedError("NSE index scraping not yet implemented")


class CBKScraper(BaseScraper):
    """Scraper for Central Bank of Kenya website."""

    CBK_BASE_URL = "https://www.centralbank.go.ke"

    def __init__(self, rate_limit: float = 0.5):
        super().__init__(
            base_url=self.CBK_BASE_URL,
            rate_limit=rate_limit,
        )

    async def fetch_rates(self) -> Dict[str, Any]:
        """
        Fetch CBK interest rates.

        Returns:
            Dictionary of rates data
        """
        # TODO: Implement based on actual CBK website structure
        raise NotImplementedError("CBK rates scraping not yet implemented")

    async def fetch_forex_rates(self) -> Dict[str, Any]:
        """
        Fetch CBK forex rates.

        Returns:
            Dictionary of forex rates
        """
        # TODO: Implement based on actual CBK website structure
        raise NotImplementedError("CBK forex scraping not yet implemented")
