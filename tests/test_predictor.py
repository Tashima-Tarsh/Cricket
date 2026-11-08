"""
Unit tests for predictor.py
"""
import pandas as pd
import numpy as np
from predictor import CricketPredictor, FEATURE_COLS


def make_training_df(n_rows: int = 60) -> pd.DataFrame:
    rng = np.random.RandomState(0)
    return pd.DataFrame({
        "skill_rating": rng.uniform(40, 95, n_rows),
        "recent_form_last_5": rng.uniform(40, 100, n_rows),
        "opposition_strength": rng.uniform(50, 90, n_rows),
        "phase_strike_rate": rng.uniform(110, 180, n_rows),
        "economy_rate": rng.uniform(6.0, 10.5, n_rows),
        "venue_factor": rng.uniform(0.9, 1.1, n_rows),
        "travel_fatigue": rng.uniform(0.0, 0.15, n_rows),
        "fantasy_points": rng.uniform(0, 80, n_rows),
    })


def test_predictor_train_and_predict():
    df = make_training_df()
    p = CricketPredictor()
    metrics = p.train(df)
    assert "val_rmse" in metrics
    assert "n_train" in metrics
    assert metrics["n_train"] > 0

    upcoming = pd.DataFrame({
        "skill_rating": [85.0], "recent_form_last_5": [70.0],
        "opposition_strength": [70.0], "phase_strike_rate": [140.0],
        "economy_rate": [9.0], "venue_factor": [1.0], "travel_fatigue": [0.0],
    })
    out = p.predict(upcoming)
    assert "expected_points" in out.columns
    assert "variance_score" in out.columns
    assert (out["expected_points"] >= 0).all()
    assert (out["variance_score"] >= 0).all()
    assert (out["variance_score"] <= 1.0).all()


def test_feature_cols():
    assert "skill_rating" in FEATURE_COLS
    assert "recent_form_last_5" in FEATURE_COLS
    assert "opposition_strength" in FEATURE_COLS
    assert "phase_strike_rate" in FEATURE_COLS
    assert "economy_rate" in FEATURE_COLS
    assert "venue_factor" in FEATURE_COLS
    assert "travel_fatigue" in FEATURE_COLS
