# ok-source-harvester

Discover, deduplicate, validate, score, and export publicly shared OK影视 / TVBox source configurations.

## Current status

Phase 1 implements GitHub active discovery. It searches public GitHub code when an optional token is available, falls back to repository/README scanning without a token, extracts source-like URLs, canonicalizes duplicates, and persists provenance plus incremental collector state in SQLite.

No real source URLs are committed to this repository.

## Quick start

```bash
python -m venv .venv
pip install -e ".[dev]"
cp .env.example .env
python -m ok_source_harvester discover-github
```

`OSH_GITHUB_TOKEN` is optional, but authenticated code search materially improves coverage and rate limits. The token is read only from the environment and must never be committed.

## Quality checks

```bash
ruff check .
mypy src
pytest
```

## Development policy

Development happens on phase branches. `main` is not updated until a phase has passed CI and explicit review.
