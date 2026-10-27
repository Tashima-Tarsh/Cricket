import unittest
from fastapi.testclient import TestClient
from gl_engine.web_app import app
from gl_engine.datasets_2026 import Datasets2026Pipeline

class NoMockSchedules(unittest.TestCase):
    def test_unattested_handwritten_schedule_is_not_live(self):
        self.assertEqual(Datasets2026Pipeline().get_season_2026_fixtures(), [])
        data = TestClient(app).get("/api/datasets/2026-schedule").json()
        self.assertEqual(data["status"], "unavailable")
        self.assertEqual(data["fixtures"], [])

if __name__ == "__main__":
    unittest.main()
