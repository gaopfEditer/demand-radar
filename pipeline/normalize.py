"""Keyword normalization utilities."""

from __future__ import annotations

import re
import unicodedata
from typing import Optional

# Common intent signals
COMMERCIAL_PATTERNS = [
    r"\bbest\b",
    r"\balternative\b",
    r"\bvs\b",
    r"\bpricing\b",
    r"\bprice\b",
    r"\bbuy\b",
    r"\bpaid\b",
    r"\bpremium\b",
    r"\bsubscription\b",
]
TRANSACTIONAL_PATTERNS = [
    r"\bfree\b",
    r"\bonline\b",
    r"\bdownload\b",
    r"\bgenerator\b",
    r"\bconverter\b",
    r"\btool\b",
    r"\bapi\b",
]
INFORMATIONAL_PATTERNS = [
    r"\bhow to\b",
    r"\bwhat is\b",
    r"\btutorial\b",
    r"\bguide\b",
    r"\bexample\b",
]


def normalize_keyword(text: str) -> str:
    """Lowercase, strip, collapse whitespace, remove surrounding punctuation."""
    if not text:
        return ""
    text = unicodedata.normalize("NFKC", text)
    text = text.lower().strip()
    text = re.sub(r"\s+", " ", text)
    text = text.strip(".,;:!?\"'`")
    return text


def detect_intent(keyword: str) -> str:
    """Heuristic search-intent classification."""
    k = normalize_keyword(keyword)
    for pat in COMMERCIAL_PATTERNS:
        if re.search(pat, k):
            return "commercial_investigation"
    for pat in TRANSACTIONAL_PATTERNS:
        if re.search(pat, k):
            return "transactional"
    for pat in INFORMATIONAL_PATTERNS:
        if re.search(pat, k):
            return "informational"
    # Brand-like single tokens → navigational guess is weak; keep informational default
    if " " not in k and len(k) < 20:
        return "navigational"
    return "informational"


def normalize_record(
    keyword: str,
    *,
    category: Optional[str] = None,
    source: Optional[str] = None,
    extra: Optional[dict] = None,
) -> dict:
    norm = normalize_keyword(keyword)
    rec = {
        "keyword": keyword.strip(),
        "normalized": norm,
        "intent": detect_intent(keyword),
        "category": category,
        "source": source,
    }
    if extra:
        rec.update(extra)
    return rec
