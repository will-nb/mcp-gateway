from __future__ import annotations

from typing import Optional

from pymongo import MongoClient

from app.core.config import get_settings


_client: Optional[MongoClient] = None


def get_mongo_client() -> MongoClient:
    global _client
    if _client is None:
        settings = get_settings()
        _client = MongoClient(settings.mongo_uri, serverSelectionTimeoutMS=2000)
    return _client


def get_database():
    settings = get_settings()
    return get_mongo_client()[settings.mongo_db]
