const DATA_BASE = (() => {
  const p = window.location.pathname;
  if (p.includes("/demand-radar/")) {
    return "/demand-radar/data";
  }
  return "data";
})();

export async function loadJson(name) {
  const res = await fetch(`${DATA_BASE}/${name}`);
  if (!res.ok) throw new Error(`Failed to load ${name}: ${res.status}`);
  return res.json();
}

export function qs(sel, root = document) {
  return root.querySelector(sel);
}

export function qsa(sel, root = document) {
  return [...root.querySelectorAll(sel)];
}

export function setActiveNav() {
  const page = document.body.dataset.page;
  qsa("nav a").forEach((a) => {
    if (a.dataset.page === page) a.classList.add("active");
  });
}

export function formatMetaDisplay(iso) {
  if (!iso) return "—";
  const m = iso.match(/^(\d{4}-\d{2}-\d{2})T(\d{2}:\d{2})/);
  if (m) return `${m[1]} ${m[2]} UTC`;
  return iso.slice(0, 16);
}

export function confidenceBadge(c) {
  const key = (c || "unknown").toLowerCase();
  const cls =
    key === "high" ? "badge-high" : key === "medium" ? "badge-medium" : "badge-low";
  const label = { high: "高", medium: "中", low: "低", unknown: "—" }[key] || c;
  return `<span class="badge ${cls}">${label}</span>`;
}

export async function renderSiteMetaBar() {
  const el = document.getElementById("site-meta-bar");
  if (!el) return;
  try {
    const meta = await loadJson("meta.json");
    const when = formatMetaDisplay(meta.updated_at);
    let html = `数据更新于 <strong>${when}</strong> · 市场 <strong>${meta.market || "—"}</strong>`;
    const st = meta.stats || {};
    if (st.opportunities != null) {
      html += ` · 机会 <strong>${st.opportunities}</strong> · 关键词 <strong>${st.keywords ?? "—"}</strong>`;
    }
    if (meta.trends_degraded) {
      html += ` · <span class="status-partial">Trends 已降级/mock</span>`;
    }
    el.innerHTML = html;
  } catch (e) {
    el.textContent = "无法加载 meta.json";
  }
}

export function pendingLabel(dims) {
  if (!dims || !dims.length) return "—";
  return dims.join(", ");
}

export function escapeHtml(s) {
  return String(s ?? "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

const VERDICT_ORDER = { Go: 0, Watch: 1, Kill: 2 };

export function sortDecisionCards(cards) {
  return [...(cards || [])].sort(
    (a, b) => (VERDICT_ORDER[a.verdict] ?? 9) - (VERDICT_ORDER[b.verdict] ?? 9)
  );
}

export function verdictBadge(verdict) {
  const key = (verdict || "").toLowerCase();
  const cls =
    key === "go" ? "verdict-go" : key === "watch" ? "verdict-watch" : "verdict-kill";
  const label = { go: "Go", watch: "Watch", kill: "Kill" }[key] || escapeHtml(verdict);
  return `<span class="badge verdict-badge ${cls}">${label}</span>`;
}

export function evidenceStatusTag(status) {
  if (status === "verified") {
    return '<span class="evidence-status status-verified">已验证</span>';
  }
  if (status === "unverified") {
    return '<span class="evidence-status status-unverified">未验证</span>';
  }
  return "";
}

export function renderGrowthList(items, label) {
  if (!items?.length) return "";
  const lis = items
    .map((item) => {
      const url = item.evidence_url
        ? `<a href="${escapeHtml(item.evidence_url)}" target="_blank" rel="noopener">来源</a>`
        : "";
      return `<li>${escapeHtml(item.claim)} ${evidenceStatusTag(item.status)} ${url}</li>`;
    })
    .join("");
  return `<div class="decision-section"><h3>${escapeHtml(label)}</h3><ul class="evidence-list">${lis}</ul></div>`;
}

export function renderKeywordSignals(kwTrend) {
  if (!kwTrend?.signals?.length) return "";
  const meta = [
    kwTrend.market ? `市场 ${kwTrend.market}` : "",
    kwTrend.window ? `窗口 ${kwTrend.window}` : "",
    kwTrend.metric_type ? `指标 ${kwTrend.metric_type}` : "",
  ]
    .filter(Boolean)
    .join(" · ");
  const lis = kwTrend.signals
    .map((s) => {
      const url = s.evidence_url
        ? `<a href="${escapeHtml(s.evidence_url)}" target="_blank" rel="noopener">来源</a>`
        : "";
      return `<li><strong>${escapeHtml(s.keyword_or_cluster)}</strong> (${escapeHtml(s.direction)}): ${escapeHtml(s.note)} ${evidenceStatusTag(s.status)} ${url}</li>`;
    })
    .join("");
  const note = kwTrend.trends_ui_note
    ? `<p class="meta">${escapeHtml(kwTrend.trends_ui_note)}</p>`
    : "";
  return `<div class="decision-section"><h3>关键词增长趋势</h3><p class="meta">${escapeHtml(meta)}</p>${note}<ul class="evidence-list">${lis}</ul></div>`;
}

export function renderDecisionCard(card, { detail = false } = {}) {
  const vKey = (card.verdict || "").toLowerCase();
  const support = (card.support_keywords || [])
    .map((k) => `<span class="kw-tag">${escapeHtml(k)}</span>`)
    .join("");
  const serpRefs = (card.serp_gap_refs || [])
    .map(
      (u) =>
        `<li><a href="${escapeHtml(u)}" target="_blank" rel="noopener">${escapeHtml(u)}</a></li>`
    )
    .join("");
  const peripherals = (card.related_peripheral_content || [])
    .map((p) => `<li>${escapeHtml(p)}</li>`)
    .join("");
  const mvpTitles = (card.mvp_7d?.url_titles || [])
    .map((t) => `<li>${escapeHtml(t)}</li>`)
    .join("");
  const mvpLimit = detail ? mvpTitles.length : 5;
  const mvpSlice = (card.mvp_7d?.url_titles || []).slice(0, mvpLimit);
  const mvpHtml = mvpSlice.map((t) => `<li>${escapeHtml(t)}</li>`).join("");
  const mvpMore =
    !detail && (card.mvp_7d?.url_titles || []).length > 5
      ? `<p class="meta">另有 ${card.mvp_7d.url_titles.length - 5} 个标题，见<a href="decision.html?id=${encodeURIComponent(card.card_id)}">完整卡</a></p>`
      : "";

  const detailLink = detail
    ? ""
    : `<p class="card-link"><a href="decision.html?id=${encodeURIComponent(card.card_id)}">查看完整决策卡 →</a></p>`;

  return `
    <article class="decision-card verdict-${vKey}" id="${escapeHtml(card.card_id)}">
      <div class="decision-card-header">
        <div>
          ${verdictBadge(card.verdict)}
          <h2>${escapeHtml(card.title)}</h2>
        </div>
        <p class="primary-kw">${escapeHtml(card.primary_keyword)}</p>
      </div>
      ${card.kill_note ? `<p class="meta kill-note">${escapeHtml(card.kill_note)}</p>` : ""}
      <div class="decision-section">
        <h3>支撑词（5）</h3>
        <div class="kw-tags">${support}</div>
        ${card.support_keywords_note ? `<p class="meta">${escapeHtml(card.support_keywords_note)}</p>` : ""}
      </div>
      <div class="decision-section">
        <h3>谁在搜、谁付钱</h3>
        <p>${escapeHtml(card.who_searches_who_pays)}</p>
      </div>
      <div class="decision-grid-summary">
        <div class="decision-section">
          <h3>变现 · 主路径</h3>
          <p>${escapeHtml(card.monetization?.primary?.path)}</p>
          <p class="meta stack-fit">${escapeHtml(card.monetization?.primary?.stack_fit)}</p>
        </div>
        <div class="decision-section">
          <h3>变现 · 备路径</h3>
          <p>${escapeHtml(card.monetization?.backup?.path)}</p>
          <p class="meta stack-fit">${escapeHtml(card.monetization?.backup?.stack_fit)}</p>
        </div>
      </div>
      <div class="decision-section">
        <h3>SERP 缺口</h3>
        <p>${escapeHtml(card.serp_gap)}</p>
        ${serpRefs ? `<ul class="serp-refs">${serpRefs}</ul>` : ""}
      </div>
      <div class="decision-section">
        <h3>7 天 MVP · ${escapeHtml(card.mvp_7d?.site_type || "—")}</h3>
        ${mvpHtml ? `<ol class="mvp-titles">${mvpHtml}</ol>` : '<p class="meta">无建议 URL 清单</p>'}
        ${mvpMore}
      </div>
      <div class="decision-section">
        <h3>不做/降级 & 30 天标准</h3>
        <p>${escapeHtml(card.scope_and_success?.wont_do_or_downgrade)}</p>
        <p class="meta"><strong>30 天：</strong>${escapeHtml(card.scope_and_success?.success_30d)}</p>
      </div>
      ${renderGrowthList(card.product_growth_trend?.upside, "产品增长 · 增量")}
      ${renderGrowthList(card.product_growth_trend?.downside_or_stale, "产品增长 · 减量/停滞")}
      ${renderKeywordSignals(card.keyword_growth_trend)}
      <div class="decision-section">
        <h3>周边相关内容</h3>
        <ul>${peripherals}</ul>
      </div>
      ${
        card.evidence_vs_inference
          ? `<p class="meta evidence-note"><strong>证据 vs 推测：</strong>${escapeHtml(card.evidence_vs_inference)}</p>`
          : ""
      }
      ${detailLink}
    </article>`;
}

export async function renderWeekMetaBar() {
  const el = document.getElementById("site-meta-bar");
  if (!el) return;
  try {
    const week = await loadJson("week_decisions.json");
    let html = `批次 <strong>${escapeHtml(week.week_id)}</strong> · 调研截止 <strong>${escapeHtml(week.as_of)}</strong>（${escapeHtml(week.timezone)}）`;
    html += ` · 分布 Go / Watch / Kill 各 1`;
    if (week.source_markdown) {
      html += ` · 源文件 <code>${escapeHtml(week.source_markdown)}</code>`;
    }
    el.innerHTML = html;
  } catch {
    await renderSiteMetaBar();
  }
}

function narrativeItemRow(item, { showCategory = true, showLink = true } = {}) {
  const url = item.evidence_url
    ? `<a href="${escapeHtml(item.evidence_url)}" target="_blank" rel="noopener">来源</a>`
    : "";
  const cat =
    showCategory && item.category
      ? `<span class="narrative-cat">${escapeHtml(item.category)}</span>`
      : "";
  const cardLink =
    showLink && item.linked_card_id
      ? `<a class="narrative-card-link" href="decision.html?id=${encodeURIComponent(item.linked_card_id)}">决策卡</a>`
      : "";
  const name = item.name ? `<strong>${escapeHtml(item.name)}</strong> · ` : "";
  return `<li class="narrative-item">${cat}${name}${escapeHtml(item.claim)} ${evidenceStatusTag(item.status)} ${url} ${cardLink}</li>`;
}

function displacementRow(item) {
  const urls = (item.evidence_urls || [])
    .map(
      (u, i) =>
        `<a href="${escapeHtml(u)}" target="_blank" rel="noopener">来源${item.evidence_urls.length > 1 ? i + 1 : ""}</a>`
    )
    .join(" ");
  const cardLink = item.linked_card_id
    ? `<a class="narrative-card-link" href="decision.html?id=${encodeURIComponent(item.linked_card_id)}">决策卡</a>`
    : "";
  return `<li class="narrative-displacement">
    <p class="displacement-head"><span class="disp-old">${escapeHtml(item.old)}</span>
    <span class="disp-arrow">→</span>
    <span class="disp-new">${escapeHtml(item.new)}</span> ${evidenceStatusTag(item.status)}</p>
    <p class="meta"><strong>缺口：</strong>${escapeHtml(item.gap_filled)}</p>
    <p class="meta"><strong>Indie SEO：</strong>${escapeHtml(item.indie_seo_angle)}</p>
    <p class="narrative-refs">${urls} ${cardLink}</p>
  </li>`;
}

function demandSignalRow(s) {
  const meta = [
    s.market ? `市场 ${s.market}` : "",
    s.window ? `窗口 ${s.window}` : "",
    s.metric_type ? `指标 ${s.metric_type}` : "",
    s.direction ? `方向 ${s.direction}` : "",
  ]
    .filter(Boolean)
    .join(" · ");
  const url = s.evidence_url
    ? `<a href="${escapeHtml(s.evidence_url)}" target="_blank" rel="noopener">来源</a>`
    : "";
  const cardLink = s.linked_card_id
    ? `<a class="narrative-card-link" href="decision.html?id=${encodeURIComponent(s.linked_card_id)}">决策卡</a>`
    : "";
  return `<li class="narrative-demand">
    <p><strong>${escapeHtml(s.keyword_or_cluster)}</strong> ${evidenceStatusTag(s.status)}</p>
    <p class="meta">${escapeHtml(meta)}</p>
    <p>${escapeHtml(s.note)}</p>
    ${s.ideation_hint ? `<p class="ideation-hint"><strong>发散：</strong>${escapeHtml(s.ideation_hint)}</p>` : ""}
    <p class="narrative-refs">${url} ${cardLink}</p>
  </li>`;
}

/**
 * @param {object} narratives - market_narratives.json
 * @param {{ compact?: boolean, maxPerSection?: number }} opts
 */
export function renderMarketNarratives(narratives, { compact = false, maxPerSection = 4 } = {}) {
  if (!narratives) return "";

  const slice = (arr) =>
    compact && maxPerSection > 0 ? (arr || []).slice(0, maxPerSection) : arr || [];

  const rising = slice(narratives.rising);
  const falling = slice(narratives.falling_or_stale);
  const displacement = slice(narratives.displacement);
  const signals = slice(narratives.demand_signals);

  const limitations = (narratives.methodology_limitations || [])
    .map(
      (m) =>
        `<li><strong>${escapeHtml(m.item)}</strong>：${escapeHtml(m.status)}</li>`
    )
    .join("");

  const moreLink = compact
    ? `<p class="narratives-more"><a href="trends.html">查看完整市场叙事层 →</a></p>`
    : "";

  return `
    <section class="market-narratives" id="market-narratives">
      <div class="narratives-header">
        <h2>${escapeHtml(narratives.title || "产品兴衰 · 需求发散")}</h2>
        ${narratives.intro ? `<p class="site-intro narratives-intro">${escapeHtml(narratives.intro)}</p>` : ""}
      </div>
      <div class="narratives-grid">
        <div class="narrative-panel narrative-rising">
          <h3>上升 · 新产品 / 新功能</h3>
          <ul class="evidence-list">${rising.map((i) => narrativeItemRow(i)).join("") || "<li class='meta'>暂无</li>"}</ul>
        </div>
        <div class="narrative-panel narrative-falling">
          <h3>衰退 / 停滞 · 旧产品</h3>
          <ul class="evidence-list">${falling.map((i) => narrativeItemRow(i)).join("") || "<li class='meta'>暂无</li>"}</ul>
        </div>
      </div>
      <div class="narrative-panel narrative-displacement-block">
        <h3>替代叙事 · 旧 → 新</h3>
        <ul class="displacement-list">${displacement.map(displacementRow).join("") || "<li class='meta'>暂无</li>"}</ul>
      </div>
      <div class="narrative-panel narrative-demand-block">
        <h3>需求信号 · 相对趋势（发散用）</h3>
        <p class="meta">仅相对份额 / rising 标签 / 内容密度；不含未标注的绝对搜索量。</p>
        <ul class="demand-signal-list">${signals.map(demandSignalRow).join("") || "<li class='meta'>暂无</li>"}</ul>
      </div>
      ${
        limitations && !compact
          ? `<div class="narrative-panel narrative-limits"><h3>方法与局限</h3><ul>${limitations}</ul></div>`
          : ""
      }
      ${moreLink}
    </section>`;
}

const WAIST_VERDICT_ORDER = { pursue: 0, watch: 1, skip: 2 };

export function waistVerdictBadge(verdict) {
  const key = (verdict || "").toLowerCase();
  const cls =
    key === "pursue"
      ? "waist-pursue"
      : key === "watch"
        ? "waist-watch"
        : key === "skip"
          ? "waist-skip"
          : "";
  const label =
    { pursue: "Pursue", watch: "Watch", skip: "Skip" }[key] || escapeHtml(verdict);
  return `<span class="badge verdict-badge waist-verdict ${cls}">${label}</span>`;
}

function renderMethodChecklist(items) {
  if (!items?.length) return "";
  const lis = items
    .map(
      (m) =>
        `<li><strong>${escapeHtml(m.step)}. ${escapeHtml(m.title)}</strong> — ${escapeHtml(m.rule)}</li>`
    )
    .join("");
  return `<ol class="waist-checklist">${lis}</ol>`;
}

function renderSourceRefs(refs) {
  if (!refs?.length) return "";
  const links = refs
    .map(
      (r) =>
        `<li><a href="${escapeHtml(r.url)}" target="_blank" rel="noopener">${escapeHtml(r.label)}</a></li>`
    )
    .join("");
  return `<ul class="waist-source-refs">${links}</ul>`;
}

function renderWaistCandidateRow(c) {
  const support = (c.support_keywords || [])
    .map((k) => `<span class="kw-tag">${escapeHtml(k)}</span>`)
    .join("");
  const urls = (c.evidence_urls || [])
    .map(
      (u, i) =>
        `<a href="${escapeHtml(u)}" target="_blank" rel="noopener">证据${c.evidence_urls.length > 1 ? i + 1 : ""}</a>`
    )
    .join(" ");
  const cardLink = c.linked_card_id
    ? `<a href="decision.html?id=${encodeURIComponent(c.linked_card_id)}">周卡</a>`
    : "—";
  const serp = c.serp_gap || {};
  const serpFlags = [
    serp.low_dr_new_site === true ? "低DR新站" : "",
    serp.big_site_monopoly === true ? "大站垄断" : "",
  ]
    .filter(Boolean)
    .join(" · ") || "—";
  return `
    <tr class="waist-row verdict-row-${escapeHtml((c.verdict || "").toLowerCase())}">
      <td>
        <strong class="waist-kw">${escapeHtml(c.keyword)}</strong>
        ${support ? `<div class="kw-tags waist-support">${support}</div>` : ""}
      </td>
      <td>${escapeHtml(c.target_rank_band || "—")}</td>
      <td><code>${escapeHtml(c.band || "—")}</code></td>
      <td class="hide-sm">${escapeHtml(c.volume_band_note || "—")}</td>
      <td class="hide-sm">${escapeHtml(c.kd_band_note || "—")}</td>
      <td>${escapeHtml(serpFlags)}<br /><span class="meta">${escapeHtml(serp.summary || "")}</span></td>
      <td>${waistVerdictBadge(c.verdict)} ${evidenceStatusTag(c.status)}</td>
      <td class="hide-sm">${escapeHtml(c.mvp_angle || "—")}</td>
      <td>${cardLink}<br /><span class="meta waist-refs">${urls}</span></td>
    </tr>`;
}

function renderWaistCandidateCard(c) {
  const support = (c.support_keywords || [])
    .map((k) => `<span class="kw-tag">${escapeHtml(k)}</span>`)
    .join("");
  const urls = (c.evidence_urls || [])
    .map(
      (u) =>
        `<li><a href="${escapeHtml(u)}" target="_blank" rel="noopener">${escapeHtml(u)}</a></li>`
    )
    .join("");
  const tc = c.trends_check || {};
  const serp = c.serp_gap || {};
  const cardLink = c.linked_card_id
    ? `<a href="decision.html?id=${encodeURIComponent(c.linked_card_id)}">关联周决策卡 →</a>`
    : "";
  return `
    <article class="card waist-card verdict-${escapeHtml((c.verdict || "").toLowerCase())}" id="${escapeHtml(c.id)}">
      <div class="waist-card-head">
        ${waistVerdictBadge(c.verdict)}
        ${evidenceStatusTag(c.status)}
        <h2>${escapeHtml(c.keyword)}</h2>
        <p class="meta">目标位 <strong>${escapeHtml(c.target_rank_band)}</strong> · ${escapeHtml(c.band)}</p>
      </div>
      ${support ? `<div class="kw-tags">${support}</div>` : ""}
      <p>${escapeHtml(c.why)}</p>
      <p class="meta"><strong>MVP：</strong>${escapeHtml(c.mvp_angle)}</p>
      <div class="decision-section">
        <h3>Trends（7d / 12m）</h3>
        <p class="meta">${escapeHtml(tc.window_7d || "—")} / ${escapeHtml(tc.window_12m || "—")} ${evidenceStatusTag(tc.status)}</p>
        ${tc.note ? `<p class="meta">${escapeHtml(tc.note)}</p>` : ""}
      </div>
      <div class="decision-section">
        <h3>SERP 缺口</h3>
        <p>${escapeHtml(serp.summary || "—")}</p>
      </div>
      ${c.similarweb_loop_note ? `<p class="meta"><strong>Similarweb 循环：</strong>${escapeHtml(c.similarweb_loop_note)}</p>` : ""}
      ${urls ? `<ul class="serp-refs">${urls}</ul>` : ""}
      ${cardLink ? `<p class="card-link">${cardLink}</p>` : ""}
    </article>`;
}

/**
 * @param {object} waist - waist_keywords.json
 * @param {{ view?: 'table' | 'cards' }} opts
 */
export function renderWaistKeywords(waist, { view = "table" } = {}) {
  if (!waist) return "";
  const sorted = [...(waist.candidates || [])].sort(
    (a, b) =>
      (WAIST_VERDICT_ORDER[a.verdict] ?? 9) - (WAIST_VERDICT_ORDER[b.verdict] ?? 9)
  );

  const checklist = renderMethodChecklist(waist.method_checklist);
  const sources = renderSourceRefs(waist.source_refs);

  const body =
    view === "cards"
      ? `<div class="waist-cards">${sorted.map(renderWaistCandidateCard).join("")}</div>`
      : `<div class="waist-table-wrap">
          <table class="waist-table">
            <thead>
              <tr>
                <th>关键词</th>
                <th>目标位</th>
                <th>Band</th>
                <th class="hide-sm">量级</th>
                <th class="hide-sm">KD</th>
                <th>SERP</th>
                <th>结论</th>
                <th class="hide-sm">MVP 角度</th>
                <th>链接</th>
              </tr>
            </thead>
            <tbody>${sorted.map(renderWaistCandidateRow).join("")}</tbody>
          </table>
        </div>`;

  return `
    <section class="waist-keywords">
      <h2>${escapeHtml(waist.title || "腰部词")}</h2>
      ${waist.intro ? `<p class="site-intro">${escapeHtml(waist.intro)}</p>` : ""}
      <div class="narrative-panel waist-method">
        <h3>方法 checklist</h3>
        ${checklist}
        ${sources ? `<h3>来源</h3>${sources}` : ""}
      </div>
      ${body}
    </section>`;
}

export async function renderWaistMetaBar() {
  const el = document.getElementById("site-meta-bar");
  if (!el) return;
  try {
    const waist = await loadJson("waist_keywords.json");
    let html = `批次 <strong>${escapeHtml(waist.week_id)}</strong> · 截止 <strong>${escapeHtml(waist.as_of)}</strong>（${escapeHtml(waist.timezone)}）`;
    html += ` · 候选 <strong>${(waist.candidates || []).length}</strong>`;
    const rankRaw =
      (waist.candidates || []).map((c) => c.target_rank_band).find(Boolean) || "10-20";
    const rankDisplay = String(rankRaw).replace("-", "–");
    html += ` · 目标位 <strong>${escapeHtml(rankDisplay)}</strong>`;
    el.innerHTML = html;
  } catch {
    el.textContent = "无法加载 waist_keywords.json";
  }
}

export function formatUsd(n) {
  if (n == null || n === "" || Number.isNaN(Number(n))) return "—";
  const v = Number(n);
  const abs = Math.abs(v);
  if (abs >= 1e9) return `$${(v / 1e9).toFixed(2)}B`;
  if (abs >= 1e6) return `$${(v / 1e6).toFixed(2)}M`;
  if (abs >= 1e4) return `$${(v / 1e3).toFixed(1)}K`;
  if (abs >= 1e3) return `$${(v / 1e3).toFixed(2)}K`;
  return `$${v.toFixed(2)}`;
}

export function formatGrowthPct(n) {
  if (n == null || n === "" || Number.isNaN(Number(n))) return "—";
  const v = Number(n);
  const sign = v > 0 ? "+" : "";
  return `${sign}${v.toFixed(1)}%`;
}

/** One-line preview; full string unchanged when within maxLen. */
export function truncateText(text, maxLen = 140) {
  if (text == null) return "";
  const s = String(text);
  if (s.length <= maxLen) return s;
  return `${s.slice(0, maxLen - 1).trimEnd()}…`;
}

/** Product blurb from row.extra.description or top-level row.description. */
export function revenueProductDescription(row) {
  if (!row || typeof row !== "object") return null;
  for (const c of [row.extra?.description, row.description]) {
    if (typeof c === "string") {
      const t = c.trim();
      if (t) return t;
    }
  }
  return null;
}

export const OLLAMA_CONFIG_STORAGE_KEY = "demand-radar.ollama.config";
export const OLLAMA_DESC_CACHE_STORAGE_KEY = "demand-radar.ollama.descriptions";
export const OLLAMA_GENERATION_STORE_KEY = "demand-radar.ollama.generation-store";
export const REVENUE_FAVORITES_STORAGE_KEY = "demand-radar.revenue.favorites";
export const OLLAMA_ARCHIVE_AFTER_DAYS = 30;
export const OLLAMA_DEFAULT_ACTIVITY_DAYS = 7;
export const OLLAMA_DEFAULT_BASE_URL = "http://localhost:11434";
/** Matches typical `ollama list` tag (e.g. qwen3.5:latest). */
export const OLLAMA_DEFAULT_MODEL = "qwen3.5:latest";
/** Descriptions shorter than this may be expanded via Ollama when configured. */
export const OLLAMA_SHORT_DESCRIPTION_LEN = 80;

export function normalizeOllamaBaseUrl(url) {
  const t = String(url || "").trim();
  if (!t) return "";
  return t.replace(/\/+$/, "");
}

export function getOllamaConfig() {
  try {
    const raw = localStorage.getItem(OLLAMA_CONFIG_STORAGE_KEY);
    if (!raw) return { baseUrl: "", model: "" };
    const parsed = JSON.parse(raw);
    return {
      baseUrl: normalizeOllamaBaseUrl(parsed.baseUrl),
      model: String(parsed.model || "").trim(),
    };
  } catch {
    return { baseUrl: "", model: "" };
  }
}

/** Stored config with built-in defaults for auto-generation and UI prefill. */
export function getEffectiveOllamaConfig() {
  const stored = getOllamaConfig();
  return {
    baseUrl: stored.baseUrl || OLLAMA_DEFAULT_BASE_URL,
    model: stored.model || OLLAMA_DEFAULT_MODEL,
  };
}

export function saveOllamaConfig({ baseUrl, model }) {
  const payload = {
    baseUrl: normalizeOllamaBaseUrl(baseUrl),
    model: String(model || "").trim(),
  };
  localStorage.setItem(OLLAMA_CONFIG_STORAGE_KEY, JSON.stringify(payload));
  return payload;
}

export const OLLAMA_ANALYSIS_CACHE_STORAGE_KEY = "demand-radar.ollama.analysis";

export function clearOllamaDescriptionCache() {
  localStorage.removeItem(OLLAMA_DESC_CACHE_STORAGE_KEY);
  localStorage.setItem(
    OLLAMA_GENERATION_STORE_KEY,
    JSON.stringify({ version: 1, active: {}, archived: {} })
  );
}

/** Local calendar date `YYYY-MM-DD` for day buckets. */
export function localDateKey(date = new Date()) {
  const d = date instanceof Date ? date : new Date(date);
  const y = d.getFullYear();
  const m = String(d.getMonth() + 1).padStart(2, "0");
  const day = String(d.getDate()).padStart(2, "0");
  return `${y}-${m}-${day}`;
}

function shiftLocalDateKey(dayKey, deltaDays) {
  const [y, m, d] = dayKey.split("-").map((n) => Number(n));
  const dt = new Date(y, m - 1, d);
  dt.setDate(dt.getDate() + deltaDays);
  return localDateKey(dt);
}

function emptyGenerationStore() {
  return { version: 1, active: {}, archived: {} };
}

function normalizeGenerationRecord(value, fallbackName = "") {
  if (typeof value === "string") {
    const text = value.trim();
    if (!text) return null;
    return { text, productName: fallbackName, updatedAt: Date.now() };
  }
  if (!value || typeof value !== "object") return null;
  const text = String(value.text ?? value.description ?? "").trim();
  if (!text) return null;
  return {
    text,
    productName: String(value.productName || fallbackName || "").trim(),
    updatedAt: Number(value.updatedAt) || Date.now(),
  };
}

let generationStoreLoaded = false;

export function loadGenerationStore() {
  let store = emptyGenerationStore();
  try {
    const raw = localStorage.getItem(OLLAMA_GENERATION_STORE_KEY);
    if (raw) {
      const parsed = JSON.parse(raw);
      if (parsed && typeof parsed === "object") {
        store = {
          version: 1,
          active: parsed.active && typeof parsed.active === "object" ? parsed.active : {},
          archived:
            parsed.archived && typeof parsed.archived === "object" ? parsed.archived : {},
        };
      }
    }
  } catch {
    store = emptyGenerationStore();
  }

  if (!generationStoreLoaded) {
    generationStoreLoaded = true;
    store = migrateLegacyOllamaDescriptionCache(store);
  }
  return store;
}

export function saveGenerationStore(store) {
  localStorage.setItem(OLLAMA_GENERATION_STORE_KEY, JSON.stringify(store));
}

export function migrateLegacyOllamaDescriptionCache(store = null) {
  const next = store ?? loadGenerationStore();
  let legacy = null;
  try {
    const raw = localStorage.getItem(OLLAMA_DESC_CACHE_STORAGE_KEY);
    if (raw) legacy = JSON.parse(raw);
  } catch {
    legacy = null;
  }
  if (!legacy || typeof legacy !== "object" || !Object.keys(legacy).length) {
    return next;
  }
  const day = localDateKey();
  if (!next.active[day]) next.active[day] = {};
  for (const [key, value] of Object.entries(legacy)) {
    if (!key) continue;
    const rec = normalizeGenerationRecord(value);
    if (rec) next.active[day][key] = rec;
  }
  localStorage.removeItem(OLLAMA_DESC_CACHE_STORAGE_KEY);
  saveGenerationStore(next);
  return next;
}

/** Move day buckets older than {@link OLLAMA_ARCHIVE_AFTER_DAYS} into `archived` (not deleted). */
export function runOllamaArchiveMaintenance(store = null, { persist = true } = {}) {
  const next = store ?? loadGenerationStore();
  const cutoff = shiftLocalDateKey(localDateKey(), -OLLAMA_ARCHIVE_AFTER_DAYS);
  let moved = false;
  for (const day of Object.keys(next.active)) {
    if (day >= cutoff) continue;
    next.archived[day] = { ...(next.archived[day] || {}), ...(next.active[day] || {}) };
    delete next.active[day];
    moved = true;
  }
  if (moved && persist) saveGenerationStore(next);
  return next;
}

export function flattenStoreDescriptions(store) {
  const best = new Map();
  const scan = (buckets) => {
    for (const day of Object.keys(buckets || {}).sort()) {
      for (const [key, raw] of Object.entries(buckets[day] || {})) {
        const rec = normalizeGenerationRecord(raw);
        if (!rec || !key) continue;
        const prev = best.get(key);
        if (!prev || rec.updatedAt >= prev.updatedAt) {
          best.set(key, rec);
        }
      }
    }
  };
  scan(store.archived);
  scan(store.active);
  const flat = {};
  for (const [key, rec] of best) flat[key] = rec.text;
  return flat;
}

export function setOllamaDescriptionForRow(row, text, store = null) {
  const trimmed = String(text || "").trim();
  const key = revenueRowKey(row);
  if (!key || !trimmed) return store ?? loadGenerationStore();
  const next = store ?? loadGenerationStore();
  runOllamaArchiveMaintenance(next, { persist: false });
  const day = localDateKey();
  if (!next.active[day]) next.active[day] = {};
  next.active[day][key] = {
    text: trimmed,
    productName: String(row.name || "").trim(),
    updatedAt: Date.now(),
  };
  saveGenerationStore(next);
  return next;
}

/**
 * List locally cached Ollama description rows for the data-management UI.
 * @returns {{ day: string, archived: boolean, items: Array<{ key, productName, text, updatedAt }> }[]}
 */
export function listOllamaGenerationRecords(options = {}) {
  const {
    days = OLLAMA_DEFAULT_ACTIVITY_DAYS,
    includeArchived = false,
    query = "",
  } = options;
  const store = runOllamaArchiveMaintenance(loadGenerationStore());
  const q = String(query || "")
    .trim()
    .toLowerCase();
  const cutoff =
    days == null || days === "all"
      ? null
      : shiftLocalDateKey(localDateKey(), -(Number(days) || OLLAMA_DEFAULT_ACTIVITY_DAYS));

  const groups = new Map();

  const ingest = (buckets, archived) => {
    for (const day of Object.keys(buckets || {}).sort().reverse()) {
      if (cutoff && day < cutoff) continue;
      for (const [key, raw] of Object.entries(buckets[day] || {})) {
        const rec = normalizeGenerationRecord(raw);
        if (!rec) continue;
        const hay = `${rec.productName} ${key} ${rec.text}`.toLowerCase();
        if (q && !hay.includes(q)) continue;
        if (!groups.has(day)) {
          groups.set(day, { day, archived, items: [] });
        }
        groups.get(day).items.push({
          key,
          productName: rec.productName || key.split(":").slice(1).join(":") || key,
          text: rec.text,
          updatedAt: rec.updatedAt,
        });
      }
    }
  };

  ingest(store.active, false);
  if (includeArchived) ingest(store.archived, true);

  return [...groups.values()]
    .filter((g) => g.items.length)
    .sort((a, b) => (a.day < b.day ? 1 : -1));
}

export function restoreArchivedOllamaDay(dayKey) {
  const store = loadGenerationStore();
  const bucket = store.archived?.[dayKey];
  if (!bucket) return false;
  store.active[dayKey] = { ...(store.active[dayKey] || {}), ...bucket };
  delete store.archived[dayKey];
  saveGenerationStore(store);
  return true;
}

export function loadRevenueFavorites() {
  try {
    const raw = localStorage.getItem(REVENUE_FAVORITES_STORAGE_KEY);
    if (!raw) return new Set();
    const parsed = JSON.parse(raw);
    if (!Array.isArray(parsed)) return new Set();
    return new Set(parsed.filter((k) => typeof k === "string" && k));
  } catch {
    return new Set();
  }
}

export function saveRevenueFavorites(favorites) {
  const list = favorites instanceof Set ? [...favorites] : favorites;
  localStorage.setItem(REVENUE_FAVORITES_STORAGE_KEY, JSON.stringify(list));
}

export function isRevenueFavorite(rowKey, favorites = null) {
  const set = favorites ?? loadRevenueFavorites();
  return set.has(rowKey);
}

export function toggleRevenueFavorite(rowKey) {
  const set = loadRevenueFavorites();
  if (set.has(rowKey)) set.delete(rowKey);
  else set.add(rowKey);
  saveRevenueFavorites(set);
  return set.has(rowKey);
}

export function clearOllamaAnalysisCache() {
  localStorage.removeItem(OLLAMA_ANALYSIS_CACHE_STORAGE_KEY);
}

export function clearOllamaRevenueCaches() {
  clearOllamaDescriptionCache();
  clearOllamaAnalysisCache();
}

/** Stable cache key: source + slug, else source + name. */
export function revenueRowKey(row) {
  if (!row || typeof row !== "object") return "";
  const source = String(row.source || "unknown");
  const slug = row.extra?.slug;
  if (slug) return `${source}:${slug}`;
  return `${source}:${String(row.name || "").trim() || "unnamed"}`;
}

export function loadOllamaDescriptionCache() {
  const store = runOllamaArchiveMaintenance(loadGenerationStore());
  return flattenStoreDescriptions(store);
}

export function persistOllamaDescriptionCache(cache) {
  if (!cache || typeof cache !== "object") return;
  const store = loadGenerationStore();
  const day = localDateKey();
  if (!store.active[day]) store.active[day] = {};
  for (const [key, value] of Object.entries(cache)) {
    const rec = normalizeGenerationRecord(value);
    if (rec) store.active[day][key] = rec;
  }
  saveGenerationStore(store);
}

export function ollamaCachedDescription(row, cache = null) {
  const key = revenueRowKey(row);
  if (!key) return null;
  const store = cache ?? loadOllamaDescriptionCache();
  const v = store[key];
  if (typeof v === "string") {
    const t = v.trim();
    if (t) return t;
  }
  return null;
}

/** Display text: Ollama cache when present, else API/raw description. */
export function revenueDisplayDescription(row, aiCache = null) {
  const ai = ollamaCachedDescription(row, aiCache);
  if (ai) return ai;
  return revenueProductDescription(row);
}

export function revenueDescriptionIsFromOllama(row, aiCache = null) {
  return Boolean(ollamaCachedDescription(row, aiCache));
}

export function needsOllamaDescription(row, cache = null) {
  const key = revenueRowKey(row);
  if (!key) return false;
  const store = cache ?? loadOllamaDescriptionCache();
  if (ollamaCachedDescription(row, store)) return false;
  const raw = revenueProductDescription(row);
  if (!raw) return true;
  return raw.length < OLLAMA_SHORT_DESCRIPTION_LEN;
}

function formatUsdForPrompt(n) {
  const s = formatUsd(n);
  return s === "—" ? null : s;
}

function appendRevenueEnrichmentContextLines(lines, row) {
  const extra = row.extra || {};
  const total = formatUsdForPrompt(row.total_revenue);
  if (total) lines.push(`Total revenue: ${total}`);
  if (extra.paymentProvider) lines.push(`Payment provider: ${extra.paymentProvider}`);
  if (extra.onSale != null) lines.push(`On sale: ${extra.onSale ? "yes" : "no"}`);
  if (extra.growthMRR30d != null && !Number.isNaN(Number(extra.growthMRR30d))) {
    lines.push(`30d MRR growth: ${formatGrowthPct(extra.growthMRR30d)}`);
  }
  const longDesc = extra.long_description;
  if (typeof longDesc === "string" && longDesc.trim()) {
    lines.push(`Long description: ${truncateText(longDesc.trim(), 1200)}`);
  }
  const features = extra.features;
  if (Array.isArray(features) && features.length) {
    lines.push(`Features: ${features.slice(0, 16).join("; ")}`);
  }
  const siteMeta = extra.website_meta_description;
  if (typeof siteMeta === "string" && siteMeta.trim()) {
    lines.push(`Site meta: ${truncateText(siteMeta.trim(), 400)}`);
  }
}

function buildRevenueOllamaContextLines(row, descriptionOverride = null) {
  const raw =
    descriptionOverride != null
      ? String(descriptionOverride).trim() || null
      : revenueProductDescription(row);
  const lines = [`Product name: ${row.name || "Unknown"}`];
  if (row.source) lines.push(`Listing source: ${row.source}`);
  if (row.board) lines.push(`Board: ${row.board}`);
  if (row.category) lines.push(`Category: ${row.category}`);
  const mrr = formatUsdForPrompt(row.mrr);
  const monthly = formatUsdForPrompt(row.monthly_revenue);
  if (mrr) lines.push(`MRR: ${mrr}`);
  if (monthly) lines.push(`Monthly revenue: ${monthly}`);
  if (row.growth_30d != null && !Number.isNaN(Number(row.growth_30d))) {
    lines.push(`30d growth: ${formatGrowthPct(row.growth_30d)}`);
  }
  appendRevenueEnrichmentContextLines(lines, row);
  if (row.website) lines.push(`Website: ${row.website}`);
  if (row.url) lines.push(`Listing URL: ${row.url}`);
  const tags = row.extra?.tags || row.tags;
  if (Array.isArray(tags) && tags.length) {
    lines.push(`Tags: ${tags.slice(0, 12).join(", ")}`);
  }
  if (raw) lines.push(`Description: ${raw}`);
  return lines;
}

export function buildRevenueOllamaPrompt(row) {
  const raw = revenueProductDescription(row);
  const lines = [
    "You write concise, factual one-line product blurbs for a revenue leaderboard.",
    "Use English. No hype, no invented metrics. Max ~200 characters.",
    "",
    ...buildRevenueOllamaContextLines(row),
  ];
  if (raw) {
    lines.push("", `Existing short blurb (expand/improve if needed): ${raw}`);
  } else {
    lines.push("", "No existing blurb — infer likely product purpose from the fields above only.");
  }
  lines.push("", "Reply with the blurb only, no quotes or prefix.");
  return lines.join("\n");
}

export const OLLAMA_REVENUE_ANALYSIS_TIMEOUT_MS = 45_000;
export const OLLAMA_REVENUE_ANALYSIS_TIMEOUT_MESSAGE =
  "生成超时（45s），请稍后重试或换更小模型 / Generation timed out (45s)";

export async function ollamaGenerateDescription(baseUrl, model, row, { signal } = {}) {
  const url = normalizeOllamaBaseUrl(baseUrl);
  if (!url) throw new Error("missing base URL");
  const prompt = buildRevenueOllamaPrompt(row);
  const body = {
    model: model || OLLAMA_DEFAULT_MODEL,
    prompt,
    stream: false,
    think: false,
    options: { temperature: 0.35, num_predict: 220 },
  };
  const res = await fetch(`${url}/api/generate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
    signal,
  });
  if (!res.ok) {
    const detail = await res.text().catch(() => "");
    throw new Error(`HTTP ${res.status}${detail ? `: ${detail.slice(0, 120)}` : ""}`);
  }
  const data = await res.json();
  const text = String(data.response || "").trim();
  if (!text) throw new Error("empty response");
  return text.replace(/^["']|["']$/g, "").trim();
}

async function mapWithConcurrency(items, limit, fn) {
  const results = new Array(items.length);
  let idx = 0;
  async function worker() {
    while (idx < items.length) {
      const i = idx++;
      results[i] = await fn(items[i], i);
    }
  }
  const workers = Array.from({ length: Math.min(limit, items.length) }, () => worker());
  await Promise.all(workers);
  return results;
}

/**
 * Generate missing/short descriptions via local Ollama. Updates localStorage cache.
 * @returns {{ status: string, generated?: number, failed?: number, message?: string }}
 */
export async function enrichRevenueDescriptionsWithOllama(rows, options = {}) {
  const {
    onProgress,
    onRowDone,
    concurrency = 2,
    cache: externalCache,
    config: externalConfig,
  } = options;

  const config = externalConfig ?? getEffectiveOllamaConfig();
  if (!config.baseUrl) {
    return { status: "skipped", reason: "no-url" };
  }

  const cache = externalCache ?? loadOllamaDescriptionCache();
  const todo = (rows || []).filter((r) => needsOllamaDescription(r, cache));
  if (!todo.length) {
    return { status: "done", generated: 0, failed: 0 };
  }

  let generated = 0;
  let failed = 0;
  let aborted = false;

  const report = () => {
    if (typeof onProgress === "function") {
      onProgress({ done: generated + failed, total: todo.length, generated, failed });
    }
  };

  report();

  try {
    await mapWithConcurrency(todo, concurrency, async (row) => {
      if (aborted) return;
      const key = revenueRowKey(row);
      try {
        const text = await ollamaGenerateDescription(config.baseUrl, config.model, row);
        cache[key] = text;
        setOllamaDescriptionForRow(row, text);
        generated += 1;
        if (typeof onRowDone === "function") onRowDone(key, text, row);
      } catch (err) {
        failed += 1;
        if (generated === 0 && failed === 1) {
          aborted = true;
          throw err;
        }
      } finally {
        report();
      }
    });
  } catch (err) {
    return {
      status: "error",
      generated,
      failed,
      message: err instanceof Error ? err.message : String(err),
    };
  }

  return { status: "done", generated, failed };
}

/** @typedef {{ tongLei?: string, shangXiaYou?: string, liangDian?: string }} RevenueOllamaAnalysis */

export function loadOllamaAnalysisCache() {
  try {
    const raw = localStorage.getItem(OLLAMA_ANALYSIS_CACHE_STORAGE_KEY);
    if (!raw) return {};
    const parsed = JSON.parse(raw);
    return parsed && typeof parsed === "object" ? parsed : {};
  } catch {
    return {};
  }
}

export function persistOllamaAnalysisCache(cache) {
  localStorage.setItem(OLLAMA_ANALYSIS_CACHE_STORAGE_KEY, JSON.stringify(cache));
}

/** @returns {RevenueOllamaAnalysis | null} */
export function ollamaCachedAnalysis(row, cache = null) {
  const key = revenueRowKey(row);
  if (!key) return null;
  const store = cache ?? loadOllamaAnalysisCache();
  const v = store[key];
  if (!v || typeof v !== "object") return null;
  const out = {
    tongLei: typeof v.tongLei === "string" ? v.tongLei.trim() : "",
    shangXiaYou: typeof v.shangXiaYou === "string" ? v.shangXiaYou.trim() : "",
    liangDian: typeof v.liangDian === "string" ? v.liangDian.trim() : "",
  };
  if (!out.tongLei && !out.shangXiaYou && !out.liangDian) return null;
  return out;
}

export function buildRevenueOllamaAnalysisPrompt(row, descriptionText = null) {
  const lines = [
    "You analyze indie/SaaS products on a revenue leaderboard for a Chinese-speaking founder audience.",
    "Using ONLY the context below (do not invent revenue figures), write concise Simplified Chinese copy for three angles.",
    "Reply with a single JSON object only — no markdown fences, no extra text.",
    'Keys must be exactly: "同类", "上下游", "亮点".',
    "- 同类: similar or competing products (short paragraph or bullet-style in one string)",
    "- 上下游: upstream/downstream products or services in the value chain",
    "- 亮点: key selling points / differentiation",
    "",
    "Context:",
    ...buildRevenueOllamaContextLines(row, descriptionText),
  ];
  return lines.join("\n");
}

function coerceOllamaAnalysisFieldValue(v) {
  if (v == null) return "";
  if (typeof v === "string") return v.trim();
  if (Array.isArray(v)) {
    return v
      .map((item) => {
        if (item == null) return "";
        if (typeof item === "string") return item.trim();
        if (typeof item === "object") {
          try {
            return JSON.stringify(item);
          } catch {
            return String(item);
          }
        }
        return String(item).trim();
      })
      .filter(Boolean)
      .join("；");
  }
  if (typeof v === "object") {
    try {
      return JSON.stringify(v);
    } catch {
      return String(v).trim();
    }
  }
  return String(v).trim();
}

/** @returns {RevenueOllamaAnalysis | null} */
export function parseOllamaAnalysisResponse(text) {
  if (!text) return null;
  let raw = String(text).trim();
  const fence = raw.match(/```(?:json)?\s*([\s\S]*?)```/i);
  if (fence) raw = fence[1].trim();
  const start = raw.indexOf("{");
  const end = raw.lastIndexOf("}");
  if (start >= 0 && end > start) raw = raw.slice(start, end + 1);
  let parsed;
  try {
    parsed = JSON.parse(raw);
  } catch {
    return null;
  }
  if (!parsed || typeof parsed !== "object") return null;

  const pick = (...keys) => {
    for (const k of keys) {
      if (!(k in parsed)) continue;
      const coerced = coerceOllamaAnalysisFieldValue(parsed[k]);
      if (coerced) return coerced;
    }
    return "";
  };

  const out = {
    tongLei: pick("同类", "tongLei", "peers", "competitors"),
    shangXiaYou: pick("上下游", "shangXiaYou", "upstream_downstream", "chain"),
    liangDian: pick("亮点", "liangDian", "highlights", "selling_points"),
  };
  if (!out.tongLei && !out.shangXiaYou && !out.liangDian) return null;
  return out;
}

export async function ollamaGenerateAnalysis(baseUrl, model, row, descriptionText, { signal } = {}) {
  const url = normalizeOllamaBaseUrl(baseUrl);
  if (!url) throw new Error("missing base URL");
  const prompt = buildRevenueOllamaAnalysisPrompt(row, descriptionText);
  const body = {
    model: model || OLLAMA_DEFAULT_MODEL,
    prompt,
    stream: false,
    think: false,
    options: { temperature: 0.4, num_predict: 800 },
  };
  const res = await fetch(`${url}/api/generate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
    signal,
  });
  if (!res.ok) {
    const detail = await res.text().catch(() => "");
    throw new Error(`HTTP ${res.status}${detail ? `: ${detail.slice(0, 120)}` : ""}`);
  }
  const data = await res.json();
  let parsed = parseOllamaAnalysisResponse(data.response);
  if (!parsed && data.thinking) {
    parsed = parseOllamaAnalysisResponse(data.thinking);
  }
  if (!parsed) throw new Error("could not parse analysis JSON");
  return parsed;
}

/**
 * On-demand: generate 同类 / 上下游 / 亮点 for one row. Updates analysis localStorage cache.
 * @returns {{ status: 'done' | 'cached' | 'error', analysis?: RevenueOllamaAnalysis, message?: string }}
 */
export async function fetchRevenueAnalysisWithOllama(row, options = {}) {
  const { cache: externalCache, config: externalConfig, descriptionCache, signal } = options;
  const config = externalConfig ?? getEffectiveOllamaConfig();
  if (!config.baseUrl) {
    return { status: "error", message: "no-url" };
  }

  const cache = externalCache ?? loadOllamaAnalysisCache();
  const existing = ollamaCachedAnalysis(row, cache);
  if (existing) return { status: "cached", analysis: existing };

  const key = revenueRowKey(row);
  if (!key) return { status: "error", message: "invalid row" };

  const descCache = descriptionCache ?? loadOllamaDescriptionCache();
  const descriptionText = revenueDisplayDescription(row, descCache);

  try {
    const analysis = await ollamaGenerateAnalysis(
      config.baseUrl,
      config.model,
      row,
      descriptionText,
      { signal }
    );
    cache[key] = analysis;
    persistOllamaAnalysisCache(cache);
    return { status: "done", analysis };
  } catch (err) {
    if (err instanceof Error && err.name === "AbortError") {
      return { status: "error", message: OLLAMA_REVENUE_ANALYSIS_TIMEOUT_MESSAGE };
    }
    return {
      status: "error",
      message: err instanceof Error ? err.message : String(err),
    };
  }
}

export const REVENUE_ANALYSIS_LABELS = {
  tongLei: "同类",
  shangXiaYou: "上下游",
  liangDian: "亮点",
};

export const REVENUE_SOURCE_LABELS = {
  trustmrr: "TrustMRR",
  bizpeel: "BizPeel",
  getlatka: "GetLatka",
  acquire: "Acquire",
  flippa: "Flippa",
};

export function revenueSourceLabel(source) {
  const key = (source || "").toLowerCase();
  return REVENUE_SOURCE_LABELS[key] || source || "—";
}

export async function renderRevenueMetaBar() {
  const el = document.getElementById("site-meta-bar");
  if (!el) return;
  try {
    const snap = await loadJson("revenue_boards.json");
    let html = `快照 <strong>${escapeHtml(snap.as_of || "—")}</strong>（${escapeHtml(snap.timezone || "—")}）`;
    html += ` · 条目 <strong>${snap.count ?? (snap.rows || []).length}</strong>`;
    const srcs = (snap.sources || []).map(revenueSourceLabel).join("、");
    if (srcs) html += ` · 源 ${escapeHtml(srcs)}`;
    el.innerHTML = html;
  } catch {
    el.textContent = "无法加载 revenue_boards.json";
  }
}
