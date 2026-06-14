"""FastAPI 应用入口模块."""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes import router
from api.steam_api import router as steam_router
from api.xd_api import router as xd_router
from config import get_settings
from db import close_pool


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """应用生命周期管理."""
    settings = get_settings()
    app.state.settings = settings
    yield
    await close_pool()


def create_app() -> FastAPI:
    """创建并配置 FastAPI 应用."""
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="数据爬虫 API - 提供数据采集与查询接口",
        lifespan=lifespan,
    )

    # CORS 中间件
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 注册路由
    app.include_router(router, prefix="/api/v1")

    # 注册 Steam 路由
    app.include_router(steam_router, prefix="/api/v1")

    # 注册 XD 路由
    app.include_router(xd_router, prefix="/api/v1")

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn

    settings = get_settings()
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
    )