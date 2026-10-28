# 市场叙事层字段规格（market-narratives-schema）

> 版本：2026-10-28  
> 用途：与周决策卡并列的**发散思维层**——产品/功能兴衰、替代叙事、相对需求信号（用于 ideation，不替代 Go/Watch/Kill 评分）。

## 顶层元数据

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `week_id` | string | 与 `week_decisions.json` 对齐，如 `2026-W44` |
| `as_of` | string | 调研截止日（YYYY-MM-DD） |
| `timezone` | string | 如 `Asia/Hong_Kong` |
| `title` | string | 展示标题，默认「产品兴衰 · 需求发散」 |
| `intro` | text | 本层在 AI 时代的价值说明（位移叙事 > 关键词堆砌） |
| `linked_week_decisions` | string | 关联的 `week_id` |
| `source_markdown` | string | 人类源文档路径 |
| `methodology_limitations` | array | 与周卡一致的局限条目（可选） |

## `rising[]` — 新产品 / 新功能上升

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `id` | string | 稳定 id，如 `w44-rise-browser-use` |
| `name` | string | 产品或功能簇名称 |
| `category` | string | 可选类目标签 |
| `claim` | string | 一句话主张 |
| `evidence_url` | string | 来源 URL |
| `evidence_date` | string | 证据日期 |
| `status` | enum | `verified` \| `unverified` |
| `linked_card_id` | string | 可选，关联决策卡 `card_id` |

## `falling_or_stale[]` — 旧产品 / 旧站衰退或停滞

结构同 `rising[]`（无 `linked_card_id` 时也可填）。

## `displacement[]` — 旧 → 新替代叙事

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `id` | string | 稳定 id |
| `old` | string | 被替代或失势的一方 |
| `new` | string | 承接需求的一方 |
| `gap_filled` | text | 新方案如何填旧方案留下的缺口 |
| `indie_seo_angle` | text | 对 indie SEO / 对比站 / 工具站的可建页角度 |
| `evidence_urls` | string[] | ≥1 个来源 |
| `evidence_date` | string | 可选 |
| `status` | enum | `verified` \| `unverified` |
| `linked_card_id` | string | 可选 |

## `demand_signals[]` — 相对需求趋势（ideation 用）

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `keyword_or_cluster` | string | 词或簇 |
| `direction` | enum | `up` \| `down` \| `flat` \| `breakout` \| `rising` |
| `metric_type` | enum | `share_of_search` \| `relative_interest` \| `rising_label` \| `qualitative_density` \| `other_relative` |
| `market` | string | 如 `US`、`global` |
| `window` | string | 时间窗描述 |
| `note` | string | **仅相对变化**；禁止伪绝对搜索量 |
| `ideation_hint` | string | 可发散的建站/内容角度 |
| `evidence_url` | string | 来源 |
| `status` | enum | `verified` \| `unverified` |
| `linked_card_id` | string | 可选 |

## 质量门禁

1. 每条主张附 `evidence_url`；无法核验则 `status: unverified`。  
2. `demand_signals` 不得写入未标注来源的绝对月搜/Volume。  
3. 叙事层**不**改变周卡 verdict；仅辅助发散与选题。  
4. 与周卡重复的证据应复用同一 URL，避免矛盾表述。

## 输出文件约定

- 结构化数据：`data/market_narratives.json`  
- `scripts/build_public.py` 镜像至 `public/data/market_narratives.json`  
- 人类长文仍可在 `docs/week-decision-cards-*.md` 中维护；JSON 供静态 UI 加载。
