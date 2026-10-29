# 腰部词发现流水线（keyword-discovery-pipeline）

> 版本：2026-10-29  
> 产出：`data/waist_keywords.json` 候选池（发现层，**不替代** `week_decisions.json` Go/Watch/Kill）  
> 字段规格：`docs/waist-keywords-schema.md`  
> 首站 SERP 目标位：**10–20**（realistic 腰位，非硬冲 #1）

本流水线把《2026出海第一课：找词》类手工流程拆成可脚本化阶段；各阶段可独立 mock，**不强依赖** Semrush API / OpenAI key。

## 总览

```mermaid
flowchart LR
  S0[阶段0 Composer 联想] --> S1[阶段1 Google Trends]
  S1 --> S2[阶段2 Semrush 美国]
  S2 --> S3[阶段3 Similarweb 循环]
  S3 --> S4[阶段4 需求串]
  S4 --> S5[阶段5 AI 产品要素]
  S5 --> JSON[waist_keywords.json]
  S5 --> SITE[建站 / 周决策卡]
```

| 阶段 | 输入 | 输出 | 本仓入口 |
|------|------|------|----------|
| 0 | 词根 / 品类种子 | 查询簇、对比词、定价词、长尾修饰、skip 列表 | `prompts/waist_expand.md` · `pipeline/waist_expand.py` |
| 1 | 阶段 0 簇 | 7d 飙升词 + 12m 确认真涨 | 手工 / Playwright（见文末） |
| 2 | 候选英文 query | US 月搜带、KD、CPC、SERP 前十 AS/外链 | 手工 Semrush（立项只看 **美国** 量） |
| 3 | SERP 参与者 | 新站 ↔ NEW/上涨词循环 | 手工 Similarweb |
| 4 | 过检词 | demand chain（主词 + 支撑 + pain + 变现暗示） | 更新 JSON `candidates[]` |
| 5 | 需求串 | 站点类型、核心 URL、变现、MVP 7 天、Kill 条件 | `prompts/waist_to_product.md` |

### 横切筛选偏好（写入 intro / schema）

1. **持续热度**：12 个月窗口不能是假飙升、单新闻尖峰或球赛/品牌事件；7d 热但 12m 异常尖刺 → 降级或 skip。  
2. **可产品化**：能沉淀成对比站 / 计算器 / 工具页；纯品牌导航、无独立页价值 → skip。  
3. **证据诚实**：保持 `status: verified | unverified`；无 Semrush 实测 **不写** 绝对月搜 / 绝对 KD。

---

## 阶段 0 · Composer 组织联想（LLM）

**目的**：在进 Trends 前把「可搜的英文 query 空间」摊开，并显式标记噪声。

- **输入**：词根或品类种子（如 `cloud browser`、`playwright hosting`）。  
- **输出**（建议 JSON 簇结构）：
  - `clusters[]`：主题簇 + 代表 query  
  - `comparison_queries`：`X vs Y`、`alternatives to X`  
  - `pricing_queries`：`X pricing`、`cost of X`  
  - `long_tail_modifiers`：教程 / benchmark / calculator 修饰  
  - `skip_brand_or_news`：品牌直达、新闻、球赛、币圈等 **明确 skip**

**实现说明**：

- 后续可接 **Cursor Composer** 或任意兼容 OpenAI Chat Completions 的本地/云端端点。  
- 本仓仅保留提示词草稿 `prompts/waist_expand.md` 与接口骨架 `pipeline/waist_expand.py`（默认 **mock**，不读取 API key）。  
- 扩展点：`waist_expand.py --provider openai` 时读取 `OPENAI_API_KEY` / `DEMAND_RADAR_API_KEY`（可选，非 MVP 必需）。

---

## 阶段 1 · Google Trends

**操作顺序**（与 yanhua1010 帖一致）：

1. 词根 → **过去 7 天**「相关查询 / 相关主题」中的 **飙升** 项。  
2. 对飙升项 **下钻**（换 query 再开 Trends）。  
3. **新标签页** 切 **过去 12 个月** 确认是否为 **真涨**（非单点尖峰）。  
4. **跳过**：纯品牌、新闻事件、球赛、短期 meme；与阶段 0 `skip` 列表合并。

**写入 JSON**：`candidates[].trends_check`（`window_7d` / `window_12m` / `status` / `note`）。

**自动化（可选）**：Playwright 打开 Trends 公开页；注意 **429 / 反爬**，失败时 `status: unverified` + note，不编造曲线。

---

## 阶段 2 · Semrush 定生死（仅美国）

**只看 Semrush 美国库** 作为立项量级；**不要用** Similarweb 全球量代替 US 月搜。

| 指标 | 腰部带偏好 |
|------|------------|
| 月搜（US） | 约 **1K–10K**（`band: waist_1k_10k`） |
| KD | **&lt; 40** |
| 意图 | 偏 **信息类**；商业对比 / pricing 加分 |
| CPC | 高 CPC **优先**（变现信号） |
| SERP | 前十 **Authority Score**、外链概况；是否有 &lt;1y 低 DR 新站 |

**不通过**：大站垄断（Grammarly 级占满）、KD 虚低但 SERP 全是 DR80+ 文档站且无缺口。

**写入 JSON**：`volume_band_note`、`kd_band_note`、`cpc_signal`、`serp_gap`、`status`（无导出则 `unverified`）。

---

## 阶段 3 · Similarweb 站 ↔ 词循环

1. 从 Google **前十** 拎 **注册最晚 / 流量上涨** 的站。  
2. Similarweb → **Organic Search** 上涨词、**NEW** 词。  
3. 对该词再看 SERP 参与者 → 再挑 **最新站** 循环 2–3 轮。  
4. 检查：流量是否 **真来自搜索**（非纯 Direct/Referral 刷量）；页面上是否有 **affiliate / pricing / lead** 等变现痕迹。

**写入 JSON**：`similarweb_loop_note`、补充 `support_keywords[]`。

---

## 阶段 4 · 需求串（demand chain）

把通过阶段 1–3 的词组织成一条可建站的需求链：

- **主词**（1 个 landing / hub）  
- **支撑词**（对比页、定价页、教程、计算器）  
- **pain**（用户卡点，一句话）  
- **变现暗示**（affiliate、lead、SaaS trial、广告位等，不写未验证收入数字）

**动作**：新增或更新 `data/waist_keywords.json` 的 `candidates[]`（`keyword`、`support_keywords`、`why`、`mvp_angle`、`verdict` 初判）。

**同步**：`python scripts/build_public.py` 或仅 `sync_waist_keywords` 镜像到 `public/data/`。

---

## 阶段 5 · AI 产品要素 → 建站入口

从需求串抽出可执行建站包：

| 要素 | 说明 |
|------|------|
| 站点类型 | 对比枢纽 / 单工具 / 计算器 / 教程站 |
| 核心 URL 列表 | 7 天内可上线的路径 |
| 变现路径 | 与 SERP 意图一致的 MVP 变现 |
| MVP 7 天 | 与 `mvp_angle` 对齐的可交付 |
| Kill 条件 | 30 天内无索引 / 无点击 / SERP 被大站碾压等 |

提示词草稿：`prompts/waist_to_product.md`。  
可与现有 **周决策卡** schema（`docs/decision-card-schema.md`）对接：发现层 `pursue` 候选挂 `linked_card_id`，但 **verdict 独立**，不自动 Go。

---

## 本仓脚本（stub）

```bash
# 阶段 0 mock：种子 → exports/waist_expanded.json
python -m pipeline.waist_expand --seeds config/seeds.yaml --out exports/waist_expanded.json

# 串联说明 + mock 路径（不调用真实 Semrush）
python -m pipeline.run_waist_discovery --mock
```

- `pipeline/waist_expand.py`：读 YAML 种子，写 expanded clusters JSON（mock 模板）。  
- `pipeline/run_waist_discovery.py`：按阶段打印 checklist / 注释，mock 时跳过外部 API。

---

## 最小可跑实验

### 无 Semrush key

1. 手工或 LLM mock 产出 `exports/waist_expanded.json`。  
2. 手工填 1–3 条 `candidates` 进 `data/waist_keywords.json`（`status: unverified`，band 描述，**禁止** 编造月搜）。  
3. `python scripts/build_public.py --no-sync-root`（若仅改 JSON）或完整 build 后本地 `python -m http.server --directory public`。  
4. 打开 `waist.html` 检查表格与 meta 栏目标位 **10–20**。

### 有 Playwright、无 Semrush

- 可先自动化 Trends **公开页** 抓 7d 飙升列表（选择器随 Google UI 变化需维护）。  
- **429 / 验证码**：降级为手工 + `trends_check.note` 记录失败原因。  
- 仍不在 JSON 写绝对搜索量。

### 有 Semrush（推荐立项路径）

- 仅导出 **United States** 数据库截图或 CSV，再填 `volume_band_note` / `kd_band_note`；满足证据门槛时可标 `verified`。

---

## 与现有管线的关系

| 模块 | 关系 |
|------|------|
| `run_daily.py` / `run_weekly.py` | 通用 Trends + 评分；**不**自动写 waist 池 |
| `week_decisions.json` | 每周 1 Go / 1 Watch / 1 Kill；**不被** waist 流水线覆盖 |
| `market_narratives.json` | 产品兴衰叙事；**不被**本流水线覆盖 |
| `scripts/build_public.py` | 发布前同步 `waist_keywords.json` 与静态页 |

---

## 参考

- 方法帖：<https://x.com/yanhua1010/status/2115296994289987695>  
- 腰部字段：`docs/waist-keywords-schema.md`
