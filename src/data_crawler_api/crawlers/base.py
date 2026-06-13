"""爬虫基类模块."""

import asyncio
from typing import Any

import httpx
from bs4 import BeautifulSoup
from tenacity import retry, stop_after_attempt, wait_exponential

from data_crawler_api.config import get_settings


class BaseCrawler:
    """爬虫基类，提供通用的网页抓取与解析能力."""

    def __init__(self, client: httpx.AsyncClient | None = None) -> None:
        settings = get_settings()
        self._headers = {"User-Agent": settings.user_agent}
        self._timeout = settings.request_timeout
        self._max_retries = settings.max_retries
        self._client = client
        self._owns_client = client is None

    async def _get_client(self) -> httpx.AsyncClient:
        """获取 HTTP 客户端实例."""
        if self._client is None:
            self._client = httpx.AsyncClient(
                headers=self._headers,
                timeout=self._timeout,
                follow_redirects=True,
            )
        return self._client

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        reraise=True,
    )
    async def fetch(self, url: str, headers: dict[str, str] | None = None) -> httpx.Response:
        """获取 URL 对应的响应.

        Args:
            url: 目标 URL
            headers: 额外的请求头

        Returns:
            HTTP 响应对象
        """
        client = await self._get_client()
        request_headers = {**self._headers}
        if headers:
            request_headers.update(headers)
        response = await client.get(url, headers=request_headers)
        response.raise_for_status()
        return response

    @staticmethod
    def parse_html(html: str, selector: str | None = None) -> BeautifulSoup:
        """解析 HTML 内容.

        Args:
            html: HTML 字符串
            selector: CSS 选择器，可选

        Returns:
            BeautifulSoup 对象或选中元素的文本
        """
        soup = BeautifulSoup(html, "lxml")
        if selector:
            element = soup.select_one(selector)
            if element:
                return element.get_text(strip=True)
            return ""
        return soup

    @staticmethod
    def extract_title(soup: BeautifulSoup) -> str | None:
        """从 BeautifulSoup 对象中提取页面标题."""
        if title_tag := soup.find("title"):
            return title_tag.get_text(strip=True)
        return None

    async def crawl(
        self, url: str, selector: str | None = None
    ) -> dict[str, Any]:
        """执行一次完整的爬取操作.

        Args:
            url: 目标 URL
            selector: 可选的 CSS 选择器

        Returns:
            包含爬取结果的字典
        """
        response = await self.fetch(url)
        html = response.text
        soup = self.parse_html(html)
        title = self.extract_title(soup)

        content: str | None = None
        if selector:
            content = self.parse_html(html, selector)

        return {
            "url": str(response.url),
            "status_code": response.status_code,
            "title": title,
            "content": content,
            "raw_length": len(html),
        }

    async def close(self) -> None:
        """关闭 HTTP 客户端."""
        if self._owns_client and self._client is not None:
            await self._client.aclose()
            self._client = None