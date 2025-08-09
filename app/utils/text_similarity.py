from __future__ import annotations

import re
from typing import Set


_non_alnum = re.compile(r"[^\w]+", re.UNICODE)


def _tokens(s: str) -> Set[str]:
    s = s.lower().strip()
    parts = [p for p in _non_alnum.split(s) if p]
    return set(parts)


def jaccard_token_similarity(a: str, b: str) -> float:
    ta = _tokens(a)
    tb = _tokens(b)
    if not ta or not tb:
        return 0.0
    inter = len(ta & tb)
    union = len(ta | tb)
    return inter / union if union else 0.0
