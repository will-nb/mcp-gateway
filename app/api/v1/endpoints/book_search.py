from __future__ import annotations

from typing import Dict, List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.schemas.common import ApiStandardResponse, create_object_response, DataType
from app.services.isbn.search_manager import search_title
from app.services.isbn import manager as isbn_manager


router = APIRouter()


class SearchByTitleRequest(BaseModel):
    title: str = Field(..., description="书名关键词")
    minSimilarity: float = Field(0.6, description="最小相似度阈值，范围 0-1")
    maxResultsPerSource: int = Field(5, description="每个来源最大返回条数")
    forceSource: Optional[str] = Field(None, description="强制来源")


@router.post(
    "/books/search-title",
    response_model=ApiStandardResponse,
    summary="按书名搜索",
    description=(
        "中文说明:\n"
        "- 对 LOC / Open Library / Google Books 进行标题搜索\n"
        "- 使用分词 Jaccard 相似度过滤，建议阈值 0.5-0.7\n"
        "- 可选 forceSource 强制单一来源\n"
    ),
    openapi_extra={
        "requestBody": {
            "content": {
                "application/json": {
                    "example": {
                        "title": "The 7 Habits of Highly Effective People",
                        "minSimilarity": 0.6,
                        "maxResultsPerSource": 3,
                        
                    }
                }
            }
        }
    }
)
def search_books_by_title(req: SearchByTitleRequest) -> ApiStandardResponse:
    results = search_title(
        req.title,
        max_results_per_source=req.maxResultsPerSource,
        min_similarity=req.minSimilarity,
        api_keys=None,
        lang=None,
        timeout=10.0,
        prefer_order=None,
        force_source=req.forceSource,
    )
    return create_object_response(message="OK", data_value={"items": results}, data_type=DataType.LIST, code=200)


class SearchByIsbnRequest(BaseModel):
    isbn: str = Field(..., description="ISBN-10 或 ISBN-13")
    forceSource: Optional[str] = Field(None, description="强制来源常量")
    # 其余策略在服务端自动推断（超时、国别优先级、去重防抖）


@router.post(
    "/books/search-isbn",
    response_model=ApiStandardResponse,
    summary="按 ISBN 搜索图书",
    openapi_extra={
        "requestBody": {
            "content": {
                "application/json": {
                    "example": {
                        "isbn": "9787801207647",
                        "forceSource": "juhe_isbn"
                    }
                }
            }
        }
    }
)
def search_books_by_isbn(req: SearchByIsbnRequest) -> ApiStandardResponse:
    from app.services.isbn.client_base import RateLimitError
    try:
        doc = isbn_manager.resolve_isbn(
            req.isbn,
            force_source=req.forceSource,
        )
    except RateLimitError as e:
        raise HTTPException(status_code=429, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"resolve failed: {e}")
    if not doc:
        raise HTTPException(status_code=404, detail="未找到对应书籍")
    return create_object_response(message="OK", data_value=doc, data_type=DataType.OBJECT, code=200)
