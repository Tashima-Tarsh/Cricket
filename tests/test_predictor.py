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
        "skill_rating": [85.0],
        "recent_form_last_5": [70.0],
        "opposition_strength": [70.0],
        "phase_strike_rate": [140.0],
        "economy_rate": [9.0],
    })
    out = p.predict(upcoming)
    assert "expected_points" in out.columns
    assert "variance_score" in out.columns
    assert (out["expected_points"] >= 0).all()
    assert (out["variance_score"] >= 0).all()
    assert (out["variance_score"] <= 1.0).all()


def test_predictor_save_and_load(tmp_path):
    df = make_training_df()
    p = CricketPredictor()
    p.train(df)

    save_dir = tmp_path / "models"
    p.save(path=str(save_dir))
    assert (save_dir / "mean_model.pkl").exists()
    assert (save_dir / "var_model.pkl").exists()

    p2 = CricketPredictor()
    p2.load(path=str(save_dir))
    upcoming = pd.DataFrame({
        "skill_rating": [85.0],
        "recent_form_last_5": [70.0],
        "opposition_strength": [70.0],
        "phase_strike_rate": [140.0],
        "economy_rate": [9.0],
    })
    out1 = p.predict(upcoming)
    out2 = p2.predict(upcoming)
    pd.testing.assert_series_equal(out1["expected_points"], out2["expected_points"])


def test_feature_cols_match():
    assert FEATURE_COLS == [
        "skill_rating", "recent_form_last_5", "opposition_strength",
        "phase_strike_rate", "economy_rate",
    ]
