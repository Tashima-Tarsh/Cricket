"""Guard against replaying per-match screenshots as production data."""
import unittest
from pathlib import Path
from gl_engine.web_app import app


class MatchDataIsolationTests(unittest.TestCase):
    def test_current_match_snapshots_not_packaged(self):
        root = Path(__file__).resolve().parents[1]
        self.assertFalse((root / "gl_engine" / "pretoss_research.py").exists())
        self.assertFalse(list((root / "data" / "snapshots").glob("nz_ind_*.json")))

    def test_no_fixture_specific_snapshot_endpoint(self):
        paths = {route.path for route in app.routes}
        self.assertFalse(any("/research/nz-ind-" in path for path in paths))


if __name__ == "__main__":
    unittest.main()
