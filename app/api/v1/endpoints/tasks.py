from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Header, HTTPException, Request
from pydantic import BaseModel, Field

from app.core.config import get_settings
from app.schemas.common import ApiStandardResponse, create_object_response, DataType
from app.schemas.tasks import (
    EnqueueAccepted,
    EnqueueRequest,
    JobStatus,
    TaskClass,
    TaskPriority,
)
from app.services.tasks import enqueue_task, get_job, wait_for_completion, cancel_job


router = APIRouter(prefix="/tasks", tags=["tasks"])  # Mounted under /api/v1


class EnqueueResponseData(BaseModel):
    job_id: str
    status_url: str
    poll_after: int = Field(default=2)
    status: str = Field(default="queued")


def _status_url(job_id: str) -> str:
    s = get_settings()
    return f"{s.api_v1_prefix}/tasks/{job_id}"


async def _handle_enqueue(
    *,
    task_type: str,
    req: EnqueueRequest,
    x_task_class: TaskClass = Header(default=TaskClass.interactive, alias="X-Task-Class"),
    x_priority: Optional[TaskPriority] = Header(default=None, alias="X-Priority"),
    idempotency_key: Optional[str] = Header(default=None, alias="Idempotency-Key"),
) -> ApiStandardResponse:
    job_id, _ = enqueue_task(
        task_type=task_type,
        req=req,
        task_class=x_task_class,
        priority=x_priority,
        idempotency_key=idempotency_key,
    )

    # Try sync fast-path only for interactive
    if x_task_class == TaskClass.interactive and (req.sync_timeout_ms or 0) > 0:
        doc = wait_for_completion(job_id, req.sync_timeout_ms or 0)
        if doc and doc.get("status") == JobStatus.succeeded:
            # Direct pass-through minimal result
            return create_object_response(
                message="OK",
                data_value={
                    "jobId": job_id,
                    "status": doc.get("status"),
                    "resultRef": doc.get("result_ref"),
                },
                data_type=DataType.OBJECT,
                code=200,
            )

    data = EnqueueResponseData(job_id=job_id, status_url=_status_url(job_id), poll_after=2, status="queued").model_dump()
    return create_object_response(message="Accepted", data_value=data, data_type=DataType.OBJECT, code=202)


@router.post("/ocr", response_model=ApiStandardResponse, summary="Enqueue OCR task")
async def enqueue_ocr(
    req: EnqueueRequest,
    x_task_class: TaskClass = Header(default=TaskClass.interactive, alias="X-Task-Class"),
    x_priority: Optional[TaskPriority] = Header(default=None, alias="X-Priority"),
    idempotency_key: Optional[str] = Header(default=None, alias="Idempotency-Key"),
) -> ApiStandardResponse:
    return await _handle_enqueue(
        task_type="ocr",
        req=req,
        x_task_class=x_task_class,
        x_priority=x_priority,
        idempotency_key=idempotency_key,
    )


@router.post("/ai", response_model=ApiStandardResponse, summary="Enqueue AI bridge task")
async def enqueue_ai(
    req: EnqueueRequest,
    x_task_class: TaskClass = Header(default=TaskClass.interactive, alias="X-Task-Class"),
    x_priority: Optional[TaskPriority] = Header(default=None, alias="X-Priority"),
    idempotency_key: Optional[str] = Header(default=None, alias="Idempotency-Key"),
) -> ApiStandardResponse:
    return await _handle_enqueue(
        task_type="ai",
        req=req,
        x_task_class=x_task_class,
        x_priority=x_priority,
        idempotency_key=idempotency_key,
    )


@router.post("/isbn", response_model=ApiStandardResponse, summary="Enqueue ISBN lookup task")
async def enqueue_isbn(
    req: EnqueueRequest,
    x_task_class: TaskClass = Header(default=TaskClass.interactive, alias="X-Task-Class"),
    x_priority: Optional[TaskPriority] = Header(default=None, alias="X-Priority"),
    idempotency_key: Optional[str] = Header(default=None, alias="Idempotency-Key"),
) -> ApiStandardResponse:
    return await _handle_enqueue(
        task_type="isbn",
        req=req,
        x_task_class=x_task_class,
        x_priority=x_priority,
        idempotency_key=idempotency_key,
    )


@router.get("/{job_id}", response_model=ApiStandardResponse, summary="Get job status")
async def get_task_status(job_id: str) -> ApiStandardResponse:
    doc = get_job(job_id)
    if not doc:
        raise HTTPException(status_code=404, detail="job not found")
    return create_object_response(message="OK", data_value=doc, data_type=DataType.OBJECT, code=200)


@router.delete("/{job_id}", response_model=ApiStandardResponse, summary="Cancel queued job")
async def cancel_task(job_id: str) -> ApiStandardResponse:
    ok = cancel_job(job_id)
    if not ok:
        raise HTTPException(status_code=409, detail="cannot cancel in current state")
    return create_object_response(message="Canceled", data_value={"jobId": job_id}, data_type=DataType.OBJECT, code=200)
