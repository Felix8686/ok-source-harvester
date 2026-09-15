from pathlib import Path

from ok_source_harvester.domain import DiscoveryRecord, SourceCandidate
from ok_source_harvester.storage.sqlite import SQLiteRepository


def test_candidate_upsert_and_collector_state(tmp_path: Path) -> None:
    repository = SQLiteRepository(tmp_path / "test.db")
    repository.initialize()
    candidate = SourceCandidate(canonical_url="https://example.com/config.json")

    stored = repository.upsert_candidate(candidate)
    duplicate = repository.upsert_candidate(SourceCandidate(canonical_url=candidate.canonical_url))

    assert duplicate.id == stored.id
    repository.set_collector_state("github", "last_success_at", "2026-09-15T00:00:00+00:00")
    assert (
        repository.get_collector_state("github", "last_success_at")
        == "2026-09-15T00:00:00+00:00"
    )


def test_discovery_deduplicates_same_origin(tmp_path: Path) -> None:
    repository = SQLiteRepository(tmp_path / "test.db")
    repository.initialize()
    candidate = repository.upsert_candidate(
        SourceCandidate(canonical_url="https://example.com/config.json")
    )
    first = DiscoveryRecord(candidate.id, "github", "https://github.com/a/b")
    second = DiscoveryRecord(candidate.id, "github", "https://github.com/a/b")

    repository.add_discovery(first)
    repository.add_discovery(second)
