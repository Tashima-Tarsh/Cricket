"""Authenticated research intake endpoints must fail closed on absent evidence."""
from datetime import datetime, timezone
from tempfile import TemporaryDirectory
from unittest.mock import patch
import os
from fastapi.testclient import TestClient
from gl_engine.web_app import app


def payload():
    return {
        "match_id": "wbbl-e2e-test", "page_url": "https://www.dream11.com/cricket/match/123",
        "observed_at_utc": datetime.now(timezone.utc).isoformat(),
        "players": [{"player_id":"p1","name":"Player One","team":"Sixers",
                     "role":"WK","credits":8.5,"selected_by_pct":30.5}]
    }


def test_api_ingestion_requires_admin_and_labels_unverified():
    with TemporaryDirectory() as tmp:
        with patch.dict(os.environ, {
            "CRICKET_FREE_DATA_DB": tmp+"/free.sqlite3",
            "CRICKET_ADMIN_TOKEN": "test-only-token",
        }):
            with TestClient(app) as client:
                data=payload()
                r=client.post("/api/v1/free/browser-pool",json=data)
                assert r.status_code==401
                headers={"Authorization":"Bearer test-only-token"}
                r=client.post("/api/v1/free/browser-pool",json=data,headers=headers)
                assert r.status_code==200, r.text
                assert r.json()["status"]=="RECORDED_UNVERIFIED"
                view=client.get("/api/v1/free/matches/wbbl-e2e-test",headers=headers)
                assert view.status_code==200,view.text
                doc=view.json()
                assert doc["browser_pool"]["player_count"]==1
                assert doc["browser_pool"]["players"][0]["selected_by_pct"]==30.5
                assert doc["optimization_ready"] is False
                assert doc["xi_evidence"]["official_status"]=="NOT_INDEPENDENTLY_AUTHENTICATED"
