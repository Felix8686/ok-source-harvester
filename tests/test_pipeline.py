from collections.abc import AsyncIterator
from pathlib import Path

import pytest

from ok_source_harvester.collectors.base import Collector, DiscoveryItem
from ok_source_harvester.pipeline import persist_discoveries
from ok_source_harvester.storage.sqlite import SQLiteRepository


class StaticCollector(Collector):
    @property
    def name(self) -> str:
        return "static"

    async def collect(self) -> AsyncIterator[DiscoveryItem]:
        yield DiscoveryItem(
            "https://github.com/a/b/blob/main/config.json",
            "static",
            "https://github.com/a/b",
        )
        yield DiscoveryItem(
            "https://raw.githubusercontent.com/a/b/main/config.json",
            "static",
            "https://github.com/c/d",
        )


@pytest.mark.asyncio
async def test_pipeline_canonicalizes_and_deduplicates_candidates(tmp_path: Path) -> None:
    repository = SQLiteRepository(tmp_path / "test.db")
    repository.initialize()

    stats = await persist_discoveries(StaticCollector(), repository)

    assert stats.observed == 2
    assert stats.new_candidates == 1
    assert stats.existing_candidates == 1
    assert (
        repository.get_candidate_by_url("https://raw.githubusercontent.com/a/b/main/config.json")
        is not None
    )
