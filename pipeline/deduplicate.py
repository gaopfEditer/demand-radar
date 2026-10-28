"""Deduplicate and merge keyword records."""

from __future__ import annotations

from typing import Iterable

from pipeline.normalize import normalize_keyword


def deduplicate_keywords(records: Iterable[dict]) -> list[dict]:
    """Keep first occurrence per normalized form; merge sources."""
    seen: dict[str, dict] = {}
    for rec in records:
        key = rec.get("normalized") or normalize_keyword(rec.get("keyword", ""))
        if not key:
            continue
        if key not in seen:
            seen[key] = dict(rec)
            seen[key]["normalized"] = key
            sources = rec.get("source")
            seen[key]["sources"] = (
                [sources] if isinstance(sources, str) else list(sources or [])
            )
        else:
            existing = seen[key]
            src = rec.get("source")
            if src:
                if isinstance(src, str) and src not in existing["sources"]:
                    existing["sources"].append(src)
                elif isinstance(src, list):
                    for s in src:
                        if s not in existing["sources"]:
                            existing["sources"].append(s)
            # Prefer non-null category / intent
            if not existing.get("category") and rec.get("category"):
                existing["category"] = rec["category"]
            if not existing.get("intent") and rec.get("intent"):
                existing["intent"] = rec["intent"]
            # Merge trend hints
            for field in ("trend_score", "is_rising", "is_breakout"):
                if existing.get(field) is None and rec.get(field) is not None:
                    existing[field] = rec[field]
    # Flatten sources back to primary source string for DB
    out = []
    for rec in seen.values():
        sources = rec.pop("sources", [])
        rec["source"] = ",".join(sources) if sources else rec.get("source")
        out.append(rec)
    return out
