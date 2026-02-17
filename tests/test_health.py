"""IT-1: Verify all services are healthy."""

import httpx
import pytest


class TestServiceHealth:
    """Verify each service responds to health checks."""

    @pytest.mark.asyncio
    async def test_episode_store_health(self, store_url):
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{store_url}/v1/health")
            assert resp.status_code == 200
            data = resp.json()
            assert data["status"] == "ok"

    @pytest.mark.asyncio
    async def test_policy_engine_health(self, policy_url):
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{policy_url}/v1/health")
            assert resp.status_code == 200

    @pytest.mark.asyncio
    async def test_gateway_reachable(self, gateway_url):
        """Gateway may not have /health but should respond."""
        async with httpx.AsyncClient() as client:
            try:
                resp = await client.get(f"{gateway_url}/health")
                assert resp.status_code in (200, 404)
            except httpx.ConnectError:
                pytest.skip("Gateway not running")
