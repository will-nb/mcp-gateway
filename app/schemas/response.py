from __future__ import annotations

from typing import Generic, Optional, TypeVar
from pydantic import BaseModel, Field


T = TypeVar("T")


class SuccessResponse(BaseModel, Generic[T]):
    code: int = Field(0, description="0 indicates success; non-zero for errors")
    message: str = Field("success", description="Human readable message")
    data: Optional[T] = Field(None, description="Successful response payload")


class EmptyPayload(BaseModel):
    pass
