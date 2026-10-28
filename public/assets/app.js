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
