"""IT-2: Audit and analytics endpoints, plus a live LLM round-trip.

The audit chain is the core EU AI Act Article 12 feature: every call through
the gateway produces an HMAC-chained record. These tests confirm the audit
surface responds; the live round-trip (needs OPENAI_API_KEY) confirms a call
actually lands in the audit chain.
"""

import time

import httpx

# The gateway appends to the audit chain in the background, after the
# response has already been sent, so the new record can lag slightly.
AUDIT_WAIT_SECONDS = 15


def _chain_length(gateway_url, headers):
    resp = httpx.get(f"{gateway_url}/v1/audit", headers=headers, timeout=10)
    resp.raise_for_status()
    return resp.json()["chain_length"]


class TestAuditSurface:
    def test_audit_endpoint_responds(self, gateway_url, gateway_headers):
        resp = httpx.get(f"{gateway_url}/v1/audit", headers=gateway_headers, timeout=10)
        assert resp.status_code == 200
        assert "application/json" in resp.headers.get("content-type", "")
        assert "chain_length" in resp.json()

    def test_analytics_endpoint_responds(self, gateway_url, gateway_headers):
        resp = httpx.get(f"{gateway_url}/v1/analytics", headers=gateway_headers, timeout=10)
        assert resp.status_code == 200
        assert "application/json" in resp.headers.get("content-type", "")

    def test_audit_export_responds(self, gateway_url, gateway_headers):
        resp = httpx.get(f"{gateway_url}/v1/audit/export", headers=gateway_headers, timeout=10)
        assert resp.status_code == 200


class TestLiveRoundTrip:
    def test_chat_completion_is_audited(self, gateway_url, gateway_headers, openai_api_key):
        """A proxied chat completion succeeds and the audit chain grows."""
        before = _chain_length(gateway_url, gateway_headers)

        resp = httpx.post(
            f"{gateway_url}/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {openai_api_key}",
                "Content-Type": "application/json",
                **gateway_headers,
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

        deadline = time.monotonic() + AUDIT_WAIT_SECONDS
        after = before
        while time.monotonic() < deadline:
            after = _chain_length(gateway_url, gateway_headers)
            if after > before:
                break
            time.sleep(0.5)
        assert after > before, (
            f"audit chain did not grow within {AUDIT_WAIT_SECONDS}s "
            f"(still {before} records) after a proxied call"
        )
