from __future__ import annotations

from typing import Dict, List, Optional

from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel, Field

from app.schemas.common import ApiStandardResponse, create_object_response, DataType
from app.core.config import get_settings
from app.services.isbn.search_manager import search_title
from app.services.isbn import manager as isbn_manager
from app.schemas.tasks import EnqueueRequest, TaskClass, TaskPriority, JobStatus
from app.services.tasks import enqueue_task, wait_for_completion


router = APIRouter()


class SearchByTitleRequest(BaseModel):
    title: str = Field(..., description="书名关键词")
    minSimilarity: float = Field(0.6, description="最小相似度阈值，范围 0-1")
    maxResultsPerSource: int = Field(5, description="每个来源最大返回条数")
    forceSource: Optional[str] = Field(None, description="强制来源")


@router.post(
    "/books/search-title",
    response_model=ApiStandardResponse,
    summary="按书名搜索（排队执行 + 快返）",
)
def search_books_by_title(
    req: SearchByTitleRequest,
    x_task_class: TaskClass = Header(default=TaskClass.interactive, alias="X-Task-Class"),
    x_priority: TaskPriority | None = Header(default=None, alias="X-Priority"),
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
) -> ApiStandardResponse:
    s = get_settings()
    task_req = EnqueueRequest(payload_ref="inline://books_search_title", params=req.model_dump())
    job_id, _ = enqueue_task(
        task_type="books_search_title",
        req=task_req,
        task_class=x_task_class,
        priority=x_priority,
        idempotency_key=idempotency_key,
    )
    doc = wait_for_completion(job_id, s.interactive_sync_timeout_ms)
    if doc and doc.get("status") == JobStatus.succeeded and doc.get("result") is not None:
        return create_object_response(message="OK", data_value={"items": doc.get("result")}, data_type=DataType.LIST, code=200)
    status_url = f"{s.api_v1_prefix}/jobs/{job_id}"
    return create_object_response(message="Accepted", data_value={"job_id": job_id, "status_url": status_url, "poll_after": 2}, data_type=DataType.OBJECT, code=202)


class SearchByIsbnRequest(BaseModel):
    isbn: str = Field(..., description="ISBN-10 或 ISBN-13")
    forceSource: Optional[str] = Field(None, description="强制来源常量")
    # 其余策略在服务端自动推断（超时、国别优先级、去重防抖）


@router.post(
    "/books/search-isbn",
    response_model=ApiStandardResponse,
    summary="按 ISBN 搜索图书（排队执行 + 快返）",
)
def search_books_by_isbn(
    req: SearchByIsbnRequest,
    x_task_class: TaskClass = Header(default=TaskClass.interactive, alias="X-Task-Class"),
    x_priority: TaskPriority | None = Header(default=None, alias="X-Priority"),
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
) -> ApiStandardResponse:
    s = get_settings()
    task_req = EnqueueRequest(payload_ref="inline://books_search_isbn", params=req.model_dump())
    job_id, _ = enqueue_task(
        task_type="books_search_isbn",
        req=task_req,
        task_class=x_task_class,
        priority=x_priority,
        idempotency_key=idempotency_key,
    )
    doc = wait_for_completion(job_id, s.interactive_sync_timeout_ms)
    if doc and doc.get("status") == JobStatus.succeeded and doc.get("result") is not None:
        return create_object_response(message="OK", data_value=doc.get("result"), data_type=DataType.OBJECT, code=200)
    status_url = f"{s.api_v1_prefix}/jobs/{job_id}"
    return create_object_response(message="Accepted", data_value={"job_id": job_id, "status_url": status_url, "poll_after": 2}, data_type=DataType.OBJECT, code=202)
