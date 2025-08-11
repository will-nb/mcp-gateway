from __future__ import annotations

import time
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional, Tuple

from fastapi import Header
from pymongo.collection import Collection

from app.core.config import get_settings
from app.services.redis_client import get_redis_service
from app.services.mongo_client import get_database
from app.schemas.tasks import (
    EnqueueRequest,
    TaskClass,
    TaskPriority,
    JobStatus,
)


def _utc_iso(dt: Optional[datetime] = None) -> str:
    return (dt or datetime.now(timezone.utc)).isoformat()


def _jobs_collection() -> Collection:
    db = get_database()
    return db["jobs"]


def _compute_lane(task_class: TaskClass, priority: Optional[TaskPriority]) -> Tuple[str, TaskPriority]:
    # Default mapping by class
    default_priority = {
        TaskClass.interactive: TaskPriority.high,
        TaskClass.bulk: TaskPriority.low,
        TaskClass.offline: TaskPriority.low,
    }[task_class]
    final_priority = priority or default_priority
    lane = final_priority.value
    return lane, final_priority


def _stream_key(lane: str) -> str:
    s = get_settings()
    return f"{s.redis_key_prefix}:tasks:{lane}"


def _idempotent_find(task_type: str, idempotency_key: Optional[str], payload_ref: Optional[str]) -> Optional[Dict[str, Any]]:
    if not idempotency_key:
        return None
    col = _jobs_collection()
    doc = col.find_one(
        {
            "type": task_type,
            "idempotency_key": idempotency_key,
            "payload_ref": payload_ref,
        },
        projection={"_id": False},
    )
    return doc


def enqueue_task(
    *,
    task_type: str,
    req: EnqueueRequest,
    task_class: TaskClass,
    priority: Optional[TaskPriority],
    idempotency_key: Optional[str],
) -> Tuple[str, str]:
    # Idempotency check
    existing = _idempotent_find(task_type, idempotency_key, req.payload_ref)
    if existing:
        job_id = existing["id"]
        return job_id, existing.get("status", JobStatus.queued)

    lane, final_priority = _compute_lane(task_class, priority)

    job_id = str(uuid.uuid4())
    now = _utc_iso()

    # Persist to Mongo first
    col = _jobs_collection()
    doc = {
        "id": job_id,
        "type": task_type,
        "status": JobStatus.queued,
        "tries": 0,
        "priority": final_priority.value,
        "task_class": task_class.value,
        "payload_ref": req.payload_ref,
        "params": req.params or {},
        "result_ref": None,
        "error": None,
        "created_at": now,
        "updated_at": now,
        "batch_id": req.batch_id,
        "batch_max_parallel": req.batch_max_parallel,
        "callback_url": req.callback_url,
        "idempotency_key": idempotency_key,
    }
    col.insert_one(doc)

    # Enqueue to Redis Stream
    r = get_redis_service().get_client()
    message: Dict[str, Any] = {
        "id": job_id,
        "type": task_type,
        "task_class": task_class.value,
        "priority": final_priority.value,
        "payload_ref": req.payload_ref,
        "params": json_dumps_safe(req.params or {}),
        "batch_id": req.batch_id or "",
        "batch_max_parallel": str(req.batch_max_parallel or 2),
        "callback_url": req.callback_url or "",
        "created_at": now,
    }
    r.xadd(_stream_key(lane), message)

    return job_id, JobStatus.queued


def json_dumps_safe(obj: Any) -> str:
    try:
        import json

        return json.dumps(obj, ensure_ascii=False)
    except Exception:
        return "{}"


def get_job(job_id: str) -> Optional[Dict[str, Any]]:
    col = _jobs_collection()
    doc = col.find_one({"id": job_id}, projection={"_id": False})
    return doc


def cancel_job(job_id: str) -> bool:
    col = _jobs_collection()
    res = col.update_one(
        {"id": job_id, "status": {"$in": [JobStatus.queued, JobStatus.running]}},
        {"$set": {"status": JobStatus.canceled, "updated_at": _utc_iso()}},
    )
    return res.modified_count > 0


def wait_for_completion(job_id: str, timeout_ms: int) -> Optional[Dict[str, Any]]:
    # Simple polling on Mongo for demo purposes
    deadline = time.time() + (timeout_ms / 1000.0)
    col = _jobs_collection()
    while time.time() < deadline:
        doc = col.find_one({"id": job_id}, projection={"_id": False})
        if doc and doc.get("status") in {JobStatus.succeeded, JobStatus.failed, JobStatus.canceled}:
            return doc
        time.sleep(0.05)
    return None
