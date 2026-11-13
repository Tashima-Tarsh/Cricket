"""Tests for free-only match data intake: never infer missing XI, credits or ownership."""
from datetime import datetime, timezone, timedelta
from tempfile import TemporaryDirectory
from unittest.mock import patch
import os

import pytest
from pydantic import ValidationError

from gl_engine.free_intake import (
    BrowserPoolSnapshot, TossObservation, XIObservation, save_snapshot, get_match_state,
)


def stamp():
    return datetime.now(timezone.utc).isoformat()


def player(n, role="BAT", team="Sydney Sixers"):
    return {"player_id": f"p{n}", "name": f"Player {n}", "team": team, "role": role, "credits": 8.5}


def browser(players=None, **kwargs):
    return BrowserPoolSnapshot.model_validate({
        "match_id": "wbbl-test-1", "page_url": "https://www.dream11.com/cricket/match/123",
        "observed_at_utc": stamp(), "players": players or [player(1)], **kwargs
    })


def test_browser_requires_real_fields():
    with pytest.raises(ValidationError):
        BrowserPoolSnapshot.model_validate({
            "match_id": "m", "page_url": "https://www.dream11.com/match/42",
            "observed_at_utc": stamp(), "players": [{"name": "Someone"}],
        })
    with pytest.raises(ValidationError):
        browser([dict(player(1), selected_by_pct=111)])
    with pytest.raises(ValidationError):
        BrowserPoolSnapshot.model_validate({
            "match_id": "m", "page_url": "https://evil.example/m",
            "observed_at_utc": stamp(), "players": [player(1)],
        })


def test_capture_is_idempotent_and_never_official():
    with TemporaryDirectory() as tmp, patch.dict(os.environ, {"CRICKET_FREE_DATA_DB": tmp + "/data.db"}):
        snap = browser([player(1, "WK")])
        save_snapshot("browser", snap)
        save_snapshot("browser", snap)
        current = get_match_state("wbbl-test-1")
        assert current["browser_pool"]["player_count"] == 1
        assert current["browser_pool"]["players"][0]["selected_by_pct"] is None
        assert current["optimization_ready"] is False
        assert current["xi_evidence"]["official_status"] == "NOT_INDEPENDENTLY_AUTHENTICATED"


def test_partial_browser_tabs_merge_without_substitution():
    with TemporaryDirectory() as tmp, patch.dict(os.environ, {"CRICKET_FREE_DATA_DB": tmp + "/data.db"}):
        save_snapshot("browser", browser([player(1, "WK")]))
        save_snapshot("browser", browser([player(2, "BOWL")]))
        current = get_match_state("wbbl-test-1")
        assert current["browser_pool"]["player_count"] == 2
        assert not current["browser_pool"]["candidate_pool_complete"]


def test_toss_is_not_an_official_xi():
    with TemporaryDirectory() as tmp, patch.dict(os.environ, {"CRICKET_FREE_DATA_DB": tmp + "/data.db"}):
        event = TossObservation.model_validate({
            "match_id": "wbbl-test-1", "source_url": "https://www.espncricinfo.com/series/test",
            "source_type": "ESPN_REFERENCE", "observed_at_utc": stamp(),
            "toss_winner": "Sydney Sixers", "toss_decision": "bowl"
        })
        save_snapshot("toss", event)
        state = get_match_state("wbbl-test-1")
        assert state["toss"]["toss_decision"] == "bowl"
        assert state["optimization_ready"] is False


def test_distinct_sources_only_count_as_unattested_agreement():
    with TemporaryDirectory() as tmp, patch.dict(os.environ, {"CRICKET_FREE_DATA_DB": tmp + "/data.db"}):
        base = {
            "match_id": "wbbl-test-1", "observed_at_utc": stamp(),
            "team_a": "Sixers", "team_b": "Thunder",
            "players_a": [f"A {i}" for i in range(11)],
            "players_b": [f"B {i}" for i in range(11)],
            "announcement_type": "ANNOUNCED_PLAYING_XI",
        }
        a = XIObservation.model_validate(dict(base, source_url="https://www.cricket.com.au/matches/1"))
        b = XIObservation.model_validate(dict(base, source_url="https://www.espncricinfo.com/scorecard/1"))
        save_snapshot("xi", a)
        save_snapshot("xi", b)
        state = get_match_state("wbbl-test-1")
        assert state["xi_evidence"]["agreement"]["status"] == "TWO_SOURCES_AGREE_UNATTESTED"
        assert state["optimization_ready"] is False


def test_rejects_stale_or_naive_observations():
    with pytest.raises(ValidationError):
        browser([player(1)], observed_at_utc=(datetime.now(timezone.utc) - timedelta(days=3)).isoformat())
    with pytest.raises(ValidationError):
        browser([player(1)], observed_at_utc="2026-11-13T22:00:00")
