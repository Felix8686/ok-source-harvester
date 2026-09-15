import sqlite3
from pathlib import Path


class SQLiteRepository:
    """SQLite schema bootstrap. Repository operations are implemented in Phase 1/3 as needed."""

    def __init__(self, path: Path) -> None:
        self.path = path

    def initialize(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self.path) as connection:
            connection.executescript(
                """
                PRAGMA foreign_keys = ON;

                CREATE TABLE IF NOT EXISTS source_candidates (
                    id TEXT PRIMARY KEY,
                    canonical_url TEXT NOT NULL UNIQUE,
                    status TEXT NOT NULL,
                    first_seen_at TEXT NOT NULL,
                    last_seen_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS discovery_records (
                    id TEXT PRIMARY KEY,
                    source_candidate_id TEXT NOT NULL,
                    origin_type TEXT NOT NULL,
                    origin_url TEXT NOT NULL,
                    discovered_at TEXT NOT NULL,
                    FOREIGN KEY (source_candidate_id) REFERENCES source_candidates(id),
                    UNIQUE (source_candidate_id, origin_type, origin_url)
                );

                CREATE TABLE IF NOT EXISTS validation_records (
                    id TEXT PRIMARY KEY,
                    source_candidate_id TEXT NOT NULL,
                    status TEXT NOT NULL,
                    stage TEXT NOT NULL,
                    checked_at TEXT NOT NULL,
                    latency_ms INTEGER,
                    detail TEXT,
                    FOREIGN KEY (source_candidate_id) REFERENCES source_candidates(id)
                );

                CREATE INDEX IF NOT EXISTS idx_validation_candidate_time
                    ON validation_records(source_candidate_id, checked_at DESC);
                """
            )
