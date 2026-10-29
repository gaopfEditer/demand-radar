"""Orchestrate waist keyword discovery stages (documentation + mock paths).

Does not call Semrush or Similarweb. Stage 0 can write exports/waist_expanded.json via waist_expand.

Usage:
  python -m pipeline.run_waist_discovery --mock
  python -m pipeline.run_waist_discovery --stage0-only
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from pipeline.waist_expand import expand_mock, _load_seeds

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SEEDS = ROOT / "config" / "seeds.yaml"
DEFAULT_EXPANDED = ROOT / "exports" / "waist_expanded.json"
WAIST_JSON = ROOT / "data" / "waist_keywords.json"

STAGES = [
    ("0", "Composer 组织联想", "prompts/waist_expand.md · pipeline/waist_expand.py"),
    ("1", "Google Trends", "7d 飙升 → 12m 确认真涨；跳过品牌/新闻/球赛"),
    ("2", "Semrush（美国）", "1K–10K · KD<40 · 信息意图 · CPC 优先；立项只看 US 月搜"),
    ("3", "Similarweb 站↔词循环", "最新站 → NEW/上涨词 → SERP 再挑站"),
    ("4", "需求串", "写入 data/waist_keywords.json candidates[]"),
    ("5", "AI 产品要素", "prompts/waist_to_product.md → 建站包 / 可选挂周卡"),
]


def _print_stages() -> None:
    print("Keyword discovery pipeline (see docs/keyword-discovery-pipeline.md)\n")
    for num, title, detail in STAGES:
        print(f"  阶段 {num} · {title}")
        print(f"    → {detail}\n")


def run_mock(stage0_only: bool) -> dict:
    _print_stages()
    seeds = _load_seeds(DEFAULT_SEEDS)
    expanded = expand_mock(seeds)
    DEFAULT_EXPANDED.parent.mkdir(parents=True, exist_ok=True)
    DEFAULT_EXPANDED.write_text(json.dumps(expanded, ensure_ascii=False, indent=2), encoding="utf-8")

    result = {
        "mode": "mock",
        "stage0_out": str(DEFAULT_EXPANDED),
        "seed_count": len(seeds),
        "cluster_count": len(expanded.get("clusters") or []),
        "waist_json": str(WAIST_JSON),
        "next_manual": [
            "阶段 1–3：手工 Trends / Semrush US / Similarweb（或 Playwright Trends，注意 429）",
            "阶段 4：编辑 data/waist_keywords.json（status verified|unverified，无实测不写绝对月搜）",
            "阶段 5：prompts/waist_to_product.md 产出 MVP 包",
            "发布：python scripts/build_public.py 同步 public/data/waist_keywords.json",
        ],
    }
    if stage0_only:
        result["stopped_after"] = "stage0"
    else:
        result["stopped_after"] = "mock_run_complete"
        if WAIST_JSON.is_file():
            data = json.loads(WAIST_JSON.read_text(encoding="utf-8"))
            result["existing_candidates"] = len(data.get("candidates") or [])
        else:
            result["existing_candidates"] = 0
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Waist keyword discovery orchestrator (mock)")
    parser.add_argument("--mock", action="store_true", help="Run mock stage 0 and print stage map")
    parser.add_argument("--stage0-only", action="store_true", help="Only write exports/waist_expanded.json")
    args = parser.parse_args(argv)

    if not (args.mock or args.stage0_only):
        parser.print_help()
        print("\nHint: pass --mock for a minimal dry run.")
        return 0

    result = run_mock(stage0_only=args.stage0_only)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
