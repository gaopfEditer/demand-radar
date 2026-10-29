#!/usr/bin/env python3
"""Build static GitHub Pages data from pipeline exports.

Weekly decision cards (周决策卡):
  1. Author ``docs/week-decision-cards-YYYY-MM-DD.md`` (see ``docs/decision-card-schema.md``).
  2. Update ``data/week_decisions.json`` to match the schema (1 Go / 1 Watch / 1 Kill).
  3. Update ``data/market_narratives.json`` (see ``docs/market-narratives-schema.md``) for the
     产品兴衰 · 需求发散 layer.
  4. Update ``data/waist_keywords.json`` (see ``docs/waist-keywords-schema.md``) for the
     腰部词 · 可抢位 10–20 discovery layer.
  5. Run ``python scripts/build_public.py`` — copies JSON to ``public/data/`` and ``data/``,
     and syncs HTML/assets from ``public/`` to the repo root for branch-based Pages.
  Markdown in ``docs/`` is the human source of truth; JSON is what the static UI loads.
"""

from __future__ import annotations

import argparse
import csv
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DEMAND = ROOT / "exports" / "dev_site_demand.json"
DEFAULT_KW_CSV = ROOT / "exports" / "keywords.csv"
PUBLIC_DATA = ROOT / "public" / "data"
ROOT_DATA = ROOT / "data"
PUBLIC_DIR = ROOT / "public"
STATIC_PAGES = (
    "index.html",
    "trends.html",
    "opportunities.html",
    "decision.html",
    "keywords.html",
    "detail.html",
    "waist.html",
    "revenue.html",
)
WEEK_DECISIONS_JSON = "week_decisions.json"
MARKET_NARRATIVES_JSON = "market_narratives.json"
WAIST_KEYWORDS_JSON = "waist_keywords.json"
REVENUE_BOARDS_JSON = "revenue_boards.json"


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


def _write_json_bundle(
    meta: dict,
    opportunities: list,
    keywords: list,
    out_dir: Path,
) -> dict[str, str]:
    out_dir.mkdir(parents=True, exist_ok=True)
    paths = {
        "meta.json": out_dir / "meta.json",
        "opportunities.json": out_dir / "opportunities.json",
        "keywords.json": out_dir / "keywords.json",
    }
    payloads = {
        "meta.json": meta,
        "opportunities.json": opportunities,
        "keywords.json": keywords,
    }
    for name, path in paths.items():
        path.write_text(
            json.dumps(payloads[name], ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
    return {k: str(v) for k, v in paths.items()}


def _sync_json_artifact(filename: str, out_dirs: list[Path] | None = None) -> list[str]:
    """Mirror data/<filename> into each public data directory."""
    src = ROOT_DATA / filename
    if not src.is_file():
        return []
    dirs = out_dirs if out_dirs is not None else [PUBLIC_DATA, ROOT_DATA]
    copied: list[str] = []
    for out_dir in dirs:
        out_dir.mkdir(parents=True, exist_ok=True)
        dest = out_dir / filename
        if dest.resolve() == src.resolve():
            copied.append(str(dest))
            continue
        shutil.copy2(src, dest)
        copied.append(str(dest))
    return copied


def sync_week_decisions(out_dirs: list[Path] | None = None) -> list[str]:
    """Mirror data/week_decisions.json into each public data directory."""
    return _sync_json_artifact(WEEK_DECISIONS_JSON, out_dirs)


def sync_market_narratives(out_dirs: list[Path] | None = None) -> list[str]:
    """Mirror data/market_narratives.json into each public data directory."""
    return _sync_json_artifact(MARKET_NARRATIVES_JSON, out_dirs)


def sync_waist_keywords(out_dirs: list[Path] | None = None) -> list[str]:
    """Mirror data/waist_keywords.json into each public data directory."""
    return _sync_json_artifact(WAIST_KEYWORDS_JSON, out_dirs)


def sync_revenue_boards(out_dirs: list[Path] | None = None) -> list[str]:
    """Mirror data/revenue_boards.json into each public data directory."""
    return _sync_json_artifact(REVENUE_BOARDS_JSON, out_dirs)


def sync_pages_root() -> dict[str, list[str]]:
    """Copy static UI to repo root for branch-based GitHub Pages (Jekyll bypass)."""
    copied: dict[str, list[str]] = {"html": [], "assets": [], "other": []}

    nojekyll_src = PUBLIC_DIR / ".nojekyll"
    if nojekyll_src.is_file():
        shutil.copy2(nojekyll_src, ROOT / ".nojekyll")
        copied["other"].append(str(ROOT / ".nojekyll"))

    for name in STATIC_PAGES:
        src = PUBLIC_DIR / name
        if src.is_file():
            shutil.copy2(src, ROOT / name)
            copied["html"].append(str(ROOT / name))

    src_assets = PUBLIC_DIR / "assets"
    dst_assets = ROOT / "assets"
    if src_assets.is_dir():
        dst_assets.mkdir(parents=True, exist_ok=True)
        # Copy every file under public/assets (CSS/JS, favicon.svg/.ico/.png, etc.).
        for item in sorted(src_assets.iterdir()):
            dest = dst_assets / item.name
            if item.is_file():
                shutil.copy2(item, dest)
                copied["assets"].append(str(dest))

    return copied


def build_public(
    demand_path: Path = DEFAULT_DEMAND,
    keywords_csv: Path | None = DEFAULT_KW_CSV,
    out_dirs: list[Path] | None = None,
    sync_root: bool = True,
) -> dict[str, object]:
    if not demand_path.is_file():
        raise FileNotFoundError(f"Missing export: {demand_path}")

    demand = json.loads(demand_path.read_text(encoding="utf-8"))
    meta, opportunities, keywords = build_from_demand(demand)

    if not keywords and keywords_csv and keywords_csv.is_file():
        keywords = keywords_from_csv(keywords_csv)

    dirs = out_dirs if out_dirs is not None else [PUBLIC_DATA, ROOT_DATA]
    written: dict[str, dict[str, str]] = {}
    for out_dir in dirs:
        written[str(out_dir)] = _write_json_bundle(meta, opportunities, keywords, out_dir)

    week_decisions = sync_week_decisions(dirs)
    market_narratives = sync_market_narratives(dirs)
    waist_keywords = sync_waist_keywords(dirs)
    revenue_boards = sync_revenue_boards(dirs)
    root_sync = sync_pages_root() if sync_root else None
    return {
        "data": written,
        "week_decisions": week_decisions,
        "market_narratives": market_narratives,
        "waist_keywords": waist_keywords,
        "revenue_boards": revenue_boards,
        "root_static": root_sync,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build public/data for GitHub Pages")
    parser.add_argument("--demand", type=Path, default=DEFAULT_DEMAND)
    parser.add_argument("--keywords-csv", type=Path, default=DEFAULT_KW_CSV)
    parser.add_argument(
        "--out",
        type=Path,
        action="append",
        dest="outs",
        help="Output data dir (repeatable; default: public/data and ./data)",
    )
    parser.add_argument(
        "--no-sync-root",
        action="store_true",
        help="Do not copy HTML/assets/.nojekyll to repo root",
    )
    args = parser.parse_args()
    out_dirs = args.outs if args.outs else [PUBLIC_DATA, ROOT_DATA]
    result = build_public(
        args.demand,
        args.keywords_csv,
        out_dirs=out_dirs,
        sync_root=not args.no_sync_root,
    )
    print(json.dumps({"status": "ok", **result}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
