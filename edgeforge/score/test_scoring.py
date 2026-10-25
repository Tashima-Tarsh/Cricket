"""Basic tests for the clean Dream11 scorer."""
from edgeforge.score.dream11 import Dream11Scorer


def test_basic_t20_batter():
    scorer = Dream11Scorer()
    res = scorer.calculate(
        runs=52, balls_faced=35, fours=5, sixes=2,
        is_playing=True, match_format="T20"
    )
    assert res.total > 70
    assert "batting" in res.breakdown


def test_dot_balls_count():
    scorer = Dream11Scorer()
    res = scorer.calculate(
        overs_bowled=4.0, runs_conceded=28, wickets=1, dots=12,
        is_playing=True, match_format="T20"
    )
    assert res.breakdown["dot_balls"] == 12.0
    assert res.total > 40


def test_duck_penalty():
    scorer = Dream11Scorer()
    res = scorer.calculate(
        runs=0, balls_faced=4, is_playing=True, match_format="T20"
    )
    assert res.breakdown["batting"] == -2.0
