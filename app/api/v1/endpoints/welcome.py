import logging
from datetime import datetime, UTC

from fastapi import APIRouter

from app.core.config import get_settings
from app.core.mongo_async import get_mongo_health
from app.core.redis_async import get_redis_health
from app.core.qdrant_async import get_qdrant_health
from app.schemas.common import ApiStandardResponse, create_object_response
from app.schemas.welcome import HealthResponse, ServiceStatus

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/welcome", tags=["Welcome"])


@router.get("/health", response_model=ApiStandardResponse)
async def health():
    s = get_settings()
    # gather service health concurrently
    mongo = await get_mongo_health()
    redis = await get_redis_health()
    qdrant = await get_qdrant_health()

    services = {
        "mongodb": ServiceStatus(status=mongo["status"], message=mongo["message"]),
        "redis": ServiceStatus(status=redis["status"], message=redis["message"]),
        "qdrant": ServiceStatus(status=qdrant["status"], message=qdrant["message"]),
    }

    data = HealthResponse(
        status="healthy"
        if all(v.status == "healthy" for v in services.values())
        else "unhealthy",
        version=s.version if hasattr(s, "version") else "1.0.0",
        timestamp=datetime.now(UTC).isoformat(),
        services=services,
    )
    return create_object_response(
        message="健康检查成功",
        data_value=data.model_dump(by_alias=True),
        data_type="health",
        code=200,
    )


@router.get("/info", response_model=ApiStandardResponse)
async def info():
    s = get_settings()
    data = {
        "version": s.version if hasattr(s, "version") else "1.0.0",
        "environment": "development",
    }
    return create_object_response(
        message="应用信息", data_value=data, data_type="info", code=200
    )
