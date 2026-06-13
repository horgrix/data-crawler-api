"""Pydantic 数据模型定义."""

from datetime import datetime

from pydantic import BaseModel, Field, HttpUrl


class CrawlRequest(BaseModel):
    """爬取请求."""

    url: HttpUrl = Field(..., description="目标 URL")
    selector: str | None = Field(None, description="CSS 选择器，用于提取特定内容")
    headers: dict[str, str] | None = Field(None, description="自定义请求头")


class CrawlResponse(BaseModel):
    """爬取响应."""

    url: str = Field(..., description="请求 URL")
    status_code: int = Field(..., description="HTTP 状态码")
    title: str | None = Field(None, description="页面标题")
    content: str | None = Field(None, description="提取的内容")
    raw_length: int = Field(0, description="原始 HTML 长度")
    crawled_at: datetime = Field(default_factory=datetime.now, description="爬取时间")


class HealthResponse(BaseModel):
    """健康检查响应."""

    status: str = Field("ok", description="服务状态")
    version: str = Field(..., description="应用版本")
    timestamp: datetime = Field(default_factory=datetime.now, description="时间戳")