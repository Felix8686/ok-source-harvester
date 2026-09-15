from dataclasses import dataclass

from ok_source_harvester.collectors.base import Collector
from ok_source_harvester.common.urls import canonicalize_url
from ok_source_harvester.domain import DiscoveryRecord, SourceCandidate, utc_now
from ok_source_harvester.storage.base import Repository


@dataclass(frozen=True, slots=True)
class DiscoveryStats:
    observed: int = 0
    accepted: int = 0
    new_candidates: int = 0
    existing_candidates: int = 0


async def persist_discoveries(collector: Collector, repository: Repository) -> DiscoveryStats:
    observed = accepted = new_candidates = existing_candidates = 0
    async for item in collector.collect():
        observed += 1
        try:
            canonical = canonicalize_url(item.candidate_url)
        except ValueError:
            continue
        accepted += 1
        existing = repository.get_candidate_by_url(canonical)
        if existing is None:
            candidate = SourceCandidate(canonical_url=canonical)
            new_candidates += 1
        else:
            candidate = SourceCandidate(
                id=existing.id,
                canonical_url=existing.canonical_url,
                status=existing.status,
                first_seen_at=existing.first_seen_at,
                last_seen_at=utc_now(),
            )
            existing_candidates += 1
        stored = repository.upsert_candidate(candidate)
        repository.add_discovery(
            DiscoveryRecord(
                source_candidate_id=stored.id,
                origin_type=item.origin_type,
                origin_url=item.origin_url,
            )
        )
    return DiscoveryStats(
        observed=observed,
        accepted=accepted,
        new_candidates=new_candidates,
        existing_candidates=existing_candidates,
    )
