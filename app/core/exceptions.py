from __future__ import annotations

from fastapi import Request
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.responses import JSONResponse

from app.schemas.common import ErrorResponse, ErrorDetail


async def http_422_handler(_: Request, exc):  # type: ignore[no-untyped-def]
    error = ErrorResponse(error=ErrorDetail(code="validation_error", message=str(exc)))
    return JSONResponse(status_code=422, content=error.model_dump())


async def http_error_handler(_: Request, exc: StarletteHTTPException):
    status = getattr(exc, "status_code", 500)
    if status == 404:
        code = "not_found"
    elif status == 400:
        code = "bad_request"
    elif status == 401:
        code = "unauthorized"
    elif status == 403:
        code = "forbidden"
    else:
        code = "http_error"
    error = ErrorResponse(error=ErrorDetail(code=code, message=str(exc)))
    return JSONResponse(status_code=status, content=error.model_dump())


async def http_500_handler(_: Request, exc):  # type: ignore[no-untyped-def]
    error = ErrorResponse(error=ErrorDetail(code="internal_error", message=str(exc)))
    return JSONResponse(status_code=500, content=error.model_dump())
