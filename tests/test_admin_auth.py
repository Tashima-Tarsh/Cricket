"""Prove remote clients cannot alter persistent cricket application state."""
import os
import unittest
from unittest.mock import patch
from fastapi.testclient import TestClient
from gl_engine.web_app import app
from edgeforge.app import app as edge_app


class AdminAuthorizationTests(unittest.TestCase):
    def test_write_endpoints_fail_closed_without_token(self):
        with patch.dict(os.environ, {"CRICKET_ADMIN_TOKEN": ""}):
            with TestClient(app) as client:
                for path in ("/teams/save", "/api/fusion/run-pipeline",
                             "/api/trigger/simulate-toss/test",
                             "/api/trigger/simulate-lineup/test",
                             "/api/trigger/advance-cutoff/test"):
                    with self.subTest(path=path):
                        self.assertEqual(client.post(path, json={}).status_code, 503)

    def test_incorrect_token_rejected(self):
        with patch.dict(os.environ, {"CRICKET_ADMIN_TOKEN": "test-only-secret"}):
            with TestClient(app) as client:
                for path in ("/teams/save", "/api/fusion/run-pipeline",
                             "/api/trigger/simulate-toss/test",
                             "/api/trigger/simulate-lineup/test",
                             "/api/trigger/advance-cutoff/test"):
                    with self.subTest(path=path):
                        self.assertEqual(client.post(path, json={},
                                                     headers={"Authorization": "Bearer wrong"}).status_code, 401)
            with TestClient(edge_app) as client:
                self.assertEqual(client.post("/edge/fixtures", json={},
                                             headers={"Authorization": "Bearer wrong"}).status_code, 401)


if __name__ == "__main__":
    unittest.main()
