"""Guard against replaying per-match screenshots as production data."""
import unittest
from pathlib import Path
from gl_engine.web_app import app


class MatchDataIsolationTests(unittest.TestCase):
    def test_current_match_snapshots_not_packaged(self):
        root = Path(__file__).resolve().parents[1]
        self.assertFalse((root / "gl_engine" / "pretoss_research.py").exists())
        self.assertFalse(list((root / "data" / "snapshots").glob("nz_ind_*.json")))

    def test_runtime_has_no_preloaded_match_and_nonexistent_snapshot_route(self):
        from fastapi.testclient import TestClient
        from tempfile import TemporaryDirectory
        from gl_engine import universal_engine as ue
        from unittest.mock import patch
        with TemporaryDirectory() as temp:
            fresh = ue.UniversalMatchEngine(Path(temp) / "fresh.sqlite3")
            self.assertEqual(fresh.list_available_matches(), [])
            self.assertIsNone(fresh._active_match_id)
            with patch.object(ue, "_ENGINE_INSTANCE", fresh):
                c = TestClient(app)
                self.assertEqual(c.get("/api/matches").json()["matches"], [])
                self.assertEqual(c.get("/api/state").status_code, 409)
                self.assertEqual(c.get("/api/portal/match-data?match_id=unknown").status_code, 409)
                status = c.get("/api/v1/readiness").json()
                self.assertFalse(status["model_calibrated_rank1_probabilities"])

    def test_no_hardcoded_production_fixture_sources(self):
        root = Path(__file__).resolve().parents[1]
        forbidden = [
            "ind_w_vs_zim_w_2026_02", "ind_vs_wi_5th_t20_2026",
            "afg_vs_zim_sharjah_odi", "nz_ind_2026_10_27",
        ]
        for source in ("gl_engine/universal_engine.py", "gl_engine/match_catalog.py",
                       "gl_engine/mcp_server.py", "gl_engine/portal_fixtures.py",
                       "frontend/src/context/MatchContext.tsx", "frontend/src/views/CommandCenter.tsx",
                       "frontend/src/views/PitchLab.tsx", "frontend/src/components/IntelligenceDrawer.tsx"):
            text = (root / source).read_text(encoding="utf-8")
            for fixture_id in forbidden:
                self.assertNotIn(fixture_id, text, source)
        self.assertFalse((root / "frontend/dist").exists(),
                         "Old tracked JS bundles must not shadow new UI sources")

    def test_no_fixture_specific_snapshot_endpoint(self):
        paths = {route.path for route in app.routes if hasattr(route, "path")}
        self.assertFalse(any("/research/nz-ind-" in path for path in paths))


if __name__ == "__main__":
    unittest.main()
