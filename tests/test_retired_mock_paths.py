"""Unsafe historic match defaults must not be served as current research."""
import unittest
from fastapi.testclient import TestClient
from gl_engine.web_app import app
from gl_engine.live_feed import load_cricdata_match_detail


class RetiredMockPaths(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_legacy_fixed_portfolio_is_retired(self):
        self.assertEqual(self.client.get("/api/teams").status_code, 410)
        self.assertEqual(self.client.get("/api/teams/portfolio").status_code, 410)

    def test_unsourced_sdk_detail_is_not_fabricated(self):
        self.assertIsNone(load_cricdata_match_detail("unverified-fixture"))

    def test_unlicensed_commentary_does_not_guess_pitch(self):
        from gl_engine.daily_match_sync import DailyMatchSyncEngine
        data = DailyMatchSyncEngine().fetch_live_commentary_and_scorecard("123")
        self.assertEqual(data["status"], "UNAVAILABLE")
        self.assertIsNone(data["pitch_report"])


if __name__ == "__main__":
    unittest.main()
