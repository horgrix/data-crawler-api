"""Pydantic 数据模型定义."""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field

class HealthResponse(BaseModel):
    """健康检查响应."""

    status: str = Field("ok", description="服务状态")
    version: str = Field(..., description="应用版本")
    timestamp: datetime = Field(default_factory=datetime.now, description="时间戳")


# ========== Steam 相关模型 ==========


class RegionRankType(str, Enum):
    """地区排名时间类型."""

    WEEKLY = "weekly"
    HOURLY = "hourly"


class PlayersType(str, Enum):
    """玩家数时间类型."""

    MONTHLY = "monthly"
    DAILY = "daily"
    HOURLY = "hourly"


class RecommendationsType(str, Enum):
    """推荐评价时间类型."""

    ROLLUP = "rollup"
    RECENT = "recent"


class SteamQueryBase(BaseModel):
    """Steam 查询基类参数."""

    start_date: str = Field(
        ..., pattern=r"^\d{8}$", description="开始日期，格式 yyyymmdd"
    )
    end_date: str = Field(
        ..., pattern=r"^\d{8}$", description="结束日期，格式 yyyymmdd"
    )
    steam_id: int = Field(..., ge=0, description="Steam ID")


class RegionRankResponse(BaseModel):
    """地区排名响应."""

    stat_date: str = Field(..., description="统计日期 yyyymmdd")
    steam_id: int = Field(..., description="Steam ID")
    rank: int = Field(..., description="排名")
    region: str = Field(..., description="区域")


class PlayersResponse(BaseModel):
    """玩家数响应."""

    stat_date: str = Field(..., description="统计日期 yyyymmdd")
    steam_id: int = Field(..., description="Steam ID")
    peak_players: int = Field(..., description="峰值玩家")


class RecommendationsResponse(BaseModel):
    """推荐评价响应."""

    stat_date: str = Field(..., description="统计日期 yyyymmdd")
    type: str = Field(..., description="类型")
    steam_id: int = Field(..., description="Steam ID")
    up: int = Field(..., description="推荐数")
    down: int = Field(..., description="不推荐数")
    all: int = Field(..., description="评价总数")
    recommendation_rate: float = Field(..., description="推荐率")


class RegionCodeNameResponse(BaseModel):
    """区域代码名称响应."""

    code: str = Field(..., description="区域代码")
    name: str = Field(..., description="区域名称")
