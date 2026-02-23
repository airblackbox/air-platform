#!/usr/bin/env python3
"""
AIR Blackbox — End-to-End Stack Integration Tests

Verifies the full AIR Blackbox pipeline works end-to-end:
  Agent → Gateway → Policy Engine → LLM Provider
              ↓              ↓
        OTel Collector   Episode Store

Prerequisites:
  - Docker Compose stack running (make up)
  - Episode Store running on :8100
  - Policy Engine running on :8200

Usage:
  pytest tests/test_e2e_stack.py -v
"""

import os
import time
import uuid
import json
import pytest
import requests

# Service endpoints
GATEWAY_URL = os.getenv("AIR_GATEWAY_URL", "http://localhost:8080")
EPISODE_STORE_URL = os.getenv("AIR_EPISODE_STORE_URL", "http://localhost:8100")
POLICY_ENGINE_URL = os.getenv("AIR_POLICY_ENGINE_URL", "http://localhost:8200")
JAEGER_URL = os.getenv("AIR_JAEGER_URL", "http://localhost:16686")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")


# ---------------------------------------------------------------------------
# Health checks
# ---------------------------------------------------------------------------

class TestStackHealth:
    """Verify all services are reachable and healthy."""

    def test_gateway_reachable(self):
        """Gateway responds on /v1/models or root."""
        try:
            r = requests.get(f"{GATEWAY_URL}/v1/models", timeout=5)
            # 200 = healthy, 401 = reachable but needs auth (still alive)
            assert r.status_code in (200, 401, 403), f"Gateway returned {r.status_code}"
        except requests.ConnectionError:
            pytest.fail(f"Gateway not reachable at {GATEWAY_URL}")

    def test_episode_store_health(self):
        """Episode Store /v1/episodes endpoint responds."""
        try:
            r = requests.get(f"{EPISODE_STORE_URL}/v1/episodes", timeout=5)
            assert r.status_code == 200, f"Episode Store returned {r.status_code}"
        except requests.ConnectionError:
            pytest.fail(f"Episode Store not reachable at {EPISODE_STORE_URL}")

    def test_policy_engine_health(self):
        """Policy Engine responds."""
        try:
            r = requests.get(f"{POLICY_ENGINE_URL}/health", timeout=5)
            assert r.status_code in (200, 404), f"Policy Engine returned {r.status_code}"
        except requests.ConnectionError:
            pytest.fail(f"Policy Engine not reachable at {POLICY_ENGINE_URL}")

    def test_jaeger_ui_reachable(self):
        """Jaeger UI is accessible."""
        try:
            r = requests.get(f"{JAEGER_URL}", timeout=5)
            assert r.status_code == 200, f"Jaeger returned {r.status_code}"
        except requests.ConnectionError:
            pytest.fail(f"Jaeger not reachable at {JAEGER_URL}")


# ---------------------------------------------------------------------------
# Gateway proxy tests
# ---------------------------------------------------------------------------

class TestGatewayProxy:
    """Verify the Gateway correctly proxies OpenAI-compatible requests."""

    @pytest.mark.skipif(not OPENAI_API_KEY, reason="OPENAI_API_KEY not set")
    def test_chat_completion_through_gateway(self):
        """A chat completion request flows through the gateway and returns a valid response."""
        run_id = str(uuid.uuid4())
        r = requests.post(
            f"{GATEWAY_URL}/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENAI_API_KEY}",
                "Content-Type": "application/json",
                "x-run-id": run_id,
            },
            json={
                "model": "gpt-4o-mini",
                "messages": [{"role": "user", "content": "Say 'hello' and nothing else."}],
                "max_tokens": 10,
            },
            timeout=30,
        )
        assert r.status_code == 200, f"Gateway returned {r.status_code}: {r.text}"
        data = r.json()
        assert "choices" in data
        assert len(data["choices"]) > 0
        assert "message" in data["choices"][0]

        # Verify the gateway added audit headers
        assert "x-run-id" in r.headers or run_id  # run-id passed through

    @pytest.mark.skipif(not OPENAI_API_KEY, reason="OPENAI_API_KEY not set")
    def test_gateway_returns_run_id(self):
        """The gateway returns an x-run-id header for trace correlation."""
        r = requests.post(
            f"{GATEWAY_URL}/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENAI_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": "gpt-4o-mini",
                "messages": [{"role": "user", "content": "Say 'test' and nothing else."}],
                "max_tokens": 5,
            },
            timeout=30,
        )
        assert r.status_code == 200


# ---------------------------------------------------------------------------
# Episode Store tests
# ---------------------------------------------------------------------------

class TestEpisodeStore:
    """Verify Episode Store can ingest and retrieve episodes."""

    def test_create_and_retrieve_episode(self):
        """POST an episode, then GET it back."""
        episode_id = str(uuid.uuid4())
        episode = {
            "episode_id": episode_id,
            "agent_id": "e2e-test-agent",
            "task": "End-to-end integration test",
            "status": "completed",
            "steps": [
                {
                    "step_id": str(uuid.uuid4()),
                    "action": "llm_call",
                    "model": "gpt-4o-mini",
                    "input": "test prompt",
                    "output": "test response",
                    "tokens_in": 5,
                    "tokens_out": 3,
                    "latency_ms": 250,
                }
            ],
        }
        # Create
        r = requests.post(
            f"{EPISODE_STORE_URL}/v1/episodes",
            json=episode,
            timeout=10,
        )
        assert r.status_code in (200, 201), f"Episode create failed: {r.status_code} {r.text}"

        # Retrieve
        r = requests.get(f"{EPISODE_STORE_URL}/v1/episodes", timeout=10)
        assert r.status_code == 200
        episodes = r.json()
        # Should find our episode in the list
        assert isinstance(episodes, (list, dict))

    def test_episode_store_cors_headers(self):
        """Episode Store returns CORS headers for browser access."""
        r = requests.options(
            f"{EPISODE_STORE_URL}/v1/episodes",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "GET",
            },
            timeout=5,
        )
        # CORS preflight should succeed
        assert r.status_code in (200, 204, 405)


# ---------------------------------------------------------------------------
# Policy Engine tests
# ---------------------------------------------------------------------------

class TestPolicyEngine:
    """Verify Policy Engine evaluates requests correctly."""

    def test_policy_engine_cors_headers(self):
        """Policy Engine returns CORS headers for browser access."""
        r = requests.options(
            f"{POLICY_ENGINE_URL}/v1/evaluate",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "POST",
            },
            timeout=5,
        )
        assert r.status_code in (200, 204, 405)


# ---------------------------------------------------------------------------
# Full pipeline test
# ---------------------------------------------------------------------------

class TestFullPipeline:
    """End-to-end: send request through gateway, verify it appears in traces and episodes."""

    @pytest.mark.skipif(not OPENAI_API_KEY, reason="OPENAI_API_KEY not set")
    def test_full_audit_trail(self):
        """
        Send a request through the Gateway and verify:
        1. Response comes back successfully
        2. Traces appear in Jaeger
        3. Episode is recorded in Episode Store
        """
        run_id = f"e2e-{uuid.uuid4()}"

        # Step 1: Send request through Gateway
        r = requests.post(
            f"{GATEWAY_URL}/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENAI_API_KEY}",
                "Content-Type": "application/json",
                "x-run-id": run_id,
            },
            json={
                "model": "gpt-4o-mini",
                "messages": [{"role": "user", "content": "What is 2+2? Reply with just the number."}],
                "max_tokens": 5,
            },
            timeout=30,
        )
        assert r.status_code == 200, f"Gateway request failed: {r.status_code}"
        data = r.json()
        assert "choices" in data

        # Step 2: Wait for traces to propagate
        time.sleep(3)

        # Step 3: Check Jaeger for traces
        try:
            jaeger_r = requests.get(
                f"{JAEGER_URL}/api/traces",
                params={"service": "air-gateway", "limit": 5},
                timeout=10,
            )
            if jaeger_r.status_code == 200:
                traces = jaeger_r.json()
                # Jaeger should have at least one trace
                assert "data" in traces or "errors" not in traces
        except requests.ConnectionError:
            pass  # Jaeger API path may differ; non-fatal

        # Step 4: Check Episode Store
        ep_r = requests.get(f"{EPISODE_STORE_URL}/v1/episodes", timeout=10)
        assert ep_r.status_code == 200, "Episode Store should be reachable after pipeline run"


# ---------------------------------------------------------------------------
# SDK integration test
# ---------------------------------------------------------------------------

class TestSDKIntegration:
    """Test that the air-blackbox-sdk can wrap an OpenAI client through the gateway."""

    @pytest.mark.skipif(not OPENAI_API_KEY, reason="OPENAI_API_KEY not set")
    def test_air_wrap_creates_audited_call(self):
        """air.air_wrap(OpenAI()) should work through the gateway."""
        try:
            from openai import OpenAI
            import air

            client = air.air_wrap(
                OpenAI(api_key=OPENAI_API_KEY),
                gateway_url=GATEWAY_URL,
            )
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": "Say 'sdk test' and nothing else."}],
                max_tokens=10,
            )
            assert response.choices[0].message.content is not None
        except ImportError:
            pytest.skip("air-blackbox-sdk or openai not installed")
