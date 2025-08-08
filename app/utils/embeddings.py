from __future__ import annotations

import hashlib
from typing import List


def char_ngram_embedding(text: str, dim: int = 256, n: int = 3) -> List[float]:
    if not text:
        return [0.0] * dim
    vec = [0] * dim
    padded = f" {text} "
    for i in range(len(padded) - n + 1):
        gram = padded[i:i+n]
        h = int(hashlib.md5(gram.encode('utf-8')).hexdigest(), 16)
        idx = h % dim
        vec[idx] += 1
    # L2 normalize
    norm = sum(v*v for v in vec) ** 0.5
    if norm == 0:
        return [0.0] * dim
    return [v / norm for v in vec]
