"""API 路由定义."""

from datetime import datetime

from fastapi import APIRouter, HTTPException

from data_crawler_api import __version__
from data_crawler_api.crawlers.base import BaseCrawler
from data_crawler_api.models.schemas import CrawlRequest, CrawlResponse, HealthResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse, tags=["系统"])
async def health_check():
    """健康检查接口."""
    return HealthResponse(
        status="ok",
        version=__version__,
        timestamp=datetime.now(),
    )


@router.post("/crawl", response_model=CrawlResponse, tags=["爬虫"])
async def crawl_url(request: CrawlRequest):
    """爬取指定 URL 并返回解析结果."""
    crawler = BaseCrawler()
    try:
        result = await crawler.crawl(
            url=str(request.url),
            selector=request.selector,
        )
        return CrawlResponse(
            url=result["url"],
            status_code=result["status_code"],
            title=result["title"],
            content=result["content"] if request.selector else None,
            raw_length=result["raw_length"],
            crawled_at=datetime.now(),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"爬取失败: {str(e)}") from e
    finally:
        await crawler.close()