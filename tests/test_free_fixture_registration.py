"""Fixture registration must preserve cutoff and avoid invented competition details."""
from datetime import datetime, timezone, timedelta
import os
from tempfile import TemporaryDirectory
from unittest.mock import patch
import pytest
from pydantic import ValidationError
from gl_engine.free_intake import (
    RegisteredFixture, get_registered_fixture, register_fixture, list_active_fixtures
)


def valid(**kw):
    start = datetime.now(timezone.utc) + timedelta(hours=1)
    raw = dict(match_id="wbbl-new", competition="WBBL",
               team_a="Sydney Sixers", team_b="Sydney Thunder",
               scheduled_start_utc=start,
               fantasy_lock_utc=start - timedelta(minutes=5))
    raw.update(kw)
    return RegisteredFixture(**raw)


def test_register_retrieves_and_lists_active_only():
    with TemporaryDirectory() as tmp, patch.dict(os.environ, {
        "CRICKET_FREE_DATA_DB": tmp + "/free.sqlite3"}):
        r=register_fixture(valid())
        assert r["status"] == "REGISTERED_UNVERIFIED"
        stored=get_registered_fixture("wbbl-new")
        assert stored["competition"] == "WBBL"
        assert stored["team_a"] == "Sydney Sixers"
        assert len(list_active_fixtures()) == 1
        assert get_registered_fixture("nonexistent") is None


def test_bad_cutoff_rejected():
    start = datetime.now(timezone.utc)
    with pytest.raises(ValidationError):
        valid(fantasy_lock_utc=start+timedelta(hours=2))
    with pytest.raises(ValidationError):
        valid(latitude=2.0)
