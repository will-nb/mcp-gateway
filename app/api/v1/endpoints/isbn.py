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
    # apiKey 仅从服务端配置读取，不允许从接口传入


@router.post(
    
    "/isbn/resolve",
    response_model=ApiStandardResponse,
    summary="根据 ISBN 获取书籍信息",
    description=(
        "中文说明:\n"
        "- 按照优先级顺序(本地Mongo → 国别国家级API → 免费强 → 免费小 → 收费)查询书籍\n"
        "- 支持 forceSource 强制指定来源；若该来源被上游限流，返回 429\n"
        "- 支持 countryCode 指定国别以优先国家级接口 (CN/HK/JP/KR/GB/US)\n"
        "- 上游限流(429/403)将触发 24 小时抑制并自动换源\n"
    ),
    openapi_extra={
        "requestBody": {
            "content": {
                "application/json": {
                    "example": {
                        "isbn": "9781982137274",
                        "countryCode": "US",
                        "forceSource": None,
                        "preferOrder": ["loc", "open_library", "google_books"],
                        "timeout": 10.0,
                        "apiKeys": {
                            "google_books": "YOUR_GOOGLE_BOOKS_KEY",
                            "isbndb": "YOUR_ISBNDB_KEY",
                            "worldcat": "YOUR_WORLDCAT_WSKEY"
                        }
                    }
                }
            }
        },
        "responses": {
            "200": {
                "description": "成功示例",
                "content": {
                    "application/json": {
                        "example": {
                            "success": True,
                            "message": "OK",
                            "dataType": "object",
                            "data": {
                                "source": "open_library",
                                "isbn": "9781982137274",
                                "title": "The 7 Habits of Highly Effective People",
                                "subtitle": "30th Anniversary Edition",
                                "creators": [{"name": "Stephen R. Covey", "role": None}],
                                "publisher": "Simon & Schuster",
                                "published_date": "2020-05-19",
                                "language": "en",
                                "subjects": ["Self-Help", "Personal Development"],
                                "description": "Powerful lessons in personal change...",
                                "page_count": 432,
                                "identifiers": {"isbn_10": "1982137274", "isbn_13": "9781982137274"},
                                "cover": {"thumbnail": "https://covers.openlibrary.org/b/id/9876543-M.jpg"},
                                "preview_urls": [
                                    "https://books.google.com/books?id=EXAMPLE",
                                    "https://openlibrary.org/isbn/9781982137274"
                                ],
                                "raw": {}
                            },
                            "code": 200,
                            "timestamp": "2025-01-01T00:00:00Z"
                        }
                    }
                }
            },
            "404": {"description": "未找到对应书籍"},
            "429": {"description": "指定来源被上游限流/封禁"},
            "502": {"description": "上游错误/解析失败"}
        }
    }
)
def isbn_resolve(req: ResolveIsbnRequest) -> ApiStandardResponse:
    try:
        doc = isbn_manager.resolve_isbn(
            req.isbn,
            country_code=req.countryCode,
            prefer_order=req.preferOrder,
            api_keys=None,
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
