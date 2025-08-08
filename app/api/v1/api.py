from fastapi import APIRouter

from app.api.v1.endpoints import health, info, settings, qdrant, ai


api_router = APIRouter()

# Health and liveness endpoints
api_router.include_router(health.router, tags=["health"]) 
api_router.include_router(settings.router, tags=["settings"]) 
api_router.include_router(qdrant.router, tags=["qdrant"]) 
api_router.include_router(ai.router, tags=["ai"])
api_router.include_router(info.router, tags=["info"])
