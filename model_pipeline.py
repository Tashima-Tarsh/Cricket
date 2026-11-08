"""
Automated model training pipeline with versioning and model registry.
Trains LightGBM mean + variance models, tracks metrics, and persists versioned
artifacts so the optimizer always loads the latest validated model.
"""
import os
import json
import glob
import shutil
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, Tuple

import joblib
import numpy as np
import pandas as pd

from predictor import CricketPredictor, FEATURE_COLS

logger = logging.getLogger(__name__)

DEFAULT_MODEL_DIR = Path("models")
METRICS_LOG = "metrics.jsonl"


class ModelPipeline:
    """Automated training pipeline with model registry."""

    def __init__(self, model_dir: str | Path = DEFAULT_MODEL_DIR):
        self.model_dir = Path(model_dir)
        self.model_dir.mkdir(parents=True, exist_ok=True)
        self.metrics_path = self.model_dir / METRICS_LOG
        self.predictor = CricketPredictor()

    def _version_dir(self, version: str) -> Path:
        return self.model_dir / f"v{version}"

    def _latest_version(self) -> Optional[str]:
        dirs = [d.name for d in self.model_dir.iterdir()
                if d.is_dir() and d.name.startswith("v")]
        if not dirs:
            return None
        return sorted(dirs, key=lambda x: float(x[1:]))[-1]

    def _next_version(self) -> str:
        latest = self._latest_version()
        if latest is None:
            return "1.0"
        try:
            v = float(latest[1:])
        except ValueError:
            v = 0.0
        return f"{v + 0.1:.1f}"

    def train(
        self,
        df: pd.DataFrame,
        version: Optional[str] = None,
        force: bool = False,
    ) -> Dict[str, Any]:
        """Train models, validate, and save versioned artifacts."""
        if version is None:
            version = self._next_version()

        version_dir = self._version_dir(version)
        if version_dir.exists() and not force:
            raise FileExistsError(f"Version {version} already exists. Use force=True.")

        X = df[FEATURE_COLS].values
        y_mean = df["fantasy_points"].values
        y_var = (y_mean - y_mean.mean()) ** 2

        from sklearn.model_selection import train_test_split
        X_tr, X_val, y_tr, y_val = train_test_split(
            X, y_mean, test_size=0.2, random_state=42
        )
        _, _, yv_var, _ = train_test_split(
            X, y_var, test_size=0.2, random_state=42
        )

        import lightgbm as lgb

        model_mean = lgb.LGBMRegressor(
            n_estimators=300, learning_rate=0.05, max_depth=6,
            num_leaves=31, subsample=0.8, colsample_bytree=0.8,
            random_state=42, verbose=-1
        )
        model_mean.fit(
            X_tr, y_tr, eval_set=[(X_val, y_val)],
            callbacks=[lgb.early_stopping(20), lgb.log_evaluation(0)]
        )

        model_var = lgb.LGBMRegressor(
            n_estimators=200, learning_rate=0.05, max_depth=5,
            random_state=42, verbose=-1
        )
        model_var.fit(X_tr, yv_var)

        preds = model_mean.predict(X_val)
        rmse = float(np.sqrt(np.mean((preds - y_val) ** 2)))
        mae = float(np.mean(np.abs(preds - y_val)))

        version_dir.mkdir(parents=True, exist_ok=True)
        joblib.dump(model_mean, version_dir / "mean_model.pkl")
        joblib.dump(model_var, version_dir / "var_model.pkl")

        metrics = {
            "version": version,
            "timestamp": datetime.now().isoformat(),
            "val_rmse": round(rmse, 4),
            "val_mae": round(mae, 4),
            "n_train": int(len(X_tr)),
            "n_val": int(len(X_val)),
            "n_features": len(FEATURE_COLS),
            "feature_cols": FEATURE_COLS,
            "model_dir": str(version_dir),
        }

        # Append to metrics log
        with open(self.metrics_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(metrics) + "\n")

        # Save latest symlink/copy
        latest_dir = self.model_dir / "latest"
        if latest_dir.exists():
            shutil.rmtree(latest_dir)
        shutil.copytree(version_dir, latest_dir)

        # Update predictor in-memory
        self.predictor.model_mean = model_mean
        self.predictor.model_var = model_var

        logger.info(
            "Trained model v%s: val_rmse=%.4f val_mae=%.4f n_train=%d",
            version, rmse, mae, len(X_tr)
        )
        return metrics

    def load_latest(self) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """Load the latest model version into the predictor. Returns (ok, metrics)."""
        latest_dir = self.model_dir / "latest"
        if not latest_dir.exists():
            return False, None

        mean_path = latest_dir / "mean_model.pkl"
        var_path = latest_dir / "var_model.pkl"
        if not mean_path.exists() or not var_path.exists():
            return False, None

        self.predictor.model_mean = joblib.load(mean_path)
        self.predictor.model_var = joblib.load(var_path)

        # Find metrics for this version
        metrics = None
        if self.metrics_path.exists():
            with open(self.metrics_path, encoding="utf-8") as f:
                lines = f.readlines()
            if lines:
                metrics = json.loads(lines[-1])

        return True, metrics

    def should_retrain(
        self,
        new_df: pd.DataFrame,
        min_new_matches: int = 10,
        rmse_threshold: Optional[float] = None,
    ) -> Tuple[bool, str]:
        """Decide whether a retrain is warranted based on new data volume."""
        if not (self.model_dir / "latest").exists():
            return True, "No model exists yet"

        n_new = new_df["match_id"].nunique() if "match_id" in new_df.columns else len(new_df)
        if n_new >= min_new_matches:
            return True, f"{n_new} new matches >= {min_new_matches} threshold"

        return False, f"Only {n_new} new matches (< {min_new_matches})"
