# 周决策卡字段规格（decision-card-schema）

> 版本：2026-10-28  
> 用途：出海 SEO 找词建站变现的周决策卡；币圈不进评分；禁止脏 Suggest 当主词。

## 必填：基础 7

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `verdict` | enum | `Go` / `Watch` / `Kill`。同一周批次须正好 1 个 Go、1 个 Watch、1 个 Kill。 |
| `primary_keyword` | string | 主词。清洗后；禁止城市名乱入、`free for students` 堆砌、纯品牌官网意图（除非本卡为 Kill 示范）。 |
| `support_keywords` | string[5] | 恰好 5 个支撑词，同簇、可建页、商业/工具意图优先。 |
| `who_searches_who_pays` | text | 谁在搜、谁付钱：意图分层 + 买家画像（开发者 / 团队预算 / 代理商等）。 |
| `monetization` | object | `primary` + `backup` 两条路径，并说明为何匹配用户栈（Python / Playwright / 扩展 / Next.js）。 |
| `serp_gap` | text | 前 10 缺口一句话；须基于真实打开或抓取的公开 SERP/竞品页，并引用 ≥1 个 URL。 |
| `mvp_7d` | object | `site_type` + `url_titles`（8–12 个可上线 URL 标题）。 |
| `scope_and_success` | object | `wont_do_or_downgrade`（不做/降级理由）+ `success_30d`（可量化成败标准）。 |

## 必填：证据 3（用户新增信号，2026-10-28 固化）

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `product_growth_trend` | object | **产品增长趋势**。至少 1 条「增量」信号；尽量 1 条「减量/停滞」旧站/老产品对照。证据可来自 Similarweb 公开估计、公开报道、Product Hunt、Indie Hackers、GitHub stars、Hacker News 等。每条注明来源 URL 与日期；无数据标 `未验证`，禁止编造流量数字。 |
| `keyword_growth_trend` | object | **关键词增长趋势**。主词或同簇的 rising / breakout / 相对兴趣变化。必须标明：市场（优先 US）、时间窗、指标类型为**相对兴趣或份额**而非绝对搜索量。Google Trends、Brandwave Share of Search、公开 rising 列表均可；无 Trends 截图则写 `未验证（本轮未打开 Trends UI）` 并给替代相对证据。 |
| `related_peripheral_content` | string[≥5] | **周边相关内容**。同簇可建的对比 / 替代 / 定价 / 教程 / 工具页标题，以及可做的小工具周边点子。 |

### `product_growth_trend` 子结构

```yaml
product_growth_trend:
  upside:           # 增量（≥1）
    - claim: string
      evidence_url: string
      evidence_date: string   # YYYY-MM-DD 或可解析日期
      status: verified | unverified
  downside_or_stale: # 减量/停滞对照（尽量 ≥1）
    - claim: string
      evidence_url: string
      evidence_date: string
      status: verified | unverified
```

### `keyword_growth_trend` 子结构

```yaml
keyword_growth_trend:
  market: US | global | other
  window: string              # 如 "2025-10 → 2026-09"
  metric_type: relative_interest | share_of_search | rising_label | other_relative
  signals:
    - keyword_or_cluster: string
      direction: up | down | flat | breakout | rising
      note: string            # 相对变化描述；禁止伪绝对量
      evidence_url: string
      status: verified | unverified
```

## 推荐元数据（非缺则不合格，但强烈建议）

| 字段名 | 说明 |
|--------|------|
| `card_id` | 如 `2026-W44-go-browserbase-alternatives` |
| `title` | 给人读的卡标题 |
| `as_of` | 调研日期（Asia/Hong_Kong） |
| `evidence_vs_inference` | 哪些主张是已验证事实、哪些是推测 |
| `fit_user_stack` | 与 Python / Playwright / 扩展 / Next.js 的契合度简述 |
| `crypto_excluded` | 恒为 true（币圈不进评分） |

## 质量门禁

1. 本批 `verdict` 分布必须为 1 Go / 1 Watch / 1 Kill。  
2. 主词不得直接复用脏聚类标题（如笼统 `vs code` / `code ai`）。  
3. 避开纯 Cursor / Claude 品牌红海做 **Go**；可用作 Kill 示范或 Watch。  
4. 关键主张附来源 URL；流量数字无公开核验则写「未验证」。  
5. `related_peripheral_content` ≥ 5 条。  
6. SERP 缺口须引用真实打开过的页面 URL。

## 输出文件约定

- 周卡正文：`week-decision-cards-YYYY-MM-DD.md`  
- 本规格：`decision-card-schema.md`（同目录）
