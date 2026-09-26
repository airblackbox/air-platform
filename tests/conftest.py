"""Integration test fixtures for AIR Platform.

These tests run against the live Docker Compose stack (`make up`). If the
stack is not running, the whole suite is skipped with a clear message —
unless AIR_REQUIRE_STACK=1 is set (used in CI), in which case an unreachable
stack is a hard failure.

Settings come from real environment variables first, then from the repo's
`.env` file (the same file Docker Compose reads), so a GATEWAY_KEY or
OPENAI_API_KEY set there is picked up without exporting it in your shell.
"""

import os
from pathlib import Path

import httpx
import pytest


def _load_dotenv(path: Path) -> None:
    """Load simple KEY=value lines from a .env file.

    Real environment variables always win. Supports comments, blank lines,
    an optional `export ` prefix, quoted values, and ` # inline comments`
    after unquoted values — the subset Docker Compose users typically write.
    """
    if not path.is_file():
        return
    for raw in path.read_text().splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        line = line.removeprefix("export ")
        key, value = line.split("=", 1)
        key, value = key.strip(), value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]
        elif " #" in value:
            value = value.split(" #", 1)[0].rstrip()
        os.environ.setdefault(key, value)


_load_dotenv(Path(__file__).resolve().parent.parent / ".env")

GATEWAY_URL = os.environ.get("GATEWAY_URL", "http://localhost:8080")
JAEGER_URL = os.environ.get("JAEGER_URL", "http://localhost:16686")
MINIO_URL = os.environ.get("MINIO_URL", "http://localhost:9000")

REQUIRE_STACK = os.environ.get("AIR_REQUIRE_STACK") == "1"


def _stack_reachable() -> bool:
    try:
        httpx.get(f"{GATEWAY_URL}/health", timeout=5)
        return True
    except httpx.TransportError:
        return False


@pytest.fixture(scope="session", autouse=True)
def require_stack():
    if not _stack_reachable():
        msg = (
            f"AIR stack not reachable at {GATEWAY_URL}. "
            "Start it with `make up` (or `docker compose up -d`)."
        )
        if REQUIRE_STACK:
            pytest.fail(msg)
        pytest.skip(msg)


@pytest.fixture
def gateway_url():
    return GATEWAY_URL


@pytest.fixture
def gateway_headers():
    """X-Gateway-Key header when the gateway requires one, else nothing."""
    key = os.environ.get("GATEWAY_KEY", "")
    return {"X-Gateway-Key": key} if key else {}


@pytest.fixture
def jaeger_url():
    return JAEGER_URL


@pytest.fixture
def minio_url():
    return MINIO_URL


@pytest.fixture
def openai_api_key():
    key = os.environ.get("OPENAI_API_KEY", "")
    if not key or key.startswith("sk-..."):
        pytest.skip("OPENAI_API_KEY not set — skipping live LLM round-trip")
    return key
