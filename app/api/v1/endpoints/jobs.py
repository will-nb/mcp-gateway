from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.schemas.common import ApiStandardResponse, create_object_response, DataType
from app.services.tasks import get_job, cancel_job


router = APIRouter(prefix="/jobs", tags=["jobs"])  # Mounted under /api/v1


@router.get("/{job_id}", response_model=ApiStandardResponse, summary="Get job status")
async def get_job_status(job_id: str) -> ApiStandardResponse:
    doc = get_job(job_id)
    if not doc:
        raise HTTPException(status_code=404, detail="job not found")
    return create_object_response(message="OK", data_value=doc, data_type=DataType.OBJECT, code=200)


@router.delete("/{job_id}", response_model=ApiStandardResponse, summary="Cancel queued job")
async def cancel_job_status(job_id: str) -> ApiStandardResponse:
    ok = cancel_job(job_id)
    if not ok:
        raise HTTPException(status_code=409, detail="cannot cancel in current state")
    return create_object_response(message="Canceled", data_value={"jobId": job_id}, data_type=DataType.OBJECT, code=200)
