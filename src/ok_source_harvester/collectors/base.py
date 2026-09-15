from abc import ABC, abstractmethod
from collections.abc import AsyncIterator
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class DiscoveryItem:
    candidate_url: str
    origin_type: str
    origin_url: str


class Collector(ABC):
    """Uniform boundary for every discovery source."""

    @property
    @abstractmethod
    def name(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def collect(self) -> AsyncIterator[DiscoveryItem]:
        """Yield normalized candidate URLs plus discovery provenance."""
        raise NotImplementedError
