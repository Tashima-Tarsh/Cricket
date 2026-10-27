"""Security regression tests for HTTP headers, payload bounding, and authorization."""
import os
import unittest
from unittest.mock import patch
from fastapi.testclient import TestClient
from gl_engine.web_app import app


class TestProductionSecurity(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_response_security_headers_present(self):
        resp = self.client.get("/api/health")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.headers.get("x-content-type-options"), "nosniff")
        self.assertEqual(resp.headers.get("x-frame-options"), "DENY")
        self.assertEqual(resp.headers.get("referrer-policy"), "strict-origin-when-cross-origin")

    def test_oversized_payload_rejected_with_413(self):
        headers = {"content-length": str(2 * 1024 * 1024)}  # 2MB
        resp = self.client.post("/api/v1/score", json={}, headers=headers)
        self.assertEqual(resp.status_code, 413)
        self.assertIn("exceeds maximum allowed limit", resp.json()["detail"])

    def test_admin_write_endpoint_without_token_fails_closed(self):
        with patch.dict(os.environ, {"CRICKET_ADMIN_TOKEN": ""}):
            resp = self.client.post("/api/fusion/run-pipeline", json={})
            self.assertEqual(resp.status_code, 503)

    def test_admin_write_endpoint_with_invalid_token_rejected(self):
        with patch.dict(os.environ, {"CRICKET_ADMIN_TOKEN": "secret-admin-pass"}):
            resp = self.client.post(
                "/api/fusion/run-pipeline",
                json={},
                headers={"Authorization": "Bearer invalid-token"}
            )
            self.assertEqual(resp.status_code, 401)


if __name__ == "__main__":
    unittest.main()
