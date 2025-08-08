from __future__ import annotations

from typing import Dict, Any

from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse

from app.core.config import get_settings
import httpx


router = APIRouter()


@router.post(
    "/v1beta/models/{model}:generateContent",
    summary="Gemini 兼容: generateContent",
    description=(
        "中文说明:\n"
        "- 兼容 Google Generative Language API v1beta 的 generateContent 接口\n"
        "- 使用 GEMINI_API_KEY 鉴权；请求体将原样转发\n"
        "- 返回值为下游响应 JSON\n"
    ),
)
async def gemini_generate_content(model: str, request: Request):
    """
    Gemini 兼容接口: `POST /v1beta/models/{model}:generateContent`

    - 按 Google Generative Language API v1beta 的路径与请求体透传
    - 使用 `GEMINI_API_KEY` 进行鉴权
    - 返回下游响应 JSON
    """
    s = get_settings()
    if not s.gemini_api_key:
        raise HTTPException(status_code=500, detail="GEMINI_API_KEY not configured")

    body: Dict[str, Any] = await request.json()
    url = s.gemini_base_url.rstrip('/') + f"/v1beta/models/{model}:generateContent?key={s.gemini_api_key}"

    async with httpx.AsyncClient(timeout=60) as client:
        resp = await client.post(url, json=body)
        resp.raise_for_status()
        return JSONResponse(resp.json())
