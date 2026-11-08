"""Per-delivery multinomial outcome model.

Falls back to empirical phase base rates when no artifact exists, so the
project always runs.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from ..config import settings

OUTCOMES = ["0", "1", "2", "3", "4", "6", "W", "wd", "nb"]
OIDX = {o: i for i, o in enumerate(OUTCOMES)}

FEATS = ["phase_pp", "phase_mid", "phase_death", "bat_sr", "bat_bnd",
         "bat_pout", "bowl_eco", "bowl_wkt", "matchup_sr", "matchup_dis",
         "venue_par", "balls_faced", "wkts_in_hand"]


class BallModel:
    def __init__(self, booster=None):
        self.booster = booster

    @classmethod
    def load(cls, path: Path | None = None) -> "BallModel":
        import lightgbm as lgb
        p = path or (settings().artifacts / "ball_model.txt")
        if p.exists():
            return cls(lgb.Booster(model_file=str(p)))
        return cls(None)

    def fit(self, df: pd.DataFrame) -> "BallModel":
        import lightgbm as lgb
        X = df[FEATS].to_numpy(float)
        y = df["outcome"].map(OIDX).fillna(OIDX["0"]).astype(int).to_numpy()
        ds = lgb.Dataset(X, y)
        self.booster = lgb.train(
            dict(objective="multiclass", num_class=len(OUTCOMES),
                 learning_rate=0.05, num_leaves=63, min_data_in_leaf=200,
                 feature_fraction=0.8, bagging_fraction=0.8, bagging_freq=1,
                 verbose=-1),
            ds, num_boost_round=400)
        settings().ensure_dirs()
        self.booster.save_model(str(settings().artifacts / "ball_model.txt"))
        return self

    def predict(self, X: np.ndarray):
        if self.booster is None:
            return None
        return self.booster.predict(X)


class EmpiricalFallback:
    """Phase base rates from history. Used when no model artifact exists."""

    DEFAULT = np.array([0.36, 0.32, 0.09, 0.01, 0.11, 0.05, 0.05, 0.005, 0.005])

    def __init__(self, balls: pd.DataFrame | None = None):
        self.tab = None
        if balls is not None and len(balls):
            b = balls.copy()
            b["is_ball"] = (~b["outcome"].isin(["wd", "nb"])).astype(int)
            self.tab = (b.groupby(["phase", "outcome"]).size()
                        / b.groupby("phase").size()).unstack(fill_value=0.0)
            self.tab = self.tab.reindex(columns=OUTCOMES, fill_value=0.0)

    def probs(self, phase: str) -> np.ndarray:
        if self.tab is not None and phase in self.tab.index:
            p = self.tab.loc[phase].to_numpy(float)
            if p.sum() > 0:
                return p / p.sum()
        return self.DEFAULT.copy()
