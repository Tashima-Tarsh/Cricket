"""
ML predictor using LightGBM.
Predicts BOTH expected fantasy points AND variance (for Grand League upside).
"""
import lightgbm as lgb
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
import joblib
import os

FEATURE_COLS = [
    "skill_rating", "recent_form_last_5", "opposition_strength",
    "phase_strike_rate", "economy_rate"
]

class CricketPredictor:
    def __init__(self):
        self.model_mean = None   # Predicts expected points
        self.model_var = None    # Predicts variance (upside potential)

    def train(self, df: pd.DataFrame) -> dict:
        """Train two models: one for mean points, one for variance."""
        X = df[FEATURE_COLS].values
        y_mean = df["fantasy_points"].values
        # Variance proxy: squared deviation from rolling mean (high = high upside)
        y_var = (y_mean - y_mean.mean()) ** 2

        X_tr, X_val, y_tr, y_val = train_test_split(X, y_mean, test_size=0.2, random_state=42)
        _, _, yv_var_train, _ = train_test_split(X, y_var, test_size=0.2, random_state=42)

        # Mean model
        self.model_mean = lgb.LGBMRegressor(
            n_estimators=300, learning_rate=0.05, max_depth=6,
            num_leaves=31, subsample=0.8, colsample_bytree=0.8,
            random_state=42, verbose=-1
        )
        self.model_mean.fit(X_tr, y_tr, eval_set=[(X_val, y_val)],
                            callbacks=[lgb.early_stopping(20), lgb.log_evaluation(0)])

        # Variance model
        self.model_var = lgb.LGBMRegressor(
            n_estimators=200, learning_rate=0.05, max_depth=5,
            random_state=42, verbose=-1
        )
        self.model_var.fit(X_tr, yv_var_train)

        # Validation metrics
        preds = self.model_mean.predict(X_val)
        rmse = np.sqrt(np.mean((preds - y_val) ** 2))
        return {"val_rmse": round(rmse, 2), "n_train": len(X_tr)}

    def predict(self, players_df: pd.DataFrame) -> pd.DataFrame:
        """Predict expected points + variance for upcoming match players."""
        X = players_df[FEATURE_COLS].values
        players_df = players_df.copy()
        preds_mean = self.model_mean.predict(X)
        preds_var = self.model_var.predict(X)
        players_df["expected_points"] = np.clip(preds_mean, 0, None)
        players_df["variance_score"] = np.clip(preds_var, 0, None)
        # Normalize variance to 0-1 scale
        v = players_df["variance_score"]
        players_df["variance_score"] = (v - v.min()) / (v.max() - v.min() + 1e-6)
        return players_df

    def save(self, path: str = "models/"):
        os.makedirs(path, exist_ok=True)
        joblib.dump(self.model_mean, f"{path}/mean_model.pkl")
        joblib.dump(self.model_var, f"{path}/var_model.pkl")

    def load(self, path: str = "models/"):
        self.model_mean = joblib.load(f"{path}/mean_model.pkl")
        self.model_var = joblib.load(f"{path}/var_model.pkl")
