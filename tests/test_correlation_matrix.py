"""
Unit tests for correlation_matrix.py
"""
import pandas as pd
from correlation_matrix import CorrelationMatrix


def make_balls_df():
    return pd.DataFrame([
        {"match_id": "m1", "innings": 1, "over": 1.0, "ball": 1,
         "batter": "Virat_Kohli", "non_striker": "Rohit_Sharma", "bowler": "Jasprit_Bumrah",
         "fielder": "", "runs_batter": 4, "runs_extra": 0, "runs_total": 4,
         "is_wicket": 0, "wicket_type": "", "batting_team": "MI", "bowling_team": "RCB"},
        {"match_id": "m1", "innings": 1, "over": 1.0, "ball": 2,
         "batter": "Virat_Kohli", "non_striker": "Rohit_Sharma", "bowler": "Jasprit_Bumrah",
         "fielder": "", "runs_batter": 0, "runs_extra": 0, "runs_total": 0,
         "is_wicket": 1, "wicket_type": "bowled", "fielder": "", "batting_team": "MI", "bowling_team": "RCB"},
        {"match_id": "m1", "innings": 1, "over": 1.0, "ball": 3,
         "batter": "Rohit_Sharma", "non_striker": "Virat_Kohli", "bowler": "Jasprit_Bumrah",
         "fielder": "", "runs_batter": 1, "runs_extra": 0, "runs_total": 1,
         "is_wicket": 0, "wicket_type": "", "fielder": "", "batting_team": "MI", "bowling_team": "RCB"},
    ])


def test_correlation_matrix_builds():
    cm = CorrelationMatrix(make_balls_df())
    assert cm is not None


def test_negative_correlations():
    cm = CorrelationMatrix(make_balls_df())
    dismissed = cm.get_negative_correlations("Jasprit_Bumrah")
    assert "Virat_Kohli" in dismissed


def test_dismissal_count():
    cm = CorrelationMatrix(make_balls_df())
    assert cm.dismissal_count("Jasprit_Bumrah", "Virat_Kohli") == 1
    assert cm.dismissal_count("Jasprit_Bumrah", "Rohit_Sharma") == 0


def test_positive_correlations():
    cm = CorrelationMatrix(make_balls_df())
    partners = cm.get_positive_correlations("Virat_Kohli")
    assert "Rohit_Sharma" in partners


def test_summary():
    cm = CorrelationMatrix(make_balls_df())
    s = cm.summary()
    assert "bowler_batter_rivalries" in s
    assert s["bowler_batter_rivalries"] >= 1
