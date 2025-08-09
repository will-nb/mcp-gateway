from typing import List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.core.config import get_settings
from app.schemas.common import ApiStandardResponse, create_object_response, DataType
from app.services.qwen_client import get_qwen_client
from app.services.semantic_cache import get_semantic_cache


router = APIRouter()


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    model: str = Field(default="qwen-plus")
    messages: List[ChatMessage]
    stream: bool = False
    extra_body: Optional[dict] = None


class ChatResponse(BaseModel):
    raw: dict
    cache_hit: bool = False
    cache_score: float | None = None


@router.post(
    "/ai/chat",
    response_model=ApiStandardResponse,
    summary="Qwen 聊天补全（OpenAI 兼容后端）",
    description=(
        "中文说明:\n"
        "- 使用与 OpenAI Chat Completions 兼容的 DashScope/Qwen 后端\n"
        "- 请求参数: model, messages, stream, extra_body（透传到下游）\n"
        "- 返回值: {code, message, data}，data.raw 为下游原始响应；并包含 cache 命中信息\n"
    ),
    openapi_extra={
        "requestBody": {
            "content": {
                "application/json": {
                    "example": {
                        "model": "qwen-plus",
                        "messages": [
                            {"role": "system", "content": "You are a helpful assistant."},
                            {"role": "user", "content": "用一句话介绍你自己"}
                        ],
                        "stream": False
                    }
                }
            }
        }
    },
)
def chat(req: ChatRequest) -> ApiStandardResponse:
    s = get_settings()
    if req.model not in s.qwen_allowed_models:
        raise HTTPException(status_code=400, detail=f"Model {req.model} not allowed")
    # semantic cache check using last user message
    user_msgs = [m for m in req.messages if m.role == 'user']
    cache = get_semantic_cache()
    if user_msgs:
        probe = cache.query(user_msgs[-1].content)
        if probe is not None:
            score, payload = probe
            return create_object_response(
                message="OK",
                data_value={
                    "raw": payload.get("raw", {}),
                    "cacheHit": True,
                    "cacheScore": score,
                },
                data_type=DataType.AI,
                code=200,
            )

    client = get_qwen_client()
    result = client.chat_completion(model=req.model, messages=[m.model_dump() for m in req.messages], stream=req.stream, extra_body=req.extra_body)

    # write to cache
    if user_msgs:
        cache.upsert(user_msgs[-1].content, {"raw": result})
    return create_object_response(
        message="OK",
        data_value={"raw": result, "cacheHit": False},
        data_type=DataType.AI,
        code=200,
    )
