# Demand Radar 实验 A · 周边机会卡（TrustMRR 锚点）

- **as_of 收入快照口径**：TrustMRR 公开页，**as_of 2026-10-30**（撰写日 2026-11-04 又用公开页复核；若与快照漂移已在卡内注明）
- **原则**：补位/周边，**不对打整站**；禁止完整 iOS 重做
- **用户栈偏好**：Python · Playwright · 爬虫 · Chrome 扩展 · Next/静态站 · SEO

## 推荐优先序（先看这个）

| 序 | 锚点 | 周边机会 | 优先级 | 为何 |
|---|---|---|---|---|
| 1 | HiddenRoles | ATS careers URL 检测器 + 自建 watchlist 教程站 | **Go** | 与 Playwright/爬虫最贴；不碰大盘职位聚合；SERP 仍有低 DR 教程/工具位 |
| 2 | Savebase | X/社媒 bookmarks → Markdown/MCP 模板包 | **Go** | 不做全平台收藏 SaaS；模板+$19 买断贴合栈；MCP 信息意图升温 |
| 3 | ihatepdf.cv | PDF 元数据剥离 + 发送前隐私清单站 | **Watch→可升 Go** | 单点工具+SEO 可做，但 strip metadata / redact 已有 Scrubbr 等；先测主词点击再升 |
| 4 | ClipUtils | Discord/Email 精确体积视频压缩落地页簇 | **Watch** | 本地 ffmpeg.wasm 红海；只做精确意图页+Ads，不做 28+ 套件 |
| 5 | FlipScan | 转售「已售 comps + 费率」静态计算器/清单（非扫描 App） | **Skip（本周）** | iOS 扫描与 listing alert 簇拥挤；费率计算器也被多家占；等更窄 SKU 词再 Watch |

**建议你下周只做 1 个 MVP**：HiddenRoles 周边 —— **ATS Careers Detector + Greenhouse/Lever/Ashby 公开 API 告警教程站（静态/Next + 可选 Playwright 巡检脚本）**。

---

## 卡 1 · HiddenRoles 周边 · ATS Careers Detector（Go）

### 锚点产品
- **HiddenRoles**（https://hiddenroles.co/）— 从公司官网招聘页聚合「未上 LinkedIn/Indeed」的职位，让求职者直接投递。
- **公开收入信号（TrustMRR 快照，as_of 2026-10-30）**：https://trustmrr.com/startup/bestjobs-hq — 近 30 天收入约 **$26.8k**（页面标题级信号）；DR 极低（公开页约 1）。撰写日复核仍指向同一 slug。

### 周边机会（非克隆）
不做又一个职位大盘。补 **「已知目标公司名单」求职者** 的一步：粘贴 careers URL → **识别 ATS（Greenhouse / Lever / Ashby / Workday…）** → 给出公开 jobs JSON 端点与「如何自建邮件告警」清单；可选轻量 watchlist（≤20 家公司）。

### 主词 + 支撑词
- **主词**：`which ATS does this company use`
- **支撑词**：`greenhouse job board api` · `track company career page alerts` · `lever careers page json`

### 付费/商业意图证据
- **已见**：同簇付费产品存在（JobTailor、Job Board Watcher、PageCrawl 博客推监控、WorkWay Pro ~$3.99、JobBeacon Pro ~$8）——说明「盯公司 careers」愿意付钱。
- **已见**：HiddenRoles 自身以 Whop 验证流水，证明「避开大板」叙事有付费池。
- **推测**：免费检测器 → 邮件 watchlist $9–15/mo 可转化；转化率未验证。

### SERP / 缺口
- 权威/半权威：Greenhouse 官方 MyGreenhouse 告警、PageCrawl 长文、JobTailor 产品页。
- **可插**：DEV 教程文、GitHub Pages ATS checker（低 DR）仍靠前；缺「粘贴 URL → 一键检出 + 复制 API URL + 自建 cron 模板」的**工具型落地页**。对比/清单页空间仍在。

### 变现路径
优先：**Ads + 后续 $9–15/mo watchlist**；备选 Affiliate（通用网页变更监控）+ **$19 模板包**（Playwright 巡检脚本）。

### 7 天 MVP
1. Next/静态站：检测器（URL 规则 + 可选 fetch 公开 JSON）
2. 3–5 篇英文 SEO：Greenhouse/Lever/Ashby API 对照、自建 alert、Workday 限制说明
3. GitHub 公开 `watchlist.yml` + Python/Playwright 示例 cron（不做成重 SaaS）
4. IndexNow/GSC；禁止做全网职位爬虫产品

### Kill 理由
若 30 天内主词无展示/点击，或必须变成「全网职位聚合」才能获客 → Kill（退化成对打 HiddenRoles）。

### 30 天成败标准
- ≥8 个可索引页上线；GSC 展示 ≥800 **或** 点击 ≥40
- 检测器 UV ≥250；邮件 waitlist ≥30 **或** 付费意向 ≥5
- 外链/社区提及 ≥2（DEV/Reddit/HN 皆可）

### 相对优先级
**Go**（五卡第一；下周唯一建议开工项）

---

## 卡 2 · Savebase 周边 · Bookmarks → MCP 模板包（Go）

### 锚点产品
- **Savebase**（https://savebase.space/）— 多平台（约 11 个社媒）收藏库 + 文件夹/标签/提醒，并提供 **MCP** 供 ChatGPT/Claude/Cursor 查询个人收藏。
- **公开收入信号（TrustMRR 快照，as_of 2026-10-30）**：https://trustmrr.com/startup/savebase — 近 30 天约 **$682**，MRR 公开值较低（撰写日页约 $62 MRR / 8 订）→ **增长早期、叙事强于绝对 MRR**；免费档 **已见**：100 social bookmarks / 2 平台。

### 周边机会（非克隆）
不做「再造多平台收藏 SaaS」。补 **已有大量 X/浏览器书签、想喂给 AI 助手** 的开发者/研究者：一键导出 → 本地 Markdown/SQLite → **现成 MCP server 模板**。

### 主词 + 支撑词
- **主词**：`chatgpt mcp bookmarks`
- **支撑词**：`export twitter bookmarks` · `claude mcp bookmark server` · `x bookmarks to markdown`

### 付费/商业意图证据
- **已见**：Savebase 推 MCP Plugin；ContextBolt 博文教 ChatGPT 接 bookmarks MCP；TweetsMash 等提供 X bookmarks MCP 文档。
- **已见**：Savebase Free→Pro 升级墙（平台数/数量）。
- **推测**：$19–29 买断模板对「不想再订一份 SaaS」的开发者成立。

### SERP / 缺口
- 前排多为产品博文与 GitHub README（x-bookmarks-mcp、xsh），权威媒体少。
- **可插**：面向小白的「10 分钟接通 ChatGPT Developer Mode」图文站 + 可下载模板；对比「SaaS MCP vs 自建本地 MCP」清单页 DR 要求不高。

### 变现路径
优先：**$19–29 模板包/买断**（Gumroad/Lemon）；备选 Ads；不做月费除非加托管。

### 7 天 MVP
1. Chrome 扩展 MVP：导出当前平台书签/已打开收藏页为 JSON/MD（先 X + 浏览器 bookmarks）
2. 附赠 Python MCP server 脚手架（stdio）
3. 静态教程站 5 URL；禁止做 11 平台同步后端

### Kill 理由
若 X/API 政策使导出不稳定且无浏览器书签备路径；或 30 天模板 0 销售且教程无点击。

### 30 天成败标准
- 教程站点击 ≥60 或展示 ≥1,000
- 模板销售 ≥8 份 **或** GitHub star/fork ≥25 + 邮件询价 ≥10
- 付费页 CVR 可计算（访购）

### 相对优先级
**Go**（五卡第二；若只做一张则让位 HiddenRoles）

---

## 卡 3 · ihatepdf.cv 周边 · PDF 元数据剥离隐私清单（Watch）

### 锚点产品
- **ihatepdf.cv**（https://ihatepdf.cv/）— 隐私优先、浏览器本地 PDF 工具箱（合并/压缩/编辑/OCR 等），强调无水印、不上传。
- **公开收入信号（TrustMRR 快照，as_of 2026-10-30）**：https://trustmrr.com/startup/ihatepdf-cv — 历史收入约 **$1.3k** 量级；撰写日页约 all-time **$1,344**、MRR **~$896**（订户少、客单/计量可能波动，以快照+页面为准）。定价叙事以 **Free** 为主（**已见**）。

### 周边机会（非克隆）
不做 60+ 工具全集。补 **发简历/合同前** 人群：本地 **Strip PDF metadata / 检查遗留批注与隐藏层** +「发送前隐私清单」SEO。

### 主词 + 支撑词
- **主词**：`remove metadata from pdf`
- **支撑词**：`strip pdf metadata online` · `pdf privacy checklist before sending` · `exifr pdf author remove`

### 付费/商业意图证据
- **已见**：ihatepdf 以隐私/无水印打 iLovePDF/Smallpdf；同类 Scrubbr、VeriRedact 走付费/专业验证。
- **推测**：Ads RPM 尚可；Pro 检测报告 $9–15 买断可测。

### SERP / 缺口
- 「compress pdf to 2mb / visa」已被 KBPDF、LiteDoc、findmyvisa 等占较多。
- **相对更好插**：metadata/privacy checklist + 本地小工具；Scrubbr 等存在但对比/清单/「求职投递场景」长尾仍稀。

### 变现路径
**Ads** 为主；备选 **$9 买断**「批量清理+报告」。

### 7 天 MVP
静态/Next + pdf-lib/pdfjs：上传本地剥离 Producer/Author/XMP；3–4 篇投递/律师/设计师场景 SEO。禁止上全套编辑器。

### Kill 理由
主词被大站+Scrubbr 锁死前三且 30 天无点击；或用户期望「完整 redact 认证」导致支持成本爆。

### 30 天成败标准
展示 ≥1,200 或点击 ≥50；工具 UV ≥400；若 Ads RPM×点击无法覆盖域名/时间 → 保持 Watch 不升。

### 相对优先级
**Watch**（证据够但红海边缘；HiddenRoles/Savebase 之后再动）

---

## 卡 4 · ClipUtils 周边 · Discord/Email 精确体积压缩页（Watch）

### 锚点产品
- **ClipUtils**（https://cliputils.com/）— 浏览器端 28+/32 音视频图工具（含 ffmpeg.wasm 与部分 AI），**在售**。
- **公开收入信号（TrustMRR 快照，as_of 2026-10-30）**：https://trustmrr.com/startup/cliputils — 近 30 天约 **$408**，MRR 约 **$333** / ~29 订；**已见** Freemium + Pro（美国约 $2.99 档位文案）+ 赞助位。

### 周边机会（非克隆）
不做工具超市。只切 **「压到 Discord 10MB / Email 25MB」** 精确意图落地页 + 本地压缩（单工具），用 SEO 吃长尾，不碰字幕/配音大模型。

### 主词 + 支撑词
- **主词**：`compress video for discord 10mb`
- **支撑词**：`compress video to 25mb email` · `browser video compressor no upload` · `ffmpeg wasm compress to size`

### 付费/商业意图证据
- **已见**：ClipUtils「Compress to Size」、Slimcast/ShrinkVideo 等同形态；Pro/赞助说明流量可广告变现。
- **推测**：纯 Ads 站可行；订阅难（免费预期强）。

### SERP / 缺口
- 「compress video without uploading」已被多家新站占满，**权威媒体少、同质化高**。
- **缺口窄**：更具体的 Discord/WhatsApp/LMS 体积词 + 中立「如何用 DevTools 验证未上传」清单；可插但壁垒弱。

### 变现路径
**Ads**；备选 $9 批量队列买断。

### 7 天 MVP
1 个 Next 工具页 + 4 个意图镜像页（Discord/Email/WhatsApp/Classroom）；ffmpeg.wasm；不做 AI 套件。

### Kill 理由
CPC/RPM 过低或被 Chrome 内存限制差评淹没；一旦要靠 AI 功能续命 → Kill（超出周边）。

### 30 天成败标准
工具 UV ≥800；Ads 可估 RPM；GSC 主词有展示。达不到则 Skip 扩词。

### 相对优先级
**Watch**

---

## 卡 5 · FlipScan 周边 · 费率/利润静态计算器（Skip 本周）

### 锚点产品
- **FlipScan**（https://flipscan.app/）— iOS 转售估价扫描（拍照估转售价、验假、库存）。
- **公开收入信号（TrustMRR 快照，as_of 2026-10-30）**：https://trustmrr.com/startup/flipscan — MRR 约 **$300+**（撰写日页约 **$315 MRR**、RevenueCat 验证、增长叙事）；**已见** App Store Pro Monthly **$14.99** / Yearly **$49.99**（官网 FAQ 另写过 $9.99 档，以商店/TrustMRR 为准）。同簇还有 marketplace listing alert（anonymous-startup-40）。

### 周边机会（非克隆）
**禁止重做 iOS 扫描。** 理论上可做：eBay final value fee + 运费利润静态计算器、或「已售 comps 搜索技巧」内容站。但——

### 主词 + 支撑词
- **主词**：`ebay final value fee calculator`
- **支撑词**：`thrift flip profit calculator` · `ebay sold comps` · `reseller fee calculator 2026`

### 付费/商业意图证据
- **已见**：FlipScan/Underpriced/Pocket Pricer/FlipIQ 等付费或免费获客工具证明转售者付费意愿。
- **已见**：费率计算器站大量存在（Seller Fee Kit、Calcilo、Feeculate…）。

### SERP / 缺口
- 费率计算器与 AI scanner **均拥挤**；listing alert 亦有产品。
- **缺口不足以本周开工**：除非做极窄品类（如「Pokémon card eBay fee + grading cost」）——需另开词研。

### 变现路径
理论：Ads / Affiliate（电商工具）；实操建议暂不投入。

### 7 天 MVP
**不启动。** 若强行：仅静态费率表 + 1 个计算器页验证流量（≤2 天探针），不做扩展、不做扫描。

### Kill 理由
（本周直接 Skip）与「禁完整 iOS 重做」一致；web 计算器红海且难形成订阅。

### 30 天成败标准
不适用；若探针页 14 天点击 <20 → 确认 Skip。

### 相对优先级
**Skip**

---

## 附录 · 证据备注
- TrustMRR 数字随验证源波动；卡内以 **as_of 2026-10-30 快照 + 撰写日公开页复核** 双记。
- SERP 为 WebSearch 快扫，**非**完整前 10 HTML/DR 表；KD/量级未接 Semrush 本轮 → 绝对搜索量标未验证。
- 币圈未纳入。