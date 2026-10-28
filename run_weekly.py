#!/usr/bin/env python3
"""Weekly pipeline: multi-window Trends + re-score + optional deep research.

Usage:
  python run_weekly.py
  python run_weekly.py --limit-seeds 5 --force-mock-trends
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from collectors.trends import TrendsCollector
from pipeline.cluster import cluster_keywords, opportunities_from_clusters
from pipeline.deduplicate import deduplicate_keywords
from pipeline.normalize import normalize_record
from pipeline.score import score_opportunity
from storage.repository import Repository

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("run_weekly")

WINDOWS = [
    ("now 7-d", "7d"),
    ("today 3-m", "3m"),
    ("today 12-m", "12m"),
]


def main() -> int:
    parser = argparse.ArgumentParser(description="Demand Radar weekly pipeline")
    parser.add_argument("--db", default=str(ROOT / "data" / "demand_radar.db"))
    parser.add_argument("--seeds", default=str(ROOT / "config" / "seeds.yaml"))
    parser.add_argument("--limit-seeds", type=int, default=0)
    parser.add_argument("--force-mock-trends", action="store_true")
    parser.add_argument("--market", default="US")
    parser.add_argument("--deep-top", type=int, default=3, help="Deep research top N")
    parser.add_argument("--skip-ai", action="store_true")
    parser.add_argument("--trends-delay", type=float, default=1.5)
    args = parser.parse_args()

    cfg = yaml.safe_load(Path(args.seeds).read_text(encoding="utf-8"))
    categories = cfg.get("categories") or {}
    seed_list = []
    for cat, words in categories.items():
        for w in words:
            seed_list.append({"keyword": w, "category": cat})
    if args.limit_seeds:
        seed_list = seed_list[: args.limit_seeds]

    repo = Repository(args.db)
    run_id = repo.start_run("weekly")
    errors: list[str] = []

    try:
        tc = TrendsCollector(
            delay_seconds=args.trends_delay,
            force_mock=args.force_mock_trends,
            prefer_pytrends=True,
        )
        raw_records: list[dict] = []
        seed_cat = {s["keyword"].lower(): s["category"] for s in seed_list}

        for timeframe, label in WINDOWS:
            kws = [s["keyword"] for s in seed_list]
            points = tc.collect(
                kws,
                timeframe=timeframe,
                markets=[args.market],
                allow_mock_fallback=True,
            )
            errors.extend(tc.errors)
            for p in points:
                if p.error:
                    errors.append(p.error)
                    continue
                rec = normalize_record(
                    p.keyword,
                    category=seed_cat.get(p.keyword.lower()),
                    source=f"trends_{label}",
                    extra={
                        "trend_score": p.interest,
                        "is_rising": p.is_rising,
                        "is_breakout": p.is_breakout,
                        "timeframe": p.timeframe,
                    },
                )
                raw_records.append(rec)
                kid = repo.upsert_keyword(
                    p.keyword,
                    rec["normalized"],
                    intent=rec["intent"],
                    category=rec.get("category"),
                    source=rec["source"],
                )
                repo.append_snapshot(
                    kid,
                    "google_trends",
                    timeframe=p.timeframe,
                    market=p.market,
                    trend_score=p.interest,
                    is_rising=p.is_rising,
                    is_breakout=p.is_breakout,
                    raw={"window": label, "meta": p.raw},
                )
            logger.info("Window %s done (%d points)", label, len(points))

        # Merge with existing keywords from DB for clustering context
        for kw in repo.list_keywords(limit=2000):
            raw_records.append(
                {
                    "keyword": kw["keyword"],
                    "normalized": kw["normalized"],
                    "intent": kw.get("intent"),
                    "category": kw.get("category"),
                    "source": kw.get("source"),
                }
            )

        deduped = deduplicate_keywords(raw_records)
        # Prefer latest weekly trend score when available
        for rec in deduped:
            for r in raw_records:
                if r.get("normalized") == rec["normalized"] and r.get("trend_score") is not None:
                    rec["trend_score"] = r["trend_score"]
                    rec["is_rising"] = r.get("is_rising")
                    rec["is_breakout"] = r.get("is_breakout")

        clustered = cluster_keywords(deduped)
        opps = opportunities_from_clusters(clustered)
        scored = [score_opportunity(o) for o in opps]
        scored.sort(
            key=lambda x: (x.get("score") is not None, x.get("score") or 0),
            reverse=True,
        )

        for s in scored:
            oid = repo.upsert_opportunity(
                s["title"],
                category=s.get("category"),
                status="discovered",
                score=s.get("score"),
                demand_score=s.get("demand_score"),
                monetization_score=s.get("monetization_score"),
                competition_score=s.get("competition_score"),
                feasibility_score=s.get("feasibility_score"),
                evidence_score=s.get("evidence_score"),
                confidence=s.get("confidence") or "pending",
                cluster_id=s.get("cluster_id"),
                notes=json.dumps({"keywords": s.get("keywords")}, ensure_ascii=False),
            )
            s["opportunity_id"] = oid

        if not args.skip_ai:
            from ai.deep_research import generate_project_plan
            from ai.screening import analyze_opportunities

            top = scored[: max(args.deep_top, 5)]
            analyze_opportunities(top[:10])
            for s in scored[: args.deep_top]:
                plan = generate_project_plan(s)
                if s.get("opportunity_id"):
                    repo.add_report(
                        s["opportunity_id"],
                        json.dumps(plan, ensure_ascii=False) if plan.get("stub") else plan.get("content") or "",
                        report_type="project_plan",
                        report_path=plan.get("report_path"),
                    )

        stats = {
            "seeds": len(seed_list),
            "windows": [w[1] for w in WINDOWS],
            "opportunities": len(scored),
            "errors": len(errors),
        }
        repo.finish_run(
            run_id,
            status="ok" if not errors else "ok_with_errors",
            error_log="\n".join(errors[:50]) if errors else None,
            stats=stats,
        )
        print(json.dumps({"status": "ok", "stats": stats}, indent=2))
        return 0
    except Exception as exc:  # noqa: BLE001
        logger.exception("Weekly pipeline failed")
        repo.finish_run(run_id, status="failed", error_log=str(exc))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
