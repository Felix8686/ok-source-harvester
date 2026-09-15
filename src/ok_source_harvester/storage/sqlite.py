import sqlite3
from dataclasses import replace
from datetime import datetime
from pathlib import Path
from uuid import UUID

from ok_source_harvester.domain import (
    DiscoveryRecord,
    SourceCandidate,
    SourceStatus,
    ValidationRecord,
)


class SQLiteRepository:
    """Small SQLite persistence adapter used by the single-node VPS deployment."""

    def __init__(self, path: Path) -> None:
        self.path = path

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        return connection

    def initialize(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as connection:
            connection.executescript(
                """
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

                CREATE TABLE IF NOT EXISTS collector_state (
                    collector_name TEXT NOT NULL,
                    state_key TEXT NOT NULL,
                    state_value TEXT NOT NULL,
                    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (collector_name, state_key)
                );

                CREATE INDEX IF NOT EXISTS idx_validation_candidate_time
                    ON validation_records(source_candidate_id, checked_at DESC);
                """
            )

    def upsert_candidate(self, candidate: SourceCandidate) -> SourceCandidate:
        existing = self.get_candidate_by_url(candidate.canonical_url)
        if existing is None:
            with self._connect() as connection:
                connection.execute(
                    """
                    INSERT INTO source_candidates
                        (id, canonical_url, status, first_seen_at, last_seen_at)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        str(candidate.id),
                        candidate.canonical_url,
                        candidate.status.value,
                        candidate.first_seen_at.isoformat(),
                        candidate.last_seen_at.isoformat(),
                    ),
                )
            return candidate

        last_seen_at = max(existing.last_seen_at, candidate.last_seen_at)
        if last_seen_at != existing.last_seen_at:
            with self._connect() as connection:
                connection.execute(
                    "UPDATE source_candidates SET last_seen_at = ? WHERE id = ?",
                    (last_seen_at.isoformat(), str(existing.id)),
                )
        return replace(existing, last_seen_at=last_seen_at)

    def get_candidate_by_url(self, canonical_url: str) -> SourceCandidate | None:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT * FROM source_candidates WHERE canonical_url = ?", (canonical_url,)
            ).fetchone()
        if row is None:
            return None
        return SourceCandidate(
            id=UUID(str(row["id"])),
            canonical_url=str(row["canonical_url"]),
            status=SourceStatus(str(row["status"])),
            first_seen_at=datetime.fromisoformat(str(row["first_seen_at"])),
            last_seen_at=datetime.fromisoformat(str(row["last_seen_at"])),
        )

    def add_discovery(self, record: DiscoveryRecord) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                INSERT OR IGNORE INTO discovery_records
                    (id, source_candidate_id, origin_type, origin_url, discovered_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    str(record.id),
                    str(record.source_candidate_id),
                    record.origin_type,
                    record.origin_url,
                    record.discovered_at.isoformat(),
                ),
            )

    def add_validation(self, record: ValidationRecord) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO validation_records
                    (id, source_candidate_id, status, stage, checked_at, latency_ms, detail)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    str(record.id),
                    str(record.source_candidate_id),
                    record.status.value,
                    record.stage,
                    record.checked_at.isoformat(),
                    record.latency_ms,
                    record.detail,
                ),
            )

    def list_validations(self, source_candidate_id: UUID) -> list[ValidationRecord]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT * FROM validation_records
                WHERE source_candidate_id = ?
                ORDER BY checked_at DESC
                """,
                (str(source_candidate_id),),
            ).fetchall()
        return [
            ValidationRecord(
                id=UUID(str(row["id"])),
                source_candidate_id=UUID(str(row["source_candidate_id"])),
                status=SourceStatus(str(row["status"])),
                stage=str(row["stage"]),
                checked_at=datetime.fromisoformat(str(row["checked_at"])),
                latency_ms=int(row["latency_ms"]) if row["latency_ms"] is not None else None,
                detail=str(row["detail"]) if row["detail"] is not None else None,
            )
            for row in rows
        ]

    def get_collector_state(self, collector_name: str, key: str) -> str | None:
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT state_value FROM collector_state
                WHERE collector_name = ? AND state_key = ?
                """,
                (collector_name, key),
            ).fetchone()
        return None if row is None else str(row["state_value"])

    def set_collector_state(self, collector_name: str, key: str, value: str) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO collector_state (collector_name, state_key, state_value, updated_at)
                VALUES (?, ?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(collector_name, state_key)
                DO UPDATE SET state_value = excluded.state_value, updated_at = CURRENT_TIMESTAMP
                """,
                (collector_name, key, value),
            )
