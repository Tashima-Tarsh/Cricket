"""Explicit, isolated test-only fixture generated from archived sample player records.

This helper is *never* imported by runtime code. It intentionally uses real
archived names solely to exercise the APIs without preloading any opponent.
"""
import json
from contextlib import contextmanager
from pathlib import Path
from unittest.mock import patch

from gl_engine import universal_engine as ue

FIXTURE_ID = "custom_test_archive"
ROOT = Path(__file__).resolve().parents[1]


def build_fixture():
    doc = json.loads((ROOT / "gl_engine" / "data" / "ind_wi_match.json").read_text(encoding="utf-8"))
    raw = doc["players"]
    teams = sorted({p["team"] for p in raw})
    if len(teams) != 2:
        raise AssertionError("Test archive must have precisely two teams")
    home, away = teams
    def xi(team):
        players = [p for p in raw if p["team"] == team]
        if len(players) != 11:
            raise AssertionError(f"Expected exactly 11 archived players for {team}")
        return [
            {"name": p["name"], "role": p["role"], "credits": p["credits"],
             "order": idx, "bat_hand": p.get("batting_style") or "RHB",
             "bowl_style": p.get("bowling_style") or "not recorded",
             "projected_ownership": p.get("projected_ownership")}
            for idx, p in enumerate(players, 1)
        ]
    return {
        "id": FIXTURE_ID,
        "match_id": FIXTURE_ID,
        "name": "Integration-test fixture",
        "format": "T20",
        "status": "USER SUPPLIED | [VERIFY REQUIRED]",
        "data_provenance": "TEST_ONLY_ARCHIVE",
        "teams": {
            "home": {"code": home, "name": "Test home"},
            "away": {"code": away, "name": "Test away"},
        },
        "venue": {"name": "Test ground"},
        "toss": {"winner": "Test home", "choice": "bat"},
        "current_crr": 0,
        "projected_total": 0,
        "chasing_win_prob": 0,
        "playing_xi_home": xi(home),
        "playing_xi_away": xi(away),
    }


@contextmanager
def connected_fixture():
    engine = ue.UniversalMatchEngine()
    fixture = build_fixture()
    engine._matches[FIXTURE_ID] = fixture
    engine._active_match_id = FIXTURE_ID
    with patch.object(ue, "_ENGINE_INSTANCE", engine):
        yield engine
