"""Data access layer for Demand Radar."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from storage.database import get_connection, init_db


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


class Repository:
    def __init__(self, db_path: Optional[Path | str] = None):
        self.db_path = db_path
        init_db(db_path)

    def _conn(self):
        return get_connection(self.db_path)

    # --- seeds ---
    def upsert_seed(
        self,
        keyword: str,
        category: str,
        market: str = "US",
        language: str = "en",
        enabled: bool = True,
    ) -> int:
        with self._conn() as conn:
            conn.execute(
                """
                INSERT INTO seeds (keyword, category, market, language, enabled)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(keyword, category, market) DO UPDATE SET
                    enabled=excluded.enabled,
                    language=excluded.language
                """,
                (keyword, category, market, language, 1 if enabled else 0),
            )
            row = conn.execute(
                "SELECT id FROM seeds WHERE keyword=? AND category=? AND market=?",
                (keyword, category, market),
            ).fetchone()
            return int(row["id"])

    def list_seeds(self, enabled_only: bool = True) -> list[dict]:
        with self._conn() as conn:
            sql = "SELECT * FROM seeds"
            if enabled_only:
                sql += " WHERE enabled=1"
            sql += " ORDER BY category, keyword"
            return [dict(r) for r in conn.execute(sql).fetchall()]

    # --- keywords ---
    def upsert_keyword(
        self,
        keyword: str,
        normalized: str,
        intent: Optional[str] = None,
        category: Optional[str] = None,
        cluster_id: Optional[str] = None,
        source: Optional[str] = None,
    ) -> int:
        with self._conn() as conn:
            existing = conn.execute(
                "SELECT id FROM keywords WHERE keyword=?", (keyword,)
            ).fetchone()
            if existing:
                conn.execute(
                    """
                    UPDATE keywords SET
                        normalized=?,
                        intent=COALESCE(?, intent),
                        category=COALESCE(?, category),
                        cluster_id=COALESCE(?, cluster_id),
                        source=COALESCE(?, source),
                        updated_at=?
                    WHERE id=?
                    """,
                    (
                        normalized,
                        intent,
                        category,
                        cluster_id,
                        source,
                        _now(),
                        existing["id"],
                    ),
                )
                return int(existing["id"])
            cur = conn.execute(
                """
                INSERT INTO keywords (keyword, normalized, intent, category, cluster_id, source)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (keyword, normalized, intent, category, cluster_id, source),
            )
            return int(cur.lastrowid)

    def get_keyword_id(self, keyword: str) -> Optional[int]:
        with self._conn() as conn:
            row = conn.execute(
                "SELECT id FROM keywords WHERE keyword=?", (keyword,)
            ).fetchone()
            return int(row["id"]) if row else None

    def list_keywords(self, limit: int = 5000) -> list[dict]:
        with self._conn() as conn:
            rows = conn.execute(
                "SELECT * FROM keywords ORDER BY updated_at DESC LIMIT ?", (limit,)
            ).fetchall()
            return [dict(r) for r in rows]

    # --- snapshots (append-only) ---
    def append_snapshot(
        self,
        keyword_id: int,
        source: str,
        *,
        timeframe: Optional[str] = None,
        market: Optional[str] = None,
        trend_score: Optional[float] = None,
        monthly_volume: Optional[int] = None,
        is_rising: bool = False,
        is_breakout: bool = False,
        raw: Optional[dict] = None,
    ) -> int:
        with self._conn() as conn:
            cur = conn.execute(
                """
                INSERT INTO snapshots (
                    keyword_id, source, timeframe, market, trend_score,
                    monthly_volume, is_rising, is_breakout, raw_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    keyword_id,
                    source,
                    timeframe,
                    market,
                    trend_score,
                    monthly_volume,
                    1 if is_rising else 0,
                    1 if is_breakout else 0,
                    json.dumps(raw) if raw else None,
                ),
            )
            return int(cur.lastrowid)

    def list_snapshots(
        self, keyword_id: Optional[int] = None, limit: int = 1000
    ) -> list[dict]:
        with self._conn() as conn:
            if keyword_id is not None:
                rows = conn.execute(
                    """
                    SELECT * FROM snapshots
                    WHERE keyword_id=?
                    ORDER BY collected_at DESC LIMIT ?
                    """,
                    (keyword_id, limit),
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT * FROM snapshots ORDER BY collected_at DESC LIMIT ?",
                    (limit,),
                ).fetchall()
            return [dict(r) for r in rows]

    # --- evidence ---
    def add_evidence(
        self,
        evidence_type: str,
        *,
        keyword_id: Optional[int] = None,
        opportunity_id: Optional[int] = None,
        source_url: Optional[str] = None,
        content: Optional[str] = None,
    ) -> int:
        with self._conn() as conn:
            cur = conn.execute(
                """
                INSERT INTO evidence (
                    keyword_id, opportunity_id, source_url, evidence_type, content
                ) VALUES (?, ?, ?, ?, ?)
                """,
                (keyword_id, opportunity_id, source_url, evidence_type, content),
            )
            return int(cur.lastrowid)

    def list_evidence(
        self, keyword_id: Optional[int] = None, opportunity_id: Optional[int] = None
    ) -> list[dict]:
        with self._conn() as conn:
            clauses, params = [], []
            if keyword_id is not None:
                clauses.append("keyword_id=?")
                params.append(keyword_id)
            if opportunity_id is not None:
                clauses.append("opportunity_id=?")
                params.append(opportunity_id)
            where = (" WHERE " + " AND ".join(clauses)) if clauses else ""
            rows = conn.execute(
                f"SELECT * FROM evidence{where} ORDER BY collected_at DESC", params
            ).fetchall()
            return [dict(r) for r in rows]

    # --- opportunities ---
    def upsert_opportunity(
        self,
        title: str,
        *,
        category: Optional[str] = None,
        status: str = "discovered",
        score: Optional[float] = None,
        demand_score: Optional[float] = None,
        monetization_score: Optional[float] = None,
        competition_score: Optional[float] = None,
        feasibility_score: Optional[float] = None,
        evidence_score: Optional[float] = None,
        confidence: str = "pending",
        cluster_id: Optional[str] = None,
        notes: Optional[str] = None,
    ) -> int:
        with self._conn() as conn:
            existing = conn.execute(
                "SELECT id FROM opportunities WHERE title=? AND COALESCE(cluster_id,'')=COALESCE(?, '')",
                (title, cluster_id),
            ).fetchone()
            if existing:
                conn.execute(
                    """
                    UPDATE opportunities SET
                        category=COALESCE(?, category),
                        status=?,
                        score=?,
                        demand_score=?,
                        monetization_score=?,
                        competition_score=?,
                        feasibility_score=?,
                        evidence_score=?,
                        confidence=?,
                        notes=COALESCE(?, notes),
                        updated_at=?
                    WHERE id=?
                    """,
                    (
                        category,
                        status,
                        score,
                        demand_score,
                        monetization_score,
                        competition_score,
                        feasibility_score,
                        evidence_score,
                        confidence,
                        notes,
                        _now(),
                        existing["id"],
                    ),
                )
                return int(existing["id"])
            cur = conn.execute(
                """
                INSERT INTO opportunities (
                    title, category, status, score, demand_score, monetization_score,
                    competition_score, feasibility_score, evidence_score,
                    confidence, cluster_id, notes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    title,
                    category,
                    status,
                    score,
                    demand_score,
                    monetization_score,
                    competition_score,
                    feasibility_score,
                    evidence_score,
                    confidence,
                    cluster_id,
                    notes,
                ),
            )
            return int(cur.lastrowid)

    def update_opportunity_status(self, opportunity_id: int, status: str) -> None:
        with self._conn() as conn:
            conn.execute(
                "UPDATE opportunities SET status=?, updated_at=? WHERE id=?",
                (status, _now(), opportunity_id),
            )

    def list_opportunities(
        self, min_score: float = 0, status: Optional[str] = None, limit: int = 500
    ) -> list[dict]:
        with self._conn() as conn:
            sql = "SELECT * FROM opportunities WHERE COALESCE(score,0) >= ?"
            params: list[Any] = [min_score]
            if status:
                sql += " AND status=?"
                params.append(status)
            sql += " ORDER BY (score IS NULL), score DESC, updated_at DESC LIMIT ?"
            params.append(limit)
            return [dict(r) for r in conn.execute(sql, params).fetchall()]

    def get_opportunity(self, opportunity_id: int) -> Optional[dict]:
        with self._conn() as conn:
            row = conn.execute(
                "SELECT * FROM opportunities WHERE id=?", (opportunity_id,)
            ).fetchone()
            return dict(row) if row else None

    # --- reports ---
    def add_report(
        self,
        opportunity_id: int,
        content: str,
        *,
        report_type: str = "screening",
        report_path: Optional[str] = None,
    ) -> int:
        with self._conn() as conn:
            version_row = conn.execute(
                """
                SELECT COALESCE(MAX(version), 0) + 1 AS v
                FROM reports WHERE opportunity_id=? AND report_type=?
                """,
                (opportunity_id, report_type),
            ).fetchone()
            version = int(version_row["v"])
            cur = conn.execute(
                """
                INSERT INTO reports (opportunity_id, report_type, report_path, content, version)
                VALUES (?, ?, ?, ?, ?)
                """,
                (opportunity_id, report_type, report_path, content, version),
            )
            return int(cur.lastrowid)

    def list_reports(self, opportunity_id: Optional[int] = None) -> list[dict]:
        with self._conn() as conn:
            if opportunity_id is not None:
                rows = conn.execute(
                    """
                    SELECT * FROM reports WHERE opportunity_id=?
                    ORDER BY version DESC
                    """,
                    (opportunity_id,),
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT * FROM reports ORDER BY created_at DESC LIMIT 200"
                ).fetchall()
            return [dict(r) for r in rows]

    # --- validations ---
    def add_validation(
        self,
        opportunity_id: int,
        result: str,
        *,
        traffic: Optional[int] = None,
        signups: Optional[int] = None,
        revenue: Optional[float] = None,
        notes: Optional[str] = None,
    ) -> int:
        with self._conn() as conn:
            cur = conn.execute(
                """
                INSERT INTO validations (
                    opportunity_id, result, traffic, signups, revenue, notes
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                (opportunity_id, result, traffic, signups, revenue, notes),
            )
            return int(cur.lastrowid)

    def list_validations(self, opportunity_id: Optional[int] = None) -> list[dict]:
        with self._conn() as conn:
            if opportunity_id is not None:
                rows = conn.execute(
                    """
                    SELECT * FROM validations WHERE opportunity_id=?
                    ORDER BY validated_at DESC
                    """,
                    (opportunity_id,),
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT * FROM validations ORDER BY validated_at DESC LIMIT 200"
                ).fetchall()
            return [dict(r) for r in rows]

    # --- pipeline runs ---
    def start_run(self, run_type: str) -> int:
        with self._conn() as conn:
            cur = conn.execute(
                "INSERT INTO pipeline_runs (run_type, status) VALUES (?, 'running')",
                (run_type,),
            )
            return int(cur.lastrowid)

    def finish_run(
        self,
        run_id: int,
        status: str = "ok",
        error_log: Optional[str] = None,
        stats: Optional[dict] = None,
    ) -> None:
        with self._conn() as conn:
            conn.execute(
                """
                UPDATE pipeline_runs
                SET finished_at=?, status=?, error_log=?, stats_json=?
                WHERE id=?
                """,
                (
                    _now(),
                    status,
                    error_log,
                    json.dumps(stats) if stats else None,
                    run_id,
                ),
            )

    def counts(self) -> dict[str, int]:
        with self._conn() as conn:
            tables = [
                "seeds",
                "keywords",
                "snapshots",
                "evidence",
                "opportunities",
                "reports",
                "validations",
            ]
            out = {}
            for t in tables:
                out[t] = int(conn.execute(f"SELECT COUNT(*) AS c FROM {t}").fetchone()["c"])
            return out
