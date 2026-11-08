"""
Dual-head LightGBM predictor for BBL/WBBL fantasy cricket.
Predicts both expected fantasy points (mean) and variance (upside potential).
"""
import logging
import os
from typing import Optional

import joblib
import lightgbm as lgb
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

from config import FEATURE_COLS

logger = logging.getLogger(__name__)


class CricketPredictor:
    def __init__(self):
        self.model_mean: Optional[lgb.LGBMRegressor] = None
        self.model_var: Optional[lgb.LGBMRegressor] = None

    def train(self, df: pd.DataFrame) -> dict:
        """Train two LightGBM models: mean points and variance (upside)."""
        if df.empty:
            raise ValueError("Training DataFrame is empty.")

        missing = [c for c in FEATURE_COLS if c not in df.columns]
        if missing:
            raise ValueError(f"Missing feature columns: {missing}")
        if "fantasy_points" not in df.columns:
            raise ValueError("DataFrame must contain 'fantasy_points' target column.")

        X = df[FEATURE_COLS].values
        y_mean = df["fantasy_points"].values
        y_var = (y_mean - y_mean.mean()) ** 2

        X_tr, X_val, y_tr, y_val = train_test_split(
            X, y_mean, test_size=0.2, random_state=42
        )
        _, _, yv_var_train, _ = train_test_split(
            X, y_var, test_size=0.2, random_state=42
        )

        # Mean model
        self.model_mean = lgb.LGBMRegressor(
            n_estimators=300, learning_rate=0.05, max_depth=6,
            num_leaves=31, subsample=0.8, colsample_bytree=0.8,
            random_state=42, verbose=-1
        )
        self.model_mean.fit(
            X_tr, y_tr, eval_set=[(X_val, y_val)],
            callbacks=[lgb.early_stopping(20), lgb.log_evaluation(0)]
        )

        # Variance model
        self.model_var = lgb.LGBMRegressor(
            n_estimators=200, learning_rate=0.05, max_depth=5,
            random_state=42, verbose=-1
        )
        self.model_var.fit(X_tr, yv_var_train)

        preds = self.model_mean.predict(X_val)
        rmse = float(np.sqrt(np.mean((preds - y_val) ** 2)))
        mae = float(np.mean(np.abs(preds - y_val)))

        logger.info("Trained predictor: val_rmse=%.4f val_mae=%.4f n_train=%d", rmse, mae, len(X_tr))
        return {"val_rmse": round(rmse, 4), "val_mae": round(mae, 4), "n_train": int(len(X_tr))}

    def predict(self, players_df: pd.DataFrame) -> pd.DataFrame:
        """Predict expected points + variance for upcoming players."""
        if self.model_mean is None or self.model_var is None:
            raise RuntimeError("Predictor not trained. Call train() first or load().")

        missing = [c for c in FEATURE_COLS if c not in players_df.columns]
        if missing:
            raise ValueError(f"Missing feature columns: {missing}")

        X = players_df[FEATURE_COLS].values
        out = players_df.copy()
        preds_mean = self.model_mean.predict(X)
        preds_var = self.model_var.predict(X)
        out["expected_points"] = np.clip(preds_mean, 0, None)
        out["variance_score"] = np.clip(preds_var, 0, None)

        # Normalize variance to 0-1 scale
        v = out["variance_score"]
        v_range = v.max() - v.min()
        out["variance_score"] = (v - v.min()) / (v_range + 1e-6)

        return out

    def save(self, path: str = "models/"):
        os.makedirs(path, exist_ok=True)
        joblib.dump(self.model_mean, os.path.join(path, "mean_model.pkl"))
        joblib.dump(self.model_var, os.path.join(path, "var_model.pkl"))
        logger.info("Saved models to %s", path)

    def load(self, path: str = "models/"):
        self.model_mean = joblib.load(os.path.join(path, "mean_model.pkl"))
        self.model_var = joblib.load(os.path.join(path, "var_model.pkl"))
        logger.info("Loaded models from %s", path)
