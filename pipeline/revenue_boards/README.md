# 收入榜公开快照采集

研究用聚合脚本：优先各站**公开 API / 公开 HTML**，不做登录、不绕过付费墙。

## 依赖

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r pipeline/revenue_boards/requirements.txt
```

需要 Playwright 时（BizPeel / GetLatka / Acquire / Flippa 等）：

```bash
playwright install chromium
```

## 运行（仓库根目录）

```bash
# 推荐：仅 TrustMRR 官方公开 discovery API
python pipeline/revenue_boards/scrape_revenue_boards.py --sources trustmrr

# 多源 + 无头浏览器（本地/manual；勿在 CI 默认跑）
python pipeline/revenue_boards/scrape_revenue_boards.py --sources all --browser
```

## 输出

| 路径 | 说明 |
|------|------|
| `data/revenue_boards.json` | 站点 UI 加载的快照 |
| `data/archive/revenue_boards_YYYY-MM-DD.csv` | 按日归档 CSV |

更新 JSON 后请同步到 GitHub Pages 目录：

```bash
cp data/revenue_boards.json public/data/revenue_boards.json
```

（或在合并前运行 `python scripts/build_public.py` 时一并复制，若已接入 sync。）

## 数据源说明

- **TrustMRR** — `GET https://trustmrr.com/api/ai/discovery` 等官方公开端点；完整分页榜需认证 API。采集时会按 `slug`  polite 拉取 `https://trustmrr.com/startup/{slug}.md`，写入 `extra.long_description` / `extra.features`；若有 `website` 则尽力抓取 `extra.website_meta_description`（失败则跳过）。
- **BizPeel / GetLatka** — 公开页可见部分；完整报告常需订阅。
- **Acquire / Flippa** — 挂牌列表；收入多为卖家自报，非支付校验。
