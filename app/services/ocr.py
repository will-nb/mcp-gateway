from __future__ import annotations

from typing import List, Tuple

import io
from PIL import Image, ImageOps, ImageFilter  # type: ignore


class OCRService:
    """
    Simple OCR service built on Tesseract with robust preprocessing to handle
    variable angles, contrast, sizes and noisy backgrounds.
    """

    def __init__(self, languages: str = "eng+chi_sim") -> None:
        self.languages = languages

    def _preprocess_variants(self, image: Image.Image) -> List[Image.Image]:
        variants: List[Image.Image] = []
        base = image.convert("L")
        variants.append(base)
        # Increase contrast and sharpness
        variants.append(ImageOps.autocontrast(base))
        variants.append(ImageOps.equalize(base))
        # Binarize
        variants.append(base.point(lambda p: 255 if p > 180 else 0).convert("L"))
        # Slight blur then sharpen to remove noise
        variants.append(base.filter(ImageFilter.MedianFilter(size=3)))
        # Try rotations (deskew approximate)
        for angle in (-10, -5, 5, 10):
            variants.append(base.rotate(angle, expand=True, fillcolor=255))
        return variants

    def image_bytes_to_texts(self, content: bytes) -> List[Tuple[str, str]]:
        # Lazy import pytesseract to avoid hard dependency during tests
        try:
            import importlib
            pytesseract = importlib.import_module("pytesseract")  # type: ignore
        except Exception as exc:  # pragma: no cover
            raise RuntimeError("pytesseract is not installed. Please install runtime deps.") from exc

        image = Image.open(io.BytesIO(content))
        texts: List[Tuple[str, str]] = []
        for variant in self._preprocess_variants(image):
            txt = pytesseract.image_to_string(variant, lang=self.languages)
            if txt:
                texts.append(("plain", txt))
            # Also try oem/psm tweaks for strong block text
            txt2 = pytesseract.image_to_string(variant, lang=self.languages, config="--oem 3 --psm 6")
            if txt2 and txt2 != txt:
                texts.append(("psm6", txt2))
        return texts


def get_ocr_service() -> OCRService:
    return OCRService()
