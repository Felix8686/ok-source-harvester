# Handoff

## Current phase

Phase 1 GitHub active discovery implemented on `dev/phase1-github-discovery`; awaiting clean CI and runtime verification.

## Implemented

- GitHub authenticated code search plus tokenless repository-search fallback.
- README and bounded candidate-file scanning.
- Context-aware source URL extraction with GitHub blob-to-raw canonicalization.
- Candidate deduplication with multiple provenance records preserved.
- Full SQLite candidate/discovery operations and collector state.
- Incremental repository query overlap based on last successful run.
- GitHub rate-limit reserve protection.
- `python -m ok_source_harvester discover-github` CLI entry point.
- Unit tests for extraction, persistence, collector modes and pipeline deduplication.

## Safety / scope

- Only public GitHub content is read.
- No credentials are persisted in source control.
- No discovered real source addresses are committed to the repository.
- Phase 1 discovers candidates but does not claim they are valid; validation belongs to Phase 3.

## Next entry point

After CI and a real GitHub run pass, Phase 2 can add ordinary public-web discovery while keeping the existing Collector contract.
