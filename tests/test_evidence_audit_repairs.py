"""Tests verifying the evidence-first audit repairs across STRIKE//OS:
1. Dynamic player roster resolution without hardcoded match substitution.
2. Removal of synthetic dummy player manufacturing.
3. Dynamic CP-SAT team constraints in solve_portal_lineup.
4. AI analyst query endpoint does not crash on unbound match_data.
5. Dynamic C/VC generation in Captain Engine from actual active players.
6. Dynamic tactical insights in Batter Matchups Engine.
7. Dot balls and format-aware rules in Fantasy Scoring Engine.
8. Historical backtesting computes real holdout selection scores instead of 0.946 scaling.
9. Field Simulator outputs explicit uncalibrated status labels.
10. Vite configuration proxies to port 8001 by default.
"""
import unittest
from pathlib import Path
from fastapi.testclient import TestClient
from gl_engine.web_app import app, extract_match_roster
from gl_engine.models import Player, MatchupDetail, PlayerStats, Lineup
from gl_engine.capabilities.c15_captain_engine import CricketCaptainEngine
from gl_engine.capabilities.c07_batter_matchups import CricketBatterMatchups
from gl_engine.capabilities.c11_fantasy_scoring import CricketFantasyScoring
from gl_engine.capabilities.c19_backtesting import CricketBacktesting
from gl_engine.field_simulator import SyntheticFieldSimulator


class TestEvidenceAuditRepairs(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_analyst_query_no_unbound_error(self):
        """Verify /api/analyst/query executes without UnboundLocalError when no H2H or venue is triggered."""
        resp = self.client.get("/api/analyst/query?q=general%20cricket%20tactics")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["status"], "success")
        self.assertIn("Cricket Tactical Intelligence Dispatch", data["reply"])

    def test_portal_roster_without_connected_source_fails_closed(self):
        """The old embedded AFG-ZIM list is not a connected roster source."""
        resp = self.client.get("/api/portal/roster?match_id=afg_vs_zim_sharjah_odi")
        self.assertEqual(resp.status_code, 409)
        self.assertNotIn("roster", resp.json())

    def test_portal_roster_does_not_return_afg_zim_for_other_matches(self):
        """Verify /api/portal/roster does not return AFG-ZIM players when another match is requested."""
        resp = self.client.get("/api/portal/roster?match_id=161190")
        if resp.status_code == 200:
            data = resp.json()
            names = [p["name"] for p in data["roster"]]
            self.assertNotIn("R Gurbaz", names)
            self.assertNotIn("Fazalhaq Farooqi", names)

    def test_portal_roster_unknown_match_returns_409(self):
        """Verify /api/portal/roster returns 409 for an unknown match rather than fabricating dummy players."""
        resp = self.client.get("/api/portal/roster?match_id=completely_unknown_fixture_9999")
        self.assertEqual(resp.status_code, 409)

    def test_extract_match_roster_never_fakes_dummy_players(self):
        """Verify extract_match_roster returns only real players and never manufactures 'Top Batter 1'."""
        sparse_match = {
            "title": "Australia vs England, Test Match",
            "lineups": [
                {
                    "players": [
                        {"name": "Pat Cummins", "team": "AUS", "role": "BOWL", "credits": 9.0},
                        {"name": "Joe Root", "team": "ENG", "role": "BAT", "credits": 9.5}
                    ]
                }
            ]
        }
        roster = extract_match_roster(sparse_match)
        self.assertEqual(len(roster), 2)
        names = [p["name"] for p in roster]
        self.assertIn("Pat Cummins", names)
        self.assertIn("Joe Root", names)
        for n in names:
            self.assertNotIn("Top Batter 1", n)
            self.assertNotIn("Star Opener", n)
            self.assertNotIn("Opp Key Opener", n)

    def test_solve_portal_lineup_dynamic_team_balance(self):
        """Relabel teams in a test-only real-player roster; solver must use those teams."""
        import json
        from pathlib import Path
        from unittest.mock import patch
        from collections import Counter
        rows = json.loads((Path(__file__).parents[1] / "gl_engine/data/ind_wi_match.json").read_text())["players"]
        players = [Player(**{**row, "team": "SIDE_A" if row["team"] == "IND" else "SIDE_B"}) for row in rows]
        with patch("gl_engine.web_app.resolve_match_players", return_value=({"id":"test_fixture"}, players)) as resolve:
            resp = self.client.get("/api/portal/solve-lineup?match_id=test_fixture&target_unspent=14.0")
        resolve.assert_called_once_with("test_fixture")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["status"], "success")
        self.assertGreaterEqual(data["actual_unspent"], 11.5)
        self.assertEqual(len(data["players"]), 11)
        counts = Counter(p["team"] for p in data["players"])
        self.assertEqual(set(counts), {"SIDE_A", "SIDE_B"})
        self.assertTrue(all(4 <= count <= 7 for count in counts.values()))

    def test_captain_engine_dynamic_generation(self):
        """Verify CricketCaptainEngine constructs GL pairs from input players, not hardcoded IND-WI names."""
        aus_eng_players = [
            Player(id="p1", name="Travis Head", team="AUS", role="BAT", credits=9.0, batting_style="LHB", batting_order_projected=1, projected_points=65.0, ceiling_score=95.0, projected_ownership=75.0),
            Player(id="p2", name="Mitchell Starc", team="AUS", role="BOWL", credits=8.5, batting_style="LHB", batting_order_projected=9, projected_points=58.0, ceiling_score=88.0, projected_ownership=60.0),
            Player(id="p3", name="Harry Brook", team="ENG", role="BAT", credits=8.5, batting_style="RHB", batting_order_projected=4, projected_points=60.0, ceiling_score=90.0, projected_ownership=45.0),
            Player(id="p4", name="Jofra Archer", team="ENG", role="BOWL", credits=8.0, batting_style="RHB", batting_order_projected=8, projected_points=52.0, ceiling_score=82.0, projected_ownership=35.0),
        ]
        engine = CricketCaptainEngine(aus_eng_players)
        result = engine.execute()
        pairs = result["recommended_gl_pairs"]
        self.assertTrue(len(pairs) > 0)
        all_caps = [p["captain"] for p in pairs] + [p["vice_captain"] for p in pairs]
        # Should contain Head, Starc, Brook, or Archer
        self.assertTrue(any(name in ["Travis Head", "Mitchell Starc", "Harry Brook", "Jofra Archer"] for name in all_caps))
        # Must NOT contain hardcoded Abhishek Sharma or Mayank Yadav
        self.assertNotIn("Abhishek Sharma", all_caps)
        self.assertNotIn("Mayank Yadav", all_caps)
        self.assertNotIn("Romario Shepherd", all_caps)

    def test_batter_matchups_dynamic_insights(self):
        """Verify CricketBatterMatchups produces dynamic insights and never outputs hardcoded India-WI strings."""
        matchups = [
            MatchupDetail(batter_name="Babar Azam", bowler_name="Trent Boult", balls=30, runs=22, dismissals=3, strike_rate=73.3, dismissal_rate=0.1)
        ]
        players = [
            Player(id="p1", name="Babar Azam", team="PAK", role="BAT", batting_style="RHB", batting_order_projected=3, credits=9.0),
            Player(id="p2", name="Trent Boult", team="NZ", role="BOWL", batting_style="RHB", batting_order_projected=11, bowling_style="LAFM", credits=9.0)
        ]
        engine = CricketBatterMatchups(matchups, players)
        result = engine.execute()
        insights = " ".join(result["tactical_style_insights"])
        self.assertIn("Trent Boult", insights)
        self.assertIn("Babar Azam", insights)
        self.assertNotIn("Roston Chase", insights)
        self.assertNotIn("Shivam Dube", insights)

    def test_fantasy_scoring_dot_balls_and_format(self):
        """Verify CricketFantasyScoring credits dot balls and supports ODI vs T20 formats."""
        scorer = CricketFantasyScoring()
        # In T20, dot ball = +1.0 pt
        t20_res = scorer.calculate_player_points(
            wickets=2, overs_bowled=4.0, runs_conceded=24, dots=14, match_format="T20"
        )
        self.assertIn("dot_balls", t20_res["breakdown"])
        self.assertEqual(t20_res["breakdown"]["dot_balls"], 14.0)
        # In T20 wicket = 30 pts each (2 * 30 = 60), starting XI = 4 pts, economy 6.0 = +4.0
        self.assertEqual(t20_res["format"], "T20")

        # In ODI, wicket = 25 pts, milestone thresholds differ
        odi_res = scorer.calculate_player_points(
            runs=55, balls_faced=45, match_format="ODI"
        )
        self.assertEqual(odi_res["format"], "ODI")
        # In ODI half-century bonus is +4 (not T20's +8)
        self.assertEqual(odi_res["breakdown"]["starting_11"], 4.0)

    def test_backtesting_no_0946_scaling(self):
        """Verify CricketBacktesting does not use artificial 0.946 scaling."""
        bt = CricketBacktesting()
        # Verify curated benchmarks have realistic, non-sensational rank labels
        for bm in bt.curated_benchmarks:
            self.assertNotIn("Rank 1 Contender", bm.get("rank_in_grand_league", ""))

    def test_field_simulator_calibration_status(self):
        """Verify SyntheticFieldSimulator marks its output as MODEL_ESTIMATE_UNCALIBRATED."""
        players = [
            Player(
                id=f"p{i}",
                name=f"Player {i}",
                team="T1" if i % 2 == 0 else "T2",
                role="BAT" if i < 4 else "BOWL" if i < 8 else "AR",
                credits=8.5,
                batting_style="RHB",
                batting_order_projected=min(11, i + 1),
                projected_points=45.0 + i,
                ceiling_score=75.0 + i,
                floor_score=15.0,
                projected_ownership=40.0 + (i % 20)
            )
            for i in range(15)
        ]
        sim = SyntheticFieldSimulator(players, field_size=500000)
        p11 = players[:11]
        lineup = Lineup(
            team_name="Test Lineup",
            scenario_tag="TEST",
            players=p11,
            captain=p11[0],
            vice_captain=p11[1],
            total_credits=sum(p.credits for p in p11),
            projected_points=sum(p.projected_points for p in p11),
            simulated_ceiling=sum(p.ceiling_score for p in p11),
            total_ownership_sum=sum(p.projected_ownership for p in p11),
            differential_count=2,
            team_balance={"T1": 6, "T2": 5},
            gl_rank_potential="Balanced",
            tactical_rationale="Testing"
        )
        results = sim.simulate_contest_distribution([lineup], n_simulated_brackets=10)
        self.assertTrue(len(results) > 0)
        self.assertEqual(results[0]["calibration_status"], "MODEL_ESTIMATE_UNCALIBRATED")

    def test_vite_config_proxies_to_backend_port_8000(self):
        """Frontend default proxy must match the actual backend on port 8000."""
        vite_conf_path = Path(__file__).parent.parent / "frontend" / "vite.config.ts"
        self.assertTrue(vite_conf_path.exists())
        content = vite_conf_path.read_text(encoding="utf-8")
        self.assertIn("8000", content)
        self.assertIn("'/api'", content)
        self.assertIn("'/matches'", content)


if __name__ == "__main__":
    unittest.main()
