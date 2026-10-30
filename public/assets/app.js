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
