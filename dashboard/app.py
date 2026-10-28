"""Streamlit Demand Radar dashboard."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from storage.repository import Repository

DB_DEFAULT = str(ROOT / "data" / "demand_radar.db")

st.set_page_config(page_title="Demand Radar", page_icon="📡", layout="wide")


@st.cache_resource
def get_repo(db_path: str) -> Repository:
    return Repository(db_path)


def main() -> None:
    st.sidebar.title("Demand Radar")
    st.sidebar.caption("Overseas Software Opportunity Dashboard")
    db_path = st.sidebar.text_input("SQLite path", DB_DEFAULT)
    repo = get_repo(db_path)

    page = st.sidebar.radio(
        "页面",
        ["总览", "关键词库", "趋势监控", "机会排行", "AI 研究报告", "项目验证"],
    )

    counts = repo.counts()
    if page == "总览":
        render_overview(repo, counts)
    elif page == "关键词库":
        render_keywords(repo)
    elif page == "趋势监控":
        render_trends(repo)
    elif page == "机会排行":
        render_opportunities(repo)
    elif page == "AI 研究报告":
        render_reports(repo)
    elif page == "项目验证":
        render_validations(repo)


def render_overview(repo: Repository, counts: dict) -> None:
    st.title("📡 Demand Radar 总览")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("关键词", counts.get("keywords", 0))
    c2.metric("快照", counts.get("snapshots", 0))
    c3.metric("机会", counts.get("opportunities", 0))
    c4.metric("验证记录", counts.get("validations", 0))

    opps = repo.list_opportunities(min_score=0)
    pending = [o for o in opps if o.get("confidence") in ("pending", "low")]
    research = [o for o in opps if (o.get("score") or 0) >= 65]
    validating = [o for o in opps if o.get("status") in ("validating", "validated")]

    a, b, c = st.columns(3)
    a.metric("候选机会", len(opps))
    b.metric("待深度分析 (≥65)", len(research))
    c.metric("待/已验证项目", len(validating))

    st.subheader("Top 机会")
    if opps:
        df = pd.DataFrame(opps)[
            ["id", "title", "category", "score", "confidence", "status"]
        ]
        st.dataframe(df.head(20), use_container_width=True)
    else:
        st.info("暂无机会。请先运行: `python run_daily.py`")

    st.caption(
        "注意：Google Trends 为相对热度，不等于绝对搜索量。"
        f" 低置信度机会: {len(pending)}"
    )


def render_keywords(repo: Repository) -> None:
    st.title("关键词库")
    rows = repo.list_keywords(limit=5000)
    if not rows:
        st.info("暂无关键词")
        return
    df = pd.DataFrame(rows)
    cats = ["全部"] + sorted({c for c in df["category"].dropna().unique()})
    cat = st.selectbox("分类", cats)
    q = st.text_input("搜索")
    view = df
    if cat != "全部":
        view = view[view["category"] == cat]
    if q:
        view = view[view["keyword"].str.contains(q, case=False, na=False)]
    st.dataframe(
        view[["id", "keyword", "intent", "category", "cluster_id", "source", "updated_at"]],
        use_container_width=True,
    )
    st.download_button(
        "导出当前 CSV",
        view.to_csv(index=False).encode("utf-8"),
        file_name="keywords_filtered.csv",
        mime="text/csv",
    )


def render_trends(repo: Repository) -> None:
    st.title("趋势监控")
    snaps = repo.list_snapshots(limit=2000)
    if not snaps:
        st.info("暂无快照。运行 daily/weekly 采集后可见。")
        return
    df = pd.DataFrame(snaps)
    rising = df[df["is_rising"] == 1]
    st.metric("Rising 标记快照数", len(rising))
    st.subheader("最近快照")
    st.dataframe(
        df[
            [
                "id",
                "keyword_id",
                "source",
                "timeframe",
                "market",
                "trend_score",
                "is_rising",
                "is_breakout",
                "collected_at",
            ]
        ].head(100),
        use_container_width=True,
    )
    # Simple chart for a selected keyword_id
    kids = sorted(df["keyword_id"].unique().tolist())
    kid = st.selectbox("查看 keyword_id 历史曲线", kids)
    sub = df[df["keyword_id"] == kid].sort_values("collected_at")
    if not sub.empty and sub["trend_score"].notna().any():
        st.line_chart(sub.set_index("collected_at")["trend_score"])
    else:
        st.caption("该关键词暂无可用 trend_score")


def render_opportunities(repo: Repository) -> None:
    st.title("机会排行")
    min_score = st.slider("最低评分", 0, 100, 50)
    status = st.selectbox(
        "状态",
        ["全部", "discovered", "researching", "validating", "validated", "dropped"],
    )
    opps = repo.list_opportunities(min_score=float(min_score))
    if status != "全部":
        opps = [o for o in opps if o.get("status") == status]
    if not opps:
        st.info("无匹配机会")
        return
    for o in opps:
        score = o.get("score")
        with st.container(border=True):
            cols = st.columns([4, 1, 1, 1])
            cols[0].markdown(f"**{o['title']}**  \n{o.get('category') or '—'}")
            cols[1].metric("评分", f"{score:.0f}" if score is not None else "—")
            cols[2].write(o.get("confidence") or "pending")
            cols[3].write(o.get("status"))
            with st.expander("分项得分 / 备注"):
                st.write(
                    {
                        "demand": o.get("demand_score"),
                        "monetization": o.get("monetization_score"),
                        "competition": o.get("competition_score"),
                        "feasibility": o.get("feasibility_score"),
                        "evidence": o.get("evidence_score"),
                    }
                )
                if o.get("notes"):
                    try:
                        st.json(json.loads(o["notes"]))
                    except Exception:  # noqa: BLE001
                        st.text(o["notes"])
            new_status = st.selectbox(
                f"更新状态 #{o['id']}",
                ["discovered", "researching", "validating", "validated", "dropped"],
                index=["discovered", "researching", "validating", "validated", "dropped"].index(
                    o.get("status") or "discovered"
                ),
                key=f"status_{o['id']}",
            )
            if st.button("保存状态", key=f"save_status_{o['id']}"):
                repo.update_opportunity_status(o["id"], new_status)
                st.success(f"已更新 #{o['id']} → {new_status}")
                st.cache_resource.clear()


def render_reports(repo: Repository) -> None:
    st.title("AI 研究报告")
    reports = repo.list_reports()
    export_dir = ROOT / "exports" / "reports"
    if export_dir.exists():
        files = sorted(export_dir.glob("*"))
        st.caption(f"导出目录文件数: {len(files)}")
        for f in files[:20]:
            st.write(f"- `{f}`")
    if not reports:
        st.info("暂无报告。设置 OPENAI_API_KEY 后运行 pipeline，或查看 stub 报告。")
        return
    for r in reports:
        with st.expander(
            f"#{r['id']} opp={r['opportunity_id']} {r['report_type']} v{r['version']}"
        ):
            st.write(r.get("report_path"))
            content = r.get("content") or ""
            if content.strip().startswith("{"):
                try:
                    st.json(json.loads(content))
                except Exception:  # noqa: BLE001
                    st.markdown(content)
            else:
                st.markdown(content)


def render_validations(repo: Repository) -> None:
    st.title("项目验证闭环")
    opps = repo.list_opportunities(min_score=0)
    if not opps:
        st.info("暂无机会可验证")
        return
    labels = {f"#{o['id']} {o['title']}": o["id"] for o in opps}
    choice = st.selectbox("选择机会", list(labels.keys()))
    oid = labels[choice]

    st.subheader("新增验证记录")
    with st.form("validation_form"):
        result = st.selectbox(
            "结果",
            ["pending", "positive", "negative", "inconclusive", "iterate"],
        )
        traffic = st.number_input("流量", min_value=0, value=0)
        signups = st.number_input("注册", min_value=0, value=0)
        revenue = st.number_input("收入 (USD)", min_value=0.0, value=0.0, step=1.0)
        notes = st.text_area("备注")
        new_status = st.selectbox(
            "同步机会状态",
            ["validating", "validated", "dropped", "researching", "discovered"],
        )
        submitted = st.form_submit_button("写入 validations")
        if submitted:
            repo.add_validation(
                oid,
                result,
                traffic=int(traffic) or None,
                signups=int(signups) or None,
                revenue=float(revenue) or None,
                notes=notes or None,
            )
            repo.update_opportunity_status(oid, new_status)
            st.success("已保存验证记录并更新状态")
            st.cache_resource.clear()

    st.subheader("历史验证")
    vals = repo.list_validations(opportunity_id=oid)
    if vals:
        st.dataframe(pd.DataFrame(vals), use_container_width=True)
    else:
        st.caption("尚无验证记录")


if __name__ == "__main__":
    main()
