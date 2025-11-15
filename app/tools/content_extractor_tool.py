import aiohttp
import re
from readability import Document
from typing import Optional
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type


class ContentExtractorError(Exception):
    """Raised when content extraction fails."""
    pass


class ContentExtractorTool:
    """
    Fetches a webpage and extracts readable text using readability-lxml.
    Includes retry logic for robustness.
    """

    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = aiohttp.ClientSession()

    async def close(self):
        """Close aiohttp session."""
        if self.session:
            await self.session.close()

    # -----------------------------------------------------------------
    # PUBLIC METHOD: Extract content from a URL
    # -----------------------------------------------------------------
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=6),
        retry=retry_if_exception_type((aiohttp.ClientError, ContentExtractorError)),
    )
    async def extract(self, url: str) -> str:
        """
        Fetch the URL and return cleaned readable text.
        """
        html = await self._fetch_html(url)
        text = self._extract_readable_text(html)
        return text

    # -----------------------------------------------------------------
    # INTERNAL: Fetch raw HTML
    # -----------------------------------------------------------------
    async def _fetch_html(self, url: str) -> str:
        try:
            async with self.session.get(url, timeout=20) as resp:
                if resp.status != 200:
                    raise ContentExtractorError(
                        f"Failed to fetch {url}: status {resp.status}"
                    )
                return await resp.text()

        except aiohttp.ClientError as e:
            raise ContentExtractorError(f"Network error while fetching {url}: {e}")

    # -----------------------------------------------------------------
    # INTERNAL: Extract readable content using Readability
    # -----------------------------------------------------------------
    def _extract_readable_text(self, html: str) -> str:
        """
        Converts HTML → readable content → clean plaintext.
        """
        try:
            doc = Document(html)
            content_html = doc.summary()
        except Exception:
            raise ContentExtractorError("Failed to extract readable content.")

        # Strip HTML tags
        text = re.sub(r"<[^>]+>", "", content_html)

        # Normalize whitespace
        text = re.sub(r"\s+", " ", text).strip()

        # Truncate to reasonable size for LLM
        return text[:20000]
