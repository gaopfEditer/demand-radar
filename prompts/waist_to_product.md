# 腰部词 · 阶段 5 需求串 → 产品包（LLM）

输入：已通过 Semrush/SERP 粗筛的 **demand chain**（主词 + 支撑词 + pain + 变现暗示）。  
输出：7 天可执行的建站包；可对接周决策卡字段，但 **不自动** 写入 `week_decisions.json`。

## 输入模板

```json
{
  "keyword": "primary english keyword",
  "support_keywords": ["..."],
  "why": "one line",
  "mvp_angle": "existing angle from waist_keywords.json",
  "target_rank_band": "10-20",
  "verdict_hint": "pursue | watch | skip"
}
```

## 输出 JSON schema

```json
{
  "site_type": "comparison_hub | tool | calculator | tutorial",
  "core_urls": [
    { "path": "/...", "title": "...", "intent": "..." }
  ],
  "monetization_path": "affiliate | lead | ads | saas_trial | mixed",
  "mvp_7d": ["day1 task", "..."],
  "kill_conditions": ["measurable exit criteria"],
  "optional_linked_card_fields": {
    "evidence_bullets": ["..."],
    "risk_notes": ["..."]
  }
}
```

## 约束

- 不要编造流量、收入、排名保证。  
- Kill 条件必须可观测（索引、点击、SERP 结构变化）。  
- 与 `docs/decision-card-schema.md` 对齐时，仅作 **草稿**，人工确认后再进周卡。
