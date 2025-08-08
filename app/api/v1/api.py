from fastapi import APIRouter

from app.api.v1.endpoints import health, info, settings, qdrant, ai
from app.api.compat import openai as compat_openai
from app.api.compat import gemini as compat_gemini
from app.api.compat import anthropic as compat_anthropic


api_router = APIRouter()

# Health and liveness endpoints
api_router.include_router(health.router, tags=["health"]) 
api_router.include_router(settings.router, tags=["settings"]) 
api_router.include_router(qdrant.router, tags=["qdrant"]) 
api_router.include_router(ai.router, tags=["ai"])
api_router.include_router(info.router, tags=["info"])

# 兼容组（OpenAI / Gemini / Claude）
api_router.include_router(compat_openai.router, tags=["compat"]) 
api_router.include_router(compat_gemini.router, tags=["compat"]) 
api_router.include_router(compat_anthropic.router, tags=["compat"]) 
