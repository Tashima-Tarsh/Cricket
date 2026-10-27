"""Regressions: Wicket Oracle never manufactures odds, props or phase stats."""
import unittest
from fastapi.testclient import TestClient
from gl_engine.web_app import app
from gl_engine.wicket_oracle import compute_fractional_kelly, convert_prob_to_american_odds, WicketOracleEngine


class TestWicketOracle(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_math_helpers_only(self):
        self.assertTrue(2.5 <= compute_fractional_kelly(0.09, 0.55) <= 3.0)
        self.assertEqual(compute_fractional_kelly(-0.05, 0.50), 0.0)
        self.assertTrue(convert_prob_to_american_odds(0.55).startswith("-"))

    def test_bets_unavailable_without_observed_market(self):
        body = self.client.get("/api/oracle/value-bets").json()
        self.assertEqual(body["status"], "unavailable")
        self.assertEqual(body["bets"], [])
        self.assertEqual(WicketOracleEngine.get_value_bets(), [])

    def test_props_unavailable_without_real_lines(self):
        body = self.client.get("/api/oracle/player-props").json()
        self.assertEqual(body["status"], "unavailable")
        self.assertEqual(body["props"], [])
        self.assertEqual(WicketOracleEngine.get_player_props([]), [])

    def test_team_phase_unavailable(self):
        response = self.client.get("/api/oracle/team-phase/Chennai%20Super%20Kings")
        self.assertEqual(response.status_code, 503)
        self.assertNotIn("phases", response.json())

    def test_untrusted_live_ingest_is_closed(self):
        response = self.client.post("/api/live/load/cricbuzz_12345")
        self.assertIn(response.status_code, (401, 503))


if __name__ == "__main__":
    unittest.main()
