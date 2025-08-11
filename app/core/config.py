from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache
from typing import List, Dict, Any


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
    # MongoDB connection
    mongo_uri: str
    mongo_db: str
    # ISBN API keys
    google_books_api_key: str | None
    isbndb_api_key: str | None
    worldcat_wskey: str | None
    kolisnet_service_key: str | None
    juhe_isbn_api_key: str | None
    # Qwen / DashScope (OpenAI-compatible)
    dashscope_api_key: str | None
    dashscope_base_url: str
    qwen_allowed_models: List[str]
    # OpenAI / Gemini / Claude (兼容代理所需)
    openai_api_key: str | None
    openai_base_url: str
    gemini_api_key: str | None
    gemini_base_url: str
    anthropic_api_key: str | None
    anthropic_base_url: str
    # Semantic cache
    qdrant_cache_collection: str
    qdrant_cache_vector_dim: int
    qdrant_cache_score_threshold: float
    # Interactive sync fast-path default (ms)
    interactive_sync_timeout_ms: int
    # Callback security
    callback_hmac_secret: str | None
    callback_domain_whitelist: List[str]
    # Provider rate/budget configs (simple dicts for now)
    provider_limits: Dict[str, Any]
    provider_budgets: Dict[str, Any]


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

    # MongoDB (host machine)
    mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    mongo_db = os.getenv("MONGO_DB", "mcp_gateway")

    # ISBN API keys
    google_books_api_key = os.getenv("GOOGLE_BOOKS_API_KEY")
    isbndb_api_key = os.getenv("ISBNDB_API_KEY")
    worldcat_wskey = os.getenv("WORLDCAT_WSKEY")
    kolisnet_service_key = os.getenv("KOLISNET_SERVICE_KEY")
    juhe_isbn_api_key = os.getenv("JUHE_ISBN_API_KEY")

    # Qwen / DashScope (OpenAI compatible)
    dashscope_api_key = os.getenv("DASHSCOPE_API_KEY")
    dashscope_base_url = os.getenv(
        "DASHSCOPE_BASE_URL",
        "https://dashscope.aliyuncs.com/compatible-mode/v1",
    )
    # OpenAI
    openai_api_key = os.getenv("OPENAI_API_KEY")
    openai_base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    # Gemini
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    gemini_base_url = os.getenv(
        "GEMINI_BASE_URL",
        "https://generativelanguage.googleapis.com",
    )
    # Claude (Anthropic)
    anthropic_api_key = os.getenv("CLAUDE_API_KEY") or os.getenv("ANTHROPIC_API_KEY")
    anthropic_base_url = os.getenv("ANTHROPIC_BASE_URL", "https://api.anthropic.com")
    qwen_allowed_models_env = os.getenv(
        "QWEN_ALLOWED_MODELS",
        "qwen-plus,qwen3-coder-plus,qwen3-coder-flash,qwen-flash",
    )
    qwen_allowed_models = [m.strip() for m in qwen_allowed_models_env.split(",") if m.strip()]

    # Semantic cache
    qdrant_cache_collection = os.getenv("QDRANT_CACHE_COLLECTION", "mcp_chat_cache")
    qdrant_cache_vector_dim = int(os.getenv("QDRANT_CACHE_VECTOR_DIM", "256"))
    qdrant_cache_score_threshold = float(os.getenv("QDRANT_CACHE_SCORE_THRESHOLD", "0.92"))

    # Interactive sync default (global)
    interactive_sync_timeout_ms = int(os.getenv("INTERACTIVE_SYNC_TIMEOUT_MS", "2500"))

    # Callback security
    callback_hmac_secret = os.getenv("CALLBACK_HMAC_SECRET")
    # Comma-separated hosts or suffix patterns ('.fly.dev' means any subdomain)
    callback_domain_whitelist_env = os.getenv(
        "CALLBACK_DOMAIN_WHITELIST",
        ",".join([
            "localhost",
            "127.0.0.1",
            "host.docker.internal",
            ".fly.dev",
        ]),
    )
    callback_domain_whitelist = [h.strip() for h in callback_domain_whitelist_env.split(",") if h.strip()]

    # Provider limits/budgets (JSON; fallback to permissive defaults)
    import json
    provider_limits_default = {
        "google_books": {"qps": 10, "burst": 20},
        "open_library": {"qps": 5, "burst": 10},
        "isbndb": {"qps": 2, "burst": 4},
        "ai": {"global_qps": 100, "burst": 200, "max_concurrency_per_tenant": 2},
    }
    provider_budgets_default = {
        "ai": {"monthly_budget_usd": 10_000_000},  # effectively no cap by default
        "google_books": {"daily_requests": 1_000_000},
        "open_library": {"daily_requests": 1_000_000},
        "isbndb": {"daily_requests": 1_000_000},
    }
    try:
        provider_limits = json.loads(os.getenv("PROVIDER_LIMITS", "")) or provider_limits_default
    except Exception:
        provider_limits = provider_limits_default
    try:
        provider_budgets = json.loads(os.getenv("PROVIDER_BUDGETS", "")) or provider_budgets_default
    except Exception:
        provider_budgets = provider_budgets_default

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
        interactive_sync_timeout_ms=interactive_sync_timeout_ms,
        callback_hmac_secret=callback_hmac_secret,
        callback_domain_whitelist=callback_domain_whitelist,
        provider_limits=provider_limits,
        provider_budgets=provider_budgets,
        openai_api_key=openai_api_key,
        openai_base_url=openai_base_url,
        gemini_api_key=gemini_api_key,
        gemini_base_url=gemini_base_url,
        anthropic_api_key=anthropic_api_key,
        anthropic_base_url=anthropic_base_url,
        mongo_uri=mongo_uri,
        mongo_db=mongo_db,
        google_books_api_key=google_books_api_key,
        isbndb_api_key=isbndb_api_key,
        worldcat_wskey=worldcat_wskey,
        kolisnet_service_key=kolisnet_service_key,
        juhe_isbn_api_key=juhe_isbn_api_key,
    )
