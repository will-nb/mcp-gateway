from typing import List, Optional

from fastapi import APIRouter
from pydantic import BaseModel, Field
from qdrant_client import models

from app.core.config import get_settings
from app.schemas.common import ApiStandardResponse, create_object_response, DataType
from app.services.qdrant import get_qdrant_service


router = APIRouter()


class EnsureCollectionRequest(BaseModel):
    collection_name: Optional[str] = Field(
        None, description="Defaults to configured qdrant_default_collection"
    )
    vector_size: Optional[int] = Field(
        None, description="Defaults to configured qdrant_vector_dim"
    )


@router.post(
    "/qdrant/ensure-collection",
    response_model=ApiStandardResponse,
    summary="Ensure a collection exists",
)
def ensure_collection(req: EnsureCollectionRequest) -> ApiStandardResponse:
    s = get_settings()
    name = req.collection_name or s.qdrant_default_collection
    dim = req.vector_size or s.qdrant_vector_dim
    created = get_qdrant_service().ensure_collection(name, dim)
    return create_object_response(
        message="OK",
        data_value={"created": created},
        data_type=DataType.OBJECT,
        code=200,
    )


class UpsertPoint(BaseModel):
    id: int | str
    vector: List[float]
    payload: Optional[dict] = None


class UpsertPointsRequest(BaseModel):
    collection_name: Optional[str] = None
    points: List[UpsertPoint]


@router.post(
    "/qdrant/upsert", response_model=ApiStandardResponse, summary="Upsert points"
)
def upsert_points(req: UpsertPointsRequest) -> ApiStandardResponse:
    s = get_settings()
    name = req.collection_name or s.qdrant_default_collection
    pts = [
        models.PointStruct(id=p.id, vector=p.vector, payload=p.payload)
        for p in req.points
    ]
    res = get_qdrant_service().upsert_points(name, pts)
    return create_object_response(
        message="OK",
        data_value={"status": res.status.value},
        data_type=DataType.OBJECT,
        code=200,
    )


class SimpleSearchRequest(BaseModel):
    collection_name: Optional[str] = None
    vector: List[float]
    limit: int = 5


class ScoredPoint(BaseModel):
    id: int | str
    score: float
    payload: Optional[dict] = None


class SimpleSearchResponse(BaseModel):
    results: List[ScoredPoint]


@router.post(
    "/qdrant/search", response_model=ApiStandardResponse, summary="Simple vector search"
)
def simple_search(req: SimpleSearchRequest) -> ApiStandardResponse:
    s = get_settings()
    name = req.collection_name or s.qdrant_default_collection
    result = get_qdrant_service().query(name, req.vector, limit=req.limit)
    items = [
        ScoredPoint(id=p.id, score=p.score, payload=p.payload) for p in result.points
    ]
    payload = SimpleSearchResponse(results=items).model_dump()
    return create_object_response(
        message="OK", data_value=payload, data_type=DataType.OBJECT, code=200
    )
