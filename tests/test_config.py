"""
Unit tests for bbl_wbbl_engine configuration.
"""
from config import LEAGUE, SCORING, ROLE_BOUNDS, SCENARIOS, VENUE_ADJUSTMENTS, TRAVEL_FATIGUE_PENALTY


def test_config_has_required_keys():
    assert LEAGUE in ("BBL", "WBBL")
    assert "run" in SCORING
    assert "wicket" in SCORING
    assert "WK" in ROLE_BOUNDS
    assert "BAT" in ROLE_BOUNDS
    assert "AR" in ROLE_BOUNDS
    assert "BOWL" in ROLE_BOUNDS


def test_role_bounds_valid():
    for role, (lo, hi) in ROLE_BOUNDS.items():
        assert lo > 0
        assert hi >= lo
        assert hi <= 7


def test_scenarios_count():
    assert len(SCENARIOS) == 6
    for s in ["balanced", "death_bowler_special", "top_collapse",
              "high_scoring_chase", "spin_dominance", "pace_dominance"]:
        assert s in SCENARIOS


def test_scoring_values():
    assert SCORING["run"] == 1
    assert SCORING["wicket"] == 25
    assert SCORING["catch"] == 8
