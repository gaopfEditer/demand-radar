"""Opportunity scoring engine (rule-based, 0–100).

Weights:
  demand 25% + monetization 20% + competition 20% + feasibility 20% + evidence 15%

Each dimension is rated 1–5 (or None if pending). Missing data → pending / lower confidence,
never pretend low competition.
"""

from __future__ import annotations

from typing import Any, Optional

WEIGHTS = {
    "demand": 0.25,
    "monetization": 0.20,
    "competition": 0.20,
    "feasibility": 0.20,
    "evidence": 0.15,
}


def _clamp_rating(v: Optional[float]) -> Optional[float]:
    if v is None:
        return None
    return max(1.0, min(5.0, float(v)))


def rate_demand(members: list[dict]) -> tuple[Optional[float], list[str]]:
    """Rate demand from trend interest / rising flags. None if no trend data."""
    notes: list[str] = []
    scores = [m.get("trend_score") for m in members if m.get("trend_score") is not None]
    rising = any(m.get("is_rising") for m in members)
    breakout = any(m.get("is_breakout") for m in members)
    suggest_hits = sum(1 for m in members if "autocomplete" in str(m.get("source", "")))

    if not scores and not suggest_hits:
        notes.append("no_trend_or_suggest_data")
        return None, notes

    if scores:
        avg = sum(scores) / len(scores)
        # Map 0-100 interest roughly to 1-5
        if avg >= 70:
            rating = 5.0
        elif avg >= 50:
            rating = 4.0
        elif avg >= 30:
            rating = 3.0
        elif avg >= 15:
            rating = 2.0
        else:
            rating = 1.5
        notes.append(f"avg_interest={avg:.1f}")
    else:
        # Suggest-only: weak demand signal
        rating = 2.0
        notes.append("suggest_only_weak_demand")

    if rising:
        rating = min(5.0, rating + 0.5)
        notes.append("rising_signal")
    if breakout:
        rating = min(5.0, rating + 0.5)
        notes.append("breakout_signal")
    return _clamp_rating(rating), notes


def rate_monetization(members: list[dict]) -> tuple[Optional[float], list[str]]:
    """Commercial / transactional intent → higher monetization potential."""
    notes: list[str] = []
    intents = [m.get("intent") for m in members if m.get("intent")]
    if not intents:
        notes.append("intent_unknown")
        return None, notes
    commercial = sum(1 for i in intents if i == "commercial_investigation")
    transactional = sum(1 for i in intents if i == "transactional")
    total = len(intents)
    ratio = (commercial * 1.0 + transactional * 0.7) / total
    if ratio >= 0.6:
        rating = 4.5
    elif ratio >= 0.35:
        rating = 3.5
    elif ratio >= 0.15:
        rating = 2.5
    else:
        rating = 2.0
    # Modifiers suggesting freemium/API
    blob = " ".join((m.get("normalized") or "") for m in members)
    if "api" in blob or "pricing" in blob or "alternative" in blob:
        rating = min(5.0, rating + 0.5)
        notes.append("commercial_modifier")
    notes.append(f"intent_ratio={ratio:.2f}")
    return _clamp_rating(rating), notes


def rate_competition(members: list[dict]) -> tuple[Optional[float], list[str]]:
    """
    Higher score = easier to enter.
    Without SEO KD / SERP data we MUST return None (pending), not fake low competition.
    """
    notes = ["competition_data_missing_no_kd_or_serp"]
    # If we only have autocomplete long-tails, soft hint but still pending-ish
    long_tails = [m for m in members if len((m.get("normalized") or "").split()) >= 4]
    if long_tails and len(long_tails) >= max(2, len(members) // 3):
        notes.append("many_long_tail_queries_possible_niche")
        # Still mark as tentative mid score with low confidence handled upstream
        return 3.0, notes
    return None, notes


def rate_feasibility(members: list[dict], category: Optional[str]) -> tuple[Optional[float], list[str]]:
    """Heuristic MVP feasibility for solo/small team."""
    notes: list[str] = []
    title_blob = " ".join(
        (m.get("normalized") or m.get("keyword") or "") for m in members
    ).lower()
    # Tool-like utilities tend to be more feasible
    easy_signals = [
        "formatter",
        "converter",
        "generator",
        "tester",
        "checker",
        "compressor",
        "screenshot",
        "regex",
        "json",
        "webhook",
    ]
    hard_signals = [
        "agent",
        "platform",
        "monitoring",
        "automation",
        "portal",
        "enterprise",
    ]
    easy = sum(1 for s in easy_signals if s in title_blob)
    hard = sum(1 for s in hard_signals if s in title_blob)
    if category in ("online_tools", "developer_tools"):
        base = 4.0
    elif category in ("seo_tools", "micro_saas"):
        base = 3.0
    elif category == "ai_development":
        base = 2.5
    else:
        base = 3.0
        notes.append("category_unknown_default_feasibility")
    rating = base + 0.3 * easy - 0.4 * hard
    notes.append(f"easy={easy},hard={hard}")
    return _clamp_rating(rating), notes


def rate_evidence(members: list[dict], evidence_count: int = 0) -> tuple[Optional[float], list[str]]:
    notes: list[str] = []
    sources = set()
    for m in members:
        src = m.get("source") or ""
        for part in str(src).split(","):
            part = part.strip()
            if part:
                sources.add(part)
    n_sources = len(sources) + (1 if evidence_count else 0)
    if n_sources == 0:
        notes.append("no_evidence_sources")
        return None, notes
    if n_sources >= 3:
        rating = 4.5
    elif n_sources == 2:
        rating = 3.5
    else:
        rating = 2.5
    notes.append(f"distinct_sources={n_sources}")
    if any(m.get("is_rising") or m.get("is_breakout") for m in members):
        rating = min(5.0, rating + 0.5)
        notes.append("trend_evidence")
    return _clamp_rating(rating), notes


def score_opportunity(
    opportunity: dict,
    *,
    evidence_count: int = 0,
) -> dict[str, Any]:
    members = opportunity.get("members") or []
    category = opportunity.get("category")

    demand_r, demand_notes = rate_demand(members)
    mon_r, mon_notes = rate_monetization(members)
    comp_r, comp_notes = rate_competition(members)
    feas_r, feas_notes = rate_feasibility(members, category)
    evid_r, evid_notes = rate_evidence(members, evidence_count)

    ratings = {
        "demand": demand_r,
        "monetization": mon_r,
        "competition": comp_r,
        "feasibility": feas_r,
        "evidence": evid_r,
    }
    notes = {
        "demand": demand_notes,
        "monetization": mon_notes,
        "competition": comp_notes,
        "feasibility": feas_notes,
        "evidence": evid_notes,
    }

    present = {k: v for k, v in ratings.items() if v is not None}
    missing = [k for k, v in ratings.items() if v is None]

    if not present:
        total = None
        confidence = "pending"
    else:
        # Renormalize weights over available dimensions
        w_sum = sum(WEIGHTS[k] for k in present)
        total = sum(WEIGHTS[k] * (present[k] / 5.0) for k in present) / w_sum * 100.0
        if missing:
            # Missing data lowers confidence; do not fill with fake lows
            if len(missing) >= 2 or "competition" in missing:
                confidence = "low"
            else:
                confidence = "medium"
        else:
            confidence = "high"
        # Cap score slightly when pending dims
        if missing:
            total = total * (1.0 - 0.05 * len(missing))

    # Map 1-5 ratings to 0-100 component scores for storage/display
    def to_100(r: Optional[float]) -> Optional[float]:
        return None if r is None else round(r / 5.0 * 100.0, 1)

    return {
        "title": opportunity.get("title"),
        "category": category,
        "cluster_id": opportunity.get("cluster_id"),
        "keywords": opportunity.get("keywords"),
        "demand_score": to_100(demand_r),
        "monetization_score": to_100(mon_r),
        "competition_score": to_100(comp_r),
        "feasibility_score": to_100(feas_r),
        "evidence_score": to_100(evid_r),
        "score": round(total, 1) if total is not None else None,
        "confidence": confidence,
        "pending_dimensions": missing,
        "rating_notes": notes,
        "status": "discovered",
    }


def tier_for_score(score: Optional[float]) -> str:
    if score is None:
        return "pending"
    if score >= 80:
        return "priority_research"
    if score >= 65:
        return "candidate"
    if score >= 50:
        return "watch"
    return "deprioritize"
