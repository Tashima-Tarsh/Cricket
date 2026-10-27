"""Tests for End-to-End Match Pipeline and State Machine."""
import unittest
from gl_engine.match_pipeline import MatchPipeline, MatchState
from gl_engine.models import Player
from datetime import datetime, timezone


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


def checked_report(match_id, players):
    return {
        "fixture_id": match_id, "status": "CROSS_PROVIDER_CORROBORATED",
        "provider_fixture_ids": {"sportmonks": "reference_a", "cricketdata": "reference_b"},
        "count": 22, "sources": ["sportmonks_live", "cricketdata_live"],
        "checked_at_utc": datetime.now(timezone.utc).isoformat(),
        "teams": [{"name": team, "players": [p.name.lower() for p in players if p.team == team]}
                  for team in sorted({p.team for p in players})],
    }


def full_roster():
    team_roles = ["WK", "BAT", "BAT", "BAT", "BAT", "AR", "AR", "BOWL", "BOWL", "BOWL", "BOWL"]
    a = [make_test_player(f"a_{i}", f"Player A{i}", "TEAM_A", role=role, credits=9.0)
         for i, role in enumerate(team_roles)]
    b = [make_test_player(f"b_{i}", f"Player B{i}", "TEAM_B", role=role, credits=9.0)
         for i, role in enumerate(team_roles)]
    return a + b


class TestMatchPipeline(unittest.TestCase):
    def test_lifecycle_and_readiness_progression(self):
        pipe = MatchPipeline("fixture_t20_01", format_type="T20", is_womens=False)
        self.assertEqual(pipe.current_state, MatchState.DISCOVERED)
        self.assertFalse(pipe.readiness.optimization_ready)

        # 1. Supply full 22-player roster
        squad = full_roster()
        pipe.set_roster(squad, evidence_source="test_adapter")

        self.assertEqual(pipe.current_state, MatchState.ROSTER_AVAILABLE)
        self.assertTrue(pipe.readiness.roster_available)
        self.assertTrue(pipe.readiness.fantasy_credits_available)
        self.assertFalse(pipe.readiness.optimization_ready)  # XI not yet confirmed

        # 2. Register Toss
        pipe.register_toss(winner="TEAM_A", decision="bat", evidence_source="test_toss_feed")
        self.assertEqual(pipe.current_state, MatchState.TOSS_PENDING)

        # 3. Confirm 22 Lineup
        with self.assertRaises(ValueError):
            pipe.confirm_lineup(squad, evidence_source="user_attested")
        pipe.confirm_lineup(squad, evidence_source="test_verifier",
                            corroboration=checked_report(pipe.match_id, squad))
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
        pool = full_roster()
        pipe.set_roster(pool, evidence_source="test_adapter")
        pipe.register_toss(winner="TEAM_A", decision="bat", evidence_source="test_toss")
        pipe.confirm_lineup(pool, evidence_source="trusted_test_verifier",
                            corroboration=checked_report(pipe.match_id, pool))
        lineup = [pool[i] for i in (0, 1, 2, 5, 7, 8)] + [pool[12], pool[13], pool[16], pool[18], pool[19]]
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


    def test_illegal_transition_and_wrong_fixture_evidence(self):
        pipe = MatchPipeline("fixture_integrity")
        with self.assertRaises(ValueError):
            pipe.transition_to(MatchState.COMPLETED, evidence_source="jump")
        pool = full_roster()
        pipe.set_roster(pool, evidence_source="trusted_input")
        with self.assertRaises(ValueError):
            pipe.confirm_lineup(pool, evidence_source="unverified_manually")
        wrong = checked_report("different_match", pool)
        with self.assertRaises(ValueError):
            pipe.confirm_lineup(pool, evidence_source="trusted_report", corroboration=wrong)
        self.assertFalse(pipe.readiness.official_xi_confirmed)

    def test_export_illegal_rosters_are_rejected(self):
        pipe = MatchPipeline("legal_test")
        pool = full_roster()
        pipe.set_roster(pool, evidence_source="source")
        pipe.confirm_lineup(pool, evidence_source="verified",
                            corroboration=checked_report(pipe.match_id, pool))
        legal = [pool[i] for i in (0, 1, 2, 5, 7, 8)] + [pool[12], pool[13], pool[16], pool[18], pool[19]]
        for lineup, captain, vc in [
            (legal, legal[0], legal[0]),
            (legal[:10] + [legal[0]], legal[0], legal[1]),
            ([pool[i] for i in range(11)], pool[0], pool[1]),
            (legal, pool[3], legal[1]),
            ([legal[0].model_copy(update={"role": "AR"})] + legal[1:], legal[0], legal[1]),
        ]:
            with self.subTest(lineup=[p.id for p in lineup]):
                with self.assertRaises(ValueError):
                    pipe.export_lineup_json(lineup, captain, vc)
                with self.assertRaises(ValueError):
                    pipe.export_lineup_csv(lineup, captain, vc)

if __name__ == "__main__":
    unittest.main()

