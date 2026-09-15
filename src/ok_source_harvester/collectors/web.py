from collections.abc import AsyncIterator

from .base import Collector, DiscoveryItem


class WebCollector(Collector):
    """Phase 2 placeholder for public web-page discovery."""

    @property
    def name(self) -> str:
        return "web"

    async def collect(self) -> AsyncIterator[DiscoveryItem]:
        if False:
            yield DiscoveryItem("", self.name, "")
