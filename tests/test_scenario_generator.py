"""
Unit tests for scenario_generator.py
"""
from scenario_generator import SCENARIOS, describe, teams_for_scenario


def test_scenarios():
    expected = ["balanced", "death_bowler_special", "top_collapse",
                "high_scoring_chase", "spin_dominance", "pace_dominance"]
    assert SCENARIOS == expected


def test_describe():
    for s in SCENARIOS:
        d = describe(s)
        assert isinstance(d, str)
        assert len(d) > 0


def test_teams_for_scenario():
    for s in SCENARIOS:
        n = teams_for_scenario(s)
        assert isinstance(n, int)
        assert n >= 1
