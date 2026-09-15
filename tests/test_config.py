from ok_source_harvester.config import Settings


def test_nested_environment_configuration(monkeypatch) -> None:
    monkeypatch.setenv("OSH_ENVIRONMENT", "test")
    monkeypatch.setenv("OSH_COLLECTOR__CONCURRENCY", "3")

    settings = Settings(_env_file=None)

    assert settings.environment == "test"
    assert settings.collector.concurrency == 3
