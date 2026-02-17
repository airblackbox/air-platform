"""IT-2: Test the episode ingestion and retrieval flow."""

import httpx
import pytest


class TestEpisodeFlow:
    """End-to-end episode lifecycle: create → list → get → replay."""

    @pytest.mark.asyncio
    async def test_ingest_episode(self, store_url, sample_episode):
        """Ingest an episode and verify it's stored."""
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{store_url}/v1/episodes",
                json=sample_episode,
            )
            assert resp.status_code == 200
            data = resp.json()
            assert "id" in data
            self.__class__.episode_id = data["id"]

    @pytest.mark.asyncio
    async def test_list_episodes(self, store_url):
        """List episodes and find our test episode."""
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{store_url}/v1/episodes",
                params={"agent_id": "integration-test-agent"},
            )
            assert resp.status_code == 200
            episodes = resp.json()
            assert len(episodes) >= 1
            assert any(e.get("agent_id") == "integration-test-agent" for e in episodes)

    @pytest.mark.asyncio
    async def test_get_episode_detail(self, store_url):
        """Retrieve a specific episode with steps."""
        episode_id = getattr(self.__class__, "episode_id", None)
        if not episode_id:
            pytest.skip("No episode_id from previous test")

        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{store_url}/v1/episodes/{episode_id}")
            assert resp.status_code == 200
            data = resp.json()
            assert data["agent_id"] == "integration-test-agent"
            assert len(data.get("steps", [])) == 1

    @pytest.mark.asyncio
    async def test_get_replay(self, store_url):
        """Get replay-ready view of an episode."""
        episode_id = getattr(self.__class__, "episode_id", None)
        if not episode_id:
            pytest.skip("No episode_id from previous test")

        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{store_url}/v1/episodes/{episode_id}/replay")
            assert resp.status_code == 200
            data = resp.json()
            assert "steps" in data
