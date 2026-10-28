# 出海 SEO 周决策卡 · 2026-10-28（Asia/Hong_Kong）

> 角色：出海 SEO 需求研究员  
> 用户栈：Python / Playwright / 浏览器扩展 / Next.js；主线找词建站变现，不做地板价接单；**币圈不进评分**  
> 本批判定分布：**1 Go · 1 Watch · 1 Kill**  
> 线索源含清洗后的 demand-radar `keywords.json`；**未**把脏 Suggest / 笼统 `vs code` / `code ai` / 纯 Cursor·Claude 品牌词当 Go 主词。

---

## 一览

| 判定 | 卡标题 | 主词 |
|------|--------|------|
| **Go** | 云浏览器基础设施对比站 | `browserbase alternatives` |
| **Watch** | AI 代码评审工具簇 | `best ai code review tools` |
| **Kill** | Cursor 品牌导航红海 | `cursor ai` |

---

## Card 1 · Go · 云浏览器基础设施对比站

**card_id:** `2026-W44-go-browserbase-alternatives`  
**as_of:** 2026-10-28（Asia/Hong_Kong）

### 1. 判定
**Go**

### 2. 主词 + 5 个清洗后支撑词
- **主词：** `browserbase alternatives`
- **支撑词：**
  1. `cloud browser automation pricing`
  2. `steel.dev vs browserbase`
  3. `hyperbrowser pricing`
  4. `playwright cloud browser`
  5. `browserless vs browserbase`

### 3. 谁在搜、谁付钱
- **谁在搜：** 做 AI Agent / 爬虫 / 自动化的独立开发者与小团队；已用 Playwright/Puppeteer，想把本机 Chrome 换成托管会话；被 Browserbase 代理带宽账单或 6 小时会话上限卡住后搜「alternatives」。
- **意图：** 商业调研（对比 / 定价 / 选型），非纯百科。
- **谁付钱：** 团队 SaaS 预算（$20–$250+/月 基础设施）；愿意点 Affiliate / 注册返佣；后续也愿意为「独立基准测试」小工具付费或订阅。
- **买家画像：** 英文市场（优先 US）的 agent infra 买家，技术向，能读定价表与 CDP 文档。

### 4. 变现路径（1 主 1 备）
- **主：Affiliate / 合作伙伴返佣 + 对比内容站**  
  对接 Browserbase、Steel、Kernel、Hyperbrowser、Browser Use、Anchor、Firecrawl 等公开合作/联盟；Next.js 内容站承接对比页与定价页。  
  **配栈理由：** 用户已精通 Playwright，能自己写「真实会话基准」而不是抄厂商稿，信任度高于纯 SEO 站。
- **备：小 SaaS / 工具页**  
  「云浏览器成本计算器」「Playwright → connectOverCDP 一键迁移片段生成器」「代理 GB 账单估算器」。  
  **配栈理由：** Python 抓公开价表 + Next.js 前端；扩展可选做「本机 vs 云会话」调试面板。

### 5. SERP 缺口（基于真实打开的竞品页）
前 10 几乎被**厂商自推对比文**占满（Deck 推 Deck、Kernel 推 Kernel、Anchor 推 Anchor），独立站要么缺真实基准、要么更新慢；**缺口 = 无厂商立场、带可复现 Playwright 基准与「按页成本」算术的对比枢纽**。  
引用（本轮已打开）：
- https://deck.co/blog/4-browserbase-alternatives-to-consider-in-2026 （厂商向，2026-05 发 / 2026-10 改）
- https://www.kernel.sh/ai-library/browserbase-alternatives-2026 （厂商向，含 browserbench 数字，2026-08-14）
- https://webscraping.cc/blog/browserbase-alternatives/ （较独立，强调代理 $/GB 算术，2026-07；价表核对至 2026-08/10）
- https://browser-use.com/posts/best-browser-infrastructure-for-ai-agents （厂商向 7 家价表对比）

### 6. 7 天 MVP
- **站点类型：** Next.js 英文对比站（对比枢纽 + 定价算术 + Playwright 迁移教程）
- **首批 URL 标题（10）：**
  1. Browserbase Alternatives (2026): Independent Comparison
  2. Browserbase vs Steel vs Kernel: Pricing & Cold Start
  3. Cloud Browser Automation Pricing Calculator
  4. Playwright on Browserbase / Steel / Kernel (CDP Connect Guide)
  5. Browserless vs Browserbase for Existing Playwright Scripts
  6. Hyperbrowser Pricing Explained (Credits, Stealth, Concurrent)
  7. When You Don’t Need a Cloud Browser (Firecrawl / Scraping API Instead)
  8. Browserbase Proxy Bandwidth Cost per Page (Math)
  9. Best Self-Hosted Browser API: Steel & Open-Source Options
  10. Migrate Stagehand Scripts Off Browserbase (Checklist)

### 7. 不做/降级理由 + 30 天成败标准
- **不做/降级：** 不做「通用 web scraping 大而全目录」；不做币圈采集；不做纯 Cursor/Claude 品牌词站；首月不做重代理自营（合规与成本高）。
- **30 天成败（可量化）：**
  - 上线 ≥10 个索引页；GSC 展示 ≥1,000 或点击 ≥50（以先到者为参考）；
  - ≥3 个外链或社区引用（Reddit / IH / GitHub gist 均可）；
  - Affiliate 或邮件询盘 ≥5 次，或计算器工具 UV ≥300。

### A. 产品增长趋势
**增量（已验证事实）：**
- Browserbase：2025-06-18 宣布 **$40M Series B**（Notable Capital），并降价、扩并发——https://browserbase.com/blog/series-b-and-beyond/
- Firecrawl：公开博文称 Series A 前一年 **15x** 增长、GitHub stars 过 48k（2025-08）；后续报道称 Series B 与开发者规模继续放大——https://www.firecrawl.dev/blog/firecrawl-v2-series-a-announcement ；二级综述 https://partner-grow.beehiiv.com/p/firecrawl
- Creati.ai（2026-09）：Firecrawl 约 **1.86M** 月访（第三方估计）——https://creati.ai/ranking/september-2026/categories/ai-tools/coding-development/
- Product Hunt 类目「browser automation」2026-10-27 更新，Firecrawl / Browser Use / Browserbase 居前——https://www.producthunt.com/categories/browser-automation

**减量/停滞对照（已验证事实）：**
- Brandwave（全球英文品牌搜份额，截至 2026-09）：**Selenium** 份额从 2025-10 的 **26.5% → 13.3%**；**Cypress** **3.8% → 1.5%**——https://gobrandwave.com/demand/global-en/categories/browser-automation-tools
- Selenium IDE 唯一维护者 2025-03 声明 “**effectively dead**”——https://github.com/SeleniumHQ/selenium-ide/issues/1872

### B. 关键词增长趋势
- **市场：** Global 英文品牌搜（Brandwave）；主词 US Google Trends **本轮未直接打开 UI → 标未验证**
- **时间窗：** 2025-10 → 2026-09
- **指标类型：** **相对份额（Share of Search）**，非绝对搜索量
- **信号：**
  - `Browser Use`：份额 **10.3% → 20.2%**（升至第 2）——同上 Brandwave URL · **verified**
  - `Playwright`：份额 **13% → 16.4%**（峰值曾到 20.3% @2026-06）· **verified**
  - `Selenium`：份额 **26.5% → 13.3%**（下降对照）· **verified**
  - 主词 `browserbase alternatives` 的 Google Trends 相对曲线：**未验证**（本轮 Trends/Google SERP 抓取遇 429）；替代证据为 2026 年多篇「alternatives」长文密集上线（Deck / Kernel / webscraping.cc / Browser Use）

### C. 周边相关（≥5）
1. Browserbase vs Browser Use Cloud：何时用托管 Agent、何时只用 CDP 浏览器  
2. Stagehand vs 纯 Playwright：成本与可控性对比  
3. 云浏览器「按页真实成本」定价拆解页（browser-hour vs proxy-GB）  
4. Playwright MCP / Chrome DevTools MCP 与云浏览器联调教程  
5. 小工具：Cloud Browser Cost Calculator（输入并发、会话时长、代理 GB）  
6. 小工具：`launch()` → `connectOverCDP()` 迁移片段生成器  
7. Self-host Steel on Docker：成本 vs 托管对照清单  

**证据 vs 推测：** 融资/份额/竞品页结构 = 事实；「独立站 30 天可拿到 Affiliate 转化」= **推测**；主词绝对搜索量 = **未验证**。

---

## Card 2 · Watch · AI 代码评审工具簇

**card_id:** `2026-W44-watch-ai-code-review`  
**as_of:** 2026-10-28（Asia/Hong_Kong）

### 1. 判定
**Watch**

### 2. 主词 + 5 个清洗后支撑词
- **主词：** `best ai code review tools`
- **支撑词：**
  1. `coderabbit vs greptile`
  2. `coderabbit pricing`
  3. `greptile alternatives`
  4. `ai pull request review`
  5. `qodo vs coderabbit`

### 3. 谁在搜、谁付钱
- **谁在搜：** 工程经理 / Staff 工程师，为团队选 PR 机器人；被 AI 生成代码淹没后找「独立评审层」。
- **谁付钱：** B2B seat 订阅（公开价常见约 $12–$48/开发者/月量级，以各厂商定价页为准）；开源仓库常有免费档。
- **意图：** 强商业调研；决策周期长于云浏览器个人开发者。

### 4. 变现路径（1 主 1 备）
- **主：Affiliate / 合作内容 + 深度对比站**（CodeRabbit、Greptile、Qodo 等若有伙伴计划）。  
  **配栈理由：** Next.js 内容站可做；但用户栈（Playwright/扩展）**并非差异化壁垒**，故不升 Go。
- **备：开源评测脚手架 SaaS**（对同一批 PR 跑多家 reviewer 并输出 diff 报告）。  
  **配栈理由：** Python 编排 + GitHub App；工作量大，适合观察 1–2 个季度再决定。

### 5. SERP 缺口
前排多为**厂商内容库与新站对比文**互相引战（Greptile 官博贬 CodeRabbit、第三方列表站跟风）；缺口是「可复现的盲测协议 + 固定 OSS PR 集」，但做出权威基准成本高、且头部已有 Martian 等第三方榜。  
引用：
- https://repowise.dev/blog/comparisons/best-ai-code-review-tools
- https://www.greptile.com/content-library/best-ai-code-review-tools
- https://levelop.dev/blog/best-ai-code-review-tools-2026-coderabbit-greptile-qodo-compared
- https://www.greptile.com/content-library/greptile-martian-code-review-benchmark

### 6. 7 天 MVP（若从 Watch 试水）
- **站点类型：** 轻量对比博客（不建重产品）
- **首批 URL 标题（8）：**
  1. Best AI Code Review Tools (2026): Who They’re For
  2. CodeRabbit vs Greptile: Precision vs Repo-Wide Context
  3. CodeRabbit Pricing Breakdown (Seats, Credits, OSS)
  4. Greptile Alternatives for GitLab / Bitbucket Teams
  5. AI Pull Request Review: Noise vs Signal Checklist
  6. Qodo vs CodeRabbit for Test Generation
  7. Self-Hosted AI Code Review (PR-Agent & On-Prem Options)
  8. How to Trial Two Reviewers on the Same 20 PRs

### 7. 不做/降级理由 + 30 天成败标准
- **为何 Watch 不 Go：** 品类已被 CodeRabbit（十亿级估值叙事）与多家 VC 厂商标注；内容军备竞赛强；与用户 Playwright 壁垒弱；Affiliate 佣金与 cookie 周期未核实（**未验证**）。
- **30 天观察标准：** 主词周均展示是否稳定上升；是否谈成 ≥1 个伙伴链接；自有盲测是否在 HN/Reddit 获得 ≥100 互动。达不到则保持 Watch 或降级。

### A. 产品增长趋势
**增量：**
- CodeRabbit：Business Wire（2026-08-12）宣布 **$143M Series C、估值 $1.5B**；称收入 YoY **>5x**；周审 PR **>200 万**；客户 **>17,000**——https://www.businesswire.com/news/home/20260812311754/en/CodeRabbit-Raises-%24143-Million-at-%241.5-Billion-Valuation-and-Introduces-Agentic-Change-Management
- 前一轮：$60M Series B @ $550M（TechCrunch 2025-09）——https://techcrunch.com/2025/09/16/coderabbit-raises-60m-valuing-the-2-year-old-ai-code-review-startup-at-550m/

**减量/停滞对照：**
- Creati.ai 2026-09：CodeRabbit 约 **1.00M** 月访，**环比 -2.21%**（第三方估计，非 Similarweb 原表；作「流量短期走平」弱信号）——https://creati.ai/ranking/september-2026/categories/ai-tools/coding-development/
- 同表 Cursor **21.50M** 但 **环比 -4.58%**——品牌巨头也在波动，说明「有融资 ≠ 内容站好做」。

### B. 关键词增长趋势
- **市场：** US 优先（品类全球工程英语）
- **时间窗：** 2025-09 → 2026-08（融资与评测密度窗口）
- **指标类型：** 相对/定性 rising（公开报道与对比文密度）；**Google Trends 数值未验证**
- **信号：** 「ai code review / coderabbit vs greptile」类商业调研文在 2026 密集出现（见上 SERP URL）→ 判定为 **簇级 rising（定性）**；绝对量 **未验证**。

### C. 周边相关（≥5）
1. CodeRabbit vs GitHub Copilot code review（捆绑账单位）  
2. Cursor Bugbot 是否替代独立 reviewer  
3. AI code review ROI 计算器（seat × 噪音率 × 工程师时薪）  
4. 安全向：Semgrep / Sonar 与 LLM reviewer 如何叠放  
5. 开源维护者：免费档额度对比页  
6. 小工具：同一 PR 的多机器人评论去重演示  
7. 「Agentic Change Management」词条解释页（蹭 CodeRabbit 新叙事但保持中立）

**证据 vs 推测：** 融资与客户数来自新闻稿 = 事实（公司自述）；「indie 对比站难出头」= **合理推测**；Trends 曲线 = **未验证**。

---

## Card 3 · Kill · Cursor 品牌导航红海（示范）

**card_id:** `2026-W44-kill-cursor-ai`  
**as_of:** 2026-10-28（Asia/Hong_Kong）

### 1. 判定
**Kill**（对「以 `cursor ai` 做 Go 主词建站变现」；可留作反面教材）

### 2. 主词 + 5 个清洗后支撑词
- **主词：** `cursor ai`（品牌导航意图）
- **支撑词（说明为何脏/不可做 Go）：**
  1. `cursor ai download`（官网意图）
  2. `cursor ai pricing`（官网定价页截流极难）
  3. `cursor ai free for students`（**脏 Suggest** 典型）
  4. `what is cursor ai`（被官网与巨头解释页占满）
  5. `cursor ai alternative`（表面商业，实则仍被品牌与大媒体绞杀）

> 注：demand-radar `keywords.json` 中大量 `cursor ai free*` / 城市乱入 / `claude code free for students` 均属清洗对象，**禁止当主词**。

### 3. 谁在搜、谁付钱
- **谁在搜：** 已听说 Cursor 的开发者，要下载、登录、看价格 → **导航/交易向品牌词**。
- **谁付钱：** 付钱给 **Cursor 公司**，不是给你的内容站；广告主 CPC 极高，联盟空间通常被官方与大媒体占住。

### 4. 变现路径（1 主 1 备）——为何仍 Kill
- **主（理论）：** 品牌词 SEO → 广告/联盟。  
- **备（理论）：** 「Cursor alternatives」列表站。  
- **配栈：** 即使用户会 Next.js，也**打不赢**官网权威与品牌广告；与「找词建站」主线的可防守差异无关 → **Kill**。

### 5. SERP 缺口
**没有可防守缺口**：`cursor` / `cursor ai` / `cursor pricing` 一类查询由 **cursor.com 官网与品牌资产**主导；第三方综述无法稳定截走导航意图。  
引用/旁证：
- Creati 流量榜 Cursor 仍处编码工具头部（约 21.5M 月访估计，2026-09）——https://creati.ai/ranking/september-2026/categories/ai-tools/coding-development/
- 公开综述称 cursor.com 在核心品牌词上居首（第三方流量站）——https://probedex.ai/domain/cursor.com
- demand-radar 线索里 `cursor ai` rising，但 rising ≠ 可做 Go

### 6. 7 天 MVP
**不建议启动。** 若仅作归档示例，不列可执行 URL 清单；把精力转到 Go 卡。

### 7. 不做/降级理由 + 30 天成败标准
- **Kill 理由：** 纯品牌红海；脏 Suggest 污染词根；变现不归内容站；与 Playwright 差异化无关。
- **成败标准：** 不适用；若误开站，30 天内品牌词无法进前 10 即确认 Kill。

### A. 产品增长趋势
**增量（品牌本身，非你的机会）：** Cursor 仍是头部 AI IDE 流量资产（Creati 上表）。  
**减量/停滞对照：** 同表 Cursor 月访 **环比 -4.58%**（2026-09）——即使品牌走平/微降，**也不构成 indie SEO Go 条件**。  
旧工具对照：Selenium IDE “effectively dead”（见 Go 卡链接）说明「旧编辑器生态」在让位，但让位赢家是 Playwright/官方 IDE，不是山寨 Cursor 内容站。

### B. 关键词增长趋势
- **市场：** US / Global  
- **时间窗：** 2025–2026（定性）  
- **指标类型：** demand-radar 标注 `cursor ai` **is_rising**（相对 rising 标签）——来源 https://gaopfEditer.github.io/demand-radar/data/keywords.json  
- **结论：** rising 的品牌导航词 → **Kill 示范**，不是 Go。Google Trends 绝对值 **未验证**。

### C. 周边相关（≥5）——仅作「不要做」清单
1. ~~cursor ai free for students~~（脏）  
2. ~~cursor ai download mirror~~（侵权/钓鱼风险）  
3. ~~unofficial cursor ai online~~（误导导航）  
4. cursor vs windsurf（红海对比，可 Watch 观察但本批不立项）  
5. cursor api pricing（官网意图）  
6. 「从 Cursor 迁出到 Playwright+Agent 工作流」（可将来并入 Go 卡教程，不单独立项品牌站）

**证据 vs 推测：** 「官网垄断导航 SERP」有第三方旁证但仍属 **强推测+行业常识**；具体前 10 URL 截图本轮因 Google 429 **未逐条抓取** → 已在证据强度中标明。

---

## 本批方法与局限

| 项 | 状态 |
|----|------|
| 竞品长文 WebFetch | 已完成（Deck / Kernel / webscraping.cc / Browserbase 融资博文 / Business Wire / Brandwave / Creati / Selenium IDE issue） |
| Google Trends 官方 UI/API | **未验证**（429）；用 Brandwave 相对份额替代 |
| Google 前 10 完整 HTML | **未验证**（429）；用 WebSearch 结果集 + 打开的排名页代替 |
| Similarweb 原表登录数据 | **未使用**；Creati 等为第三方估计，已标注 |
| 币圈 | 未纳入任何评分 |

---

## 给执行者的下一动作（Go 卡）

1. 注册域名（建议品牌中性：如 `cloudbrowser.compare` / `agentbrowser.dev` 一类，具体自定）。  
2. Next.js 脚手架 + 首周 10 URL 中的前 4 篇（Alternatives 枢纽、三家对比、定价计算器、CDP 教程）。  
3. 用自有 Playwright 脚本跑一版「创建→load→release」延迟，公开方法与原始 JSON（差异化关键）。  
4. 平行申请 2–3 家云浏览器 Affiliate。  
5. Watch 卡仅加书签，双周复盘 CodeRabbit/Greptile 伙伴政策后再议。
