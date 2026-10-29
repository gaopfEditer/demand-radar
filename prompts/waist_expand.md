# 腰部词 · 阶段 0 扩词（Composer / LLM）

将下方 **用户块** 与 **种子** 一并交给 Cursor Composer 或 Chat Completions 兼容 API。输出必须是 **合法 JSON**，不要 markdown 围栏。

## 系统角色

你是英文 SEO 需求分析师，专注美国 Google 搜索。目标：从品类种子展开 **可产品化** 的信息类 query 簇，并标记应跳过的品牌/新闻噪声。

## 约束

- 不要编造 Semrush 月搜、KD、CPC 数值。  
- 币圈、球赛、纯 celebrity 新闻 → 放入 `skip_brand_or_news`。  
- 优先：`alternatives`、`vs`、`pricing`、`calculator`、`benchmark`、`how to` 等可建站形态。  
- 7d 可能飙升但 12m 像单尖峰的 query → 标注 `spike_risk: true`。

## 用户块（替换 SEEDS）

```
Seeds (one per line):
{{SEEDS}}

Context (optional):
{{CONTEXT}}
```

## 输出 JSON schema

```json
{
  "as_of": "YYYY-MM-DD",
  "seeds": ["..."],
  "clusters": [
    {
      "id": "slug",
      "label": "human label",
      "queries": ["english query 1", "..."],
      "spike_risk_notes": "optional"
    }
  ],
  "comparison_queries": ["..."],
  "pricing_queries": ["..."],
  "long_tail_modifiers": ["..."],
  "skip_brand_or_news": ["..."],
  "notes": "optional free text"
}
```

## 后续

将输出保存为 `exports/waist_expanded.json`，供 `pipeline/run_waist_discovery.py` 阶段 1+ 消费。
