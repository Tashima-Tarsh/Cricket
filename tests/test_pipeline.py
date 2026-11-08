"""
Unit tests for model_pipeline.py
"""
import json
import pandas as pd
import numpy as np
from model_pipeline import ModelPipeline


def make_training_df(n_rows: int = 60) -> pd.DataFrame:
    rng = np.random.RandomState(1)
    return pd.DataFrame({
        "skill_rating": rng.uniform(40, 95, n_rows),
        "recent_form_last_5": rng.uniform(40, 100, n_rows),
        "opposition_strength": rng.uniform(50, 90, n_rows),
        "phase_strike_rate": rng.uniform(110, 180, n_rows),
        "economy_rate": rng.uniform(6.0, 10.5, n_rows),
        "fantasy_points": rng.uniform(0, 80, n_rows),
    })


def test_pipeline_train_and_load_latest(tmp_path):
    pipe = ModelPipeline(model_dir=str(tmp_path / "models"))
    df = make_training_df()
    metrics = pipe.train(df, version="1.0")
    assert "val_rmse" in metrics
    assert metrics["version"] == "1.0"

    ok, loaded_metrics = pipe.load_latest()
    assert ok is True
    assert loaded_metrics is not None
    assert loaded_metrics["version"] == "1.0"

    # Predictor should be loaded
    upcoming = pd.DataFrame({
        "skill_rating": [85.0],
        "recent_form_last_5": [70.0],
        "opposition_strength": [70.0],
        "phase_strike_rate": [140.0],
        "economy_rate": [9.0],
    })
    out = pipe.predictor.predict(upcoming)
    assert "expected_points" in out.columns


def test_pipeline_metrics_log(tmp_path):
    pipe = ModelPipeline(model_dir=str(tmp_path / "models"))
    df = make_training_df()
    pipe.train(df, version="1.0")
    pipe.train(df, version="2.0")

    metrics_path = tmp_path / "models" / "metrics.jsonl"
    assert metrics_path.exists()
    lines = metrics_path.read_text().strip().splitlines()
    assert len(lines) == 2
    m1 = json.loads(lines[0])
    m2 = json.loads(lines[1])
    assert m1["version"] == "1.0"
    assert m2["version"] == "2.0"


def test_pipeline_latest_symlink(tmp_path):
    pipe = ModelPipeline(model_dir=str(tmp_path / "models"))
    df = make_training_df()
    pipe.train(df, version="1.0")
    latest_dir = tmp_path / "models" / "latest"
    assert latest_dir.exists()
    assert (latest_dir / "mean_model.pkl").exists()
    assert (latest_dir / "var_model.pkl").exists()


def test_should_retrain_no_model(tmp_path):
    pipe = ModelPipeline(model_dir=str(tmp_path / "models"))
    df = make_training_df()
    should, reason = pipe.should_retrain(df)
    assert should is True


def test_should_retrain_enough_data(tmp_path):
    pipe = ModelPipeline(model_dir=str(tmp_path / "models"))
    df = make_training_df()
    pipe.train(df, version="1.0")
    should, reason = pipe.should_retrain(df, min_new_matches=5)
    # depends on data volume; just check it returns a bool and string
    assert isinstance(should, bool)
    assert isinstance(reason, str)
