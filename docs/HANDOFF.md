# Handoff

## Current phase

Phase 0 bootstrap implemented on `dev/bootstrap`.

## Implemented

- Python package and development tooling.
- Domain models for candidates, discoveries, validation history, and lifecycle status.
- Collector and Validator extension boundaries.
- GitHub/Web collector placeholders only; no real harvesting logic yet.
- Repository protocol and SQLite schema bootstrap.
- Environment-based configuration with nested collector/validator settings.
- Unit tests for domain defaults, configuration, imports, and SQLite schema.
- CI definition for lint, type check, and tests.
- Architecture decisions and phased roadmap.

## Next entry point

Phase 1 should implement GitHub active discovery without changing the public Collector contract unless implementation evidence requires it. It should add URL canonicalization/dedup persistence and rate-limit-aware incremental state.

## Verification expected on a real environment

```bash
python -m venv .venv
pip install -e ".[dev]"
ruff check .
mypy src
pytest
```

Do not merge to `main` until those checks pass in a clean environment.
