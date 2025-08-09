from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, File, UploadFile, HTTPException
from pydantic import BaseModel, Field

from app.schemas.common import ApiStandardResponse, create_object_response, DataType
from app.services.ocr import get_ocr_service
from app.utils.isbn import extract_isbn_candidates
from app.services.barcode import decode_isbn_from_image_bytes


router = APIRouter()


class OCRISBNResponse(BaseModel):
    text_samples: List[str] = Field(default_factory=list, description="多种预处理下的 OCR 文本候选（去重后展示部分）")
    isbns: List[str] = Field(default_factory=list, description="识别出的 ISBN（去重、格式化后）")


@router.post(
    "/ocr/isbn",
    response_model=ApiStandardResponse,
    summary="图片 OCR 识别 ISBN",
    description=(
        "上传书籍封面、条形码或相关图片，自动进行多方案图像预处理+OCR，\n"
        "从文本中提取并校验 ISBN-10 / ISBN-13。适配不同角度、尺寸和光照。"
    ),
)
async def ocr_isbn(file: UploadFile = File(..., description="图片文件，如 jpg/png/jpeg")) -> ApiStandardResponse:
    if file.content_type not in {"image/png", "image/jpeg", "image/jpg"}:
        raise HTTPException(status_code=400, detail="仅支持 PNG/JPEG 图片")

    content = await file.read()
    # 1) Try barcode first (fast/robust for many covers)
    barcode_hits = decode_isbn_from_image_bytes(content)

    # 2) OCR fallback（行粒度 + 字串）
    ocr = get_ocr_service()
    variants = ocr.image_bytes_to_texts(content)
    lines = ocr.image_bytes_to_lines(content)

    # Deduplicate and keep short samples
    seen = set()
    samples: List[str] = []
    for _, txt in variants:
        t = (txt or "").strip()
        if not t:
            continue
        key = t.replace("\n", " ")
        if key not in seen:
            seen.add(key)
            samples.append(t)
        if len(samples) >= 5:
            break

    # Extract ISBNs across all variants + lines + barcode hits
    found = list(barcode_hits)
    unique = set()
    for _, txt in variants:
        for t, n in extract_isbn_candidates(txt):
            if n not in unique:
                unique.add(n)
                found.append(n)
    for ln in lines:
        for t, n in extract_isbn_candidates(ln):
            if n not in unique:
                unique.add(n)
                found.append(n)

    if not found:
        raise HTTPException(status_code=422, detail="未能从图片中识别出有效的 ISBN。请尝试更清晰的条形码或封面照片。")
    payload = OCRISBNResponse(text_samples=samples, isbns=found).model_dump()
    return create_object_response(message="OK", data_value=payload, data_type=DataType.OBJECT, code=200)
