import io
from fastapi.testclient import TestClient
from PIL import Image

from app.main import app


def create_dummy_image() -> bytes:
    # Create a small white PNG
    img = Image.new("RGB", (64, 64), color=(255, 255, 255))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def test_ocr_isbn_bad_type():
    client = TestClient(app)
    # Upload a text file as wrong content type
    files = {"file": ("x.txt", b"hello", "text/plain")}
    r = client.post("/api/v1/ocr/isbn", files=files)
    assert r.status_code == 400


def test_ocr_isbn_ok_path(monkeypatch):
    client = TestClient(app)

    # Force OCR/barcode to deterministic outputs
    monkeypatch.setattr(
        "app.api.v1.endpoints.ocr.decode_isbn_from_image_bytes",
        lambda b: ["9780134685991"],
    )

    class FakeOCR:
        def image_bytes_to_texts(self, content: bytes):
            return [("plain", "ISBN 9780134685991")]

        def image_bytes_to_lines(self, content: bytes):
            return ["Effective Java ISBN 9780134685991"]

    monkeypatch.setattr("app.api.v1.endpoints.ocr.get_ocr_service", lambda: FakeOCR())

    img_bytes = create_dummy_image()
    files = {"file": ("img.png", img_bytes, "image/png")}
    r = client.post("/api/v1/ocr/isbn", files=files)
    assert r.status_code == 200
    body = r.json()
    assert body["success"] is True
    assert body["dataType"] == "object"
    assert "isbns" in body["data"] and body["data"]["isbns"][0] == "9780134685991"
