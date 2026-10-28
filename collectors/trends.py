"""Google Trends collector with pluggable adapters and graceful degradation."""

from __future__ import annotations

import logging
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Optional

logger = logging.getLogger(__name__)


@dataclass
class TrendPoint:
    keyword: str
    timeframe: str
    market: str
    interest: Optional[float] = None  # 0-100 relative interest
    related_queries: list[dict] = field(default_factory=list)
    rising_queries: list[dict] = field(default_factory=list)
    is_rising: bool = False
    is_breakout: bool = False
    error: Optional[str] = None
    raw: dict = field(default_factory=dict)
    adapter: Optional[str] = None


class TrendsAdapter(ABC):
    """Abstract adapter so we can swap trendspyg / pytrends / mock."""

    name: str = "base"

    @abstractmethod
    def fetch(self, keyword: str, timeframe: str, geo: str) -> TrendPoint:
        raise NotImplementedError


class TrendspygAdapter(TrendsAdapter):
    """Prefer trendspyg when available (official preferred adapter)."""

    name = "trendspyg"

    def __init__(self, *, use_browser: bool = False):
        self._available = False
        self._module = None
        self._use_browser = use_browser
        try:
            import trendspyg  # type: ignore

            self._module = trendspyg
            self._available = hasattr(
                trendspyg, "download_google_trends_interest_over_time"
            ) or hasattr(trendspyg, "download_google_trends_explore")
        except Exception as exc:  # noqa: BLE001
            logger.info("trendspyg not available: %s", exc)

    @property
    def available(self) -> bool:
        return self._available

    def fetch(self, keyword: str, timeframe: str, geo: str) -> TrendPoint:
        if not self._available:
            return TrendPoint(
                keyword=keyword,
                timeframe=timeframe,
                market=geo or "Global",
                error="trendspyg_unavailable",
                adapter=self.name,
            )
        try:
            mod = self._module
            geo_code = "US" if not geo or geo == "Global" else geo
            tf = _map_timeframe(timeframe)
            interest = None
            related: list[dict] = []
            rising: list[dict] = []
            raw: dict[str, Any] = {"adapter": self.name}
            is_rising = False
            is_breakout = False

            # Prefer lightweight interest-over-time; explore is heavier (browser).
            engine = "browser" if self._use_browser else "browser"
            # trendspyg 1.9 explore/iot are browser-based; catch failures quickly
            if hasattr(mod, "download_google_trends_interest_over_time"):
                try:
                    data = mod.download_google_trends_interest_over_time(
                        keyword=keyword,
                        geo=geo_code,
                        timeframe=tf,
                        headless=True,
                        output_format="dict",
                        max_retries=2,
                        retry_wait=3.0,
                        engine=engine,
                    )
                    raw["iot"] = _safe_serialize(data)
                    interest = _extract_interest(data, keyword)
                except Exception as iot_exc:  # noqa: BLE001
                    raw["iot_error"] = str(iot_exc)
                    logger.warning("trendspyg iot failed for %s: %s", keyword, iot_exc)

            if interest is None and hasattr(mod, "download_google_trends_explore"):
                try:
                    data = mod.download_google_trends_explore(
                        keyword=keyword,
                        geo=geo_code,
                        timeframe=tf,
                        headless=True,
                        include_related=True,
                        max_retries=2,
                        retry_wait=3.0,
                        engine=engine,
                    )
                    raw["explore"] = _safe_serialize(data)
                    interest = _extract_interest_from_explore(data)
                    related, rising, is_rising, is_breakout = _extract_related(data)
                except Exception as ex_exc:  # noqa: BLE001
                    raw["explore_error"] = str(ex_exc)
                    logger.warning("trendspyg explore failed for %s: %s", keyword, ex_exc)

            if interest is None and "iot_error" in raw and "explore_error" in raw:
                return TrendPoint(
                    keyword=keyword,
                    timeframe=timeframe,
                    market=geo or "Global",
                    error="trendspyg_fetch_failed",
                    raw=raw,
                    adapter=self.name,
                )
            if interest is None and not related and not rising:
                # Partial failure
                err = raw.get("iot_error") or raw.get("explore_error") or "trendspyg_no_data"
                return TrendPoint(
                    keyword=keyword,
                    timeframe=timeframe,
                    market=geo or "Global",
                    error=str(err),
                    raw=raw,
                    adapter=self.name,
                )

            return TrendPoint(
                keyword=keyword,
                timeframe=timeframe,
                market=geo or "Global",
                interest=interest,
                related_queries=related,
                rising_queries=rising,
                is_rising=is_rising,
                is_breakout=is_breakout,
                raw=raw,
                adapter=self.name,
            )
        except Exception as exc:  # noqa: BLE001
            logger.warning("trendspyg fetch failed for %s: %s", keyword, exc)
            return TrendPoint(
                keyword=keyword,
                timeframe=timeframe,
                market=geo or "Global",
                error=f"trendspyg_error:{exc}",
                adapter=self.name,
            )


class PytrendsAdapter(TrendsAdapter):
    """Fallback using pytrends if installed."""

    name = "pytrends"

    def __init__(self):
        self._TrendReq = None
        try:
            from pytrends.request import TrendReq

            self._TrendReq = TrendReq
        except Exception as exc:  # noqa: BLE001
            logger.info("pytrends not available: %s", exc)

    @property
    def available(self) -> bool:
        return self._TrendReq is not None

    def fetch(self, keyword: str, timeframe: str, geo: str) -> TrendPoint:
        if not self.available:
            return TrendPoint(
                keyword=keyword,
                timeframe=timeframe,
                market=geo or "Global",
                error="pytrends_unavailable",
                adapter=self.name,
            )
        try:
            pytrends = self._TrendReq(hl="en-US", tz=0)
            geo_code = "" if not geo or geo == "Global" else geo
            tf = _map_timeframe(timeframe)
            pytrends.build_payload([keyword], timeframe=tf, geo=geo_code)
            iot = pytrends.interest_over_time()
            interest = None
            raw: dict[str, Any] = {"adapter": self.name}
            is_rising = False
            if iot is not None and not iot.empty and keyword in iot.columns:
                interest = float(iot[keyword].mean())
                raw["iot_tail"] = iot[keyword].tail(5).tolist()
                if len(iot) >= 4:
                    half = len(iot) // 2
                    older = float(iot[keyword].iloc[:half].mean())
                    recent = float(iot[keyword].iloc[half:].mean())
                    is_rising = recent > older * 1.15

            rising: list[dict] = []
            related: list[dict] = []
            is_breakout = False
            try:
                rq = pytrends.related_queries()
                raw["related_keys"] = list(rq.keys()) if rq else []
                if keyword in (rq or {}):
                    top = rq[keyword].get("top")
                    rise = rq[keyword].get("rising")
                    if top is not None and not top.empty:
                        related = top.head(10).to_dict(orient="records")
                    if rise is not None and not rise.empty:
                        rising = rise.head(10).to_dict(orient="records")
                        is_rising = True
                        for row in rising:
                            val = str(row.get("value", ""))
                            if "breakout" in val.lower():
                                is_breakout = True
            except Exception as rel_exc:  # noqa: BLE001
                raw["related_error"] = str(rel_exc)

            if interest is None and not related and not rising:
                return TrendPoint(
                    keyword=keyword,
                    timeframe=timeframe,
                    market=geo or "Global",
                    error="pytrends_empty",
                    raw=raw,
                    adapter=self.name,
                )

            return TrendPoint(
                keyword=keyword,
                timeframe=timeframe,
                market=geo or "Global",
                interest=interest,
                related_queries=related,
                rising_queries=rising,
                is_rising=is_rising,
                is_breakout=is_breakout,
                raw=raw,
                adapter=self.name,
            )
        except Exception as exc:  # noqa: BLE001
            logger.warning("pytrends fetch failed for %s: %s", keyword, exc)
            return TrendPoint(
                keyword=keyword,
                timeframe=timeframe,
                market=geo or "Global",
                error=f"pytrends_error:{exc}",
                adapter=self.name,
            )


class MockTrendsAdapter(TrendsAdapter):
    """Deterministic mock for offline / rate-limit demos."""

    name = "mock"

    def fetch(self, keyword: str, timeframe: str, geo: str) -> TrendPoint:
        seed = sum(ord(c) for c in keyword) % 80 + 10
        rising = seed > 50
        return TrendPoint(
            keyword=keyword,
            timeframe=timeframe,
            market=geo or "Global",
            interest=float(seed),
            related_queries=[{"query": f"{keyword} online", "value": 100}],
            rising_queries=(
                [{"query": f"{keyword} free", "value": "Breakout"}] if rising else []
            ),
            is_rising=rising,
            is_breakout=rising and seed > 70,
            raw={"mock": True, "adapter": self.name},
            adapter=self.name,
        )


class TrendsCollector:
    """Orchestrates adapters with rate limiting and graceful fallback.

    Order: trendspyg → pytrends → mock (if allowed).
    """

    def __init__(
        self,
        *,
        delay_seconds: float = 1.5,
        force_mock: bool = False,
        prefer_pytrends: bool = False,
        trendspyg_browser: bool = False,
    ):
        self.delay = delay_seconds
        self.errors: list[str] = []
        self.adapters: list[TrendsAdapter] = []
        if force_mock:
            self.adapters = [MockTrendsAdapter()]
        elif prefer_pytrends:
            self.adapters = [
                PytrendsAdapter(),
                TrendspygAdapter(use_browser=trendspyg_browser),
                MockTrendsAdapter(),
            ]
        else:
            self.adapters = [
                TrendspygAdapter(use_browser=trendspyg_browser),
                PytrendsAdapter(),
                MockTrendsAdapter(),
            ]

    def collect(
        self,
        keywords: list[str],
        *,
        timeframe: str = "today 3-m",
        markets: Optional[list[str]] = None,
        allow_mock_fallback: bool = True,
    ) -> list[TrendPoint]:
        markets = markets or ["US"]
        results: list[TrendPoint] = []
        for kw in keywords:
            for market in markets:
                point = self._fetch_one(kw, timeframe, market, allow_mock_fallback)
                results.append(point)
                time.sleep(self.delay)
        return results

    def _fetch_one(
        self,
        keyword: str,
        timeframe: str,
        market: str,
        allow_mock_fallback: bool,
    ) -> TrendPoint:
        geo = "" if market == "Global" else market
        last_error = None
        for adapter in self.adapters:
            if isinstance(adapter, MockTrendsAdapter) and not allow_mock_fallback:
                continue
            if hasattr(adapter, "available") and not adapter.available:
                continue
            # Skip trendspyg by default in fast daily path if previous runs
            # showed browser failures — still try once; failures fall through.
            point = adapter.fetch(keyword, timeframe, geo or market)
            if point.error is None and (
                point.interest is not None or point.related_queries or point.rising_queries
            ):
                if isinstance(adapter, MockTrendsAdapter):
                    point.raw = {**(point.raw or {}), "degraded": "mock_fallback"}
                return point
            last_error = point.error
            self.errors.append(f"{keyword}/{market}/{adapter.name}: {point.error}")
        if allow_mock_fallback:
            mock = MockTrendsAdapter().fetch(keyword, timeframe, market)
            mock.error = None
            mock.raw = {
                **(mock.raw or {}),
                "degraded": "mock_after_failures",
                "last_error": last_error,
            }
            return mock
        return TrendPoint(
            keyword=keyword,
            timeframe=timeframe,
            market=market,
            error=last_error or "all_adapters_failed",
        )


def _map_timeframe(tf: str) -> str:
    mapping = {
        "7d": "now 7-d",
        "7_days": "now 7-d",
        "3m": "today 3-m",
        "3_months": "today 3-m",
        "12m": "today 12-m",
        "12_months": "today 12-m",
        "5y": "today 5-y",
        "today 3-m": "today 3-m",
        "today 12-m": "today 12-m",
        "now 7-d": "now 7-d",
    }
    return mapping.get(tf, tf)


def _extract_interest(data: Any, keyword: str) -> Optional[float]:
    try:
        import pandas as pd

        if isinstance(data, pd.DataFrame):
            if keyword in data.columns:
                return float(data[keyword].mean())
            numeric = data.select_dtypes(include="number")
            if not numeric.empty:
                return float(numeric.iloc[:, 0].mean())
        if isinstance(data, list) and data:
            vals = []
            for row in data:
                if isinstance(row, dict):
                    for k in ("value", "interest", keyword, "score"):
                        if k in row and isinstance(row[k], (int, float)):
                            vals.append(float(row[k]))
                            break
            if vals:
                return sum(vals) / len(vals)
        if isinstance(data, dict):
            if keyword in data:
                vals = data[keyword]
                if isinstance(vals, (list, tuple)) and vals:
                    nums = [float(x) for x in vals if isinstance(x, (int, float))]
                    if nums:
                        return sum(nums) / len(nums)
                if isinstance(vals, (int, float)):
                    return float(vals)
            for key in ("interest", "average", "mean", "timeline_data", "interest_over_time"):
                if key in data:
                    return _extract_interest(data[key], keyword)
    except Exception:  # noqa: BLE001
        return None
    return None


def _extract_interest_from_explore(data: Any) -> Optional[float]:
    if not isinstance(data, dict):
        return _extract_interest(data, "")
    for key in ("interest_over_time", "timeseries", "interest", "data"):
        if key in data:
            val = _extract_interest(data[key], "")
            if val is not None:
                return val
    return None


def _extract_related(data: Any) -> tuple[list[dict], list[dict], bool, bool]:
    related: list[dict] = []
    rising: list[dict] = []
    is_rising = False
    is_breakout = False
    if not isinstance(data, dict):
        return related, rising, is_rising, is_breakout
    rq = data.get("related_queries") or data.get("related") or {}
    if isinstance(rq, dict):
        top = rq.get("top") or []
        rise = rq.get("rising") or []
        if isinstance(top, list):
            related = top[:10]
        if isinstance(rise, list):
            rising = rise[:10]
            is_rising = bool(rising)
            for row in rising:
                if isinstance(row, dict) and "breakout" in str(row.get("value", "")).lower():
                    is_breakout = True
    return related, rising, is_rising, is_breakout


def _safe_serialize(data: Any) -> Any:
    try:
        import pandas as pd

        if isinstance(data, pd.DataFrame):
            return {"columns": list(data.columns), "rows": len(data)}
    except Exception:  # noqa: BLE001
        pass
    if isinstance(data, (dict, list, str, int, float, bool)) or data is None:
        # Truncate huge dicts
        if isinstance(data, dict) and len(str(data)) > 5000:
            return {k: _safe_serialize(v) for k, v in list(data.items())[:20]}
        if isinstance(data, list) and len(data) > 50:
            return data[:50]
        return data
    return str(type(data))
