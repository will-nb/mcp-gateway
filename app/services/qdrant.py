from __future__ import annotations

from functools import lru_cache
from typing import Iterable, List, Optional, Sequence

from qdrant_client import QdrantClient, models

from app.core.config import get_settings


class QdrantService:
    """
    High-level helper around QdrantClient with convenient operations
    while still exposing the raw client for full flexibility.
    """

    def __init__(
        self,
        host: str = "localhost",
        port: int = 6333,
        grpc_port: int = 6334,
        prefer_grpc: bool = False,
        **kwargs,
    ) -> None:
        self._client = QdrantClient(
            host=host,
            port=port,
            grpc_port=grpc_port,
            prefer_grpc=prefer_grpc,
            **kwargs,
        )
        # smoke check
        self._client.get_collections()

    # -------- Access to raw client --------
    def get_client(self) -> QdrantClient:
        return self._client

    # -------- Collections --------
    def ensure_collection(
        self,
        collection_name: str,
        vector_size: int,
        distance: models.Distance = models.Distance.COSINE,
    ) -> bool:
        """Create collection if not exists; returns True if created, else False."""
        if self._client.collection_exists(collection_name):
            return False
        self._client.create_collection(
            collection_name=collection_name,
            vectors_config=models.VectorParams(size=vector_size, distance=distance),
        )
        return True

    # -------- Points (Upsert/Delete/Retrieve) --------
    def upsert_points(
        self,
        collection_name: str,
        points: Sequence[models.PointStruct],
        wait: bool = True,
    ) -> models.UpdateResult:
        return self._client.upsert(
            collection_name=collection_name,
            points=list(points),
            wait=wait,
        )

    def delete_points(
        self,
        collection_name: str,
        point_ids: Iterable[int | str],
        wait: bool = True,
    ) -> models.UpdateResult:
        return self._client.delete(
            collection_name=collection_name,
            points_selector=models.PointIdsList(points=list(point_ids)),
            wait=wait,
        )

    def retrieve_points(
        self,
        collection_name: str,
        point_ids: Iterable[int | str],
        with_payload: bool = True,
        with_vectors: bool = False,
    ) -> List[models.Record]:
        return self._client.retrieve(
            collection_name=collection_name,
            ids=list(point_ids),
            with_payload=with_payload,
            with_vectors=with_vectors,
        )

    # -------- Query / Search --------
    def query(
        self,
        collection_name: str,
        vector: Sequence[float],
        limit: int = 10,
        query_filter: Optional[models.Filter] = None,
        with_payload: bool = True,
        with_vectors: bool = False,
    ) -> models.ScoredPoint:
        return self._client.query_points(
            collection_name=collection_name,
            query=list(vector),
            query_filter=query_filter,
            limit=limit,
            with_payload=with_payload,
            with_vectors=with_vectors,
        )

    def recommend(
        self,
        collection_name: str,
        positive: Sequence[int | str],
        negative: Sequence[int | str] | None = None,
        limit: int = 10,
        with_payload: bool = True,
        with_vectors: bool = False,
    ) -> List[models.ScoredPoint]:
        # Using legacy recommend API for simplicity; adjust when upgrading SDK
        negative = list(negative) if negative is not None else []
        return self._client.recommend(
            collection_name=collection_name,
            positive=list(positive),
            negative=negative,
            limit=limit,
            with_payload=with_payload,
            with_vectors=with_vectors,
        )


@lru_cache(maxsize=1)
def get_qdrant_service() -> QdrantService:
    s = get_settings()
    return QdrantService(
        host=s.qdrant_host,
        port=s.qdrant_http_port,
        grpc_port=s.qdrant_grpc_port,
        prefer_grpc=s.qdrant_prefer_grpc,
    )
