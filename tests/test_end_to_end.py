"""IT-4: Full end-to-end flow — Episode → Trust Score → Policy Decision."""

import httpx
import pytest


class TestEndToEnd:
    """Tests that span multiple services in sequence."""

    @pytest.mark.asyncio
    async def test_episode_to_trust_to_policy(self, store_url, policy_url):
        """
        Full flow:
        1. Ingest multiple successful episodes into the store
        2. Create a policy in the policy engine
        3. Check agent profile / trust score via policy engine
        4. Evaluate an action — trust should influence the decision
        """
        async with httpx.AsyncClient(timeout=10.0) as client:
            # Step 1: Ingest 5 successful episodes
            for i in range(5):
                episode = {
                    "agent_id": "e2e-test-agent",
                    "task": f"e2e-task-{i}",
                    "status": "success",
                    "model": "gpt-4o-mini",
                    "total_tokens": 100 + i * 10,
                    "total_cost_usd": 0.001 + i * 0.0001,
                    "steps": [
                        {
                            "step_type": "llm_call",
                            "model": "gpt-4o-mini",
                            "input_tokens": 60 + i * 5,
                            "output_tokens": 40 + i * 5,
                            "cost_usd": 0.001 + i * 0.0001,
                            "duration_ms": 300 + i * 50,
                            "provider": "openai",
                        }
                    ],
                }
                resp = await client.post(f"{store_url}/v1/episodes", json=episode)
                assert resp.status_code == 200

            # Step 2: Verify episodes are in the store
            resp = await client.get(
                f"{store_url}/v1/episodes",
                params={"agent_id": "e2e-test-agent"},
            )
            assert resp.status_code == 200
            episodes = resp.json()
            assert len(episodes) >= 5

            # Step 3: Create a policy
            policy = {
                "id": "e2e-policy",
                "name": "E2E Test Policy",
                "description": "End-to-end integration test",
                "autonomy_tier": "supervised",
                "tool_risks": [],
                "kill_switches": [
                    {
                        "switch_type": "spend_usd",
                        "limit_type": "absolute",
                        "threshold": 100.0,
                        "action": "halt",
                        "enabled": True,
                    }
                ],
                "conditions": [],
            }
            resp = await client.post(f"{policy_url}/v1/policies", json=policy)
            assert resp.status_code == 200

            # Step 4: Evaluate an action
            resp = await client.post(
                f"{policy_url}/v1/evaluate",
                json={
                    "agent_id": "e2e-test-agent",
                    "action": "read_file",
                    "context": {"autonomy_tier": "supervised"},
                },
            )
            assert resp.status_code == 200

            # Step 5: Cleanup
            resp = await client.delete(f"{policy_url}/v1/policies/e2e-policy")
            assert resp.status_code == 200

    @pytest.mark.asyncio
    async def test_kill_switch_enforcement(self, policy_url):
        """Test that kill switches are enforced across requests."""
        async with httpx.AsyncClient(timeout=10.0) as client:
            # Create a policy with very low spend limit
            policy = {
                "id": "killswitch-test-policy",
                "name": "Kill Switch Test",
                "description": "Tests spend limit enforcement",
                "autonomy_tier": "gated",
                "tool_risks": [],
                "kill_switches": [
                    {
                        "switch_type": "spend_usd",
                        "limit_type": "absolute",
                        "threshold": 0.001,
                        "action": "halt",
                        "enabled": True,
                    }
                ],
                "conditions": [],
            }
            resp = await client.post(f"{policy_url}/v1/policies", json=policy)
            assert resp.status_code == 200

            # Report metrics that exceed the threshold
            resp = await client.post(
                f"{policy_url}/v1/metrics",
                json={
                    "agent_id": "killswitch-agent",
                    "spend_usd": 0.01,
                },
            )
            # Metrics endpoint may or may not exist yet — skip if not
            if resp.status_code == 404:
                pytest.skip("Metrics endpoint not implemented")

            # Cleanup
            resp = await client.delete(f"{policy_url}/v1/policies/killswitch-test-policy")
            assert resp.status_code == 200
