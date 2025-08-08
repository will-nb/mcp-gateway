"""
Minimal smoke test for Qdrant connectivity.
Run: python examples/qdrant_smoke_test.py
"""

from qdrant_client import QdrantClient
from qdrant_client.http.models import VectorParams, Distance, PointStruct


def main() -> None:
    client = QdrantClient(host="localhost", port=6333)
    collection_name = "test_collection"

    # connection
    client.get_collections()

    # create if not exists
    if not client.collection_exists(collection_name):
        client.create_collection(collection_name=collection_name, vectors_config=VectorParams(size=4, distance=Distance.COSINE))

    # upsert one point
    client.upsert(collection_name=collection_name, points=[PointStruct(id=1, vector=[0.1, 0.2, 0.3, 0.4], payload={"tag": "test"})])

    # query
    hits = client.query_points(collection_name=collection_name, query=[0.1, 0.2, 0.3, 0.4], limit=1, with_payload=True)
    for p in hits.points:
        print("Hit:", p.id, p.score, p.payload)


if __name__ == "__main__":
    main()
