"""
Tests for THENITISHKR-SPORTS // Wicket Oracle Integration
Verifies DraftKings value bets, fractional Kelly sizing, player props, and team phase endpoints.
Compatible with both unittest discover and pytest runners.
"""

import unittest
from fastapi.testclient import TestClient

from gl_engine.web_app import app
from gl_engine.wicket_oracle import compute_fractional_kelly, convert_prob_to_american_odds, WicketOracleEngine


class TestWicketOracle(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_kelly_criterion_math(self):
        """Verify Kelly Criterion calculation adheres to 25% fractional rule."""
        kelly = compute_fractional_kelly(edge=0.09, implied_prob=0.55, fraction=0.25)
        self.assertTrue(2.5 <= kelly <= 3.0)

        # Negative edge should yield 0% stake
        self.assertEqual(compute_fractional_kelly(edge=-0.05, implied_prob=0.50), 0.0)

        # Extreme edge capped at 10% safety ceiling
        self.assertEqual(compute_fractional_kelly(edge=0.40, implied_prob=0.80), 10.0)

    def test_american_odds_conversion(self):
        """Verify probability to American odds converter."""
        self.assertTrue(convert_prob_to_american_odds(0.55).startswith("-"))
        self.assertTrue(convert_prob_to_american_odds(0.40).startswith("+"))

    def test_value_bets_endpoint(self):
        """Verify GET /api/oracle/value-bets returns properly structured opportunities."""
        res = self.client.get("/api/oracle/value-bets")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "success")
        self.assertEqual(data["platform"], "THENITISHKR-SPORTS")
        self.assertIn("bets", data)
        self.assertIsInstance(data["bets"], list)

        for bet in data["bets"]:
            self.assertIn("match", bet)
            self.assertIn("bet", bet)
            self.assertIn("edge", bet)
            self.assertIn("kelly_stake", bet)
            self.assertIn(bet["tier"], ("Elite Pick", "Strong"))
            self.assertIn("%", bet["kelly_stake"])

    def test_player_props_endpoint(self):
        """Verify GET /api/oracle/player-props returns calibrated batter/bowler lines."""
        res = self.client.get("/api/oracle/player-props")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "success")
        self.assertEqual(data["platform"], "THENITISHKR-SPORTS")
        self.assertIn("props", data)
        self.assertIsInstance(data["props"], list)

        for prop in data["props"]:
            self.assertIn("player", prop)
            self.assertIn("market", prop)
            self.assertIn(prop["market"], ("Runs Scored", "Wickets Taken"))
            self.assertIn(prop["recommendation"], ("OVER", "UNDER"))
            self.assertIn(prop["confidence"], ("High", "Medium", "Low"))
            self.assertIn("rivalry_note", prop)

    def test_team_phase_deep_dive_endpoint(self):
        """Verify GET /api/oracle/team-phase/{team} returns 3-phase split and death economy."""
        res = self.client.get("/api/oracle/team-phase/Chennai%20Super%20Kings")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "success")
        self.assertEqual(data["platform"], "THENITISHKR-SPORTS")
        self.assertIn("deep_dive", data)
        dd = data["deep_dive"]
        self.assertEqual(dd["team"], "Chennai Super Kings")
        self.assertIn("phases", dd)
        self.assertEqual(len(dd["phases"]), 3)
        self.assertEqual(dd["phases"][0]["phase"], "Powerplay (1-6)")
        self.assertEqual(dd["phases"][1]["phase"], "Middle (7-15)")
        self.assertEqual(dd["phases"][2]["phase"], "Death (16-20)")
        self.assertIn("death_overs_economy", dd)
        self.assertGreater(dd["death_overs_economy"], 0)


if __name__ == "__main__":
    unittest.main()
