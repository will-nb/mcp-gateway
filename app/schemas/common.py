from datetime import datetime, UTC
from typing import Any, Dict, List, Optional, Union
from enum import Enum

from pydantic import ConfigDict, Field

from app.schemas.base import CamelModel


class DataType(str, Enum):
    STRING = "string"
    NUMBER = "number"
    BOOLEAN = "boolean"
    OBJECT = "object"
    LIST = "list"
    HEALTH = "health"
    INFO = "info"
    AI = "ai_chat"


class ApiStandardResponse(CamelModel):
    success: bool = True
    message: str = "操作成功"
    data_type: str = Field(..., description="数据类型")
    data: Any = Field(..., description="响应数据")
    error: Optional[Dict[str, Any]] = None
    code: int = 200
    timestamp: str = Field(
        default_factory=lambda: datetime.now(UTC).isoformat(),
        description="响应时间戳",
        json_schema_extra={"type": "string", "format": "date-time"},
    )


def create_object_response(
    *,
    message: str = "操作成功",
    data_value: Optional[Dict[str, Any]] = None,
    data_type: str = DataType.OBJECT,
    code: int = 200,
    error: Optional[Dict[str, Any]] = None,
) -> ApiStandardResponse:
    return ApiStandardResponse(
        success=True,
        message=message,
        data_type=data_type,
        data=data_value or {},
        error=error,
        code=code,
    )


class ErrorDetail(CamelModel):
    code: str = Field(..., description="错误代码")
    message: str = Field(..., description="错误消息")


class ErrorResponse(CamelModel):
    code: int = Field(500, description="错误状态码")
    message: str = Field("Internal Server Error", description="错误消息")
    data_type: str = Field("error", description="数据类型")
    error: ErrorDetail = Field(..., description="错误详情")
    timestamp: str = Field(
        default_factory=lambda: datetime.now(UTC).isoformat(),
        description="响应时间戳",
        json_schema_extra={"type": "string", "format": "date-time"},
    )
