from __future__ import annotations

from typing import Dict, Any

from fastapi import APIRouter, Body, HTTPException
from fastapi.responses import JSONResponse

from app.core.config import get_settings
import httpx


router = APIRouter()


@router.post(
    "/v1/models/{model}:generateContent",
    summary="Gemini 兼容: generateContent (v1 稳定)",
    description=(
        "中文说明:\n"
        "- 兼容 Google Generative Language API v1 的 generateContent 接口（稳定版路径）\n"
        "- 与 v1beta 行为一致，选择其一即可；若你偏好稳定版文档，请使用此路径\n"
    ),
)
async def gemini_generate_content_v1(
    model: str,
    body: Dict[str, Any] = Body(
        ...,
        example={
            "contents": [
                {
                    "role": "user",
                    "parts": [
                        {"text": "用一句话介绍你自己"}
                    ]
                }
            ]
        },
    ),
):
    """
    Gemini 兼容接口: `POST /v1/models/{model}:generateContent`

    - 使用 `GEMINI_API_KEY` 进行鉴权
    - 返回下游响应 JSON
    """
    s = get_settings()
    if not s.gemini_api_key:
        raise HTTPException(status_code=500, detail="GEMINI_API_KEY not configured")

    url = s.gemini_base_url.rstrip('/') + f"/v1/models/{model}:generateContent?key={s.gemini_api_key}"

    async with httpx.AsyncClient(timeout=60) as client:
        resp = await client.post(url, json=body)
        resp.raise_for_status()
        return JSONResponse(resp.json())
