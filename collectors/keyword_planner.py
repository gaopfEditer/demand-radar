"""Stub for Google Keyword Planner / Ads API (not implemented in MVP)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class KeywordMetrics:
    keyword: str
    monthly_volume: Optional[int] = None
    competition: Optional[str] = None
    cpc_low: Optional[float] = None
    cpc_high: Optional[float] = None
    error: Optional[str] = "not_implemented"


class KeywordPlannerCollector:
    """Placeholder — requires Google Ads API credentials."""

    def collect(self, keywords: list[str]) -> list[KeywordMetrics]:
        return [KeywordMetrics(keyword=k) for k in keywords]
