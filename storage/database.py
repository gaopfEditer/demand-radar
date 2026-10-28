"""SQLite schema and connection helpers for Demand Radar."""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Optional

DEFAULT_DB_PATH = Path(__file__).resolve().parent.parent / "data" / "demand_radar.db"

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS seeds (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    keyword TEXT NOT NULL,
    category TEXT NOT NULL,
    market TEXT NOT NULL DEFAULT 'US',
    language TEXT NOT NULL DEFAULT 'en',
    enabled INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    UNIQUE(keyword, category, market)
);

CREATE TABLE IF NOT EXISTS keywords (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    keyword TEXT NOT NULL UNIQUE,
    normalized TEXT NOT NULL,
    intent TEXT,
    category TEXT,
    cluster_id TEXT,
    source TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS snapshots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    keyword_id INTEGER NOT NULL,
    source TEXT NOT NULL,
    collected_at TEXT NOT NULL DEFAULT (datetime('now')),
    timeframe TEXT,
    market TEXT,
    trend_score REAL,
    monthly_volume INTEGER,
    is_rising INTEGER DEFAULT 0,
    is_breakout INTEGER DEFAULT 0,
    raw_json TEXT,
    FOREIGN KEY (keyword_id) REFERENCES keywords(id)
);

CREATE TABLE IF NOT EXISTS evidence (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    keyword_id INTEGER,
    opportunity_id INTEGER,
    source_url TEXT,
    evidence_type TEXT NOT NULL,
    content TEXT,
    collected_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (keyword_id) REFERENCES keywords(id),
    FOREIGN KEY (opportunity_id) REFERENCES opportunities(id)
);

CREATE TABLE IF NOT EXISTS opportunities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    category TEXT,
    status TEXT NOT NULL DEFAULT 'discovered',
    score REAL,
    demand_score REAL,
    monetization_score REAL,
    competition_score REAL,
    feasibility_score REAL,
    evidence_score REAL,
    confidence TEXT DEFAULT 'pending',
    cluster_id TEXT,
    notes TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    opportunity_id INTEGER NOT NULL,
    report_type TEXT NOT NULL DEFAULT 'screening',
    report_path TEXT,
    content TEXT,
    version INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (opportunity_id) REFERENCES opportunities(id)
);

CREATE TABLE IF NOT EXISTS validations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    opportunity_id INTEGER NOT NULL,
    result TEXT,
    traffic INTEGER,
    signups INTEGER,
    revenue REAL,
    notes TEXT,
    validated_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (opportunity_id) REFERENCES opportunities(id)
);

CREATE TABLE IF NOT EXISTS pipeline_runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_type TEXT NOT NULL,
    started_at TEXT NOT NULL DEFAULT (datetime('now')),
    finished_at TEXT,
    status TEXT NOT NULL DEFAULT 'running',
    error_log TEXT,
    stats_json TEXT
);

CREATE INDEX IF NOT EXISTS idx_snapshots_keyword ON snapshots(keyword_id);
CREATE INDEX IF NOT EXISTS idx_snapshots_collected ON snapshots(collected_at);
CREATE INDEX IF NOT EXISTS idx_keywords_normalized ON keywords(normalized);
CREATE INDEX IF NOT EXISTS idx_opportunities_status ON opportunities(status);
CREATE INDEX IF NOT EXISTS idx_opportunities_score ON opportunities(score);
"""


def get_connection(db_path: Optional[Path | str] = None) -> sqlite3.Connection:
    path = Path(db_path) if db_path else DEFAULT_DB_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(path))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db(db_path: Optional[Path | str] = None) -> Path:
    path = Path(db_path) if db_path else DEFAULT_DB_PATH
    conn = get_connection(path)
    try:
        conn.executescript(SCHEMA_SQL)
        conn.commit()
    finally:
        conn.close()
    return path
