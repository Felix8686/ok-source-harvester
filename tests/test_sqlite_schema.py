import sqlite3
from pathlib import Path

from ok_source_harvester.storage.sqlite import SQLiteRepository


def test_initialize_creates_core_tables(tmp_path: Path) -> None:
    db_path = tmp_path / "harvester.db"
    SQLiteRepository(db_path).initialize()

    with sqlite3.connect(db_path) as connection:
        names = {
            row[0]
            for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            ).fetchall()
        }

    assert {"source_candidates", "discovery_records", "validation_records"} <= names
