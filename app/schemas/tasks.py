from __future__ import annotations

from enum import Enum
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field

from app.schemas.base import CamelModel


class TaskClass(str, Enum):
    interactive = "interactive"
    bulk = "bulk"
    offline = "offline"


class TaskPriority(str, Enum):
    high = "high"
    normal = "normal"
    low = "low"


class JobStatus(str, Enum):
    queued = "queued"
    running = "running"
    succeeded = "succeeded"
    failed = "failed"
    canceled = "canceled"


class EnqueueRequest(CamelModel):
    payload_ref: str = Field(..., description="R2 URL 或对象引用，不存入队列")
    params: Dict[str, Any] | None = Field(default=None, description="执行参数")
    batch_id: Optional[str] = Field(default=None, description="批量任务批次 ID")
    batch_max_parallel: Optional[int] = Field(default=2, ge=1, le=8, description="每批最大并发")
    sync_timeout_ms: Optional[int] = Field(default=2500, ge=0, le=5000, description="同步快返等待窗口")
    callback_url: Optional[str] = Field(default=None, description="回调地址（可选）")


class EnqueueAccepted(CamelModel):
    job_id: str
    status_url: str
    poll_after: int = 2


class JobView(CamelModel):
    id: str = Field(..., description="Job ID")
    type: str = Field(..., description="任务类型，如 ocr/ai/isbn")
    status: JobStatus = Field(default=JobStatus.queued)
    tries: int = 0
    priority: TaskPriority = Field(default=TaskPriority.normal)
    task_class: TaskClass = Field(default=TaskClass.interactive)
    error: Optional[Dict[str, Any]] = None
    result_ref: Optional[str] = None
    payload_ref: Optional[str] = None
    created_at: str
    updated_at: str
    batch_id: Optional[str] = None
    batch_max_parallel: Optional[int] = None
    callback_url: Optional[str] = None
    idempotency_key: Optional[str] = None
