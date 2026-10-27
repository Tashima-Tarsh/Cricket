"""Regression checks for frontend controls and honest API failure behaviour."""
import json
import numpy as np
import unittest
from unittest.mock import patch
from fastapi.testclient import TestClient
from gl_engine.web_app import app, MATCH_FILE
from support_runtime_fixture import FIXTURE_ID, connected_fixture
from gl_engine.models import Player
from gl_engine.ortools_optimizer import ORToolsCricketOptimizer
from gl_engine import live_feed
from pathlib import Path

class WorkspaceApiTests(unittest.TestCase):
    def setUp(self):
        self._fixture_context = connected_fixture()
        self._fixture_context.__enter__()
        self.addCleanup(self._fixture_context.__exit__, None, None, None)
        self.client = TestClient(app)

    def test_invalid_settings_are_rejected(self):
        for query in ("risk=UNKNOWN", "teams=0", "teams=21", "max_overlap=12", "credit_strategy=invalid", "scenario=unknown", "captain=unknown"):
            with self.subTest(query=query):
                self.assertEqual(self.client.get("/api/ortools/optimize?" + query).status_code, 422)

    def test_unconnected_match_is_not_solved_with_old_players(self):
        response = self.client.get("/api/ortools/optimize?match_id=custom_fixture")
        self.assertEqual(response.status_code, 409)

    def test_custom_captain_and_scenario_are_solved(self):
        response = self.client.get("/api/ortools/optimize?teams=1&scenario=PACE_DOMINANCE&captain=TILAK&risk=BALANCED&match_id=custom_test_archive")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("generated_at", data)
        self.assertEqual(data["risk"], "BALANCED")
        self.assertEqual(len(data["lineups"]), 1)
        lineup = data["lineups"][0]
        self.assertIn("Tilak", lineup["captain"]["name"])
        self.assertEqual(lineup["scenario_tag"], "PACE_DOMINANCE")
        self.assertEqual(len({p["id"] for p in lineup["players"]}), 11)
        self.assertTrue(79 <= lineup["total_credits"] <= 85)

    def test_heavy_differential_setting_is_enforced(self):
        response = self.client.get(f"/api/ortools/optimize?teams=1&risk=DIFFERENTIAL_HEAVY&match_id={FIXTURE_ID}")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["lineups"])
        self.assertGreaterEqual(response.json()["lineups"][0]["differential_count"], 4)

    def test_vice_captain_only_does_not_crash(self):
        players = [Player(**p) for p in json.loads(MATCH_FILE.read_text(encoding="utf-8"))["players"]]
        vice = next(p for p in players if "Tilak" in p.name)
        scenario = {"name":"Vice only", "tag":"TEST", "rationale":"Regression", "preferred_vc":vice.id}
        lineups = ORToolsCricketOptimizer(players).generate_grand_league_portfolio(num_teams=1, custom_scenarios=[scenario])
        self.assertTrue(lineups)
        self.assertEqual(lineups[0].vice_captain.id, vice.id)

    def test_vectorized_simulation_matches_scalar_scoring(self):
        from gl_engine.field_simulator import SyntheticFieldSimulator
        players = [Player(**p) for p in json.loads(MATCH_FILE.read_text(encoding="utf-8"))["players"]]
        lineup = ORToolsCricketOptimizer(players).generate_grand_league_portfolio(num_teams=1)[0]
        opponent = {"player_ids": [p.id for p in lineup.players], "c_id":lineup.captain.id, "vc_id":lineup.vice_captain.id}
        means = np.array([p.projected_points for p in players])
        scales = np.array([max(6.0,(p.ceiling_score-p.floor_score)/4.0) for p in players])
        np.random.seed(42)
        points = np.maximum(0.0,np.random.normal(means,scales,size=(64,len(players))))
        indices = {p.id:i for i,p in enumerate(players)}
        scalar_scores = [sum(row[indices[p.id]] * (2 if p.id == lineup.captain.id else 1.5 if p.id == lineup.vice_captain.id else 1) for p in lineup.players) for row in points]
        simulator = SyntheticFieldSimulator(players)
        with patch.object(simulator,"_generate_synthetic_opponent_field",return_value=[opponent]):
            result = simulator.simulate_contest_distribution([lineup],n_simulated_brackets=64)[0]
        self.assertEqual(result["expected_points"],round(float(np.mean(scalar_scores)),1))
        self.assertEqual(result["ceiling_p99"],round(float(np.percentile(scalar_scores,99)),1))
        self.assertEqual(result["p_top_0_1_pct"],100.0)  # Identical opponent ties every trial.

    def test_missing_snapshot_is_an_error_not_example_data(self):
        client = TestClient(app, raise_server_exceptions=False)
        with patch("gl_engine.web_app._STATE_CACHES", {}), patch("gl_engine.match_catalog.MATCH_FILE_5TH", Path("__missing_snapshot__.json")):
            response = client.get("/api/state?match_id=ind_vs_wi_5th_t20_2026")
        self.assertEqual(response.status_code, 409)
        self.assertNotIn("players", response.text)

    def test_failed_live_feed_never_returns_fabricated_matches(self):
        with patch.object(live_feed.urllib.request, "urlopen", side_effect=OSError("offline")):
            self.assertEqual(live_feed.fetch_espn_cricinfo_live_matches(force_refresh=True), [])

if __name__ == "__main__":
    unittest.main()
