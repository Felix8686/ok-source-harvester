from collections.abc import AsyncIterator

from .base import Collector, DiscoveryItem


class GitHubCollector(Collector):
    """Phase 1 placeholder for GitHub public-code/repository discovery."""

    @property
    def name(self) -> str:
        return "github"

    async def collect(self) -> AsyncIterator[DiscoveryItem]:
        if False:  # keeps this an async generator until Phase 1 adds discovery logic
            yield DiscoveryItem("", self.name, "")
