"""EdgeForge – Realistic fantasy-point marginal distributions (skewed)."""
from __future__ import annotations
import numpy as np
from scipy import stats
from typing import Tuple, Optional


def fit_skewed_marginal(mean: float, std: float, floor: float = -5.0, ceiling: float = 200.0):
    mean = max(mean, 5.0)
    std = max(std, 8.0)
    cv = std / mean
    sig2 = np.log(1 + cv ** 2)
    sig = np.sqrt(sig2)
    mu = np.log(mean) - 0.5 * sig2
    return "lognorm", {"mu": float(mu), "sig": float(sig), "floor": floor, "ceiling": ceiling}


def sample_marginal(u: np.ndarray, family: str, params: dict) -> np.ndarray:
    u = np.clip(u, 1e-6, 1 - 1e-6)
    if family == "lognorm":
        x = np.exp(params["mu"] + params["sig"] * stats.norm.ppf(u))
    else:
        x = stats.norm.ppf(u, loc=params.get("mean", 40), scale=params.get("std", 15))
    return np.clip(x, params.get("floor", -5), params.get("ceiling", 220))


def player_marginal_params(projected_points, ceiling, floor, role: str):
    role_prior = {"WK": 38.0, "BAT": 42.0, "AR": 48.0, "BOWL": 40.0}.get(role, 40.0)
    mean = float(projected_points) if projected_points and projected_points > 0 else role_prior
    if ceiling and ceiling > mean:
        std = max((ceiling - mean) / 2.2, mean * 0.40, 12.0)
    else:
        std = max(mean * 0.48, 14.0)
    f = float(floor) if floor is not None else max(-4.0, mean * 0.05 - 8)
    c = float(ceiling) if ceiling is not None else mean + 3.2 * std
    return mean, std, f, min(c, 220.0)
