"""
Unit tests for feature_engineer.py
"""
import pandas as pd
import numpy as np
from feature_engineer import FantasyFeatureEngineer


def make_balls_df():
    """Create a small synthetic ball-by-ball DataFrame."""
    rows = [
        # Match 1, innings 1: Rohit bats, Bumrah bowls
        {"match_id": "m1", "date": "2024-01-01", "innings": 1, "over": 1.0, "ball": 1,
         "batter": "Rohit_Sharma", "non_striker": "Suryakumar_Yadav", "bowler": "Jasprit_Bumrah",
         "fielder": "", "runs_batter": 4, "runs_extra": 0, "runs_total": 4,
         "is_wicket": 0, "wicket_type": "", "batting_team": "MI", "bowling_team": "RCB"},
        {"match_id": "m1", "date": "2024-01-01", "innings": 1, "over": 1.0, "ball": 2,
         "batter": "Rohit_Sharma", "non_striker": "Suryakumar_Yadav", "bowler": "Jasprit_Bumrah",
         "fielder": "", "runs_batter": 0, "runs_extra": 0, "runs_total": 0,
         "is_wicket": 1, "wicket_type": "bowled", "fielder": "", "batting_team": "MI", "bowling_team": "RCB"},
        # Match 2: Rohit scores 60
        {"match_id": "m2", "date": "2024-01-02", "innings": 1, "over": 1.0, "ball": 1,
         "batter": "Rohit_Sharma", "non_striker": "Virat_Kohli", "bowler": "Jasprit_Bumrah",
         "fielder": "", "runs_batter": 1, "runs_extra": 0, "runs_total": 1,
         "is_wicket": 0, "wicket_type": "", "batting_team": "MI", "bowling_team": "RCB"},
    ]
    df = pd.DataFrame(rows)
    df["balls_faced_dummy"] = 1  # not used, ensure column presence doesn't break
    return df


def test_aggregate_match_stats():
    eng = FantasyFeatureEngineer()
    balls = make_balls_df()
    stats = eng.aggregate_match_stats(balls)
    assert not stats.empty
    assert "fantasy_points" in stats.columns
    rohit = stats[stats["player"] == "Rohit_Sharma"]
    assert len(rohit) == 2
    # m1: 4 runs + duck = 4 - 2 = 2 ; m2: need more balls to be meaningful but check non-negative
    assert (rohit["fantasy_points"] >= -2).all()


def test_fantasy_points_non_negative():
    eng = FantasyFeatureEngineer()
    balls = make_balls_df()
    stats = eng.aggregate_match_stats(balls)
    assert (stats["fantasy_points"] >= -2).all()  # duck penalty can make it -2


def test_build_player_features():
    eng = FantasyFeatureEngineer()
    balls = make_balls_df()
    stats = eng.aggregate_match_stats(balls)
    features = eng.build_player_features(stats)
    assert not features.empty
    expected_cols = {
        "match_id", "player", "role", "team", "date",
        "skill_rating", "recent_form_last_5", "opposition_strength",
        "phase_strike_rate", "economy_rate", "fantasy_points",
    }
    assert expected_cols.issubset(set(features.columns))
    assert (features["skill_rating"] >= 40).all()
    assert (features["skill_rating"] <= 95).all()
    assert (features["recent_form_last_5"] >= 0).all()


def test_build_training_frame_end_to_end():
    eng = FantasyFeatureEngineer()
    balls = make_balls_df()
    frame = eng.build_training_frame(balls)
    assert not frame.empty
    assert "fantasy_points" in frame.columns


def test_predict_upcoming_features_with_history():
    eng = FantasyFeatureEngineer()
    balls = make_balls_df()
    stats = eng.aggregate_match_stats(balls)
    history = eng.build_player_features(stats)

    upcoming = [
        {"name": "Rohit_Sharma", "role": "BAT", "team": "MI", "credit": 10.5, "projected_sel_pct": 78.0},
        {"name": "New_Player", "role": "BAT", "team": "RCB", "credit": 8.0, "projected_sel_pct": 5.0},
    ]
    feats = eng.predict_upcoming_features(upcoming, history)
    assert len(feats) == 2
    rohit = feats[feats["player"] == "Rohit_Sharma"].iloc[0]
    assert rohit["skill_rating"] > 0
    newp = feats[feats["player"] == "New_Player"].iloc[0]
    assert newp["skill_rating"] > 0  # default used


def test_role_inference_bowler():
    eng = FantasyFeatureEngineer()
    # Create a player who bowls a lot
    rows = []
    for i in range(20):
        rows.append({
            "match_id": f"m{i}", "date": f"2024-01-{i+1:02d}", "innings": 1,
            "over": 1.0, "ball": 1, "batter": "Other", "non_striker": "X",
            "bowler": "Bowler_Player", "fielder": "", "runs_batter": 0,
            "runs_extra": 0, "runs_total": 0, "is_wicket": 1, "wicket_type": "bowled",
            "fielder": "", "batting_team": "A", "bowling_team": "B",
        })
    balls = pd.DataFrame(rows)
    stats = eng.aggregate_match_stats(balls)
    feats = eng.build_player_features(stats)
    bowler_row = feats[feats["player"] == "Bowler_Player"]
    assert not bowler_row.empty
    assert bowler_row.iloc[0]["role"] in ("BOWL", "AR")
