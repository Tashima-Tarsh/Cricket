"""Regression: missing venue, odds or match inputs must not become fake facts."""
import unittest
from fastapi.testclient import TestClient
from gl_engine.web_app import app
from gl_engine.universal_engine import UniversalMatchEngine


class NoMockDefaults(unittest.TestCase):
    def test_no_hardcoded_archetype_by_country(self):
        engine = UniversalMatchEngine()
        meta = {"venue": {}, "teams": {"home": {"code": "ZIM-W"}, "away": {"code": "IND-W"}}, "toss": {}}
        self.assertEqual(engine.classify_match_archetype(meta), "UNCLASSIFIED_INSUFFICIENT_VENUE_EVIDENCE")

    def test_odds_endpoint_requires_actual_market_inputs(self):
        client = TestClient(app)
        self.assertEqual(client.get("/api/odds/devig").status_code, 422)

    def test_oracle_score_endpoints_require_context(self):
        client = TestClient(app)
        self.assertEqual(client.get("/api/oracle/projected-score").status_code, 422)
        self.assertEqual(client.get("/api/oracle/win-probability").status_code, 422)


if __name__ == "__main__":
    unittest.main()
