"""Versioned research API contract must reject unsupported scoring versions."""
import unittest
from fastapi.testclient import TestClient
from gl_engine.web_app import app


class StableApiTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_exposes_explicit_research_status(self):
        response = self.client.get("/api/v1/engines")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertFalse(data["calibrated_contest_probabilities"])
        self.assertEqual(data["scoring_rule_version"], "legacy_v3")

    def test_scoring_version_is_required_to_be_known(self):
        self.assertEqual(
            self.client.post("/api/v1/score", json={
                "rule_version": "imaginary_official_rules", "runs": 55,
            }).status_code, 422
        )
        data = self.client.post("/api/v1/score", json={
            "rule_version": "legacy_v3", "runs": 40,
            "fours": 4, "sixes": 2, "balls_faced": 30,
        }).json()
        self.assertEqual(data["data"]["total_points"], 58.0)

    def test_missing_fixture_fails_closed(self):
        response = self.client.get("/api/v1/fixtures/absolutely_missing/roster")
        self.assertIn(response.status_code, (404, 409, 503))


if __name__ == "__main__":
    unittest.main()
