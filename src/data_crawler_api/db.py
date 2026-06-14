"""MySQL 数据库连接管理模块."""

import aiomysql

from data_crawler_api.config import get_settings

_pool: aiomysql.Pool | None = None


async def get_pool() -> aiomysql.Pool:
    """获取或创建 MySQL 连接池（单例）.

    Returns:
        aiomysql 连接池实例
    """
    global _pool
    if _pool is not None:
        return _pool
    settings = get_settings()
    _pool = await aiomysql.create_pool(
        host=settings.mysql_host,
        port=settings.mysql_port,
        user=settings.mysql_user,
        password=settings.mysql_password,
        db=settings.mysql_database,
        pool_recycle=settings.mysql_pool_recycle,
        maxsize=settings.mysql_pool_size,
        autocommit=True,
        charset="utf8mb4",
    )
    return _pool


async def close_pool() -> None:
    """关闭连接池."""
    global _pool
    if _pool is not None:
        _pool.close()
        await _pool.wait_closed()
        _pool = None
