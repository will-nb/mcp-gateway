from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache
from typing import List


@dataclass(frozen=True)
class AppSettings:
    app_name: str
    version: str
    api_v1_prefix: str
    debug: bool
    allowed_origins: List[str]
    # Qdrant connection
    qdrant_host: str
    qdrant_http_port: int
    qdrant_grpc_port: int
    qdrant_prefer_grpc: bool
    qdrant_default_collection: str
    qdrant_vector_dim: int
    # Redis connection
    redis_host: str
    redis_port: int
    redis_db: int
    redis_password: str | None
    redis_key_prefix: str
    # Qwen / DashScope (OpenAI-compatible)
    dashscope_api_key: str | None
    dashscope_base_url: str
    qwen_allowed_models: List[str]
    # Semantic cache
    qdrant_cache_collection: str
    qdrant_cache_vector_dim: int
    qdrant_cache_score_threshold: float


def _parse_bool_env(value: str | None, default: bool) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "t", "yes", "y", "on"}


@lru_cache(maxsize=1)
def get_settings() -> AppSettings:
    app_name = os.getenv("APP_NAME", "MCP Gateway")
    version = os.getenv("APP_VERSION", "1.0.0")
    api_v1_prefix = os.getenv("API_V1_PREFIX", "/api/v1")
    debug = _parse_bool_env(os.getenv("DEBUG"), False)
    allowed_origins_env = os.getenv("ALLOWED_ORIGINS", "*")
    # Qdrant
    qdrant_host = os.getenv("QDRANT_HOST", "localhost")
    qdrant_http_port = int(os.getenv("QDRANT_HTTP_PORT", "6333"))
    qdrant_grpc_port = int(os.getenv("QDRANT_GRPC_PORT", "6334"))
    qdrant_prefer_grpc = _parse_bool_env(os.getenv("QDRANT_PREFER_GRPC"), False)
    qdrant_default_collection = os.getenv("QDRANT_DEFAULT_COLLECTION", "mcp_default")
    qdrant_vector_dim = int(os.getenv("QDRANT_VECTOR_DIM", "4"))

    # Redis (local dev default)
    redis_host = os.getenv("REDIS_HOST", "localhost")
    redis_port = int(os.getenv("REDIS_PORT", "6379"))
    redis_db = int(os.getenv("REDIS_DB", "1"))
    redis_password = os.getenv("REDIS_PASSWORD")  # None by default
    redis_key_prefix = os.getenv("REDIS_KEY_PREFIX", "mcp")

    # Qwen / DashScope (OpenAI compatible)
    dashscope_api_key = os.getenv("DASHSCOPE_API_KEY")
    dashscope_base_url = os.getenv(
        "DASHSCOPE_BASE_URL",
        "https://dashscope.aliyuncs.com/compatible-mode/v1",
    )
    qwen_allowed_models_env = os.getenv(
        "QWEN_ALLOWED_MODELS",
        "qwen-plus,qwen3-coder-plus,qwen3-coder-flash,qwen-flash",
    )
    qwen_allowed_models = [m.strip() for m in qwen_allowed_models_env.split(",") if m.strip()]

    # Semantic cache
    qdrant_cache_collection = os.getenv("QDRANT_CACHE_COLLECTION", "mcp_chat_cache")
    qdrant_cache_vector_dim = int(os.getenv("QDRANT_CACHE_VECTOR_DIM", "256"))
    qdrant_cache_score_threshold = float(os.getenv("QDRANT_CACHE_SCORE_THRESHOLD", "0.92"))

    if allowed_origins_env.strip() == "*":
        allowed_origins = ["*"]
    else:
        allowed_origins = [
            origin.strip() for origin in allowed_origins_env.split(",") if origin.strip()
        ]

    return AppSettings(
        app_name=app_name,
        version=version,
        api_v1_prefix=api_v1_prefix,
        debug=debug,
        allowed_origins=allowed_origins,
        qdrant_host=qdrant_host,
        qdrant_http_port=qdrant_http_port,
        qdrant_grpc_port=qdrant_grpc_port,
        qdrant_prefer_grpc=qdrant_prefer_grpc,
        qdrant_default_collection=qdrant_default_collection,
        qdrant_vector_dim=qdrant_vector_dim,
        redis_host=redis_host,
        redis_port=redis_port,
        redis_db=redis_db,
        redis_password=redis_password,
        redis_key_prefix=redis_key_prefix,
        dashscope_api_key=dashscope_api_key,
        dashscope_base_url=dashscope_base_url,
        qwen_allowed_models=qwen_allowed_models,
        qdrant_cache_collection=qdrant_cache_collection,
        qdrant_cache_vector_dim=qdrant_cache_vector_dim,
        qdrant_cache_score_threshold=qdrant_cache_score_threshold,
    )
