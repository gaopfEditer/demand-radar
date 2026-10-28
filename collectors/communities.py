"""Stub interface for Reddit / HN / Product Hunt collectors (not implemented in MVP)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class CommunitySignal:
    source: str
    title: str
    url: Optional[str]
    snippet: Optional[str]
    score: Optional[float] = None


class CommunitiesCollector:
    """Placeholder — stage-4 feature. Returns empty list."""

    def collect(self, keywords: list[str]) -> list[CommunitySignal]:
        return []
