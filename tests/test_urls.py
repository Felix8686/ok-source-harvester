from ok_source_harvester.common.urls import canonicalize_url, extract_candidate_urls


def test_canonicalize_converts_github_blob_to_raw() -> None:
    result = canonicalize_url("HTTPS://GitHub.com/Foo/Bar/blob/main/config.json#readme")
    assert result == "https://raw.githubusercontent.com/Foo/Bar/main/config.json"


def test_extract_candidate_urls_filters_noise_and_deduplicates() -> None:
    text = """
    TVBox 配置：https://example.com/config.json
    duplicate https://example.com/config.json.
    badge https://example.com/logo.png
    unrelated https://example.com/about
    """
    assert list(extract_candidate_urls(text)) == ["https://example.com/config.json"]


def test_context_can_accept_extensionless_source() -> None:
    text = "影视仓接口地址：https://source.example.net/box"
    assert list(extract_candidate_urls(text)) == ["https://source.example.net/box"]
