"""Live-match discovery must not invent toss, match date, or pitch observations."""
from unittest.mock import patch
from gl_engine import live_feed


class FakeClient:
    def live_matches(self):
        return [{
            "objectId": "match-42",
            "teams": [
                {"team": {"id": 1, "longName": "Sydney Sixers Women"}},
                {"team": {"id": 2, "longName": "Sydney Thunder Women"}},
            ],
            "stage": "PRE", "state": "PRE",
            "series": {"name": "Women's Big Bash League"},
            "ground": {"name": "North Sydney Oval"},
        }]


def test_unannounced_toss_has_no_fake_details():
    import sys
    from types import SimpleNamespace
    with patch.dict(sys.modules, {"cricdata": SimpleNamespace(CricinfoClient=FakeClient)}):
        got = live_feed._fetch_from_cricdata_sdk()[0]
    assert got["match_date"] is None
    assert got["toss"] is None
    assert got["toss_winner"] is None
    assert got["toss_decision"] is None
    assert got["pitch_report"] is None


def test_reported_toss_requires_real_team_and_decision():
    class WithToss(FakeClient):
        def live_matches(self):
            raw = super().live_matches()
            raw[0].update(tossWinnerTeamId=2, tossWinnerChoice=2)
            return raw
    import sys
    from types import SimpleNamespace
    with patch.dict(sys.modules, {"cricdata": SimpleNamespace(CricinfoClient=WithToss)}):
        got = live_feed._fetch_from_cricdata_sdk()[0]
    assert got["toss_winner"] == "Sydney Thunder Women"
    assert got["toss_decision"] == "bowl"
