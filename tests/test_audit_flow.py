"""IT-2: Audit and analytics endpoints, plus a live LLM round-trip.

The audit chain is the core EU AI Act Article 12 feature: every call through
the gateway produces an HMAC-chained record. These tests confirm the audit
surface responds; the live round-trip (needs OPENAI_API_KEY) confirms a call
actually lands in the audit log.
"""

import os

import httpx

GATEWAY_HEADERS = {}
if os.environ.get("GATEWAY_KEY"):
    GATEWAY_HEADERS["X-Gateway-Key"] = os.environ["GATEWAY_KEY"]


class TestAuditSurface:
    def test_audit_endpoint_responds(self, gateway_url):
        resp = httpx.get(f"{gateway_url}/v1/audit", headers=GATEWAY_HEADERS, timeout=10)
        assert resp.status_code == 200
        assert "application/json" in resp.headers.get("content-type", "")

    def test_analytics_endpoint_responds(self, gateway_url):
        resp = httpx.get(f"{gateway_url}/v1/analytics", headers=GATEWAY_HEADERS, timeout=10)
        assert resp.status_code == 200
        assert "application/json" in resp.headers.get("content-type", "")

    def test_audit_export_responds(self, gateway_url):
        resp = httpx.get(f"{gateway_url}/v1/audit/export", headers=GATEWAY_HEADERS, timeout=10)
        assert resp.status_code == 200


class TestLiveRoundTrip:
    def test_chat_completion_is_audited(self, gateway_url, openai_api_key):
        """A proxied chat completion succeeds and the audit log grows."""
        before = httpx.get(
            f"{gateway_url}/v1/audit", headers=GATEWAY_HEADERS, timeout=10
        ).text

        resp = httpx.post(
            f"{gateway_url}/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {openai_api_key}",
                "Content-Type": "application/json",
                **GATEWAY_HEADERS,
            },
            json={
                "model": "gpt-4o-mini",
                "messages": [{"role": "user", "content": "Reply with the word: pong"}],
                "max_tokens": 5,
            },
            timeout=60,
        )
        assert resp.status_code == 200, resp.text
        assert resp.json()["choices"], "no completion returned"

        after = httpx.get(
            f"{gateway_url}/v1/audit", headers=GATEWAY_HEADERS, timeout=10
        ).text
        assert after != before, "audit log did not change after a proxied call"
