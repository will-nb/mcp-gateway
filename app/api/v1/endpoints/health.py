from fastapi import APIRouter

from app.core.config import get_settings
from app.schemas.health import HealthResponse, QdrantHealth, RedisHealth


router = APIRouter()


from app.schemas.response import SuccessResponse


@router.get(
    "/health",
    response_model=SuccessResponse[HealthResponse],
    summary="Health check",
)
def get_health() -> SuccessResponse[HealthResponse]:
    settings = get_settings()
    # probe qdrant
    from app.services.qdrant import get_qdrant_service

    qdrant_reachable = True
    try:
        svc = get_qdrant_service()
        svc.get_client().get_collections()
    except Exception:
        qdrant_reachable = False

    qdrant = QdrantHealth(
        reachable=qdrant_reachable,
        host=settings.qdrant_host,
        http_port=settings.qdrant_http_port,
    )

    # probe redis
    from app.services.redis_client import get_redis_service
    redis_reachable = False
    try:
        rsvc = get_redis_service()
        redis_reachable = rsvc.ping()
    except Exception:
        redis_reachable = False

    redis = RedisHealth(
        reachable=redis_reachable,
        host=settings.redis_host,
        port=settings.redis_port,
        db=settings.redis_db,
        key_prefix=settings.redis_key_prefix,
    )

    return SuccessResponse(
        data=HealthResponse(status="ok", version=settings.version, qdrant=qdrant, redis=redis)
    )
