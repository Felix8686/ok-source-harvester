# Roadmap

## Phase 0 — Bootstrap — COMPLETE

- Package layout, domain models, configuration, SQLite schema, CI, tests, architecture docs.

## Phase 1 — GitHub active discovery — IMPLEMENTED / VERIFYING

- Authenticated GitHub code search when a token is available.
- Tokenless repository search and README/candidate-file scanning fallback.
- Source URL extraction and canonicalization.
- Candidate deduplication while preserving multiple discovery origins.
- SQLite collector state for overlap-safe incremental repository searches.
- Rate-limit reserve protection; never sleep indefinitely waiting for GitHub reset.

## Phase 2 — Public web discovery

- Seed discovery and bounded crawling of ordinary public pages.
- Domain throttling, robots/policy handling, content extraction, provenance.

## Phase 3 — OK影视 / TVBox validation

- HTTP reachability and response classification.
- Config structure and feature detection.
- Site/search/detail/playback probes.

## Phase 4 — Scoring and lifecycle

- Reliability history, latency, failure decay, retry/quarantine policy.

## Phase 5 — Export

- Stable ranked source list and machine-consumable subscription output.

## Phase 6 — Extended discovery

- Public Telegram channels, forums and search-engine discovery where policy and access permit.
