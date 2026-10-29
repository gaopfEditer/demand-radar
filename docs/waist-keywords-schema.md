# 腰部词发现层字段规格（waist-keywords-schema）

> 版本：2026-10-29  
> 用途：固化 yanhua1010《2026出海第一课：找词》筛词口径，供静态站浏览；**不替代**周决策 Go / Watch / Kill。  
> 方法参考：<https://x.com/yanhua1010/status/2115296994289987695>

## 与周决策卡的关系

| 层级 | 文件 | 角色 |
|------|------|------|
| 拍板 | `week_decisions.json` | 每周 1 Go / 1 Watch / 1 Kill，主交付不变 |
| 叙事 | `market_narratives.json` | 产品兴衰 · 需求发散 |
| **发现** | `waist_keywords.json` | 腰部候选池；可挂 `linked_card_id` 指向周卡，但 verdict 独立（`pursue` / `watch` / `skip`） |

腰部词栏目标 **SERP 可抢位约 20–30**（首站 realistic 目标），不是硬冲 #1 头词。

## 顶层字段

| 字段 | 类型 | 说明 |
|------|------|------|
| `week_id` | string | 对齐 `week_decisions.json`（如 `2026-W44`） |
| `as_of` | string | 调研截止日 `YYYY-MM-DD` |
| `timezone` | string | 与周卡一致（如 `Asia/Hong_Kong`） |
| `title` | string | 页面标题（如「腰部词 · 可抢位 20–30」） |
| `intro` | text | 栏目说明：发现层、未验证边界 |
| `method_checklist` | object[] | 固化方法步骤（见下） |
| `source_refs` | object[] | 外部方法来源（含 X 帖链接） |
| `candidates` | object[] | 候选词列表 |

### `method_checklist` 项

| 字段 | 说明 |
|------|------|
| `step` | 序号或短 id |
| `title` | 步骤名 |
| `rule` | 可执行规则（中文） |

### `source_refs` 项

| 字段 | 说明 |
|------|------|
| `label` | 显示名 |
| `url` | 链接 |

## 候选 `candidates[]`

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `id` | string | ✓ | 稳定 id，如 `w44-waist-browserbase-alternatives` |
| `keyword` | string | ✓ | 英文主词（US 库口径） |
| `support_keywords` | string[] | | 同簇长尾 / 支撑页 |
| `band` | enum | ✓ | 固定 `waist_1k_10k`（Semrush US 月搜 1K–10K 带，无实测时用 band 描述） |
| `target_rank_band` | string | ✓ | 首站目标位，如 `"20-30"` |
| `volume_band_note` | text | ✓ | 量级说明；**禁止**编造绝对月搜 |
| `kd_band_note` | text | ✓ | KD 带说明（目标 &lt;40）；无 Semrush 则写未验证 |
| `cpc_signal` | text | | 商业信号（高 CPC 优先）；无数据标未验证 |
| `trends_check` | object | ✓ | 见下 |
| `serp_gap` | object | ✓ | 见下 |
| `similarweb_loop_note` | text | | Similarweb 站↔词循环备注 |
| `verdict` | enum | ✓ | `pursue` \| `watch` \| `skip` |
| `why` | text | ✓ | 一句结论 |
| `mvp_angle` | text | ✓ | 7 天可建页角度 |
| `linked_card_id` | string | | 可选挂周卡 `card_id` |
| `evidence_urls` | string[] | | 公开 SERP / 竞品 / 相对趋势来源 |
| `status` | enum | ✓ | `verified` \| `unverified`（整条候选证据状态；无 Semrush 实测一般为 `unverified`） |

### `trends_check`

```yaml
trends_check:
  window_7d: string      # 7 天相关查询/主题结论
  window_12m: string     # 12 个月确认非假飙升
  status: verified | unverified
  note: string           # 如 Trends UI 429、用 Brandwave 替代等
```

### `serp_gap`

```yaml
serp_gap:
  low_dr_new_site: boolean | null   # 前十是否有 &lt;1y 低 DR 新站
  big_site_monopoly: boolean | null # 是否 Grammarly 级大站占满
  summary: text
```

## 方法 checklist（内容须与 JSON 一致）

1. **Google Trends**：词根 → 过去 7 天相关查询/主题飙升 → 切 12 个月确认非假飙升；跳过品牌/新闻/球赛。  
2. **Semrush（美国库）**：月搜 **1K–10K（腰部）**，**KD &lt; 40**，意图偏信息类，CPC 高优先。  
3. **SERP**：前十若有注册不到一年、低 DR 新站 → 可抢；若全被 Grammarly 级大站占满 → 放弃。  
4. **Similarweb**：最新站反查 NEW/上涨词，词找站 ↔ 站找词循环。  
5. **排名目标**：首站 realistic 目标 **SERP 20–30**，非硬冲 #1。

## 质量门禁

1. 无 Semrush / Ahrefs 等实测截图或 API 导出时，**不得**写绝对月搜、绝对 KD；用 `volume_band_note` / `kd_band_note` + `status: unverified`。  
2. 币圈词 **不得**进入 `candidates`。  
3. 脏 Suggest、纯品牌导航（如 Kill 示范 `cursor ai`）可进池作 `skip` 示范，不得标 `pursue` 且无周卡 Go 背书。  
4. `pursue` 候选须：`serp_gap.summary` 非空，`why` / `mvp_angle` 可执行，≥1 条 `evidence_urls`（公开页）。  
5. `week_id` 与当周 `week_decisions.json` 对齐；大改候选时同步更新 `as_of`。

## 输出文件约定

- 数据：`data/waist_keywords.json`（源）→ `public/data/waist_keywords.json`（镜像，由 `scripts/build_public.py` 的 `sync_waist_keywords` 或手工同步）  
- 页面：`public/waist.html` → 根目录 `waist.html`（`STATIC_PAGES` 同步）  
- UI 渲染：`assets/app.js` 中 `renderWaistKeywords`
