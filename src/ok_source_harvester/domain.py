from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from uuid import UUID, uuid4


def utc_now() -> datetime:
    return datetime.now(UTC)


class SourceStatus(StrEnum):
    NEW = "new"
    VALID = "valid"
    DEGRADED = "degraded"
    RETRY = "retry"
    INVALID = "invalid"


@dataclass(frozen=True, slots=True)
class SourceCandidate:
    canonical_url: str
    id: UUID = field(default_factory=uuid4)
    status: SourceStatus = SourceStatus.NEW
    first_seen_at: datetime = field(default_factory=utc_now)
    last_seen_at: datetime = field(default_factory=utc_now)


@dataclass(frozen=True, slots=True)
class DiscoveryRecord:
    source_candidate_id: UUID
    origin_type: str
    origin_url: str
    discovered_at: datetime = field(default_factory=utc_now)
    id: UUID = field(default_factory=uuid4)


@dataclass(frozen=True, slots=True)
class ValidationRecord:
    source_candidate_id: UUID
    status: SourceStatus
    stage: str
    checked_at: datetime = field(default_factory=utc_now)
    latency_ms: int | None = None
    detail: str | None = None
    id: UUID = field(default_factory=uuid4)
