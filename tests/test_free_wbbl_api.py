"""End-to-end registered fixture to free research report API contract."""
from datetime import datetime, timezone, timedelta
from tempfile import TemporaryDirectory
from unittest.mock import patch
import os
from fastapi.testclient import TestClient
from gl_engine.web_app import app


def test_fixture_registration_watchlist_and_blocked_report():
    with TemporaryDirectory() as tmp, patch.dict(os.environ, {
         "CRICKET_FREE_DATA_DB": tmp+"/free.sqlite3",
         "CRICKET_ADMIN_TOKEN": "test-only-strong-token"}):
        ts=datetime.now(timezone.utc)+timedelta(hours=2)
        headers={"Authorization":"Bearer test-only-strong-token"}
        fixture=dict(match_id="match-stage-789",competition="WBBL",
                     team_a="Sydney Sixers",team_b="Sydney Thunder",
                     scheduled_start_utc=ts.isoformat(),
                     fantasy_lock_utc=(ts-timedelta(minutes=5)).isoformat())
        with TestClient(app) as client:
            denied=client.post("/api/v1/free/fixtures",json=fixture)
            assert denied.status_code==401
            created=client.post("/api/v1/free/fixtures",json=fixture,headers=headers)
            assert created.status_code==200, created.text
            watch=client.get("/api/v1/free/watchlist",headers=headers)
            assert watch.status_code==200
            assert [x["match_id"] for x in watch.json()["matches"]]==["match-stage-789"]
            report=client.post("/api/v1/free/matches/match-stage-789/generate",
                               headers=headers)
            assert report.status_code==200, report.text
            assert report.json()["report"]["reason"]=="TOSS_NOT_OBSERVED"
            saved=client.get("/api/v1/free/matches/match-stage-789/latest-report",
                             headers=headers)
            assert saved.status_code==200
            assert saved.json()["report"]["status"]=="BLOCKED"
