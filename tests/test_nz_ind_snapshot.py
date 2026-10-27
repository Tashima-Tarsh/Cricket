"""Fixture snapshot is sourced, constrained and never called a confirmed XI."""
import unittest
from fastapi import HTTPException
from gl_engine.pretoss_research import get_pretoss_research, get_post_toss_research, validate_manual_xi, lineup_evidence


class TestNzIndResearch(unittest.TestCase):
    def test_every_provisional_portfolio_is_legal(self):
        doc=get_pretoss_research()
        self.assertEqual(len(doc["players"]),36)
        self.assertEqual(len(doc["provisional_teams"]),3)
        for team in doc["provisional_teams"]:
            self.assertEqual(len(team["names"]),11)
            self.assertLessEqual(team["credits"],100)
            self.assertLessEqual(max(team["team_split"].values()),7)
            self.assertIsNone(team["rank_1_probability"])
        self.assertFalse(any(p["is_confirmed_xi"] for p in doc["players"]))

    def test_posttoss_three_legal_portfolios_and_actual_toss(self):
        report = get_post_toss_research()
        self.assertEqual(report["toss"], {"winner": "IND", "decision": "bowl", "submitted_as": "India have won the toss and have opted to field"})
        self.assertEqual(len(report["player_pool"]), 22)
        self.assertEqual(len(report["teams"]), 3)
        self.assertIsNone(report["rank_1_probability"])
        expected = {"entry_5": 90.5, "entry_19": 88.0, "entry_49": 90.5}
        available = {p["name"] for p in report["player_pool"]}
        for team in report["teams"]:
            self.assertAlmostEqual(team["credits"], expected[team["contest"]])
            self.assertEqual(len(team["names"]), 11)
            self.assertTrue(set(team["names"]).issubset(available))
            self.assertLessEqual(max(team["team_split"].values()), 7)

    def test_pretoss_is_not_confirmed(self):
        doc=get_pretoss_research()
        a=[p["name"] for p in doc["players"] if p["team"]=="NZ" and p["group"]=="past_lineup"]
        b=[p["name"] for p in doc["players"] if p["team"]=="IND" and p["group"]=="past_lineup"]
        self.assertEqual(len(validate_manual_xi(a,b)),22)

    def test_unknown_and_duplicate_players_fail(self):
        doc=get_pretoss_research()
        with self.assertRaises(HTTPException):
            lineup_evidence(["MYSTERY"]*11,"MYSTERY","MYSTERY",doc["players"])
        a=[p["name"] for p in doc["players"] if p["team"]=="NZ" and p["group"]=="past_lineup"]
        b=[p["name"] for p in doc["players"] if p["team"]=="IND" and p["group"]=="past_lineup"]
        a[0]="Not On Screenshot"
        with self.assertRaises(HTTPException):
            validate_manual_xi(a,b)


if __name__=="__main__":
    unittest.main()
