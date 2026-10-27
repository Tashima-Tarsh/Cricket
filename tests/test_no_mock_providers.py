"""No bundled pretend provider scorecards in deployable API clients."""
import unittest
from pathlib import Path
from fastapi.testclient import TestClient
from gl_engine.web_app import app


class NoMockProviders(unittest.TestCase):
    def test_provider_clients_have_no_mock_implementations(self):
        root = Path(__file__).resolve().parents[1]
        for file in ("gl_engine/cricketdata_api.py", "gl_engine/providers/sportmonks_api.py"):
            with self.subTest(file=file):
                text = (root / file).read_text(encoding="utf-8")
                self.assertNotIn("def _mock_", text)

    def test_archive_is_not_fantasy_fixture_loader(self):
        client = TestClient(app)
        resp = client.post("/api/cricsheet/load/1082591")
        self.assertIn(resp.status_code, (401, 503))

    def test_live_feed_is_not_fantasy_fixture_loader(self):
        client = TestClient(app)
        resp = client.post("/api/live/load/12345")
        self.assertIn(resp.status_code, (401, 503))


if __name__ == "__main__":
    unittest.main()
