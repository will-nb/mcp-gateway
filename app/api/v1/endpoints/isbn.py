from __future__ import annotations

from typing import Dict, List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.schemas.common import ApiStandardResponse, create_object_response, DataType
from app.services.isbn import manager as isbn_manager
from app.services.isbn.client_base import RateLimitError


router = APIRouter()


class ResolveIsbnRequest(BaseModel):
    isbn: str = Field(..., description="ISBN-10 或 ISBN-13")
    countryCode: Optional[str] = Field(None, description="国别代码，如 CN/US/GB/JP/KR/HK")
    forceSource: Optional[str] = Field(None, description="强制指定来源常量，例如 google_books/open_library/loc 等")
    preferOrder: Optional[List[str]] = Field(None, description="可选的来源优先顺序，靠前优先")
    timeout: float = Field(10.0, description="超时秒数")
    apiKeys: Optional[Dict[str, str]] = Field(None, description="各来源所需的 key，例如 {google_books, isbndb, worldcat, kolisnet}")


@router.post("/isbn/resolve", response_model=ApiStandardResponse, summary="根据 ISBN 获取书籍信息")
def isbn_resolve(req: ResolveIsbnRequest) -> ApiStandardResponse:
    try:
        doc = isbn_manager.resolve_isbn(
            req.isbn,
            country_code=req.countryCode,
            prefer_order=req.preferOrder,
            api_keys=req.apiKeys,
            timeout=req.timeout,
            force_source=req.forceSource,
        )
    except RateLimitError as e:
        raise HTTPException(status_code=429, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"resolve failed: {e}")

    if not doc:
        raise HTTPException(status_code=404, detail="未找到对应书籍")

    return create_object_response(message="OK", data_value=doc, data_type=DataType.OBJECT, code=200)
