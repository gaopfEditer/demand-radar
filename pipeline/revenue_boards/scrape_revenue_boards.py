#!/usr/bin/env python3
"""
聚合收入榜公开快照采集器（研究用）

优先使用各站公开 API / 公开 HTML；不做登录撞库、不绕过付费墙。

数据源策略
----------
1. TrustMRR  — 官方公开 JSON（推荐，勿全站硬爬）：
     GET https://trustmrr.com/api/ai/discovery
     GET https://trustmrr.com/api/ai
     可选：https://trustmrr.com/startup/{slug}.md
   官方明确：完整市场分页需认证 API；公开 discovery 只给固定 25 条快照。

2. BizPeel   — 公开首页/Library HTML 卡片（无登录可见部分）；
               完整报告需订阅/MCP。可用 PLAYWRIGHT=1 渲染。

3. GetLatka  — 公开列表页 HTML（大量字段常需登录）；Playwright 可选。

4. Acquire.com / Flippa — 公开挂牌列表（收入多为卖家自报）；
               强反爬，默认 Playwright + 延迟。

输出（默认，自仓库根目录运行）
----
data/revenue_boards.json
data/archive/revenue_boards_YYYY-MM-DD.csv

用法
----
  cd /path/to/demand-radar
  python3 -m venv .venv && source .venv/bin/activate
  pip install -r pipeline/revenue_boards/requirements.txt
  # 仅 TrustMRR 公开 API（推荐；适合 CI / 日常快照）
  python pipeline/revenue_boards/scrape_revenue_boards.py --sources trustmrr
  # 全部（含无头浏览器；勿在 CI 默认开启）
  playwright install chromium
  python pipeline/revenue_boards/scrape_revenue_boards.py --sources all --browser
  # 额外写入带时间戳的副本到 out/
  python pipeline/revenue_boards/scrape_revenue_boards.py --sources trustmrr --stamp-out out
"""

from __future__ import annotations

import argparse
import csv
import json
import random
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urljoin

import requests

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_JSON = REPO_ROOT / "data" / "revenue_boards.json"
DEFAULT_ARCHIVE_DIR = REPO_ROOT / "data" / "archive"
from bs4 import BeautifulSoup

UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)
SESSION = requests.Session()
SESSION.headers.update(
    {
        "User-Agent": UA,
        "Accept": "application/json,text/html,application/xhtml+xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
    }
)


def sleep(a: float = 0.8, b: float = 1.8) -> None:
    time.sleep(random.uniform(a, b))


def money_to_float(text: str | None) -> float | None:
    if not text:
        return None
    t = text.strip().upper().replace(",", "").replace(" ", "")
    m = re.search(r"\$?([0-9]*\.?[0-9]+)\s*([KMB])?", t)
    if not m:
        return None
    n = float(m.group(1))
    mul = {"K": 1e3, "M": 1e6, "B": 1e9}.get(m.group(2) or "", 1.0)
    return n * mul


def row(
    source: str,
    name: str,
    *,
    monthly_revenue: float | None = None,
    mrr: float | None = None,
    total_revenue: float | None = None,
    growth_30d: float | None = None,
    category: str | None = None,
    url: str | None = None,
    website: str | None = None,
    board: str | None = None,
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "source": source,
        "board": board,
        "name": name,
        "monthly_revenue": monthly_revenue,
        "mrr": mrr,
        "total_revenue": total_revenue,
        "growth_30d": growth_30d,
        "category": category,
        "url": url,
        "website": website,
        "scraped_at": datetime.now(timezone.utc).isoformat(),
        "extra": extra or {},
    }


# ---------- TrustMRR (official public API) ----------

def scrape_trustmrr() -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    discovery = SESSION.get("https://trustmrr.com/api/ai/discovery", timeout=30)
    discovery.raise_for_status()
    data = discovery.json()
    sleep()

    def ingest(items: list[dict], board: str) -> None:
        for it in items or []:
            rev = it.get("revenue") or {}
            out.append(
                row(
                    "trustmrr",
                    it.get("name") or it.get("slug") or "",
                    monthly_revenue=rev.get("last30Days"),
                    mrr=rev.get("mrr"),
                    total_revenue=rev.get("total"),
                    growth_30d=it.get("growth30d"),
                    category=it.get("category"),
                    url=it.get("url") or f"https://trustmrr.com/startup/{it.get('slug')}",
                    website=it.get("website"),
                    board=board,
                    extra={
                        "slug": it.get("slug"),
                        "paymentProvider": it.get("paymentProvider"),
                        "growthMRR30d": it.get("growthMRR30d"),
                        "onSale": it.get("onSale"),
                        "description": it.get("description"),
                    },
                )
            )

    ingest(data.get("recentlyAddedStartups") or [], "recently_added")
    ingest(data.get("fastestGrowingStartups") or [], "fastest_growing")

    ai = SESSION.get("https://trustmrr.com/api/ai", timeout=30)
    ai.raise_for_status()
    snap = ai.json()
    sleep()
    for key, board in (
        ("recentlyListedStartups", "recently_listed_for_sale"),
        ("bestDeals", "best_deals"),
    ):
        ingest(snap.get(key) or [], board)

    print(f"[trustmrr] rows={len(out)} (public discovery + marketplace snapshot)")
    return out


def enrich_trustmrr_markdown(slug: str) -> str:
    """可选：拉公开 .md 详情（无完整历史曲线）。"""
    r = SESSION.get(f"https://trustmrr.com/startup/{slug}.md", timeout=30)
    r.raise_for_status()
    return r.text


# ---------- BizPeel (public HTML) ----------

def scrape_bizpeel_html(html: str, page_url: str) -> list[dict[str, Any]]:
    soup = BeautifulSoup(html, "lxml")
    rows: list[dict[str, Any]] = []
    # 首页/Library 卡片结构会变；用「产品名邻近 $ 金额」启发式
    text = soup.get_text("\n", strip=True)
    # 尝试卡片容器
    cards = soup.select("a[href*='/project/'], article, [class*='card'], [class*='Card']")
    seen: set[str] = set()
    for card in cards:
        name_el = card.find(["h2", "h3", "h4"]) or card
        name = name_el.get_text(" ", strip=True)
        if not name or len(name) > 80:
            continue
        blob = card.get_text(" ", strip=True)
        money = re.findall(r"\$[0-9][0-9.,]*\s*[KMBkmb]?", blob)
        if not money:
            continue
        href = card.get("href") if card.name == "a" else None
        if not href:
            a = card.find("a", href=True)
            href = a["href"] if a else None
        url = urljoin(page_url, href) if href else page_url
        key = name.lower()
        if key in seen:
            continue
        seen.add(key)
        # 常见：第一个金额像 30d revenue，第二个像 MRR
        m1 = money_to_float(money[0]) if money else None
        m2 = money_to_float(money[1]) if len(money) > 1 else None
        cat = None
        for sep in ["·", "|", "—"]:
            if sep in name:
                parts = [p.strip() for p in name.split(sep)]
                if len(parts) >= 2 and len(parts[0]) < 60:
                    name, cat = parts[0], parts[1]
                break
        rows.append(
            row(
                "bizpeel",
                name,
                monthly_revenue=m1,
                mrr=m2,
                category=cat,
                url=url,
                board="library_public",
                extra={"raw_money_tokens": money[:4], "page": page_url},
            )
        )
    if not rows:
        # 兜底：从纯文本抓「Name / $xx」弱信号，仅作调试
        rows.append(
            row(
                "bizpeel",
                "(parse_empty)",
                board="library_public",
                url=page_url,
                extra={"hint": "HTML 结构变化或需 --browser / 登录；正文长度=" + str(len(text))},
            )
        )
    return rows


def scrape_bizpeel(use_browser: bool) -> list[dict[str, Any]]:
    urls = ["https://bizpeel.com/", "https://bizpeel.com/library"]
    out: list[dict[str, Any]] = []
    for u in urls:
        if use_browser:
            html = fetch_browser(u)
        else:
            r = SESSION.get(u, timeout=45)
            r.raise_for_status()
            html = r.text
            sleep(1.2, 2.5)
        part = scrape_bizpeel_html(html, u)
        out.extend(part)
        print(f"[bizpeel] {u} -> {len(part)} rows")
    # 去重
    dedup: dict[str, dict] = {}
    for r in out:
        if r["name"] == "(parse_empty)":
            continue
        dedup[r["name"].lower()] = r
    final = list(dedup.values()) or out
    print(f"[bizpeel] unique={len(final)}")
    return final


# ---------- GetLatka / Acquire / Flippa ----------

def scrape_getlatka(use_browser: bool) -> list[dict[str, Any]]:
    url = "https://getlatka.com/saas-companies"
    html = fetch_browser(url) if use_browser else SESSION.get(url, timeout=45).text
    sleep()
    soup = BeautifulSoup(html, "lxml")
    out: list[dict[str, Any]] = []
    # 表格行启发式
    for tr in soup.select("table tr")[:200]:
        cells = [c.get_text(" ", strip=True) for c in tr.find_all(["td", "th"])]
        if len(cells) < 2:
            continue
        name = cells[0]
        if name.lower() in {"name", "company"}:
            continue
        money_cells = [c for c in cells if "$" in c or re.search(r"\d+M|\d+K", c)]
        rev = money_to_float(money_cells[0]) if money_cells else None
        a = tr.find("a", href=True)
        out.append(
            row(
                "getlatka",
                name,
                monthly_revenue=None,  # Latka 多为 ARR
                total_revenue=rev,
                category="SaaS",
                url=urljoin(url, a["href"]) if a else url,
                board="saas_companies_public",
                extra={"cells": cells[:8], "note": "公开表常为 ARR/访谈数据；完整库需登录"},
            )
        )
    print(f"[getlatka] rows={len(out)}")
    if not out:
        out.append(
            row(
                "getlatka",
                "(needs_login_or_browser)",
                board="saas_companies_public",
                url=url,
                extra={"note": "列表多为客户端渲染/登录墙，请加 --browser 或人工导出"},
            )
        )
    return out


def scrape_acquire(use_browser: bool) -> list[dict[str, Any]]:
    url = "https://acquire.com/"
    html = fetch_browser(url) if use_browser else SESSION.get(url, timeout=45).text
    sleep(1.5, 3.0)
    soup = BeautifulSoup(html, "lxml")
    out: list[dict[str, Any]] = []
    for a in soup.select("a[href*='/startup/'], a[href*='/listings/']")[:80]:
        name = a.get_text(" ", strip=True)
        if not name or len(name) < 2:
            continue
        parent = a.find_parent(["article", "div", "li"]) or a
        blob = parent.get_text(" ", strip=True)
        monies = re.findall(r"\$[0-9][0-9.,]*\s*[KMB]?", blob)
        out.append(
            row(
                "acquire",
                name[:120],
                monthly_revenue=money_to_float(monies[0]) if monies else None,
                url=urljoin(url, a["href"]),
                board="marketplace_public",
                category="acquisition_listing",
                extra={"raw_money_tokens": monies[:4], "note": "多为卖家自报，非 Stripe 校验"},
            )
        )
    print(f"[acquire] rows={len(out)}")
    if not out:
        out.append(
            row(
                "acquire",
                "(needs_browser)",
                url=url,
                board="marketplace_public",
                extra={"note": "强前端渲染，建议 --browser；并遵守站点 ToS"},
            )
        )
    return out


def scrape_flippa(use_browser: bool) -> list[dict[str, Any]]:
    # 公开搜索：按收益排序的网站类目（路径可能调整）
    url = "https://flippa.com/search?filter[property_type]=website&filter[status]=open&sort_order=most_relevant"
    html = fetch_browser(url) if use_browser else SESSION.get(url, timeout=45).text
    sleep(2.0, 4.0)
    soup = BeautifulSoup(html, "lxml")
    out: list[dict[str, Any]] = []
    for card in soup.select("[data-testid*='listing'], article, .listing-card, a[href*='/']")[:120]:
        blob = card.get_text(" ", strip=True)
        if "profit" not in blob.lower() and "revenue" not in blob.lower() and "$" not in blob:
            continue
        name_el = card.find(["h2", "h3", "h4"]) or card
        name = name_el.get_text(" ", strip=True)[:120]
        monies = re.findall(r"\$[0-9][0-9.,]*\s*[KMB]?", blob)
        href = card.get("href") if card.name == "a" else None
        if not href:
            a = card.find("a", href=True)
            href = a["href"] if a else None
        if not name or not monies:
            continue
        out.append(
            row(
                "flippa",
                name,
                monthly_revenue=money_to_float(monies[0]),
                url=urljoin(url, href) if href else url,
                board="search_public",
                category="marketplace_listing",
                extra={"raw_money_tokens": monies[:5], "note": "挂牌自报；Cloudflare 常见"},
            )
        )
    # 去重
    dedup = {r["url"] or r["name"]: r for r in out}
    out = list(dedup.values())
    print(f"[flippa] rows={len(out)}")
    if not out:
        out.append(
            row(
                "flippa",
                "(cloudflare_or_browser)",
                url=url,
                board="search_public",
                extra={"note": "常遇 Cloudflare，用 --browser；勿高频"},
            )
        )
    return out


# ---------- Playwright helper ----------

_BROWSER = None


def fetch_browser(url: str, wait_ms: int = 4000) -> str:
    global _BROWSER
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as e:
        raise SystemExit("需要: pip install playwright && playwright install chromium") from e

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(user_agent=UA, locale="en-US")
        page = context.new_page()
        page.goto(url, wait_until="domcontentloaded", timeout=60000)
        page.wait_for_timeout(wait_ms)
        html = page.content()
        browser.close()
    return html


# ---------- IO ----------

CSV_FIELDS = [
    "source",
    "board",
    "name",
    "monthly_revenue",
    "mrr",
    "total_revenue",
    "growth_30d",
    "category",
    "url",
    "website",
    "scraped_at",
]


SITE_NOTES = [
    "TrustMRR: 使用官方公开 API；完整榜分页需认证，勿硬爬全站。",
    "BizPeel/GetLatka: 完整报告常需订阅。",
    "Acquire/Flippa: 收入多为卖家自报。",
]


def _site_payload(rows: list[dict[str, Any]], sources: list[str]) -> dict[str, Any]:
    return {
        "as_of": datetime.now().strftime("%Y-%m-%d"),
        "timezone": "Asia/Shanghai",
        "title": "收入榜公开快照",
        "intro": "公开 API / 公开页快照；TrustMRR 走官方 discovery；Acquire/Flippa 多为自报。",
        "sources": sources,
        "count": len(rows),
        "notes": SITE_NOTES,
        "rows": rows,
    }


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=CSV_FIELDS, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k) for k in CSV_FIELDS})


def write_site_outputs(
    rows: list[dict[str, Any]],
    sources: list[str],
    *,
    json_path: Path = DEFAULT_JSON,
    archive_dir: Path = DEFAULT_ARCHIVE_DIR,
) -> tuple[Path, Path]:
    json_path.parent.mkdir(parents=True, exist_ok=True)
    archive_dir.mkdir(parents=True, exist_ok=True)
    date_str = datetime.now().strftime("%Y-%m-%d")
    cp = archive_dir / f"revenue_boards_{date_str}.csv"
    payload = _site_payload(rows, sources)
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    write_csv(cp, rows)
    return json_path, cp


def write_stamp_outputs(rows: list[dict[str, Any]], out_dir: Path) -> tuple[Path, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    jp = out_dir / f"revenue_boards_{stamp}.json"
    cp = out_dir / f"revenue_boards_{stamp}.csv"
    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "count": len(rows),
        "notes": SITE_NOTES,
        "rows": rows,
    }
    jp.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    write_csv(cp, rows)
    return jp, cp


def main() -> int:
    ap = argparse.ArgumentParser(description="Scrape public revenue board snapshots")
    ap.add_argument(
        "--sources",
        default="trustmrr",
        help="comma list: trustmrr,bizpeel,getlatka,acquire,flippa,all",
    )
    ap.add_argument(
        "--json",
        type=Path,
        default=DEFAULT_JSON,
        help="site snapshot JSON (default: data/revenue_boards.json)",
    )
    ap.add_argument(
        "--archive-dir",
        type=Path,
        default=DEFAULT_ARCHIVE_DIR,
        help="dated CSV archive directory (default: data/archive/)",
    )
    ap.add_argument(
        "--stamp-out",
        type=Path,
        default=None,
        help="optional directory for extra timestamped JSON+CSV copies",
    )
    ap.add_argument("--browser", action="store_true", help="use Playwright Chromium")
    args = ap.parse_args()

    sources = [s.strip().lower() for s in args.sources.split(",") if s.strip()]
    if "all" in sources:
        sources = ["trustmrr", "bizpeel", "getlatka", "acquire", "flippa"]
    ran_sources = [s for s in sources if s != "all"]

    rows: list[dict[str, Any]] = []
    dispatch = {
        "trustmrr": lambda: scrape_trustmrr(),
        "bizpeel": lambda: scrape_bizpeel(args.browser),
        "getlatka": lambda: scrape_getlatka(args.browser),
        "acquire": lambda: scrape_acquire(args.browser),
        "flippa": lambda: scrape_flippa(args.browser),
    }

    for s in sources:
        if s not in dispatch:
            print(f"unknown source: {s}", file=sys.stderr)
            continue
        try:
            part = dispatch[s]()
            rows.extend(part)
        except Exception as e:
            print(f"[{s}] FAILED: {e}", file=sys.stderr)
            rows.append(
                row(s, "(error)", board="error", extra={"error": str(e)})
            )

    jp, cp = write_site_outputs(
        rows,
        ran_sources,
        json_path=args.json,
        archive_dir=args.archive_dir,
    )
    print(f"JSON -> {jp}")
    print(f"CSV  -> {cp}")
    if args.stamp_out:
        sjp, scp = write_stamp_outputs(rows, args.stamp_out)
        print(f"stamp JSON -> {sjp}")
        print(f"stamp CSV  -> {scp}")
    print(f"total rows: {len(rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
