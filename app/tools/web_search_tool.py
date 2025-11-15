import aiohttp
import os
import re
from typing import List, Dict, Optional
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type


class WebSearchError(Exception):
    """Raised when search operation fails."""
    pass


class WebSearchTool:
    """
    Web Search Tool:
    - If BING_API_KEY is present → uses Bing Web Search API
    - Otherwise → falls back to DuckDuckGo HTML scraping
    """

    def __init__(self):
        self.bing_key = os.getenv("BING_API_KEY")
        self.session = aiohttp.ClientSession()

    async def close(self):
        """Close aiohttp session."""
        await self.session.close()

    # -------------------------------------------------------------
    # PUBLIC METHOD: Perform Search
    # -------------------------------------------------------------
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=6),
        retry=retry_if_exception_type((aiohttp.ClientError, WebSearchError)),
    )
    async def search(self, query: str, count: int = 5) -> List[Dict[str, str]]:
        """
        Returns: list of { title, url, snippet }
        """
        if self.bing_key:
            return await self._bing_search(query, count)
        return await self._duckduckgo_search(query, count)

    # -------------------------------------------------------------
    # BING SEARCH API
    # -------------------------------------------------------------
    async def _bing_search(self, query: str, count: int):
        """
        Uses Bing Web Search API via Microsoft Cognitive Services.
        """
        endpoint = "https://api.bing.microsoft.com/v7.0/search"
        headers = {"Ocp-Apim-Subscription-Key": self.bing_key}
        params = {"q": query, "count": count}

        async with self.session.get(endpoint, headers=headers, params=params, timeout=15) as resp:
            if resp.status != 200:
                text = await resp.text()
                raise WebSearchError(f"Bing search failed ({resp.status}): {text}")

            data = await resp.json()

        results = []
        web_pages = data.get("webPages", {}).get("value", [])

        for page in web_pages[:count]:
            results.append(
                {
                    "title": page.get("name", ""),
                    "url": page.get("url", ""),
                    "snippet": page.get("snippet", ""),
                }
            )

        return results

    # -------------------------------------------------------------
    # DUCKDUCKGO FALLBACK (HTML SCRAPING)
    # -------------------------------------------------------------
    async def _duckduckgo_search(self, query: str, count: int):
        """
        DuckDuckGo HTML fallback search.
        This is not officially supported but works for basic retrieval.
        """
        search_url = "https://duckduckgo.com/html/"
        data = {"q": query}

        async with self.session.post(search_url, data=data, timeout=15) as resp:
            if resp.status != 200:
                raise WebSearchError(f"DuckDuckGo search failed ({resp.status})")

            html = await resp.text()

        # Extract result links
        urls = re.findall(
            r'<a rel="noopener" class="result__a" href="(https?://[^"]+)"',
            html,
        )

        results = []
        for u in urls[:count]:
            results.append({"title": "", "url": u, "snippet": ""})

        if not results:
            raise WebSearchError("No results found from DuckDuckGo.")

        return results
