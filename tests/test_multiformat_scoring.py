"""Phase 2: Unit tests verifying multi-format fantasy scoring parity across T20, ODI, and T10.
Asserts parity between gl_engine.CricketFantasyScoring and edgeforge.Dream11Scorer against official Dream11 rules.
"""
import sys
from pathlib import Path
root = str(Path(__file__).parent.parent)
if root not in sys.path:
    sys.path.insert(0, root)

import unittest

from gl_engine.capabilities.c11_fantasy_scoring import CricketFantasyScoring
from edgeforge.score.dream11 import Dream11Scorer


class TestMultiFormatScoring(unittest.TestCase):
    def setUp(self):
        self.gl_scorer = CricketFantasyScoring()
        self.edge_scorer = Dream11Scorer()

    def test_t20_scoring_rules(self):
        """Test standard official Dream11 T20 rules: +30 wkt, +8 lbw, +1 dot, +4 XI, milestones 30/50/100."""
        # 1. Batter: 40 runs, 30 balls, 4 fours, 2 sixes
        # XI (4) + Runs (40) + 4s (4) + 6s (4) + 30-milestone (4) + SR 133.3 (2) = 58.0
        gl_res = self.gl_scorer.calculate_player_points(
            runs=40, balls_faced=30, fours=4, sixes=2, is_playing=True, match_format="T20"
        )
        edge_res = self.edge_scorer.calculate(
            runs=40, balls_faced=30, fours=4, sixes=2, is_playing=True, match_format="T20"
        )
        self.assertEqual(gl_res["total_points"], 58.0)
        self.assertEqual(edge_res.total, 58.0)

        # 2. Bowler: 2 wkts (60), 1 lbw (8), 8 dots (8), 4 overs conceded 24 (econ 6.0 -> +4), XI (4) = 84.0
        gl_bowl = self.gl_scorer.calculate_player_points(
            wickets=2, bowled_lbw=1, dots=8, overs_bowled=4.0, runs_conceded=24, is_playing=True, match_format="T20"
        )
        edge_bowl = self.edge_scorer.calculate(
            wickets=2, bowled_lbw=1, dots=8, overs_bowled=4.0, runs_conceded=24, is_playing=True, match_format="T20"
        )
        self.assertEqual(gl_bowl["total_points"], 84.0)
        self.assertEqual(edge_bowl.total, 84.0)

    def test_odi_scoring_rules(self):
        """Test official Dream11 ODI rules: 25 wkt, 4 maiden, 50/100/150 milestones (4/8/16)."""
        # Batter: 55 runs off 45 balls (SR 122.2 -> +4), 5 fours (+5), 1 six (+2), 50-bonus (+4), XI (+4)
        # Total = 55 + 5 + 2 + 4 + 4 + 4 = 74.0
        gl_res = self.gl_scorer.calculate_player_points(
            runs=55, balls_faced=45, fours=5, sixes=1, is_playing=True, match_format="ODI"
        )
        edge_res = self.edge_scorer.calculate(
            runs=55, balls_faced=45, fours=5, sixes=1, is_playing=True, match_format="ODI"
        )
        self.assertEqual(gl_res["total_points"], 74.0)
        self.assertEqual(edge_res.total, 74.0)

        # Bowler: 2 wkts (50), 1 maiden (4), 12 dots (12), 10 overs conceded 42 (econ 4.2 -> +4), XI (4) = 74.0
        gl_bowl = self.gl_scorer.calculate_player_points(
            wickets=2, maidens=1, dots=12, overs_bowled=10.0, runs_conceded=42, is_playing=True, match_format="ODI"
        )
        edge_bowl = self.edge_scorer.calculate(
            wickets=2, maidens=1, dots=12, overs_bowled=10.0, runs_conceded=42, is_playing=True, match_format="ODI"
        )
        self.assertEqual(gl_bowl["total_points"], 74.0)
        self.assertEqual(edge_bowl.total, 74.0)

    def test_t10_scoring_rules(self):
        """Test first-class Dream11 T10 rules: 30 wkt, 12 maiden, 30/50 milestones (8/16), 5-ball min SR, 1-ov min econ."""
        # Batter: 36 runs off 12 balls (SR 300.0 > 250 -> +6), 3 fours (+3), 3 sixes (+6), 30-bonus (+8), XI (+4)
        # Total = 36 + 3 + 6 + 8 + 6 + 4 = 63.0
        gl_res = self.gl_scorer.calculate_player_points(
            runs=36, balls_faced=12, fours=3, sixes=3, is_playing=True, match_format="T10"
        )
        edge_res = self.edge_scorer.calculate(
            runs=36, balls_faced=12, fours=3, sixes=3, is_playing=True, match_format="T10"
        )
        self.assertEqual(gl_res["total_points"], 63.0)
        self.assertEqual(edge_res.total, 63.0)

        # Bowler: 2 wkts (60), 1 over conceded 5 (econ 5.0 < 6.0 -> +6), 4 dots (4), XI (4) = 74.0
        gl_bowl = self.gl_scorer.calculate_player_points(
            wickets=2, dots=4, overs_bowled=1.0, runs_conceded=5, is_playing=True, match_format="T10"
        )
        edge_bowl = self.edge_scorer.calculate(
            wickets=2, dots=4, overs_bowled=1.0, runs_conceded=5, is_playing=True, match_format="T10"
        )
        self.assertEqual(gl_bowl["total_points"], 74.0)
        self.assertEqual(edge_bowl.total, 74.0)

    def test_captain_and_vice_captain_multipliers(self):
        """Test C=2.0x and VC=1.5x multipliers applied to total."""
        base_gl = self.gl_scorer.calculate_player_points(
            runs=40, balls_faced=30, fours=4, sixes=2, is_playing=True, match_format="T20"
        )
        c_gl = self.gl_scorer.calculate_player_points(
            runs=40, balls_faced=30, fours=4, sixes=2, is_playing=True, match_format="T20", is_captain=True
        )
        vc_gl = self.gl_scorer.calculate_player_points(
            runs=40, balls_faced=30, fours=4, sixes=2, is_playing=True, match_format="T20", is_vice_captain=True
        )
        self.assertEqual(base_gl["total_points"], 58.0)
        self.assertEqual(c_gl["total_points"], 116.0)
        self.assertEqual(vc_gl["total_points"], 87.0)

    def test_shared_scoring_parity_at_economy_boundary(self):
        from edge.score import BowlLine, BatLine, FieldLine, points
        from edgeforge.score.dream11 import Dream11Scorer
        from gl_engine.capabilities.c11_fantasy_scoring import CricketFantasyScoring
        common = dict(wickets=4, bowled_lbw=2, overs_bowled=4.0,
                      runs_conceded=20, is_playing=False, match_format="T20")
        core = CricketFantasyScoring().calculate_player_points(**common)["total_points"]
        adapter = Dream11Scorer().calculate(**common).total
        legacy = points(BatLine(batted=False), BowlLine(
            balls=24, runs=20, wickets=4, lbw_bowled=2
        ), FieldLine())
        self.assertEqual(core, adapter)
        self.assertEqual(core, legacy)
        self.assertEqual(core, 148.0)

    def test_duck_penalty(self):
        """Duck (-2 pts) when dismissed for 0 after facing at least 1 ball."""
        gl_res = self.gl_scorer.calculate_player_points(
            runs=0, balls_faced=3, is_playing=False, match_format="T20"
        )
        edge_res = self.edge_scorer.calculate(
            runs=0, balls_faced=3, is_playing=False, match_format="T20"
        )
        self.assertEqual(gl_res["total_points"], -2.0)
        self.assertEqual(edge_res.total, -2.0)


if __name__ == "__main__":
    unittest.main()
