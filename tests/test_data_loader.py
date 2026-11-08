"""
Unit tests for data_loader.py
"""
import pandas as pd
from data_loader import generate_sample_historical_data, load_upcoming_match_players


def test_generate_sample_historical_data_shape():
    df = generate_sample_historical_data(n_matches=10)
    assert len(df) == 150  # 10 matches * 15 players
    expected_cols = {
        "match_id", "player", "role", "team", "venue", "skill_rating",
        "recent_form_last_5", "opposition_strength", "phase_strike_rate",
        "economy_rate", "fantasy_points",
    }
    assert expected_cols.issubset(set(df.columns))
    assert (df["fantasy_points"] >= 0).all()


def test_generate_sample_deterministic():
    df1 = generate_sample_historical_data(n_matches=5)
    df2 = generate_sample_historical_data(n_matches=5)
    pd.testing.assert_frame_equal(df1, df2)


def test_load_upcoming_match_players_count():
    players = load_upcoming_match_players()
    assert len(players) == 23
    roles = {p["role"] for p in players}
    assert {"BAT", "BOWL", "AR", "WK"} <= roles
    teams = {p["team"] for p in players}
    assert {"MI", "RCB"} <= teams
    for p in players:
        assert "credit" in p
        assert "projected_sel_pct" in p
        assert 0 < p["credit"] <= 12
        assert 0 <= p["projected_sel_pct"] <= 100
