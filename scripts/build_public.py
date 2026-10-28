#!/usr/bin/env python3
"""Build static GitHub Pages data from pipeline exports."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DEMAND = ROOT / "exports" / "dev_site_demand.json"
DEFAULT_KW_CSV = ROOT / "exports" / "keywords.csv"
PUBLIC_DATA = ROOT / "public" / "data"


def _evidence_summary(rating_notes: dict | None) -> list[str]:
    if not rating_notes:
        return []
    lines: list[str] = []
    for dim, items in rating_notes.items():
        if not items:
            continue
        for item in items:
            lines.append(f"{dim}: {item}")
    return lines


def _tier(score: float | None) -> str:
    if score is None:
        return "—"
    if score >= 80:
        return "优先研究"
    if score >= 65:
        return "候选"
    if score >= 50:
        return "观察"
    return "暂缓"


def build_from_demand(demand: dict) -> tuple[dict, list, list]:
    meta = {
        "updated_at": demand.get("generated_at"),
        "market": demand.get("market"),
        "language": demand.get("language"),
        "stats": demand.get("stats") or {},
        "trends_degraded": bool(demand.get("trends_degraded")),
        "note": demand.get("note"),
        "timezone_label": "UTC",
        "repo_pages_path": "/demand-radar/",
    }

    opportunities_out: list[dict] = []
    for opp in demand.get("opportunities") or []:
        opportunities_out.append(
            {
                "id": opp.get("opportunity_id"),
                "title": opp.get("title"),
                "category": opp.get("category"),
                "cluster_id": opp.get("cluster_id"),
                "score": opp.get("score"),
                "tier": _tier(opp.get("score")),
                "confidence": opp.get("confidence"),
                "status": opp.get("status"),
                "pending_dimensions": opp.get("pending_dimensions") or [],
                "keywords": opp.get("keywords") or [],
                "rating_notes": opp.get("rating_notes") or {},
                "evidence_summary": _evidence_summary(opp.get("rating_notes")),
                "demand_score": opp.get("demand_score"),
                "monetization_score": opp.get("monetization_score"),
                "competition_score": opp.get("competition_score"),
                "feasibility_score": opp.get("feasibility_score"),
                "evidence_score": opp.get("evidence_score"),
            }
        )
    opportunities_out.sort(key=lambda x: (-(x.get("score") or 0), x.get("title") or ""))

    keywords_out: list[dict] = []
    for kw in demand.get("keywords") or []:
        keywords_out.append(
            {
                "keyword": kw.get("keyword"),
                "normalized": kw.get("normalized"),
                "intent": kw.get("intent"),
                "category": kw.get("category"),
                "cluster_id": kw.get("cluster_id"),
                "source": kw.get("source"),
                "trend_score": kw.get("trend_score"),
                "is_rising": kw.get("is_rising"),
                "is_breakout": kw.get("is_breakout"),
            }
        )

    return meta, opportunities_out, keywords_out


def keywords_from_csv(path: Path) -> list[dict]:
    rows: list[dict] = []
    with path.open(encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            ts = row.get("trend_score")
            rows.append(
                {
                    "keyword": row.get("keyword"),
                    "normalized": row.get("normalized"),
                    "intent": row.get("intent"),
                    "category": row.get("category"),
                    "cluster_id": row.get("cluster_id"),
                    "source": row.get("source"),
                    "trend_score": float(ts) if ts not in (None, "") else None,
                    "is_rising": row.get("is_rising", "").lower() == "true",
                    "is_breakout": row.get("is_breakout", "").lower() == "true",
                }
            )
    return rows


def build_public(
    demand_path: Path = DEFAULT_DEMAND,
    keywords_csv: Path | None = DEFAULT_KW_CSV,
    out_dir: Path = PUBLIC_DATA,
) -> dict[str, str]:
    if not demand_path.is_file():
        raise FileNotFoundError(f"Missing export: {demand_path}")

    demand = json.loads(demand_path.read_text(encoding="utf-8"))
    meta, opportunities, keywords = build_from_demand(demand)

    if not keywords and keywords_csv and keywords_csv.is_file():
        keywords = keywords_from_csv(keywords_csv)

    out_dir.mkdir(parents=True, exist_ok=True)
    paths = {
        "meta.json": out_dir / "meta.json",
        "opportunities.json": out_dir / "opportunities.json",
        "keywords.json": out_dir / "keywords.json",
    }
    paths["meta.json"].write_text(
        json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    paths["opportunities.json"].write_text(
        json.dumps(opportunities, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    paths["keywords.json"].write_text(
        json.dumps(keywords, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return {k: str(v) for k, v in paths.items()}


def main() -> int:
    parser = argparse.ArgumentParser(description="Build public/data for GitHub Pages")
    parser.add_argument("--demand", type=Path, default=DEFAULT_DEMAND)
    parser.add_argument("--keywords-csv", type=Path, default=DEFAULT_KW_CSV)
    parser.add_argument("--out", type=Path, default=PUBLIC_DATA)
    args = parser.parse_args()
    written = build_public(args.demand, args.keywords_csv, args.out)
    print(json.dumps({"status": "ok", "written": written}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
