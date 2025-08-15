from __future__ import annotations

from typing import Optional, Tuple

from qdrant_client import models
import uuid

from app.core.config import get_settings
from app.services.qdrant import get_qdrant_service
from app.utils.embeddings import char_ngram_embedding


class SemanticCache:
    def __init__(self) -> None:
        self.s = get_settings()
        self.enabled = True
        try:
            self.q = get_qdrant_service()
            self.q.ensure_collection(
                self.s.qdrant_cache_collection, self.s.qdrant_cache_vector_dim
            )
        except Exception:
            # Qdrant not available; disable cache gracefully
            self.enabled = False
            self.q = None  # type: ignore[assignment]

    def query(self, text: str) -> Optional[Tuple[float, dict]]:
        if not self.enabled:
            return None
        vec = char_ngram_embedding(text, self.s.qdrant_cache_vector_dim)
        try:
            res = self.q.query(self.s.qdrant_cache_collection, vec, limit=1)
        except Exception:
            return None
        if not res.points:
            return None
        top = res.points[0]
        if top.score is None or top.score < self.s.qdrant_cache_score_threshold:
            return None
        return (top.score, top.payload or {})

    def upsert(self, text: str, payload: dict) -> None:
        if not self.enabled:
            return
        vec = char_ngram_embedding(text, self.s.qdrant_cache_vector_dim)
        point_id = uuid.uuid5(uuid.NAMESPACE_URL, text).int & ((1 << 63) - 1)
        pt = models.PointStruct(id=point_id, vector=vec, payload=payload)
        try:
            self.q.upsert_points(self.s.qdrant_cache_collection, [pt])
        except Exception:
            return


def get_semantic_cache() -> SemanticCache:
    return SemanticCache()
