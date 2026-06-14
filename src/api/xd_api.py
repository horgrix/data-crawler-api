"""XD 相关数据查询 API 路由."""

import time
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from typing import Any

import aiomysql
from fastapi import APIRouter, HTTPException, Query

from db import get_pool

router = APIRouter(prefix="/xd", tags=["XD"])

# UTC+8 时区
TZ_BEIJING = timezone(timedelta(hours=8))
TZ_UTC = timezone.utc

# ===================== 内存缓存 =====================

# 缓存结构: {key: (data, expire_timestamp)}
_cache: dict[str, tuple[Any, float]] = {}

# xd_torchlight_season_cache: {ss: {start_date, end_date, ss}}
_xd_torchlight_season_cache: dict[int, dict] = {}
_torchlight_cache_expire: float = 0


def _cache_get(key: str) -> Any | None:
    """从缓存获取数据，过期返回 None."""
    entry = _cache.get(key)
    if entry is None:
        return None
    data, expire_at = entry
    if time.time() > expire_at:
        del _cache[key]
        return None
    return data


def _cache_set(key: str, data: Any, ttl_seconds: int = 3600) -> None:
    """设置缓存数据."""
    _cache[key] = (data, time.time() + ttl_seconds)


def _date_str_to_utc_ts(date_str: str) -> int:
    """将 yyyymmdd 格式的日期字符串转换为 UTC 时间戳."""
    year = int(date_str[:4])
    month = int(date_str[4:6])
    day = int(date_str[6:8])
    dt_beijing = datetime(year, month, day, tzinfo=TZ_BEIJING)
    return int(dt_beijing.timestamp())


# ==================== query_xd_steam_games ====================


@router.get("/games", summary="查询心动在 Steam 的所有游戏")
async def query_xd_steam_games() -> list[dict]:
    """查询所有 XD Steam 游戏列表（缓存 1 小时）."""
    cache_key = "xd_steam_games"
    cached = _cache_get(cache_key)
    if cached is not None:
        return cached

    pool = await get_pool()
    async with pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            await cur.execute("SELECT steam_id, steam_name FROM xd_game_steamids")
            rows = await cur.fetchall()

    result = [{"steam_id": row["steam_id"], "steam_name": row["steam_name"]} for row in rows]
    _cache_set(cache_key, result)
    return result


# ==================== query_xd_torchlight_season ====================


async def _load_torchlight_season_cache() -> dict[int, dict]:
    """加载火炬之光赛季缓存（1 小时失效）."""
    global _xd_torchlight_season_cache, _torchlight_cache_expire
    if _xd_torchlight_season_cache and time.time() < _torchlight_cache_expire:
        return _xd_torchlight_season_cache

    pool = await get_pool()
    async with pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            await cur.execute(
                """SELECT start_date, end_date, ss
                   FROM xd_torchlight_season
                   WHERE is_enable = 1
                   ORDER BY ss DESC"""
            )
            rows = await cur.fetchall()

    new_cache: dict[int, dict] = {}
    for row in rows:
        new_cache[row["ss"]] = {
            "start_date": row["start_date"],
            "end_date": row["end_date"],
            "ss": row["ss"],
        }
    _xd_torchlight_season_cache = new_cache
    _torchlight_cache_expire = time.time() + 3600
    return _xd_torchlight_season_cache


@router.get("/games/torchlight/season/configs", summary="查询火炬之光赛季配置")
async def query_xd_torchlight_season() -> list[dict]:
    """查询启用的火炬之光赛季配置（缓存 1 小时）."""
    cache = await _load_torchlight_season_cache()
    return list(cache.values())


# ==================== query_xd_torchlight_seasons_steam_players ====================

VALID_TORCHLIGHT_STEAM_IDS = {2315040, 1974050}


@router.get("/games/torchlight/seasons/players", summary="查询赛季游戏峰值玩家")
async def query_xd_torchlight_seasons_steam_players(
    seasons: str = Query(..., description="赛季编号列表，逗号分隔，如 1,2,3"),
    steam_id: int = Query(..., description="Steam ID，仅限 2315040 或 1974050"),
) -> list[dict]:
    """查询指定赛季的 Steam 玩家峰值数据（按 ss/ss_day/steam_id 分组）."""
    # 参数校验
    if steam_id not in VALID_TORCHLIGHT_STEAM_IDS:
        raise HTTPException(
            status_code=422,
            detail=f"steam_id 仅允许 {sorted(VALID_TORCHLIGHT_STEAM_IDS)}",
        )

    # 解析 seasons
    try:
        season_list = [int(s.strip()) for s in seasons.split(",") if s.strip()]
    except ValueError as e:
        raise HTTPException(status_code=422, detail=f"seasons 格式错误: {e}") from e
    if not season_list:
        raise HTTPException(status_code=422, detail="seasons 不能为空")

    # 加载赛季缓存
    season_cache = await _load_torchlight_season_cache()

    # 验证赛季存在并获取时间范围
    season_ranges: list[tuple[int, str, str]] = []  # [(ss, start_date, end_date)]
    for ss in season_list:
        if ss not in season_cache:
            raise HTTPException(status_code=404, detail=f"赛季 {ss} 不存在或未启用")
        info = season_cache[ss]
        season_ranges.append((ss, info["start_date"], info["end_date"]))

    # 收集所有赛季时间范围内的 stat_ts 条件
    pool = await get_pool()
    all_rows: list[dict] = []

    async with pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            for ss, start_date, end_date in season_ranges:
                start_ts = _date_str_to_utc_ts(start_date)
                end_ts_inclusive = _date_str_to_utc_ts(end_date) + 86399
                season_start_ts = start_ts  # 用于计算 ss_day

                await cur.execute(
                    """
                    SELECT stat_ts, steam_id, peak_players
                    FROM xd_game_steam_players
                    WHERE steam_id = %s
                      AND stat_ts >= %s
                      AND stat_ts <= %s
                    ORDER BY stat_ts ASC
                    """,
                    (steam_id, start_ts, end_ts_inclusive),
                )
                rows = await cur.fetchall()

                for row in rows:
                    # 计算 ss_day: 第1天 = 1
                    days_diff = (row["stat_ts"] - season_start_ts) // 86400 + 1
                    all_rows.append({
                        "ss": ss,
                        "ss_day": max(days_diff, 1),
                        "steam_id": row["steam_id"],
                        "peak_players": row["peak_players"],
                    })

    # Group by (ss, ss_day, steam_id) 取 MAX(peak_players)
    groups: dict[tuple[int, int, int], int] = {}
    for row in all_rows:
        key = (row["ss"], row["ss_day"], row["steam_id"])
        if key not in groups or row["peak_players"] > groups[key]:
            groups[key] = row["peak_players"]

    # 组装结果
    results: list[dict] = []
    for (ss, ss_day, sid), peak in groups.items():
        results.append({
            "ss": ss,
            "ss_day": ss_day,
            "steam_id": sid,
            "peak_players": peak,
        })
    return results


# ==================== query_region_code_name_mapping ====================


@router.get("/region_mapping", summary="查询区域代码名称映射")
async def query_region_code_name_mapping() -> list[dict]:
    """查询所有 Steam 区域代码与名称的映射（缓存 1 小时）."""
    cache_key = "xd_region_mapping"
    cached = _cache_get(cache_key)
    if cached is not None:
        return cached

    pool = await get_pool()
    async with pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            await cur.execute("SELECT code, name FROM steam_region_kv")
            rows = await cur.fetchall()

    result = [{"code": row["code"], "name": row["name"]} for row in rows]
    _cache_set(cache_key, result)
    return result