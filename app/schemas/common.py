from __future__ import annotations

from typing import Any, Optional
from pydantic import BaseModel, Field


class ErrorDetail(BaseModel):
    code: str = Field(default="bad_request", json_schema_extra={"example": "bad_request"})
    message: str = Field(default="Invalid request parameters", json_schema_extra={"example": "Invalid request parameters"})
    details: Optional[dict[str, Any]] = None


class ErrorResponse(BaseModel):
    error: ErrorDetail
