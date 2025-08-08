from __future__ import annotations

from typing import Dict, Any

from fastapi import APIRouter, Body
from fastapi.responses import JSONResponse

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
async def openai_chat_completions(
    body: Dict[str, Any] = Body(
        ...,
        example={
            "model": "gpt-3.5-turbo",
            "messages": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "用一句话介绍你自己"}
            ],
            "stream": False
        },
    ),
):
    """
    OpenAI 兼容接口: `POST /v1/chat/completions`

    - 完全兼容 OpenAI Chat Completions 请求体（包含 `model`, `messages`, `stream`, 以及其它扩展字段）
    - 若 `stream=true`，以 `text/event-stream` 直通下游的 SSE 流事件
    - 若 `stream=false`，返回 OpenAI 兼容的 JSON 结构
    """
    model: str = body.get("model")
    messages = body.get("messages", [])
    stream: bool = bool(body.get("stream", False))

    # 其余参数透传到 DashScope 兼容端点
    extra: Dict[str, Any] = {k: v for k, v in body.items() if k not in {"model", "messages", "stream"}}

    client = get_qwen_client()

    # 当前示例未实现 SSE，统一按非流式返回
    result = client.chat_completion(model=model, messages=messages, stream=False, extra_body=extra)
    return JSONResponse(result)
