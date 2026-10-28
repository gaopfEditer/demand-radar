"""Simple keyword clustering by shared tokens / category."""

from __future__ import annotations

import hashlib
import re
from collections import defaultdict
from typing import Optional

STOPWORDS = {
    "a",
    "an",
    "the",
    "for",
    "to",
    "of",
    "and",
    "or",
    "in",
    "on",
    "with",
    "without",
    "free",
    "online",
    "best",
    "tool",
    "tools",
    "api",
    "app",
}


def _tokens(text: str) -> set[str]:
    parts = re.findall(r"[a-z0-9]+", (text or "").lower())
    return {p for p in parts if p not in STOPWORDS and len(p) > 1}


def _cluster_id(label: str) -> str:
    h = hashlib.sha1(label.encode("utf-8")).hexdigest()[:10]
    return f"c_{h}"


def cluster_keywords(records: list[dict]) -> list[dict]:
    """
    Assign cluster_id using:
    1) same category + shared significant stem token, else
    2) highest-overlap token group, else
    3) singleton cluster.
    """
    # Group by category first
    by_cat: dict[Optional[str], list[dict]] = defaultdict(list)
    for r in records:
        by_cat[r.get("category")].append(r)

    clustered: list[dict] = []
    for category, items in by_cat.items():
        # Build inverted index of token -> indices
        token_map: dict[str, list[int]] = defaultdict(list)
        item_tokens: list[set[str]] = []
        for i, rec in enumerate(items):
            toks = _tokens(rec.get("normalized") or rec.get("keyword", ""))
            item_tokens.append(toks)
            for t in toks:
                token_map[t].append(i)

        assigned = [-1] * len(items)
        cluster_labels: dict[int, str] = {}
        next_id = 0

        # Prefer tokens that appear 2+ times
        frequent = sorted(
            ((t, idxs) for t, idxs in token_map.items() if len(idxs) >= 2),
            key=lambda x: -len(x[1]),
        )
        for token, idxs in frequent:
            members = [i for i in idxs if assigned[i] < 0]
            if len(members) < 2:
                continue
            cid = next_id
            next_id += 1
            label = f"{category or 'misc'}:{token}"
            cluster_labels[cid] = label
            for i in members:
                assigned[i] = cid

        for i, rec in enumerate(items):
            out = dict(rec)
            if assigned[i] >= 0:
                label = cluster_labels[assigned[i]]
                out["cluster_id"] = _cluster_id(label)
                out["cluster_label"] = label
            else:
                kw = rec.get("normalized") or rec.get("keyword") or f"row{i}"
                label = f"{category or 'misc'}:solo:{kw}"
                out["cluster_id"] = _cluster_id(label)
                out["cluster_label"] = label
            clustered.append(out)
    return clustered


def opportunities_from_clusters(records: list[dict]) -> list[dict]:
    """Collapse keyword clusters into opportunity candidates."""
    groups: dict[str, list[dict]] = defaultdict(list)
    for r in records:
        cid = r.get("cluster_id") or _cluster_id(r.get("normalized", "x"))
        groups[cid].append(r)

    opportunities = []
    for cid, members in groups.items():
        # Title = shortest / seed-like keyword
        members_sorted = sorted(members, key=lambda m: len(m.get("keyword", "")))
        title = members_sorted[0].get("keyword")
        category = next((m.get("category") for m in members if m.get("category")), None)
        label = members[0].get("cluster_label")
        opportunities.append(
            {
                "cluster_id": cid,
                "cluster_label": label,
                "title": title,
                "category": category,
                "keywords": [m.get("keyword") for m in members],
                "members": members,
            }
        )
    return opportunities
