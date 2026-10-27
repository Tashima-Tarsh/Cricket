"""Regression checks for evidence integrity and fail-closed fantasy selection."""
import unittest
from fastapi import HTTPException
from gl_engine.roster_safety import validate_confirmed_xi
from gl_engine.unique_engine import UniqueTeamEngine


def roster():
    players = []
    for team in ("ALPHA", "BRAVO"):
        for idx in range(11):
            role = ("WK" if idx == 0 else "BAT" if idx < 5 else "AR" if idx < 7 else "BOWL")
            players.append({
                "id": f"{team}_{idx}", "name": f"{team} RealName {idx}", "team": team,
                "role": role, "credits": 8.5, "predicted_points": 40.0 + idx,
                "predicted_ownership": 30.0, "is_confirmed_xi": True,
            })
    return players


class EvidenceIntegrityTests(unittest.TestCase):
    def test_confirmed_xi_requires_exact_eleven_per_team(self):
        players = roster()
        self.assertEqual(len(validate_confirmed_xi(players)), 22)
        for invalid in (players[:21], players[:11] + [dict(p, team="ALPHA") for p in players[11:]]):
            with self.assertRaises(HTTPException):
                validate_confirmed_xi(invalid)
        players[0]["is_confirmed_xi"] = False
        with self.assertRaises(HTTPException):
            validate_confirmed_xi(players)

    def test_unique_optimizer_never_restores_excluded_player(self):
        engine = UniqueTeamEngine()
        players = roster()
        excluded = players[0]["id"]
        teams = engine.generate_unique_teams(players, num_teams=1, uniqueness_level=1,
                                            excluded_player_ids=[excluded], contest_spots=20)
        self.assertTrue(teams, "Feasible pool should produce one lineup")
        team = teams[0]
        names = [p["id"] for p in team["players"]]
        self.assertEqual(len(names), 11)
        self.assertNotIn(excluded, names)
        self.assertLessEqual(max(sum(p["team"] == t for p in team["players"]) for t in ("ALPHA", "BRAVO")), 7)
        self.assertIsNone(team["rank_1_probability_pct"])

    def test_unique_optimizer_rejects_unconfirmed_after_toss(self):
        players = roster()
        players[-1]["is_confirmed_xi"] = False
        self.assertEqual(UniqueTeamEngine().generate_unique_teams(
            players, num_teams=1, uniqueness_level=1, toss_completed=True), [])

    def test_field_rank_remains_unavailable_without_calibration(self):
        engine = UniqueTeamEngine()
        players = roster()
        team = {"players": players[:11], "captain": players[0], "vice_captain": players[1]}
        result = engine._simulate_rank1_distribution([team], players, n_sims=5, contest_spots=12)
        self.assertIsNone(result[0]["rank_1_pct"])
        self.assertIsNone(result[0]["top_10_pct"])

if __name__ == "__main__":
    unittest.main()
