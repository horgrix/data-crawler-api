"""Steam 数据查询 API 路由."""

from datetime import datetime, timedelta, timezone

import aiomysql
from fastapi import APIRouter, Query

from db import get_pool
from models.schemas import (
    PlayersType,
    RecommendationsType,
    RegionRankType,
)

router = APIRouter(prefix="/steam", tags=["Steam"])

# UTC+8 时区
TZ_BEIJING = timezone(timedelta(hours=8))
# UTC 时区
TZ_UTC = timezone.utc


def date_str_to_utc_ts(date_str: str) -> int:
    """将 yyyymmdd 格式的日期字符串转换为 UTC 时间戳.

    将输入日期视为北京时间（UTC+8）当天 00:00:00，转换后返回 UTC 时间戳。
    """
    year = int(date_str[:4])
    month = int(date_str[4:6])
    day = int(date_str[6:8])
    dt_beijing = datetime(year, month, day, tzinfo=TZ_BEIJING)
    return int(dt_beijing.timestamp())


def utc_ts_to_beijing_date_str(ts: int | float) -> str:
    """将 UTC 时间戳转换为北京时间 yyyymmdd 格式."""
    dt_utc = datetime.fromtimestamp(ts, tz=TZ_UTC)
    dt_beijing = dt_utc.astimezone(TZ_BEIJING)
    return dt_beijing.strftime("%Y%m%d")

def utc_ts_to_beijing_date_with_hour_str(ts: int | float) -> str:
    """将 UTC 时间戳转换为北京时间 yyyymmdd 格式."""
    dt_utc = datetime.fromtimestamp(ts, tz=TZ_UTC)
    dt_beijing = dt_utc.astimezone(TZ_BEIJING)
    return dt_beijing.strftime("%Y%m%d %H")


# ==================== query_region_rank ====================


@router.get("/region_rank", summary="查询 Steam 地区排名")
async def query_region_rank(
    steam_id: int = Query(..., ge=0, description="Steam ID"),
    type: RegionRankType = Query(..., description="时间类型：hourly | weekly"),
) -> list[dict]:

    pool = await get_pool()
    async with pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            if type == RegionRankType.HOURLY:
                await cur.execute(
                    """
                    SELECT stat_ts, steam_id, `rank`, region
                    FROM xd_game_steam_rt_hotlist
                    WHERE steam_id = %s
                    ORDER BY stat_ts ASC
                    LIMIT 24
                    """,
                    (steam_id),
                )
            else:
                await cur.execute(
                    """
                    SELECT start_ts, steam_id, `rank`, region
                    FROM xd_game_steam_weekly_hot_list
                    WHERE steam_id = %s
                    ORDER BY start_ts ASC
                    LIMIT 27
                    """,
                    (steam_id),
                )
            rows = await cur.fetchall()

    results: list[dict] = []
    for row in rows:
        ts = row.get("stat_ts") or row.get("start_ts")
        stat_date = utc_ts_to_beijing_date_str(ts / 1000)
        if type == RegionRankType.HOURLY:
            stat_date = utc_ts_to_beijing_date_with_hour_str(ts / 1000)
        results.append({
            "stat_date": stat_date,
            "steam_id": row["steam_id"],
            "rank": row["rank"],
            "region": row["region"],
        })
    return results


# ==================== query_players ====================


@router.get("/players", summary="查询 Steam 玩家数据")
async def query_players(
    start_date: str = Query(..., pattern=r"^\d{8}$", description="开始日期 yyyymmdd"),
    end_date: str = Query(..., pattern=r"^\d{8}$", description="结束日期 yyyymmdd"),
    steam_id: int = Query(..., ge=0, description="Steam ID"),
    type: PlayersType = Query(..., description="时间类型：monthly | daily | hourly"),
) -> list[dict]:
    """查询指定游戏的 Steam 玩家峰值数据."""
    start_ts = date_str_to_utc_ts(start_date)  * 1000
    end_ts_inclusive = (date_str_to_utc_ts(end_date) + 86399) * 1000

    pool = await get_pool()
    async with pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            await cur.execute(
                """
                SELECT stat_ts, steam_id, peak_players
                FROM xd_game_steam_players
                WHERE steam_id = %s
                  AND type = %s
                  AND stat_ts >= %s
                  AND stat_ts <= %s
                ORDER BY stat_ts ASC
                """,
                (steam_id, type.value, start_ts, end_ts_inclusive),
            )
            rows = await cur.fetchall()

    results: list[dict] = []
    for row in rows:
        results.append({
            "stat_date": utc_ts_to_beijing_date_str(row["stat_ts"] / 1000),
            "steam_id": row["steam_id"],
            "peak_players": row["peak_players"],
        })
    return results


# ==================== query_recommendations ====================


@router.get("/recommendations", summary="查询 Steam 推荐评价数据")
async def query_recommendations(
    start_date: str = Query(..., pattern=r"^\d{8}$", description="开始日期 yyyymmdd"),
    end_date: str = Query(..., pattern=r"^\d{8}$", description="结束日期 yyyymmdd"),
    steam_id: int = Query(..., ge=0, description="Steam ID"),
    type: RecommendationsType = Query(..., description="类型：rollup | recent"),
) -> list[dict]:
    """查询指定游戏的 Steam 推荐评价数据（含推荐率）."""
    start_ts = date_str_to_utc_ts(start_date) * 1000
    end_ts_inclusive = (date_str_to_utc_ts(end_date) + 86399) * 1000 

    pool = await get_pool()
    async with pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            await cur.execute(
                """
                SELECT stat_ts, steam_id, type, `up`, `down`, `all`
                FROM xd_game_steam_commendations
                WHERE steam_id = %s
                  AND type = %s
                  AND stat_ts >= %s
                  AND stat_ts <= %s
                ORDER BY stat_ts ASC
                """,
                (steam_id, type.value, start_ts, end_ts_inclusive),
            )
            rows = await cur.fetchall()

    results: list[dict] = []
    for row in rows:
        total = row["all"]
        rate = round(row["up"] / total, 2) if total > 0 else 0.0
        results.append({
            "stat_date": utc_ts_to_beijing_date_str(row["stat_ts"] / 1000),
            "type": row["type"],
            "steam_id": row["steam_id"],
            "up": row["up"],
            "down": row["down"],
            "all": row["all"],
            "recommendation_rate": rate,
        })
    return results


# ==================== query_region_code_name_mapping ====================


@router.get("/region_mapping", summary="查询区域代码名称映射")
async def query_region_code_name_mapping() -> list[dict]:
    """查询所有 Steam 区域代码与名称的映射."""
    pool = await get_pool()
    async with pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            await cur.execute("SELECT code, name FROM steam_region_kv")
            rows = await cur.fetchall()

    return [{"code": row["code"], "name": row["name"]} for row in rows]