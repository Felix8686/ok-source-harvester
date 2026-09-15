from ok_source_harvester.domain import SourceCandidate, SourceStatus


def test_candidate_defaults_to_new() -> None:
    candidate = SourceCandidate(canonical_url="https://example.test/config.json")
    assert candidate.status is SourceStatus.NEW
    assert candidate.first_seen_at.tzinfo is not None
    assert candidate.last_seen_at.tzinfo is not None


def test_status_values_are_stable() -> None:
    assert {status.value for status in SourceStatus} == {
        "new",
        "valid",
        "degraded",
        "retry",
        "invalid",
    }
