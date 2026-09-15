from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

from ok_source_harvester.domain import SourceCandidate, SourceStatus


@dataclass(frozen=True, slots=True)
class ValidationContext:
    candidate: SourceCandidate
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class ValidationResult:
    stage: str
    status: SourceStatus
    latency_ms: int | None = None
    detail: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


class Validator(ABC):
    """One stage in the future progressive validation pipeline."""

    @property
    @abstractmethod
    def stage(self) -> str:
        raise NotImplementedError

    @abstractmethod
    async def validate(self, context: ValidationContext) -> ValidationResult:
        raise NotImplementedError
