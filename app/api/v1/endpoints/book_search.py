from __future__ import annotations

from typing import Dict, List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.schemas.common import ApiStandardResponse, create_object_response, DataType
from app.services.isbn.search_manager import search_title


router = APIRouter()


class SearchByTitleRequest(BaseModel):
    title: str = Field(..., description="书名关键词，支持近似匹配（分词 Jaccard 相似度）")
    minSimilarity: float = Field(0.6, description="最小相似度阈值，范围 0-1，建议 0.5-0.7")
    maxResultsPerSource: int = Field(5, description="每个来源最大返回条数")
    preferOrder: Optional[List[str]] = Field(None, description="来源优先级（如 loc/open_library/google_books）")
    forceSource: Optional[str] = Field(None, description="强制来源")
    apiKeys: Optional[Dict[str, str]] = Field(None, description="可选 key 集（google_books 等）")
    lang: Optional[str] = Field(None, description="语言限制（例如 en/zh）")
    timeout: float = Field(10.0, description="超时")


@router.post(
    "/books/search-title",
    response_model=ApiStandardResponse,
    summary="按书名搜索",
    description=(
        "中文说明:\n"
        "- 对 LOC / Open Library / Google Books 进行标题搜索\n"
        "- 使用分词 Jaccard 相似度过滤，建议阈值 0.5-0.7\n"
        "- forceSource 可强制单一来源；preferOrder 调整优先级\n"
    ),
    openapi_extra={
        "requestBody": {
            "content": {
                "application/json": {
                    "example": {
                        "title": "The 7 Habits of Highly Effective People",
                        "minSimilarity": 0.6,
                        "maxResultsPerSource": 3,
                        "preferOrder": ["open_library", "google_books"],
                        "apiKeys": {"google_books": "YOUR_GOOGLE_BOOKS_KEY"},
                        "lang": "en",
                        "timeout": 8.0
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
        api_keys=req.apiKeys,
        lang=req.lang,
        timeout=req.timeout,
        prefer_order=req.preferOrder,
        force_source=req.forceSource,
    )
    return create_object_response(message="OK", data_value={"items": results}, data_type=DataType.LIST, code=200)
