"""Golden examples against the Dream11 published points table reviewed 2026-10-27."""
import unittest
from fastapi.testclient import TestClient
from gl_engine.web_app import app
from gl_engine.official_scoring import score_official, RULE_VERSION


class PublishedDream11Points(unittest.TestCase):
    def test_t20_25_run_milestone_and_boundary_bonuses(self):
        result = score_official(match_format="T20", runs=40, balls_faced=30,
                                fours=4, sixes=2, is_playing=True)
        # 4 XI + 40 runs + 16 boundary + 12 six + 4 at 25 + 2 SR
        self.assertEqual(result["total_points"], 78)

    def test_t20_five_wickets_bonus_is_twelve(self):
        r = score_official(match_format="T20", wickets=5, dots=9,
                           overs_bowled=4, runs_conceded=24, is_playing=True)
        self.assertEqual(r["breakdown"]["wicket_haul_bonus"], 12)
        self.assertEqual(r["total_points"], 4 + 150 + 12 + 9 + 2)

    def test_odi_every_three_dots_and_milestone(self):
        r = score_official(match_format="ODI", runs=125, balls_faced=110,
                           fours=10, sixes=1, wickets=4, dots=10,
                           overs_bowled=10.0, runs_conceded=45, is_playing=True)
        self.assertEqual(r["breakdown"]["dot_balls"], 3)
        self.assertEqual(r["breakdown"]["batting_milestone_bonus"], 20)
        self.assertEqual(r["breakdown"]["wicket_haul_bonus"], 4)

    def test_t10_two_wicket_bonus(self):
        r = score_official(match_format="T10", runs=25, balls_faced=10,
                           fours=2, sixes=1, wickets=2, is_playing=True)
        self.assertEqual(r["breakdown"]["batting_milestone_bonus"], 8)
        self.assertEqual(r["breakdown"]["wicket_haul_bonus"], 4)

    def test_duck_requires_observed_dismissal(self):
        a = score_official(match_format="T20", runs=0, balls_faced=4, was_dismissed=False)
        b = score_official(match_format="T20", runs=0, balls_faced=4, was_dismissed=True)
        self.assertEqual(a["total_points"] - b["total_points"], 2)

    def test_cricket_overs_as_deliveries_not_decimal_fraction(self):
        from gl_engine.official_scoring import _overs_as_balls
        self.assertEqual(_overs_as_balls(4.2), 26)
        self.assertEqual(_overs_as_balls(2.5), 17)
        result = score_official(
            match_format="T20", overs_bowled=2.4, runs_conceded=12,
            is_playing=False
        )
        self.assertEqual(result["breakdown"]["legal_balls_bowled"], 16)
        # 12 conceded in 2.4 overs = 4.5 RPO, +6 economy, not 5.0 RPO.
        self.assertEqual(result["breakdown"]["bowling"], 6)

    def test_invalid_cricket_overs_rejected(self):
        for overs in (2.6, 4.25, -1.0, float("nan"), float("inf")):
            with self.subTest(overs=overs):
                with self.assertRaises(ValueError):
                    score_official(match_format="T20", overs_bowled=overs)

    def test_explicit_versioned_api(self):
        with TestClient(app) as client:
            res = client.post("/api/v1/score", json={
                "rule_version": RULE_VERSION, "match_format": "T20",
                "runs": 40, "balls_faced": 30, "fours": 4, "sixes": 2,
            })
            self.assertEqual(res.status_code, 200, res.text)
            self.assertEqual(res.json()["data"]["total_points"], 78)
            self.assertEqual(client.get("/api/v1/scoring/rules").status_code, 200)

    def test_invalid_inputs_fail_closed(self):
        with self.assertRaises(ValueError):
            score_official(match_format="T20", runs=1, fours=5)
        with self.assertRaises(ValueError):
            score_official(match_format="T20", wickets=1, bowled_lbw=2)


if __name__ == "__main__":
    unittest.main()
