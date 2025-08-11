from typing import List, Optional

from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel, Field

from app.core.config import get_settings
from app.schemas.common import ApiStandardResponse, create_object_response, DataType
from app.services.qwen_client import get_qwen_client
from app.services.semantic_cache import get_semantic_cache
from app.schemas.tasks import EnqueueRequest, TaskClass, TaskPriority, JobStatus
from app.services.tasks import enqueue_task, wait_for_completion


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
    summary="Qwen 聊天补全（排队执行 + 快返）",
)
def chat(
    req: ChatRequest,
    x_task_class: TaskClass = Header(default=TaskClass.interactive, alias="X-Task-Class"),
    x_priority: TaskPriority | None = Header(default=None, alias="X-Priority"),
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
) -> ApiStandardResponse:
    s = get_settings()
    if req.model not in s.qwen_allowed_models:
        raise HTTPException(status_code=400, detail=f"Model {req.model} not allowed")

    # 入队（payload_ref 用 inline 标记；params 传原请求体）
    task_req = EnqueueRequest(payload_ref=f"inline://ai_chat", params=req.model_dump())
    job_id, _ = enqueue_task(
        task_type="ai_chat",
        req=task_req,
        task_class=x_task_class,
        priority=x_priority,
        idempotency_key=idempotency_key,
    )

    # 快返尝试：等待 Worker 结果（测试可通过 monkeypatch 注入 doc.result）
    doc = wait_for_completion(job_id, s.interactive_sync_timeout_ms)
    if doc and doc.get("status") == JobStatus.succeeded:
        result = doc.get("result")
        if result is not None:
            return create_object_response(
                message="OK",
                data_value={"raw": result, "cacheHit": False},
                data_type=DataType.AI,
                code=200,
            )

    # 202 接受
    status_url = f"{s.api_v1_prefix}/jobs/{job_id}"
    return create_object_response(
        message="Accepted",
        data_value={"job_id": job_id, "status_url": status_url, "poll_after": 2},
        data_type=DataType.OBJECT,
        code=202,
    )
