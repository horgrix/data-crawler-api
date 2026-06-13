"""FastAPI 应用基础测试."""

import pytest
from httpx import ASGITransport, AsyncClient

from data_crawler_api.main import app


@pytest.fixture
async def client() -> AsyncClient:
    """创建测试用 AsyncClient."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.mark.asyncio
async def test_health_check(client: AsyncClient):
    """测试健康检查接口."""
    response = await client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "version" in data
    assert "timestamp" in data


@pytest.mark.asyncio
async def test_crawl_endpoint_exists(client: AsyncClient):
    """测试爬取接口存在且可访问."""
    response = await client.post(
        "/api/v1/crawl",
        json={"url": "https://example.com"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status_code"] == 200
    assert data["url"] is not None