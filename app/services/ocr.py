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
        # Upscale to help small text
        try:
            w, h = base.size
            variants.append(base.resize((int(w * 1.5), int(h * 1.5))))
            variants.append(base.resize((w * 2, h * 2)))
        except Exception:
            pass
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
            raise RuntimeError(
                "pytesseract is not installed. Please install runtime deps."
            ) from exc

        image = Image.open(io.BytesIO(content))
        texts: List[Tuple[str, str]] = []
        for variant in self._preprocess_variants(image):
            txt = pytesseract.image_to_string(variant, lang=self.languages)
            if txt:
                texts.append(("plain", txt))
            # Also try oem/psm tweaks for strong block text
            txt2 = pytesseract.image_to_string(
                variant, lang=self.languages, config="--oem 3 --psm 6"
            )
            if txt2 and txt2 != txt:
                texts.append(("psm6", txt2))
        return texts

    def image_bytes_to_lines(self, content: bytes) -> List[str]:
        """
        Use tesseract TSV output to assemble line-wise texts across preprocessing variants.
        Group by line number to maintain local context (help locating 'ISBN' followed by digits).
        """
        try:
            import importlib

            pytesseract = importlib.import_module("pytesseract")  # type: ignore
        except Exception as exc:  # pragma: no cover
            raise RuntimeError(
                "pytesseract is not installed. Please install runtime deps."
            ) from exc

        image = Image.open(io.BytesIO(content))
        lines: List[str] = []
        for variant in self._preprocess_variants(image):
            try:
                tsv = pytesseract.image_to_data(
                    variant,
                    lang=self.languages,
                    config="--oem 3 --psm 6",
                    output_type=getattr(pytesseract, "Output").STRING,  # type: ignore
                )
            except Exception:
                # Fallback to plain string if tsv not supported
                txt = pytesseract.image_to_string(variant, lang=self.languages)
                if txt:
                    lines.extend(
                        [line.strip() for line in txt.splitlines() if line.strip()]
                    )
                continue

            # Parse TSV manually (header present)
            try:
                rows = [r for r in tsv.splitlines() if r.strip()]
                if not rows:
                    continue
                header = rows[0].split("\t")
                idx_word = header.index("text") if "text" in header else -1
                idx_conf = header.index("conf") if "conf" in header else -1
                idx_line = header.index("line_num") if "line_num" in header else -1
                if idx_word == -1 or idx_line == -1:
                    continue
                from collections import defaultdict

                groups = defaultdict(list)
                for row in rows[1:]:
                    cols = row.split("\t")
                    if len(cols) <= max(
                        idx_word, idx_line, idx_conf if idx_conf != -1 else 0
                    ):
                        continue
                    word = cols[idx_word].strip()
                    if not word:
                        continue
                    conf_ok = True
                    if idx_conf != -1:
                        try:
                            conf_ok = (
                                float(cols[idx_conf]) >= 0
                            )  # accept all OCR words; adjust if needed
                        except Exception:
                            conf_ok = True
                    if not conf_ok:
                        continue
                    line_no = cols[idx_line]
                    groups[line_no].append(word)
                for ln in sorted(
                    groups.keys(), key=lambda x: int(x) if x.isdigit() else 0
                ):
                    line_text = " ".join(groups[ln]).strip()
                    if line_text:
                        lines.append(line_text)
            except Exception:
                # ignore parsing errors for this variant
                continue
        # Deduplicate lines preserving order
        seen = set()
        uniq: List[str] = []
        for line in lines:
            if line not in seen:
                seen.add(line)
                uniq.append(line)
        return uniq


def get_ocr_service() -> OCRService:
    return OCRService()
