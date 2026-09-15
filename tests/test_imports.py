def test_public_package_imports() -> None:
    import ok_source_harvester
    from ok_source_harvester.collectors.github import GitHubCollector
    from ok_source_harvester.collectors.web import WebCollector
    from ok_source_harvester.storage.sqlite import SQLiteRepository
    from ok_source_harvester.validators import Validator

    assert ok_source_harvester.SourceStatus.NEW.value == "new"
    assert GitHubCollector().name == "github"
    assert WebCollector().name == "web"
    assert SQLiteRepository is not None
    assert Validator is not None
