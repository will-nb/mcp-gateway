from __future__ import annotations

from typing import List

import io
from PIL import Image  # type: ignore

from app.utils.isbn import is_valid_isbn13


def decode_isbn_from_image_bytes(content: bytes) -> List[str]:
    """
    Try to decode barcodes (EAN-13) from image bytes and return valid ISBN-13 strings.
    Uses pyzbar if available; falls back to empty list if not installed.
    """
    try:
        import importlib
        pyzbar = importlib.import_module("pyzbar.pyzbar")  # type: ignore
    except Exception:
        return []

    image = Image.open(io.BytesIO(content))
    results = []
    seen = set()
    for obj in pyzbar.decode(image):  # type: ignore[attr-defined]
        data = obj.data.decode("utf-8", errors="ignore").strip()
        # Many ISBN barcodes are EAN-13 and begin with 978/979
        digits = "".join(ch for ch in data if ch.isdigit())
        if len(digits) == 13 and digits.startswith(("978", "979")) and is_valid_isbn13(digits):
            if digits not in seen:
                seen.add(digits)
                results.append(digits)
    return results
