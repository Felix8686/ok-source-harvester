# Roadmap

## Phase 0 — Bootstrap

Engineering skeleton, domain contracts, configuration, storage boundary, tests, CI, and architecture documentation.

## Phase 1 — GitHub active discovery

Discover public candidate configuration URLs from GitHub, normalize URLs, deduplicate candidates, preserve provenance, implement rate-limit-aware incremental collection, and persist results.

## Phase 2 — Public web discovery

Crawl an allowlisted/seeded public web frontier, extract candidate URLs, constrain crawl scope, and reuse the same dedup/provenance path.

## Phase 3 — OK影视/TVBox validator

Implement progressive HTTP/config/feature/API/search/detail/playback validation with retry and failure classification.

## Phase 4 — Scoring and lifecycle

Calculate quality/reliability scores, distinguish degraded from dead sources, schedule rechecks, and retire persistently invalid candidates without losing history.

## Phase 5 — Export

Generate deterministic valid-source outputs suitable for downstream OK影视 usage, with freshness metadata and safe atomic publication.

## Phase 6 — Discovery expansion

Evaluate Telegram public channels, public forums, and search-engine discovery based on coverage gained versus maintenance cost.
