"""IT-1: Verify all services in the stack are healthy."""

import httpx


class TestServiceHealth:
    """Each service responds to its health endpoint."""

    def test_gateway_health(self, gateway_url):
        resp = httpx.get(f"{gateway_url}/health", timeout=10)
        assert resp.status_code == 200
        assert resp.json()["status"] == "ok"

    def test_jaeger_ui(self, jaeger_url):
        resp = httpx.get(f"{jaeger_url}/", timeout=10, follow_redirects=True)
        assert resp.status_code == 200

    def test_minio_live(self, minio_url):
        resp = httpx.get(f"{minio_url}/minio/health/live", timeout=10)
        assert resp.status_code == 200
