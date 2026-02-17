"""Integration test fixtures for AIR Platform."""

import os
import pytest
import httpx

GATEWAY_URL = os.environ.get("GATEWAY_URL", "http://localhost:8080")
EPISODE_STORE_URL = os.environ.get("EPISODE_STORE_URL", "http://localhost:8100")
POLICY_ENGINE_URL = os.environ.get("POLICY_ENGINE_URL", "http://localhost:8200")


@pytest.fixture
def gateway_url():
    return GATEWAY_URL


@pytest.fixture
def store_url():
    return EPISODE_STORE_URL


@pytest.fixture
def policy_url():
    return POLICY_ENGINE_URL


@pytest.fixture
def sample_episode():
    """A minimal episode to ingest into the store."""
    return {
        "agent_id": "integration-test-agent",
        "task": "test-integration-flow",
        "status": "success",
        "model": "gpt-4o-mini",
        "total_tokens": 150,
        "total_cost_usd": 0.002,
        "steps": [
            {
                "step_type": "llm_call",
                "model": "gpt-4o-mini",
                "input_tokens": 100,
                "output_tokens": 50,
                "cost_usd": 0.002,
                "duration_ms": 450,
                "provider": "openai",
            }
        ],
    }


@pytest.fixture
def sample_policy():
    """A basic policy for testing enforcement."""
    return {
        "id": "integration-test-policy",
        "name": "Integration Test Policy",
        "description": "Policy for integration testing",
        "autonomy_tier": "gated",
        "tool_risks": [
            {"tool_name": "dangerous_tool", "risk_tier": "critical", "requires_approval": True}
        ],
        "kill_switches": [
            {"switch_type": "spend_usd", "limit_type": "absolute", "threshold": 10.0, "action": "halt", "enabled": True}
        ],
        "conditions": [
            {"field": "tool_name", "operator": "eq", "value": "blocked_tool", "action": "deny", "reason": "Tool is blocked by policy"}
        ],
    }
