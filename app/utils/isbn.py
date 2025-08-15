from __future__ import annotations

import re
from typing import List, Tuple, Optional

ISBN10_REGEX = re.compile(
    r"\b(?:ISBN(?:-10)?:?\s*)?([0-9]{1,5}[-\s]?[0-9]+[-\s]?[0-9]+[-\s]?[0-9Xx])\b"
)
ISBN13_REGEX = re.compile(
    r"\b(?:ISBN(?:-13)?:?\s*)?((?:978|979)[-\s]?[0-9]+[-\s]?[0-9]+[-\s]?[0-9]+[-\s]?[0-9])\b"
)


def _clean_isbn(raw: str) -> str:
    return re.sub(r"[^0-9Xx]", "", raw).upper()


def is_valid_isbn10(isbn: str) -> bool:
    s = _clean_isbn(isbn)
    if len(s) != 10:
        return False
    total = 0
    for i, ch in enumerate(s[:9], start=1):
        if not ch.isdigit():
            return False
        total += i * int(ch)
    check = s[9]
    if check == "X":
        total += 10 * 10
    elif check.isdigit():
        total += 10 * int(check)
    else:
        return False
    return total % 11 == 0


def is_valid_isbn13(isbn: str) -> bool:
    s = _clean_isbn(isbn)
    if len(s) != 13 or not s.isdigit():
        return False
    total = 0
    for i, ch in enumerate(s[:12]):
        n = int(ch)
        total += n if i % 2 == 0 else 3 * n
    check = (10 - (total % 10)) % 10
    return check == int(s[12])


_OCR_CONFUSION_MAP = str.maketrans(
    {
        "O": "0",
        "o": "0",
        "I": "1",
        "i": "1",
        "l": "1",
        "L": "1",
        "S": "5",
        "s": "5",
        "B": "8",
        "Z": "2",
        "z": "2",
    }
)


def _correction_variants(s: str) -> List[str]:
    variants = []
    # raw cleaned
    variants.append(s)
    # apply OCR confusion map
    variants.append(s.translate(_OCR_CONFUSION_MAP))
    return list(dict.fromkeys(variants))


def normalize_isbn(raw: str) -> Optional[Tuple[str, str]]:
    s0 = _clean_isbn(raw)
    for s in _correction_variants(s0):
        if is_valid_isbn13(s):
            return ("ISBN-13", s)
        if is_valid_isbn10(s):
            return ("ISBN-10", s)
    return None


def extract_isbn_candidates(text: str) -> List[Tuple[str, str]]:
    """Return list of tuples (type, normalized) for valid ISBNs found."""
    results: List[Tuple[str, str]] = []
    seen = set()
    for m in ISBN13_REGEX.finditer(text):
        norm = normalize_isbn(m.group(1))
        if norm and norm[1] not in seen:
            seen.add(norm[1])
            results.append(norm)
    for m in ISBN10_REGEX.finditer(text):
        norm = normalize_isbn(m.group(1))
        if norm and norm[1] not in seen:
            seen.add(norm[1])
            results.append(norm)
    # Fallback: scan every long digit/hyphen chunk
    for m in re.finditer(r"[0-9Xx][-\s]?[0-9Xx][-\s0-9Xx]{8,16}", text):
        norm = normalize_isbn(m.group(0))
        if norm and norm[1] not in seen:
            seen.add(norm[1])
            results.append(norm)
    return results
