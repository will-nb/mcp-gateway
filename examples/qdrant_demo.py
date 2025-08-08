"""
A step-by-step Qdrant SDK demo using the project's QdrantService.
Run: python examples/qdrant_demo.py
Requires a running Qdrant at the configured host/port.
"""

import uuid
from app.services.qdrant import get_qdrant_service
from qdrant_client import models

DEMO_COLLECTION_NAME = f"demo_collection_{str(uuid.uuid4())[:8]}"
VECTOR_DIMENSION = 4
DISTANCE_METRIC = models.Distance.COSINE


def print_title(title: str) -> None:
    print("\n" + "=" * 60)
    print(f" {title}")
    print("=" * 60)


def print_subtitle(subtitle: str) -> None:
    print(f"\n--- {subtitle} ---")


def run_collection_operations_demo():
    print_title("Collections demo")
    svc = get_qdrant_service()
    client = svc.get_client()

    print_subtitle("1. Create collection if not exists")
    created = svc.ensure_collection(DEMO_COLLECTION_NAME, VECTOR_DIMENSION, DISTANCE_METRIC)
    print("Created:" if created else "Already exists:", DEMO_COLLECTION_NAME)

    print_subtitle("2. Describe collection")
    info = client.get_collection(collection_name=DEMO_COLLECTION_NAME)
    print(" - vectors:", info.config.params.vectors)
    print(" - points_count:", info.points_count)

    print_subtitle("3. List collections")
    cols = client.get_collections().collections
    print(" - total:", len(cols))
    for c in cols[:5]:
        print("   *", c.name)


def run_point_operations_demo():
    print_title("Points demo")
    svc = get_qdrant_service()
    client = svc.get_client()

    print_subtitle("1. Upsert points")
    points = [
        models.PointStruct(id=1, vector=[0.9, 0.1, 0.1, 0.2], payload={"color": "red", "city": "London"}),
        models.PointStruct(id=2, vector=[0.1, 0.9, 0.2, 0.1], payload={"color": "blue", "city": "Paris"}),
        models.PointStruct(id=3, vector=[0.5, 0.5, 0.9, 0.3], payload={"color": "red", "city": "Moscow"}),
        models.PointStruct(id=4, vector=[0.8, 0.2, 0.3, 0.9], payload={"color": "green", "city": "London"}),
        models.PointStruct(id=5, vector=[0.2, 0.8, 0.8, 0.5], payload={"color": "blue", "city": "Berlin"}),
    ]
    svc.upsert_points(DEMO_COLLECTION_NAME, points)

    print_subtitle("2. Retrieve points by id")
    records = svc.retrieve_points(DEMO_COLLECTION_NAME, [1, 2, 99], with_payload=True, with_vectors=True)
    for r in records:
        vec_dim = len(r.vector) if r.vector is not None else 0
        print(f" - id={r.id}, payload={r.payload}, vector_dim={vec_dim}")

    print_subtitle("3. Delete some points")
    svc.delete_points(DEMO_COLLECTION_NAME, [4, 5])
    remaining = client.retrieve(collection_name=DEMO_COLLECTION_NAME, ids=[1, 2, 3])
    print(" - remaining:", [p.id for p in remaining])


def run_search_operations_demo():
    print_title("Search & Recommend demo")
    svc = get_qdrant_service()

    print_subtitle("1. Search")
    result = svc.query(DEMO_COLLECTION_NAME, [0.9, 0.1, 0.1, 0.2], limit=2)
    for i, p in enumerate(result.points):
        print(f" - Top {i+1}: id={p.id}, score={p.score:.4f}")

    print_subtitle("2. Filtered search")
    filtered = svc.query(
        DEMO_COLLECTION_NAME,
        [0.9, 0.1, 0.1, 0.2],
        limit=2,
        query_filter=models.Filter(
            must=[models.FieldCondition(key="color", match=models.MatchValue(value="blue"))]
        ),
    )
    for i, p in enumerate(filtered.points):
        print(f" - Top {i+1}: id={p.id}, score={p.score:.4f}, payload={p.payload}")

    print_subtitle("3. Recommend")
    recs = svc.recommend(DEMO_COLLECTION_NAME, positive=[1], negative=[], limit=2)
    for i, p in enumerate(recs):
        print(f" - Top {i+1}: id={p.id}, score={p.score:.4f}")


def cleanup():
    print_title("Cleanup")
    svc = get_qdrant_service()
    print("Deleting collection:", DEMO_COLLECTION_NAME)
    svc.get_client().delete_collection(collection_name=DEMO_COLLECTION_NAME)


if __name__ == "__main__":
    svc = get_qdrant_service()
    if svc.get_client():
        created = svc.ensure_collection(DEMO_COLLECTION_NAME, VECTOR_DIMENSION, DISTANCE_METRIC)
        run_collection_operations_demo()
        run_point_operations_demo()
        run_search_operations_demo()
        cleanup()
    print("\n" + "=" * 60)
    print("Qdrant demo finished")
    print("=" * 60)
