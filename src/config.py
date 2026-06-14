"""应用配置管理模块."""
import os

from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """应用配置."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # 应用
    app_name: str = "Data Crawler API"
    app_version: str = "0.1.0"
    debug: bool = False

    # 服务器
    host: str = "0.0.0.0"
    port: int = 8000

    # 爬虫
    request_timeout: float = 30.0
    max_retries: int = 3
    user_agent: str = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
    concurrency_limit: int = 5

    # MySQL
    mysql_host: str = Field(..., alias="DB_HOST")
    mysql_port: int = Field(..., alias="DB_PORT")
    mysql_user: str = Field(..., alias="DB_USER")
    mysql_password: str = Field(..., alias="DB_PASSWORD")
    mysql_database: str = Field(..., alias="DB_DATABASE")
    mysql_charset: str = Field(..., alias="DB_CHARSET")
    mysql_pool_size: int = 10
    mysql_pool_recycle: int = 3600


@lru_cache
def get_settings() -> Settings:
    """获取应用配置单例."""
    return Settings()