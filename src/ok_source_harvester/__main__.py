import argparse
import asyncio

from ok_source_harvester.collectors.github import GitHubCollector
from ok_source_harvester.pipeline import persist_discoveries
from ok_source_harvester.storage.sqlite import SQLiteRepository

from .config import get_settings


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="ok-source-harvester")
    parser.add_argument(
        "command",
        choices=("status", "discover-github"),
        nargs="?",
        default="status",
    )
    return parser


async def _discover_github() -> None:
    settings = get_settings()
    repository = SQLiteRepository(settings.sqlite_path())
    repository.initialize()
    collector = GitHubCollector(
        settings.github,
        token=settings.github_token,
        user_agent=settings.user_agent,
        timeout_seconds=settings.collector.request_timeout_seconds,
        state_store=repository,
    )
    stats = await persist_discoveries(collector, repository)
    print(
        "github discovery "
        f"observed={stats.observed} accepted={stats.accepted} "
        f"new={stats.new_candidates} existing={stats.existing_candidates} "
        f"rate_limited={collector.rate_limited}"
    )


def main() -> None:
    args = _parser().parse_args()
    settings = get_settings()
    if args.command == "discover-github":
        asyncio.run(_discover_github())
        return
    print(f"ok-source-harvester environment={settings.environment}")


if __name__ == "__main__":
    main()
