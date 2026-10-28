#!/usr/bin/env python3
"""Daily pipeline: collect → normalize → dedupe → cluster → score → export.

Usage:
  python run_daily.py
  python run_daily.py --limit-seeds 5 --force-mock-trends
  python run_daily.py --skip-ai
"""

from __future__ import annotations

import argparse
import csv
import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from collectors.autocomplete import AutocompleteCollector
from collectors.trends import TrendsCollector
from pipeline.cluster import cluster_keywords, opportunities_from_clusters
from pipeline.deduplicate import deduplicate_keywords
from pipeline.normalize import normalize_record
from pipeline.score import score_opportunity, tier_for_score
from storage.repository import Repository

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("run_daily")


def load_seeds(path: Path) -> dict:
    with path.open(encoding="utf-8") as f:
        return yaml.safe_load(f)


def main() -> int:
    parser = argparse.ArgumentParser(description="Demand Radar daily pipeline")
    parser.add_argument("--db", default=str(ROOT / "data" / "demand_radar.db"))
    parser.add_argument("--seeds", default=str(ROOT / "config" / "seeds.yaml"))
    parser.add_argument("--limit-seeds", type=int, default=0, help="0 = all seeds")
    parser.add_argument("--force-mock-trends", action="store_true")
    parser.add_argument("--no-mock-fallback", action="store_true")
    parser.add_argument("--skip-suggest", action="store_true")
    parser.add_argument("--skip-trends", action="store_true")
    parser.add_argument("--skip-ai", action="store_true")
    parser.add_argument("--market", default="US")
    parser.add_argument("--timeframe", default="now 7-d")
    parser.add_argument("--suggest-delay", type=float, default=0.35)
    parser.add_argument("--trends-delay", type=float, default=1.2)
    args = parser.parse_args()

    cfg = load_seeds(Path(args.seeds))
    markets = cfg.get("markets") or ["US"]
    language = cfg.get("language", "en")
    modifiers = cfg.get("modifiers") or AutocompleteCollector.DEFAULT_MODIFIERS
    max_per_seed = int(cfg.get("max_candidates_per_seed") or 50)
    categories = cfg.get("categories") or {}

    repo = Repository(args.db)
    run_id = repo.start_run("daily")
    errors: list[str] = []
    stats: dict = {}

    try:
        # Load seeds into DB
        seed_list: list[dict] = []
        for cat, words in categories.items():
            for w in words:
                repo.upsert_seed(w, cat, market=args.market, language=language)
                seed_list.append({"keyword": w, "category": cat})
        if args.limit_seeds and args.limit_seeds > 0:
            seed_list = seed_list[: args.limit_seeds]
        stats["seeds"] = len(seed_list)
        logger.info("Seeds loaded: %d", len(seed_list))

        # --- Autocomplete ---
        suggest_results = []
        candidates: list[str] = []
        if not args.skip_suggest:
            ac = AutocompleteCollector(
                delay_seconds=args.suggest_delay,
                max_per_seed=max_per_seed,
                language=language,
            )
            seeds_only = [s["keyword"] for s in seed_list]
            suggest_results, candidates = ac.collect(seeds_only, modifiers)
            errors.extend(ac.errors)
            stats["suggest_queries"] = len(suggest_results)
            stats["suggest_candidates"] = len(candidates)
            stats["suggest_errors"] = len(ac.errors)
            logger.info(
                "Autocomplete: %d queries, %d unique candidates, %d errors",
                len(suggest_results),
                len(candidates),
                len(ac.errors),
            )
        else:
            candidates = [s["keyword"] for s in seed_list]

        # Map seed → category
        seed_cat = {s["keyword"].lower(): s["category"] for s in seed_list}

        def guess_category(kw: str) -> str | None:
            low = kw.lower()
            if low in seed_cat:
                return seed_cat[low]
            for sk, cat in seed_cat.items():
                if sk in low or low in sk:
                    return cat
            return None

        # Normalize suggest candidates
        raw_records: list[dict] = []
        for s in seed_list:
            raw_records.append(
                normalize_record(s["keyword"], category=s["category"], source="seed")
            )
        for c in candidates:
            raw_records.append(
                normalize_record(
                    c, category=guess_category(c), source="autocomplete"
                )
            )

        # Persist suggest evidence
        for r in suggest_results:
            for sug in r.suggestions:
                kid = repo.upsert_keyword(
                    sug,
                    normalize_record(sug)["normalized"],
                    intent=normalize_record(sug)["intent"],
                    category=guess_category(sug),
                    source="autocomplete",
                )
                repo.add_evidence(
                    "autocomplete_suggestion",
                    keyword_id=kid,
                    source_url="https://suggestqueries.google.com/complete/search",
                    content=json.dumps({"seed": r.seed, "query": r.query, "suggestion": sug}),
                )

        # --- Trends (small batch: seeds only for daily speed) ---
        trend_points = []
        trends_degraded = False
        if not args.skip_trends:
            tc = TrendsCollector(
                delay_seconds=args.trends_delay,
                force_mock=args.force_mock_trends,
                # pytrends first for reliable daily; trendspyg (browser) still in chain
                prefer_pytrends=True,
            )
            trend_kws = [s["keyword"] for s in seed_list]
            # Cap trends calls for daily MVP
            trend_kws = trend_kws[: max(args.limit_seeds or 8, 8)]
            trend_points = tc.collect(
                trend_kws,
                timeframe=args.timeframe,
                markets=[args.market],
                allow_mock_fallback=not args.no_mock_fallback,
            )
            errors.extend(tc.errors)
            for p in trend_points:
                if (p.raw or {}).get("degraded") or (p.raw or {}).get("mock"):
                    trends_degraded = True
                if p.error:
                    errors.append(p.error)
                    continue
                rec = normalize_record(
                    p.keyword,
                    category=seed_cat.get(p.keyword.lower()),
                    source="trends",
                    extra={
                        "trend_score": p.interest,
                        "is_rising": p.is_rising,
                        "is_breakout": p.is_breakout,
                        "timeframe": p.timeframe,
                        "market": p.market,
                    },
                )
                raw_records.append(rec)
                kid = repo.upsert_keyword(
                    p.keyword,
                    rec["normalized"],
                    intent=rec["intent"],
                    category=rec.get("category"),
                    source="trends",
                )
                # Snapshots are append-only
                repo.append_snapshot(
                    kid,
                    "google_trends",
                    timeframe=p.timeframe,
                    market=p.market,
                    trend_score=p.interest,
                    is_rising=p.is_rising,
                    is_breakout=p.is_breakout,
                    raw={
                        "related": p.related_queries,
                        "rising": p.rising_queries,
                        "meta": p.raw,
                    },
                )
                # Add related/rising as keywords
                for rq in (p.related_queries or []) + (p.rising_queries or []):
                    q = rq.get("query") or rq.get("keyword")
                    if not q:
                        continue
                    n = normalize_record(
                        str(q),
                        category=rec.get("category"),
                        source="trends_related",
                        extra={
                            "is_rising": True,
                            "trend_score": None,
                        },
                    )
                    raw_records.append(n)
            stats["trend_points"] = len(trend_points)
            stats["trends_degraded"] = trends_degraded
            logger.info(
                "Trends: %d points (degraded=%s)", len(trend_points), trends_degraded
            )

        # --- Pipeline ---
        deduped = deduplicate_keywords(raw_records)
        # Attach latest trend scores from raw onto deduped
        trend_map = {
            normalize_record(p.keyword)["normalized"]: p
            for p in trend_points
            if not p.error
        }
        for rec in deduped:
            tp = trend_map.get(rec["normalized"])
            if tp:
                rec["trend_score"] = tp.interest
                rec["is_rising"] = tp.is_rising
                rec["is_breakout"] = tp.is_breakout
            kid = repo.upsert_keyword(
                rec["keyword"],
                rec["normalized"],
                intent=rec.get("intent"),
                category=rec.get("category"),
                source=rec.get("source"),
            )
            rec["id"] = kid

        clustered = cluster_keywords(deduped)
        for rec in clustered:
            if rec.get("id") and rec.get("cluster_id"):
                repo.upsert_keyword(
                    rec["keyword"],
                    rec["normalized"],
                    intent=rec.get("intent"),
                    category=rec.get("category"),
                    cluster_id=rec.get("cluster_id"),
                    source=rec.get("source"),
                )

        opps = opportunities_from_clusters(clustered)
        scored = [score_opportunity(o) for o in opps]
        scored.sort(key=lambda x: (x.get("score") is not None, x.get("score") or 0), reverse=True)

        for s in scored:
            oid = repo.upsert_opportunity(
                s["title"],
                category=s.get("category"),
                status=s.get("status") or "discovered",
                score=s.get("score"),
                demand_score=s.get("demand_score"),
                monetization_score=s.get("monetization_score"),
                competition_score=s.get("competition_score"),
                feasibility_score=s.get("feasibility_score"),
                evidence_score=s.get("evidence_score"),
                confidence=s.get("confidence") or "pending",
                cluster_id=s.get("cluster_id"),
                notes=json.dumps(
                    {
                        "pending_dimensions": s.get("pending_dimensions"),
                        "tier": tier_for_score(s.get("score")),
                        "keywords": s.get("keywords"),
                        "rating_notes": s.get("rating_notes"),
                    },
                    ensure_ascii=False,
                ),
            )
            s["opportunity_id"] = oid

        stats["keywords"] = len(deduped)
        stats["opportunities"] = len(scored)

        # --- Optional AI ---
        if not args.skip_ai:
            from ai.screening import analyze_opportunities

            top = [s for s in scored if s.get("score") is not None][:10]
            if not top:
                top = scored[:10]
            reports = analyze_opportunities(top)
            for rep in reports:
                # Attach to top opportunity if possible
                target_id = top[0]["opportunity_id"] if top else None
                if target_id:
                    path = rep.get("report_path")
                    content = json.dumps(rep, ensure_ascii=False, indent=2)
                    repo.add_report(
                        target_id,
                        content,
                        report_type="screening",
                        report_path=path,
                    )
            stats["ai_reports"] = len(reports)

        # --- Exports ---
        export_dir = ROOT / "exports"
        export_dir.mkdir(parents=True, exist_ok=True)

        kw_csv = export_dir / "keywords.csv"
        with kw_csv.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(
                f,
                fieldnames=[
                    "keyword",
                    "normalized",
                    "intent",
                    "category",
                    "cluster_id",
                    "source",
                    "trend_score",
                    "is_rising",
                    "is_breakout",
                ],
            )
            writer.writeheader()
            for rec in clustered:
                writer.writerow(
                    {
                        "keyword": rec.get("keyword"),
                        "normalized": rec.get("normalized"),
                        "intent": rec.get("intent"),
                        "category": rec.get("category"),
                        "cluster_id": rec.get("cluster_id"),
                        "source": rec.get("source"),
                        "trend_score": rec.get("trend_score"),
                        "is_rising": rec.get("is_rising"),
                        "is_breakout": rec.get("is_breakout"),
                    }
                )

        demand_json = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "market": args.market,
            "language": language,
            "stats": stats,
            "trends_degraded": trends_degraded,
            "keywords": clustered,
            "opportunities": scored,
            "note": (
                "Google Trends values are relative interest in a query range, "
                "NOT absolute search volume."
            ),
        }
        out_json = export_dir / "dev_site_demand.json"
        out_json.write_text(
            json.dumps(demand_json, ensure_ascii=False, indent=2), encoding="utf-8"
        )

        stats["exports"] = [str(kw_csv), str(out_json)]

        try:
            from scripts.build_public import build_public

            public_paths = build_public(out_json, kw_csv)
            stats["public_data"] = public_paths
            logger.info("Built GitHub Pages data: %s", public_paths)
        except Exception as exc:  # noqa: BLE001
            logger.warning("build_public skipped: %s", exc)

        repo.finish_run(
            run_id,
            status="ok" if not errors else "ok_with_errors",
            error_log="\n".join(errors[:50]) if errors else None,
            stats=stats,
        )
        logger.info("Done. keywords=%s opportunities=%s", stats["keywords"], stats["opportunities"])
        logger.info("Exports: %s", stats["exports"])
        print(json.dumps({"status": "ok", "stats": stats, "error_count": len(errors)}, indent=2))
        return 0
    except Exception as exc:  # noqa: BLE001
        logger.exception("Pipeline failed")
        repo.finish_run(run_id, status="failed", error_log=str(exc))
        print(json.dumps({"status": "failed", "error": str(exc)}), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
