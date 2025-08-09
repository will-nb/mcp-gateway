from datetime import datetime
from typing import Dict

from pydantic import Field

from app.schemas.base import CamelModel


class ServiceStatus(CamelModel):
    status: str = Field(..., description="服务状态")
    message: str = Field(..., description="状态消息")


class HealthResponse(CamelModel):
    status: str = Field(..., description="整体状态")
    version: str = Field(..., description="版本信息")
    timestamp: str = Field(..., description="时间戳", json_schema_extra={"format": "date-time"})
    services: Dict[str, ServiceStatus] = Field(..., description="各服务状态")
