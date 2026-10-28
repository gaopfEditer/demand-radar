# Demand Radar — 海外软件开发需求发现系统（MVP）

面向海外英文市场的需求情报 MVP：多源采集 → 标准化/聚类/评分 →（可选）ChatGPT 方案 → Streamlit 看板 → 人工验证回写。

**在线结果看板**（**本周决策卡**为主 · 原始机会表 / 关键词为辅）：<https://gaopfEditer.github.io/demand-radar/> · 本地运维与验证请用下方 Streamlit。

> **原则**：采集程序拿证据，评分规则引擎初筛，AI 做综合判断。不要让大模型只凭 Trends 热度决定做什么产品。

## 功能覆盖（第一版）

1. **多源采集**：Google Trends + Google Autocomplete，统一导出 JSON/CSV  
2. **SQLite 历史**：`seeds / keywords / snapshots / evidence / opportunities / reports / validations`（snapshots 只追加）  
3. **聚类与评分**：需求 25% + 变现 20% + 竞争可进入 20% + 开发可行性 20% + 证据质量 15%；0–100 分；缺数据标 `pending` / 降置信度，**不假装低竞争**  
4. **ChatGPT 方案**：`prompts/opportunity_screening.md` + `prompts/project_plan.md`；`ai/client.py` 可替换；无 API key 时写 stub 报告  
5. **Streamlit 看板**：总览 / 关键词 / 趋势 / 机会排行 / 报告 / 验证  
6. **人工验证闭环**：机会 `status` + `validations` 表可写  

**明确不做**：Ahrefs/Semrush 全量、Reddit/HN 全爬（留 stub）、自动建站、自动买广告、币圈种子、多 Agent。

## 环境要求

- Python 3.11+（推荐 3.11–3.13）
- 网络（访问 Google Suggest / Trends；失败会优雅降级）

## 安装

```bash
cd demand-radar   # 或本仓库根目录
python3 -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -r requirements.txt
```

若 `trendspyg` 安装失败或不可用，系统会依次尝试 `pytrends`（可选自行安装）→ Mock 降级，**整条管线不会崩**。

可选：

```bash
pip install pytrends   # Trends 备用适配器
```

## 配置

### 种子词

编辑 `config/seeds.yaml`（已含 `ai_development / developer_tools / online_tools / micro_saas / seo_tools`，**不含币圈**）。

### API Key（可选，AI 报告用）

```bash
export OPENAI_API_KEY=sk-...
# 或
export DEMAND_RADAR_API_KEY=sk-...
# 可选自定义兼容网关
export OPENAI_BASE_URL=https://api.openai.com/v1
export DEMAND_RADAR_MODEL=gpt-4o-mini
```

未设置 key 时：规则评分与导出照常；AI 阶段写入 `exports/reports/screening_stub.json` 等 stub，说明缺 key。

### 数据库

默认路径：`data/demand_radar.db`（首次运行自动建表）。

## 如何运行

### 每日采集 + 评分 + 导出

```bash
source .venv/bin/activate
python run_daily.py
```

常用参数：

```bash
# 小批量冒烟（限制种子数）
python run_daily.py --limit-seeds 5

# Trends 强制走 mock（限流/离线演示完整路径）
python run_daily.py --limit-seeds 5 --force-mock-trends

# 跳过 AI / Suggest
python run_daily.py --skip-ai --limit-seeds 8
```

产物：

- `exports/keywords.csv`
- `exports/dev_site_demand.json`（交换格式）
- SQLite：`data/demand_radar.db`
- `public/data/*.json`（若 `build_public` 成功，供 GitHub Pages 静态站）

每日管线结束时会自动调用 `scripts/build_public.py`；也可手动：

```bash
python scripts/build_public.py
```

### 每周多窗口 Trends

```bash
python run_weekly.py --limit-seeds 5
# 窗口：7d / 3m / 12m；可对 Top N 做深度方案（无 key 则 stub）
```

### 看板

```bash
streamlit run dashboard/app.py
```

在「项目验证」页可写入 `validations` 并更新 opportunity status。

### 静态预览（GitHub Pages）

**GitHub Pages 首页 = 本周决策看板**（`index.html` 加载 `data/week_decisions.json`，展示 Go / Watch / Kill 三张卡）。原始机会评分表在 `opportunities.html`；字段规格见 `docs/decision-card-schema.md`。

**新增下一周决策卡：**

1. 在 `docs/` 撰写 `week-decision-cards-YYYY-MM-DD.md`（参照 schema，每批 1 Go · 1 Watch · 1 Kill）。
2. 更新 `data/week_decisions.json`（UI 读取的结构化数据，勿编造未验证主张）。
3. 运行 `python scripts/build_public.py`（同步 `week_decisions.json` 到 `public/data/`，并把 `public/` 下 HTML/静态资源复制到仓库根目录）。

根目录与 `public/` 双份 HTML/数据供 branch Pages 与 Actions 部署；`.nojekyll` 避免 Jekyll 覆盖静态站。

- **预期地址**：<https://gaopfEditer.github.io/demand-radar/>
- **首次启用**：GitHub 仓库 **Settings → Pages → Build and deployment → Source** 选择 **GitHub Actions**（不要选 “Deploy from branch”）。`main` 推送后由 `.github/workflows/deploy-pages.yml` 发布 `public/` 目录。
- 本地预览：先 `python scripts/build_public.py`，再用任意静态服务器打开 `public/`（例如 `python -m http.server 8080 --directory public`）。

### 测试

```bash
pytest -q
```

## 评分说明（摘要）

\[
S=\sum_i w_i \frac{r_i}{5}\times 100
\]

| 维度 | 权重 | 说明 |
|------|------|------|
| 需求 | 25% | Trends 相对热度、Rising/Breakout、Suggest 覆盖 |
| 变现 | 20% | 商业/交易意图、API/pricing/alternative 等修饰 |
| 竞争可进入 | 20% | **无 KD/SERP 时标 pending**，不伪造低竞争 |
| 开发可行性 | 20% | 工具站 vs AI Agent 等启发式 |
| 证据质量 | 15% | 独立来源数 |

档位：80+ 优先研究；65–79 候选；50–64 观察；&lt;50 暂缓。

## 局限（必读）

1. **Google Trends ≠ 搜索量**：数值是查询集合内归一化相对兴趣。  
2. **Autocomplete ≠ 需求量/付费意愿**：只证明存在相关查询表达。  
3. **无 Ahrefs/Keyword Planner**：竞争与月搜多为 `pending`，置信度会下降。  
4. **Trends 非官方接口**可能限流或失效；adapters 会降级到 mock，结果带 `degraded` 标记。  
5. **AI 不会也不应**仅凭热度拍板；缺 key 时跳过并写 stub。

## 目录

```
├── config/seeds.yaml
├── collectors/          # trends / autocomplete / stubs
├── pipeline/            # normalize / dedupe / cluster / score
├── ai/                  # client / screening / deep_research
├── prompts/
├── schemas/
├── storage/
├── dashboard/app.py
├── docs/                # 周决策卡 Markdown + schema
├── public/              # GitHub Pages 静态 UI（Actions 部署源）
├── scripts/build_public.py
├── exports/
├── tests/
├── run_daily.py
├── run_weekly.py
├── requirements.txt
└── README.md
```

## 下一步建议

- 接入 Google Ads Keyword Planner（真实月搜/广告竞争）  
- 为 Top 机会补 SERP / 竞品页证据  
- 实现 `communities.py`（Reddit/HN 抽样，非全爬）  
- 根据 `validations` 回写校准评分权重  

---

本地 MVP · 证据优先 · 人工决策闭环
