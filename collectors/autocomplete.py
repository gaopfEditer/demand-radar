"""Google Autocomplete / Suggest collector with rate limiting."""

from __future__ import annotations

import logging
import time
import urllib.parse
from dataclasses import dataclass, field
from typing import Optional

import requests

logger = logging.getLogger(__name__)

SUGGEST_URL = "https://suggestqueries.google.com/complete/search"


@dataclass
class SuggestResult:
    seed: str
    query: str
    suggestions: list[str] = field(default_factory=list)
    error: Optional[str] = None


class AutocompleteCollector:
    """Collect Google suggest expansions for seed keywords."""

    DEFAULT_MODIFIERS = [
        "free",
        "online",
        "for developers",
        "alternative",
        "API",
        "without signup",
    ]

    def __init__(
        self,
        *,
        delay_seconds: float = 0.4,
        max_per_seed: int = 50,
        language: str = "en",
        timeout: float = 10.0,
    ):
        self.delay = delay_seconds
        self.max_per_seed = max_per_seed
        self.language = language
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": (
                    "Mozilla/5.0 (compatible; DemandRadar/0.1; +local-research)"
                )
            }
        )
        self.errors: list[str] = []

    def suggest(self, query: str) -> SuggestResult:
        params = {
            "client": "firefox",
            "q": query,
            "hl": self.language,
        }
        url = f"{SUGGEST_URL}?{urllib.parse.urlencode(params)}"
        try:
            resp = self.session.get(url, timeout=self.timeout)
            resp.raise_for_status()
            data = resp.json()
            suggestions = []
            if isinstance(data, list) and len(data) >= 2 and isinstance(data[1], list):
                suggestions = [str(s) for s in data[1]]
            return SuggestResult(seed=query, query=query, suggestions=suggestions)
        except Exception as exc:  # noqa: BLE001
            logger.warning("suggest failed for %r: %s", query, exc)
            self.errors.append(f"{query}: {exc}")
            return SuggestResult(seed=query, query=query, error=str(exc))

    def expand_seed(
        self,
        seed: str,
        modifiers: Optional[list[str]] = None,
    ) -> list[SuggestResult]:
        modifiers = modifiers or self.DEFAULT_MODIFIERS
        queries = [seed] + [f"{seed} {m}" for m in modifiers]
        results: list[SuggestResult] = []
        seen: set[str] = set()
        for q in queries:
            if len(seen) >= self.max_per_seed:
                break
            result = self.suggest(q)
            results.append(result)
            for s in result.suggestions:
                seen.add(s.lower().strip())
            time.sleep(self.delay)
        return results

    def collect(
        self,
        seeds: list[str],
        modifiers: Optional[list[str]] = None,
    ) -> tuple[list[SuggestResult], list[str]]:
        """Return (results, unique_candidate_keywords)."""
        all_results: list[SuggestResult] = []
        candidates: list[str] = []
        seen: set[str] = set()
        for seed in seeds:
            seed_results = self.expand_seed(seed, modifiers)
            all_results.extend(seed_results)
            seed_seen: set[str] = set()
            # Always include the seed itself
            key = seed.lower().strip()
            if key not in seen:
                seen.add(key)
                candidates.append(seed.strip())
            for r in seed_results:
                for s in r.suggestions:
                    norm = s.lower().strip()
                    if not norm or norm in seed_seen:
                        continue
                    if len(seed_seen) >= self.max_per_seed:
                        break
                    seed_seen.add(norm)
                    if norm not in seen:
                        seen.add(norm)
                        candidates.append(s.strip())
        return all_results, candidates
