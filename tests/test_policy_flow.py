"""IT-3: Test policy CRUD and evaluation flow."""

import httpx
import pytest


class TestPolicyFlow:
    """End-to-end policy lifecycle: create → evaluate → check enforcement."""

    @pytest.mark.asyncio
    async def test_create_policy(self, policy_url, sample_policy):
        """Create a policy."""
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{policy_url}/v1/policies",
                json=sample_policy,
            )
            assert resp.status_code == 200
            data = resp.json()
            assert data.get("id") == "integration-test-policy"

    @pytest.mark.asyncio
    async def test_list_policies(self, policy_url):
        """List all policies and find ours."""
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{policy_url}/v1/policies")
            assert resp.status_code == 200
            policies = resp.json()
            assert len(policies) >= 1

    @pytest.mark.asyncio
    async def test_evaluate_safe_action(self, policy_url):
        """Evaluate a safe action — should be allowed."""
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{policy_url}/v1/evaluate",
                json={
                    "agent_id": "integration-test-agent",
                    "action": "safe_tool",
                    "context": {"autonomy_tier": "gated"},
                },
            )
            assert resp.status_code == 200
            data = resp.json()
            assert data.get("allowed") in (True, None) or data.get("action") in ("allow", "log")

    @pytest.mark.asyncio
    async def test_evaluate_dangerous_action(self, policy_url):
        """Evaluate a dangerous action — should require approval or deny."""
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{policy_url}/v1/evaluate",
                json={
                    "agent_id": "integration-test-agent",
                    "action": "dangerous_tool",
                    "context": {"autonomy_tier": "gated"},
                },
            )
            assert resp.status_code == 200
            data = resp.json()
            # Should not be plain "allow" for a critical tool in gated mode
            assert data.get("action") != "allow" or data.get("requires_approval") is True


    @pytest.mark.asyncio
    async def test_evaluate_blocked_action(self, policy_url):
        """Evaluate a blocked action — condition should trigger deny."""
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{policy_url}/v1/evaluate",
                json={
                    "agent_id": "integration-test-agent",
                    "action": "blocked_tool",
                    "context": {"autonomy_tier": "gated"},
                },
            )
            assert resp.status_code == 200
            data = resp.json()
            assert data.get("action") == "deny"

    @pytest.mark.asyncio
    async def test_get_tiers(self, policy_url):
        """Fetch autonomy tier definitions."""
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{policy_url}/v1/tiers")
            assert resp.status_code == 200
            tiers = resp.json()
            assert len(tiers) == 4  # shadow, gated, supervised, autonomous

    @pytest.mark.asyncio
    async def test_cleanup_policy(self, policy_url):
        """Delete the test policy."""
        async with httpx.AsyncClient() as client:
            resp = await client.delete(f"{policy_url}/v1/policies/integration-test-policy")
            assert resp.status_code == 200
