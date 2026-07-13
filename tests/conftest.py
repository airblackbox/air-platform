"""Integration test fixtures for AIR Platform.

These tests run against the live Docker Compose stack (`make up`). If the
stack is not running, the whole suite is skipped with a clear message —
unless AIR_REQUIRE_STACK=1 is set (used in CI), in which case an unreachable
stack is a hard failure.
"""

import os

import httpx
import pytest

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
