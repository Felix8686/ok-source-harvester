# Architecture

## Core data flow

```text
Collectors -> normalized DiscoveryItem -> candidate normalization/dedup -> Repository
                                                        |
                                                        v
                                               Validation pipeline
                                                        |
                                                        v
                                            history + current status
                                                        |
                                                        v
                                               scoring -> exporter
```

## Boundaries

### Collectors

Every discovery source implements a uniform `Collector` interface and emits a candidate URL plus provenance. GitHub and ordinary public web pages are the first two source families. Telegram, forums, and search engines remain later extensions.

### Domain

`SourceCandidate` is unique by canonical URL at persistence level. A URL may have many `DiscoveryRecord` rows, so repeated discovery from different pages or repositories increases provenance without duplicating the candidate. `ValidationRecord` is append-only history.

### Validation

Validation is intentionally progressive. Planned stages are:

1. HTTP reachability and response-type check.
2. JSON/config parsing.
3. OK影视/TVBox feature recognition.
4. Required/core field checks such as `sites`.
5. Endpoint liveness checks.
6. Search sampling.
7. Detail sampling.
8. Playback sampling.
9. Latency and stability statistics.

Each stage implements `Validator`; later stages can consume metadata produced by earlier stages without coupling collectors to playback logic.

### Storage

Phase 0 uses SQLite. All higher layers depend on the `Repository` boundary rather than SQLite details. PostgreSQL can therefore replace the implementation without changing collectors or validators.

### Scheduling/deployment

The target runtime is a Linux VPS. Scheduling remains outside core collection/validation logic so the same application can be invoked manually, by systemd timers, cron, or a later orchestration layer.

## Non-goals for Phase 0

- No Web UI.
- No Cloudflare dependency.
- No Telegram collector.
- No authenticated forum scraping.
- No browser automation.
- No AI classification.
- No large-scale crawl.
- No real source dataset committed to GitHub.
