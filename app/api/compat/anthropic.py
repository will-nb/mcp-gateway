from __future__ import annotations

from typing import Dict, Any

from fastapi import APIRouter, HTTPException, Body
from fastapi.responses import JSONResponse

from app.core.config import get_settings
import httpx


router = APIRouter()


@router.post(
    "/v1/messages",
    summary="Claude 兼容: Messages API",
    description=(
        "中文说明:\n"
        "- 兼容 Anthropic Messages API 的路径与请求格式\n"
        "- 使用 ANTHROPIC_API_KEY/CLAUDE_API_KEY 鉴权\n"
        "- 返回值为下游响应 JSON\n"
    ),
)
async def anthropic_messages(
    body: Dict[str, Any] = Body(
        ...,
        example={
            "model": "qwen-plus",
            "max_tokens": 256,
            "messages": [
                {"role": "user", "content": [ {"type": "text", "text": "用一句话介绍你自己"} ]}
            ]
        }
    ),
):
    """
    Claude 兼容接口: `POST /v1/messages`

    - 兼容 Anthropic Messages API
    - 使用 `ANTHROPIC_API_KEY`/`CLAUDE_API_KEY` 鉴权
    - 返回下游响应 JSON
    """
    s = get_settings()
    api_key = s.anthropic_api_key
    if not api_key:
        raise HTTPException(status_code=500, detail="ANTHROPIC_API_KEY/CLAUDE_API_KEY not configured")

    headers = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    }
    url = s.anthropic_base_url.rstrip('/') + "/v1/messages"

    async with httpx.AsyncClient(timeout=60) as client:
        resp = await client.post(url, headers=headers, json=body)
        resp.raise_for_status()
        return JSONResponse(resp.json())
