# Architecture Decisions

## ADR-001: Python as the primary runtime

Status: accepted.

Reason: mature HTTP/crawling ecosystem, low VPS operational cost, straightforward async networking, and strong test/tooling support.

## ADR-002: SQLite first, Repository boundary from day one

Status: accepted.

Reason: the initial workload does not require a database service. A repository interface keeps domain and collection logic independent so PostgreSQL remains a migration option if concurrency or dataset size justifies it.

## ADR-003: Progressive validation rather than binary URL health checks

Status: accepted.

Reason: an HTTP 200 response does not prove an OK影视/TVBox source is usable. Validation must eventually test structure and representative application behavior.

## ADR-004: Preserve discovery and validation history

Status: accepted.

Reason: provenance and historical stability are useful signals for ranking and troubleshooting. Current state alone loses those signals.

## ADR-005: No real harvested source dataset in the code repository

Status: accepted.

Reason: source data is runtime data. Keeping it out of Git reduces repository noise and separates code review from collected third-party content.
