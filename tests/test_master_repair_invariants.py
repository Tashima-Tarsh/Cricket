"""Phase 0 Safety Net: Regression test suite enforcing Master Repair Invariants:
1. ZERO dummy / synthetic players ("Top Batter 1", "Star Opener", "Tailender", "Strike Pacer").
2. ZERO match-specific hardcoded player lists that ignore match_id ("AFG_GURBAZ").
3. Universal DataProvenance schema on Player, Lineup, and public API responses.
4. Fail closed on missing rosters (never invent data or fall back silently).
5. No unverified "Rank 1 Contender" claims or artificial 0.946 backtesting multipliers.
"""
import inspect
import unittest
from pathlib import Path
from fastapi.testclient import TestClient

from gl_engine.models import Player, Lineup, VenueConditions, MatchupDetail, DataProvenance
from gl_engine.web_app import app
import gl_engine


class TestMasterRepairInvariants(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        self.root_dir = Path(__file__).parent.parent

    def test_zero_dummy_player_names_in_production_code(self):
        """Invariant 1: No synthetic dummy player names in production code paths."""
        forbidden_substrings = [
            "Top Batter 1",
            "Star Opener",
            "Tailender",
            "Strike Pacer",
            "AFG_GURBAZ",
            "Rank 1 Contender",
        ]
        scanned_dirs = [
            self.root_dir / "gl_engine",
            self.root_dir / "edgeforge",
            self.root_dir / "dream11-edge" / "edge"
        ]

        violations = []
        for sdir in scanned_dirs:
            if not sdir.exists():
                continue
            for py_path in sdir.rglob("*.py"):
                # Skip test files and migration notes
                if "test" in py_path.name.lower() or "patch" in py_path.name.lower():
                    continue
                content = py_path.read_text(encoding="utf-8", errors="ignore")
                for fb in forbidden_substrings:
                    if fb in content:
                        violations.append(f"{py_path.name} contains forbidden string '{fb}'")

        self.assertEqual(violations, [], f"Forbidden dummy/unverified strings found: {violations}")

    def test_zero_artificial_0946_multipliers(self):
        """Invariant 6 & 8: No artificial 0.946 multiplier in backtesting or evaluations."""
        for py_path in (self.root_dir / "gl_engine").rglob("*.py"):
            content = py_path.read_text(encoding="utf-8", errors="ignore")
            self.assertNotIn("0.946", content, f"{py_path.name} contains artificial 0.946 multiplier")

    def test_provenance_schema_on_core_models(self):
        """Invariant 3: Core models must declare and populate DataProvenance."""
        # 1. Player
        p = Player(
            id="p_test",
            name="Test Player",
            team="IND",
            role="BAT",
            credits=8.5,
            batting_style="RHB",
            batting_order_projected=3
        )
        self.assertTrue(hasattr(p, "provenance"))
        self.assertIsInstance(p.provenance, DataProvenance)
        self.assertEqual(p.provenance.verification_status, "UNVERIFIED")

        # 2. Lineup
        lineup = Lineup(
            team_name="Test Lineup",
            scenario_tag="TEST",
            players=[p],
            captain=p,
            vice_captain=p,
            total_credits=8.5,
            projected_points=45.0,
            simulated_ceiling=75.0,
            total_ownership_sum=50.0,
            differential_count=1,
            team_balance={"IND": 1},
            gl_rank_potential="Balanced",
            tactical_rationale="Test"
        )
        self.assertTrue(hasattr(lineup, "provenance"))
        self.assertIsInstance(lineup.provenance, DataProvenance)

        # 3. VenueConditions
        vc = VenueConditions(name="Test Ground", city="Test City")
        self.assertTrue(hasattr(vc, "provenance"))
        self.assertIsInstance(vc.provenance, DataProvenance)
        self.assertEqual(vc.provenance.verification_status, "EXPERT_ESTIMATE_UNVERIFIED")

    def test_fail_closed_on_unknown_match_state(self):
        """Invariant 4: /api/state fails closed (409) when match does not exist; never invents data."""
        resp = self.client.get("/api/state?match_id=completely_nonexistent_fixture_9999")
        self.assertEqual(resp.status_code, 409)

    def test_fail_closed_on_unknown_portal_roster(self):
        """Invariant 4: /api/portal/roster fails closed (404) when match does not exist; never invents players."""
        resp = self.client.get("/api/portal/roster?match_id=completely_nonexistent_fixture_9999")
        self.assertEqual(resp.status_code, 404)

    def test_portal_roster_carries_provenance(self):
        """Invariant 3: /api/portal/roster response contains provenance metadata."""
        resp = self.client.get("/api/portal/roster?match_id=afg_vs_zim_sharjah_odi")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("provenance", data)
        self.assertEqual(data["provenance"]["verification_status"], "VERIFIED")
        self.assertEqual(data["total_players"], 22)

    def test_api_state_carries_provenance_metadata(self):
        """Invariant 3: /api/state response carries provenance metadata."""
        resp = self.client.get("/api/state?force_refresh=true&overs=20")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue("data_provenance" in data or "provenance" in data)
        # Verify players carry provenance in state
        self.assertTrue(len(data["players"]) > 0)
        for p in data["players"]:
            self.assertIn("provenance", p)


if __name__ == "__main__":
    unittest.main()
