# app/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.api.v1.api import api_router
from app.core.exceptions import http_422_handler, http_error_handler, http_500_handler
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException


settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version=settings.version,
)

# Force OpenAPI 3.0.3 schema
from fastapi.openapi.utils import get_openapi

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title=settings.app_name,
        version=settings.version,
        openapi_version="3.0.3",
        routes=app.routes,
        description="MCP Gateway API",
    )
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

# Register global exception handlers
app.add_exception_handler(RequestValidationError, http_422_handler)
app.add_exception_handler(StarletteHTTPException, http_error_handler)
app.add_exception_handler(Exception, http_500_handler)


# CORS configuration for local development and deployments
allow_origins = settings.allowed_origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins if allow_origins else ["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Root endpoint (simple liveness)
from app.schemas.response import SuccessResponse, EmptyPayload


@app.get("/", response_model=SuccessResponse[EmptyPayload])
def read_root() -> SuccessResponse[EmptyPayload]:
    return SuccessResponse(data=None)


# Mount API routers
app.include_router(api_router, prefix=settings.api_v1_prefix)
