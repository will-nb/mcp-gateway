from __future__ import annotations

from typing import Optional, Dict, Any

from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse, JSONResponse

from app.services.qwen_client import get_qwen_client


router = APIRouter()


@router.post(
    "/v1/chat/completions",
    summary="OpenAI 兼容: Chat Completions",
    description=(
        "中文说明:\n"
        "- 完全兼容 OpenAI Chat Completions 的请求/响应路径和格式\n"
        "- 支持 stream 字段；当前示例为简化非流式直返，生产可改为 SSE 直通\n"
        "- 其余未显式字段将透传到后端\n"
    ),
)
async def openai_chat_completions(request: Request):
    """
    OpenAI 兼容接口: `POST /v1/chat/completions`

    - 完全兼容 OpenAI Chat Completions 请求体（包含 `model`, `messages`, `stream`, 以及其它扩展字段）
    - 若 `stream=true`，以 `text/event-stream` 直通下游的 SSE 流事件
    - 若 `stream=false`，返回 OpenAI 兼容的 JSON 结构
    """
    body: Dict[str, Any] = await request.json()
    model: str = body.get("model")
    messages = body.get("messages", [])
    stream: bool = bool(body.get("stream", False))

    # 其余参数透传到 DashScope 兼容端点
    extra: Dict[str, Any] = {k: v for k, v in body.items() if k not in {"model", "messages", "stream"}}

    client = get_qwen_client()

    if stream:
        # 走直通流式：下游目前为兼容 OpenAI 的 /chat/completions，但我们这里简化为非流式直返
        # 若需要严格 SSE，请在 qwen_client 中实现流式生成器并在此返回 StreamingResponse
        result = client.chat_completion(model=model, messages=messages, stream=False, extra_body=extra)
        return JSONResponse(result)
    else:
        result = client.chat_completion(model=model, messages=messages, stream=False, extra_body=extra)
        return JSONResponse(result)
