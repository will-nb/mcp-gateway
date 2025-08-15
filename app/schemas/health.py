from __future__ import annotations

from pydantic import BaseModel, Field


class QdrantHealth(BaseModel):
    reachable: bool = Field(default=True, json_schema_extra={"example": True})
    host: str = Field(default="localhost", json_schema_extra={"example": "localhost"})
    http_port: int = Field(default=6333, json_schema_extra={"example": 6333})


class MongoHealth(BaseModel):
    reachable: bool = Field(default=True, json_schema_extra={"example": True})
    uri: str = Field(
        default="mongodb://localhost:27017",
        json_schema_extra={"example": "mongodb://localhost:27017"},
    )
    db: str = Field(default="mcp_gateway", json_schema_extra={"example": "mcp_gateway"})


class HealthResponse(BaseModel):
    status: str = Field(default="ok", json_schema_extra={"example": "ok"})
    version: str = Field(default="1.0.0", json_schema_extra={"example": "1.0.0"})
    qdrant: QdrantHealth | None = None
    redis: RedisHealth | None = None
    mongo: MongoHealth | None = None


class RedisHealth(BaseModel):
    reachable: bool = Field(default=True, json_schema_extra={"example": True})
    host: str = Field(default="localhost", json_schema_extra={"example": "localhost"})
    port: int = Field(default=6379, json_schema_extra={"example": 6379})
    db: int = Field(default=1, json_schema_extra={"example": 1})
    key_prefix: str = Field(default="mcp", json_schema_extra={"example": "mcp"})
