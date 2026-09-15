import base64
import logging
from collections.abc import AsyncIterator, Iterable
from datetime import UTC, datetime
from typing import Any, cast

import httpx

from ok_source_harvester.common.urls import extract_candidate_urls
from ok_source_harvester.config import GitHubCollectorSettings
from ok_source_harvester.storage.base import CollectorStateStore

from .base import Collector, DiscoveryItem

_LOGGER = logging.getLogger(__name__)
_API_BASE = "https://api.github.com"


class GitHubCollector(Collector):
    """Discover source URLs from public GitHub code and repositories."""

    def __init__(
        self,
        settings: GitHubCollectorSettings | None = None,
        *,
        token: str | None = None,
        user_agent: str = "ok-source-harvester/0.1",
        timeout_seconds: float = 15.0,
        state_store: CollectorStateStore | None = None,
        client: httpx.AsyncClient | None = None,
    ) -> None:
        self.settings = settings or GitHubCollectorSettings()
        self.token = token or None
        self.user_agent = user_agent
        self.timeout_seconds = timeout_seconds
        self.state_store = state_store
        self.client = client
        self.rate_limited = False
        self.remaining_requests: int | None = None

    @property
    def name(self) -> str:
        return "github"

    async def collect(self) -> AsyncIterator[DiscoveryItem]:
        started_at = datetime.now(UTC)
        if self.state_store is not None:
            self.state_store.set_collector_state(
                self.name,
                "last_attempt_at",
                started_at.isoformat(),
            )

        if self.client is not None:
            async for item in self._collect(self.client):
                yield item
        else:
            async with httpx.AsyncClient(
                base_url=_API_BASE,
                timeout=self.timeout_seconds,
                headers=self._headers(),
                follow_redirects=True,
            ) as client:
                async for item in self._collect(client):
                    yield item

        if self.state_store is not None and not self.rate_limited:
            self.state_store.set_collector_state(
                self.name,
                "last_success_at",
                started_at.isoformat(),
            )

    def _headers(self) -> dict[str, str]:
        headers = {
            "Accept": "application/vnd.github+json, application/vnd.github.text-match+json",
            "User-Agent": self.user_agent,
            "X-GitHub-Api-Version": "2022-11-28",
        }
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    async def _collect(self, client: httpx.AsyncClient) -> AsyncIterator[DiscoveryItem]:
        seen: set[str] = set()
        for query in self.settings.search_queries:
            if self.rate_limited:
                break
            if self.token and self.settings.code_search_enabled:
                async for item in self._search_code(client, query):
                    if item.candidate_url not in seen:
                        seen.add(item.candidate_url)
                        yield item
            if self.rate_limited:
                break
            async for item in self._search_repositories(client, query):
                if item.candidate_url not in seen:
                    seen.add(item.candidate_url)
                    yield item

    async def _search_code(
        self, client: httpx.AsyncClient, query: str
    ) -> AsyncIterator[DiscoveryItem]:
        for page in range(1, self.settings.max_pages + 1):
            payload = await self._request_json(
                client,
                "/search/code",
                params={"q": f"{query} in:file", "per_page": self.settings.per_page, "page": page},
            )
            if payload is None:
                return
            items = _list_of_dicts(payload.get("items"))
            if not items:
                return
            for item in items:
                origin_url = _string(item.get("html_url"))
                fragments = _text_match_fragments(item.get("text_matches"))
                if not fragments:
                    content_url = _string(item.get("url"))
                    if content_url:
                        content = await self._fetch_content(client, content_url)
                        fragments = [content] if content else []
                for fragment in fragments:
                    for candidate in extract_candidate_urls(fragment):
                        yield DiscoveryItem(
                            candidate,
                            self.name,
                            origin_url or "github-code-search",
                        )
                if self.rate_limited:
                    return
            if len(items) < self.settings.per_page:
                return

    async def _search_repositories(
        self, client: httpx.AsyncClient, query: str
    ) -> AsyncIterator[DiscoveryItem]:
        incremental_query = self._incremental_repository_query(query)
        processed = 0
        for page in range(1, self.settings.max_pages + 1):
            payload = await self._request_json(
                client,
                "/search/repositories",
                params={
                    "q": f"{incremental_query} in:name,description,readme",
                    "sort": "updated",
                    "order": "desc",
                    "per_page": self.settings.per_page,
                    "page": page,
                },
            )
            if payload is None:
                return
            items = _list_of_dicts(payload.get("items"))
            if not items:
                return
            for repository in items:
                if processed >= self.settings.max_repositories_per_query:
                    return
                processed += 1
                full_name = _string(repository.get("full_name"))
                default_branch = _string(repository.get("default_branch")) or "main"
                html_url = _string(repository.get("html_url")) or "github-repository-search"
                if not full_name:
                    continue
                async for item in self._scan_repository(
                    client,
                    full_name=full_name,
                    default_branch=default_branch,
                    origin_url=html_url,
                ):
                    yield item
                if self.rate_limited:
                    return
            if len(items) < self.settings.per_page:
                return

    async def _scan_repository(
        self,
        client: httpx.AsyncClient,
        *,
        full_name: str,
        default_branch: str,
        origin_url: str,
    ) -> AsyncIterator[DiscoveryItem]:
        readme = await self._fetch_content(client, f"/repos/{full_name}/readme")
        if readme:
            for candidate in extract_candidate_urls(readme):
                yield DiscoveryItem(candidate, self.name, origin_url)
        if self.rate_limited:
            return

        tree = await self._request_json(
            client,
            f"/repos/{full_name}/git/trees/{default_branch}",
            params={"recursive": "1"},
        )
        if tree is None:
            return
        paths = self._candidate_paths(_list_of_dicts(tree.get("tree")))
        for path in paths[: self.settings.max_files_per_repository]:
            content = await self._fetch_content(client, f"/repos/{full_name}/contents/{path}")
            if content:
                file_origin = f"https://github.com/{full_name}/blob/{default_branch}/{path}"
                for candidate in extract_candidate_urls(content):
                    yield DiscoveryItem(candidate, self.name, file_origin)
            if self.rate_limited:
                return

    def _candidate_paths(self, tree_items: list[dict[str, Any]]) -> list[str]:
        scored: list[tuple[int, str]] = []
        for item in tree_items:
            if _string(item.get("type")) != "blob":
                continue
            path = _string(item.get("path"))
            if not path:
                continue
            lowered = path.lower()
            if not lowered.endswith((".md", ".txt", ".json", ".conf")):
                continue
            score = sum(term.lower() in lowered for term in self.settings.candidate_path_terms)
            if path.lower().startswith("readme"):
                score += 2
            if lowered.endswith(".json"):
                score += 1
            if score > 0:
                scored.append((score, path))
        scored.sort(key=lambda pair: (-pair[0], pair[1]))
        return [path for _, path in scored]

    def _incremental_repository_query(self, query: str) -> str:
        if self.state_store is None:
            return query
        value = self.state_store.get_collector_state(self.name, "last_success_at")
        if not value:
            return query
        try:
            day = datetime.fromisoformat(value).date().isoformat()
        except ValueError:
            return query
        return f"{query} pushed:>={day}"

    async def _fetch_content(self, client: httpx.AsyncClient, url: str) -> str | None:
        payload = await self._request_json(client, url)
        if payload is None:
            return None
        encoded = _string(payload.get("content"))
        encoding = _string(payload.get("encoding"))
        if not encoded or encoding != "base64":
            return None
        try:
            return base64.b64decode(encoded, validate=False).decode("utf-8", errors="replace")
        except (ValueError, TypeError):
            return None

    async def _request_json(
        self,
        client: httpx.AsyncClient,
        url: str,
        *,
        params: dict[str, str | int] | None = None,
    ) -> dict[str, Any] | None:
        if self.rate_limited:
            return None
        try:
            response = await client.get(url, params=params, headers=self._headers())
        except httpx.HTTPError as exc:
            _LOGGER.warning("GitHub request failed: %s", exc)
            return None

        self._update_rate_limit(response)
        if response.status_code in {403, 429}:
            if response.headers.get("x-ratelimit-remaining") == "0" or response.status_code == 429:
                self.rate_limited = True
            _LOGGER.warning("GitHub API throttled request: status=%s", response.status_code)
            return None
        if response.status_code in {404, 409, 422}:
            return None
        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            _LOGGER.warning("GitHub API error: %s", exc)
            return None
        parsed = cast(object, response.json())
        if not isinstance(parsed, dict):
            return None
        return cast(dict[str, Any], parsed)

    def _update_rate_limit(self, response: httpx.Response) -> None:
        remaining = response.headers.get("x-ratelimit-remaining")
        if remaining is None:
            return
        try:
            self.remaining_requests = int(remaining)
        except ValueError:
            return
        if self.remaining_requests <= self.settings.rate_limit_reserve:
            self.rate_limited = True


def _list_of_dicts(value: object) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    return [cast(dict[str, Any], item) for item in value if isinstance(item, dict)]


def _string(value: object) -> str | None:
    return value if isinstance(value, str) else None


def _text_match_fragments(value: object) -> list[str]:
    fragments: list[str] = []
    for item in _iter_dicts(value):
        fragment = _string(item.get("fragment"))
        if fragment:
            fragments.append(fragment)
    return fragments


def _iter_dicts(value: object) -> Iterable[dict[str, Any]]:
    return _list_of_dicts(value)
