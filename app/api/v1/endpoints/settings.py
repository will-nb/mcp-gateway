from fastapi import APIRouter

from app.core.config import get_settings
from app.schemas.common import ApiStandardResponse, create_object_response, DataType
from pydantic import BaseModel, Field


router = APIRouter()


class PublicSettings(BaseModel):
    app_name: str = Field(default_factory=lambda: get_settings().app_name)
    version: str = Field(default_factory=lambda: get_settings().version)
    # Qdrant
    qdrant_host: str = Field(default_factory=lambda: get_settings().qdrant_host)
    qdrant_http_port: int = Field(default_factory=lambda: get_settings().qdrant_http_port)
    qdrant_grpc_port: int = Field(default_factory=lambda: get_settings().qdrant_grpc_port)
    qdrant_prefer_grpc: bool = Field(default_factory=lambda: get_settings().qdrant_prefer_grpc)
    qdrant_default_collection: str = Field(default_factory=lambda: get_settings().qdrant_default_collection)
    qdrant_vector_dim: int = Field(default_factory=lambda: get_settings().qdrant_vector_dim)
    # Redis (non-sensitive)
    redis_host: str = Field(default_factory=lambda: get_settings().redis_host)
    redis_port: int = Field(default_factory=lambda: get_settings().redis_port)
    redis_db: int = Field(default_factory=lambda: get_settings().redis_db)
    redis_key_prefix: str = Field(default_factory=lambda: get_settings().redis_key_prefix)


@router.get("/settings", response_model=ApiStandardResponse, summary="Public settings")
def get_public_settings() -> ApiStandardResponse:
    s = get_settings()
    ps = PublicSettings(
        app_name=s.app_name,
        version=s.version,
        qdrant_host=s.qdrant_host,
        qdrant_http_port=s.qdrant_http_port,
        qdrant_grpc_port=s.qdrant_grpc_port,
        qdrant_prefer_grpc=s.qdrant_prefer_grpc,
        qdrant_default_collection=s.qdrant_default_collection,
        qdrant_vector_dim=s.qdrant_vector_dim,
        redis_host=s.redis_host,
        redis_port=s.redis_port,
        redis_db=s.redis_db,
        redis_key_prefix=s.redis_key_prefix,
    )
    return create_object_response(
        message="OK",
        data_value=ps.model_dump(by_alias=True),
        data_type=DataType.OBJECT,
        code=200,
    )
