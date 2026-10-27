"""No user-facing API is allowed to masquerade simulated telemetry as observed."""
import unittest
from pathlib import Path
from fastapi.testclient import TestClient
from gl_engine.web_app import app


class PitchEvidenceSafetyTests(unittest.TestCase):
    def test_unsourced_tracking_endpoints_are_unavailable(self):
        with TestClient(app) as client:
            for path in ("/api/pitch/hawkeye", "/api/pitch/boundary-geometry",
                         "/api/pitch/degradation"):
                with self.subTest(path=path):
                    res = client.get(path)
                    self.assertEqual(res.status_code, 503)
                    self.assertIn("provenance", res.json())

    def test_stale_derived_telemetry_is_not_tracked_in_repository(self):
        root = Path(__file__).resolve().parents[1]
        for name in ("player_matchups.parquet", "venue_profiles.parquet"):
            with self.subTest(name=name):
                self.assertFalse((root / "data" / "processed" / name).exists())


if __name__ == "__main__":
    unittest.main()
