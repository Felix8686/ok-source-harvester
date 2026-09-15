import base64

import httpx
import pytest

from ok_source_harvester.collectors.github import GitHubCollector
from ok_source_harvester.config import GitHubCollectorSettings


class MemoryState:
    def __init__(self) -> None:
        self.values: dict[tuple[str, str], str] = {}

    def get_collector_state(self, collector_name: str, key: str) -> str | None:
        return self.values.get((collector_name, key))

    def set_collector_state(self, collector_name: str, key: str, value: str) -> None:
        self.values[(collector_name, key)] = value


def _response(request: httpx.Request, payload: object) -> httpx.Response:
    return httpx.Response(
        200,
        json=payload,
        headers={"x-ratelimit-remaining": "500"},
        request=request,
    )


@pytest.mark.asyncio
async def test_authenticated_code_search_extracts_source_url() -> None:
    async def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/search/code":
            return _response(
                request,
                {
                    "items": [
                        {
                            "html_url": "https://github.com/a/b/blob/main/README.md",
                            "text_matches": [
                                {"fragment": "TVBox配置 https://example.com/config.json"}
                            ],
                        }
                    ]
                },
            )
        if request.url.path == "/search/repositories":
            return _response(request, {"items": []})
        raise AssertionError(f"unexpected request: {request.url}")

    client = httpx.AsyncClient(
        base_url="https://api.github.com", transport=httpx.MockTransport(handler)
    )
    collector = GitHubCollector(
        GitHubCollectorSettings(search_queries=("TVBox",), max_pages=1),
        token="test-token",
        client=client,
    )
    items = [item async for item in collector.collect()]
    await client.aclose()

    assert [item.candidate_url for item in items] == ["https://example.com/config.json"]


@pytest.mark.asyncio
async def test_unauthenticated_repository_search_scans_readme() -> None:
    encoded = base64.b64encode("影视仓接口 https://example.net/box".encode()).decode()

    async def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/search/repositories":
            return _response(
                request,
                {
                    "items": [
                        {
                            "full_name": "owner/repo",
                            "default_branch": "main",
                            "html_url": "https://github.com/owner/repo",
                        }
                    ]
                },
            )
        if request.url.path == "/repos/owner/repo/readme":
            return _response(request, {"encoding": "base64", "content": encoded})
        if request.url.path == "/repos/owner/repo/git/trees/main":
            return _response(request, {"tree": []})
        raise AssertionError(f"unexpected request: {request.url}")

    state = MemoryState()
    client = httpx.AsyncClient(
        base_url="https://api.github.com", transport=httpx.MockTransport(handler)
    )
    collector = GitHubCollector(
        GitHubCollectorSettings(search_queries=("影视仓",), max_pages=1),
        state_store=state,
        client=client,
    )
    items = [item async for item in collector.collect()]
    await client.aclose()

    assert [item.candidate_url for item in items] == ["https://example.net/box"]
    assert state.get_collector_state("github", "last_success_at") is not None
