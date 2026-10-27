"""Tests for End-to-End Match Pipeline and State Machine."""
import unittest
from gl_engine.match_pipeline import MatchPipeline, MatchState
from gl_engine.models import Player


def make_test_player(p_id: str, name: str, team: str, role: str = "BAT", credits: float = 8.5) -> Player:
    return Player(
        id=p_id,
        name=name,
        team=team,
        role=role,
        credits=credits,
        batting_style="RHB",
        batting_order_projected=3
    )


class TestMatchPipeline(unittest.TestCase):
    def test_lifecycle_and_readiness_progression(self):
        pipe = MatchPipeline("fixture_t20_01", format_type="T20", is_womens=False)
        self.assertEqual(pipe.current_state, MatchState.DISCOVERED)
        self.assertFalse(pipe.readiness.optimization_ready)

        # 1. Supply full 22-player roster
        squad_a = [make_test_player(f"a_{i}", f"Player A{i}", "TEAM_A") for i in range(11)]
        squad_b = [make_test_player(f"b_{i}", f"Player B{i}", "TEAM_B") for i in range(11)]
        pipe.set_roster(squad_a + squad_b, evidence_source="test_adapter")

        self.assertEqual(pipe.current_state, MatchState.ROSTER_AVAILABLE)
        self.assertTrue(pipe.readiness.roster_available)
        self.assertTrue(pipe.readiness.fantasy_credits_available)
        self.assertFalse(pipe.readiness.optimization_ready)  # XI not yet confirmed

        # 2. Register Toss
        pipe.register_toss(winner="TEAM_A", decision="bat", evidence_source="test_toss_feed")
        self.assertEqual(pipe.current_state, MatchState.TOSS_PENDING)

        # 3. Confirm 22 Lineup
        pipe.confirm_lineup(squad_a + squad_b, evidence_source="test_lineup_feed")
        self.assertEqual(pipe.current_state, MatchState.XI_CONFIRMED)
        self.assertTrue(pipe.readiness.official_xi_confirmed)
        self.assertTrue(pipe.readiness.optimization_ready)

    def test_incomplete_roster_sets_roster_pending(self):
        pipe = MatchPipeline("fixture_incomplete", format_type="ODI")
        partial_squad = [make_test_player(f"p_{i}", f"Player {i}", "TEAM_A") for i in range(10)]
        pipe.set_roster(partial_squad, evidence_source="partial_feed")
        self.assertEqual(pipe.current_state, MatchState.ROSTER_PENDING)
        self.assertFalse(pipe.readiness.roster_available)

    def test_lineup_exports_json_and_csv(self):
        pipe = MatchPipeline("match_export_test", format_type="T20")
        lineup = [make_test_player(f"p_{i}", f"Player {i}", "TEAM_A" if i < 6 else "TEAM_B", credits=9.0) for i in range(11)]
        captain = lineup[0]
        vc = lineup[1]

        # JSON export
        json_out = pipe.export_lineup_json(lineup, captain, vc, scenario_label="pacer_dominance")
        self.assertEqual(json_out["fixture_id"], "match_export_test")
        self.assertEqual(len(json_out["players"]), 11)
        self.assertEqual(json_out["captain"]["id"], captain.id)
        self.assertEqual(json_out["vice_captain"]["id"], vc.id)
        self.assertEqual(json_out["total_credits_used"], 99.0)
        self.assertEqual(json_out["unused_credits"], 1.0)
        self.assertIn("provenance", json_out)

        # CSV export
        csv_out = pipe.export_lineup_csv(lineup, captain, vc, scenario_label="pacer_dominance")
        lines = csv_out.strip().splitlines()
        self.assertEqual(len(lines), 12)  # 1 header + 11 players
        self.assertIn("MatchID,PlayerID,PlayerName", lines[0])
        self.assertIn(captain.id, lines[1])


if __name__ == "__main__":
    unittest.main()

