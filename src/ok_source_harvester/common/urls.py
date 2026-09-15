import re
from collections.abc import Iterator
from urllib.parse import SplitResult, urlsplit, urlunsplit

_URL_RE = re.compile(r"https?://[^\s<>\"'`]+", re.IGNORECASE)
_TRAILING_PUNCTUATION = ".,;:!?)]}，。；：！？）》】"
_CONTEXT_TERMS = (
    "tvbox",
    "ok影视",
    "影视仓",
    "猫影视",
    "catvod",
    "配置",
    "接口",
    "点播源",
    "源地址",
)
_URL_TERMS = ("tvbox", "catvod", "config", "source", "api", "box", "接口", "影视")
_REJECTED_SUFFIXES = (
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".svg",
    ".webp",
    ".ico",
    ".mp4",
    ".mp3",
    ".zip",
    ".7z",
    ".rar",
    ".apk",
    ".jar",
)
_STRONG_SUFFIXES = (".json", ".txt", ".conf")


def canonicalize_url(raw_url: str) -> str:
    """Normalize a discovered URL without removing query parameters that may be functional."""
    cleaned = raw_url.strip().rstrip(_TRAILING_PUNCTUATION)
    parsed = urlsplit(cleaned)
    if parsed.scheme.lower() not in {"http", "https"} or not parsed.hostname:
        raise ValueError(f"unsupported candidate URL: {raw_url!r}")
    if parsed.username or parsed.password:
        raise ValueError("credential-bearing URLs are not accepted")

    scheme = parsed.scheme.lower()
    hostname = parsed.hostname.lower()
    try:
        port = parsed.port
    except ValueError as exc:
        raise ValueError("invalid URL port") from exc
    if port is not None and not ((scheme == "http" and port == 80) or (scheme == "https" and port == 443)):
        netloc = f"{hostname}:{port}"
    else:
        netloc = hostname

    normalized = SplitResult(scheme, netloc, parsed.path or "/", parsed.query, "")
    normalized = _github_blob_to_raw(normalized)
    return urlunsplit(normalized)


def _github_blob_to_raw(parsed: SplitResult) -> SplitResult:
    if parsed.hostname != "github.com":
        return parsed
    parts = parsed.path.strip("/").split("/")
    if len(parts) < 5 or parts[2] != "blob":
        return parsed
    owner, repo, _, ref, *rest = parts
    raw_path = "/" + "/".join((owner, repo, ref, *rest))
    return SplitResult("https", "raw.githubusercontent.com", raw_path, parsed.query, "")


def looks_like_source_url(url: str, context: str = "") -> bool:
    try:
        parsed = urlsplit(canonicalize_url(url))
    except ValueError:
        return False

    lowered_path = parsed.path.lower()
    if lowered_path.endswith(_REJECTED_SUFFIXES):
        return False
    if parsed.hostname == "github.com":
        return False
    if lowered_path.endswith(_STRONG_SUFFIXES):
        return True

    url_text = f"{parsed.hostname}{parsed.path}?{parsed.query}".lower()
    if any(term in url_text for term in _URL_TERMS):
        return True

    lowered_context = context.lower()
    return any(term in lowered_context for term in _CONTEXT_TERMS)


def extract_candidate_urls(text: str, context_radius: int = 180) -> Iterator[str]:
    """Yield source-like URLs from arbitrary GitHub text while preserving first-seen order."""
    seen: set[str] = set()
    for match in _URL_RE.finditer(text):
        raw_url = match.group(0).rstrip(_TRAILING_PUNCTUATION)
        start = max(0, match.start() - context_radius)
        end = min(len(text), match.end() + context_radius)
        context = text[start:end]
        try:
            canonical = canonicalize_url(raw_url)
        except ValueError:
            continue
        if canonical in seen or not looks_like_source_url(canonical, context):
            continue
        seen.add(canonical)
        yield canonical
