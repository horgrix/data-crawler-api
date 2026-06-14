"""API 路由定义."""

from datetime import datetime

from fastapi import APIRouter, HTTPException

from models.schemas import HealthResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse, tags=["系统"])
async def health_check():
    """健康检查接口."""
    return HealthResponse(
        status="ok",
        version="0.1.0",
        timestamp=datetime.now(),
    )