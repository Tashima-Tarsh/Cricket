"""Family fitting + affine matching + cricket hurdle.

Port of the NFL-DFS-Tools simulation methodology to cricket fantasy points.

Stage 1  fit empirical families per (role, projection window), select by KS
Stage 2  affine-transform samples so mean and SD match the player exactly
Stage 3  cricket-only: a hurdle component for the near-zero spike, because a
         batter who faces 3 balls and gets out is a different outcome shape
         from one who faces 30
"""
from __future__ import annotations

import pickle
from dataclasses import dataclass

import numpy as np
from scipy import stats

from ..config import settings

FAMILIES = ("gamma", "lognormal", "weibull", "skewnorm", "exgaussian")

_FIT = {
    "gamma": lambda x: stats.gamma.fit(x, floc=0),
    "lognormal": lambda x: stats.lognorm.fit(x, floc=0),
    "weibull": lambda x: stats.weibull_min.fit(x, floc=0),
    "skewnorm": lambda x: stats.skewnorm.fit(x),
    "exgaussian": lambda x: stats.exponnorm.fit(x),
}
_RVS = {
    "gamma": lambda p, n, r: stats.gamma.rvs(*p, size=n, random_state=r),
    "lognormal": lambda p, n, r: stats.lognorm.rvs(*p, size=n, random_state=r),
    "weibull": lambda p, n, r: stats.weibull_min.rvs(*p, size=n, random_state=r),
    "skewnorm": lambda p, n, r: stats.skewnorm.rvs(*p, size=n, random_state=r),
    "exgaussian": lambda p, n, r: stats.exponnorm.rvs(*p, size=n, random_state=r),
}
_CDF = {
    "gamma": lambda v, p: stats.gamma.cdf(v, *p),
    "lognormal": lambda v, p: stats.lognorm.cdf(v, *p),
    "weibull": lambda v, p: stats.weibull_min.cdf(v, *p),
    "skewnorm": lambda v, p: stats.skewnorm.cdf(v, *p),
    "exgaussian": lambda v, p: stats.exponnorm.cdf(v, *p),
}

FLOOR = -6.0
MIN_COHORT = 40


@dataclass
class Family:
    name: str
    params: tuple
    ks: float = 1.0

    @classmethod
    def fit_best(cls, x: np.ndarray) -> "Family":
        x = np.abs(np.asarray(x, float))
        x = x[np.isfinite(x)]
        if len(x) < MIN_COHORT:
            return cls("gamma", _FIT["gamma"](x + 1e-6), 1.0)
        best, best_ks = None, np.inf
        for name in FAMILIES:
            try:
                p = _FIT[name](x + 1e-6)
                k = _ks(name, p, x)
                if k < best_ks:
                    best, best_ks = cls(name, p, k), k
            except Exception:
                continue
        return best or cls("gamma", _FIT["gamma"](x + 1e-6), 1.0)

    def raw(self, n: int, rng) -> np.ndarray:
        return _RVS[self.name](self.params, n, rng)


def _ks(name: str, params, x: np.ndarray) -> float:
    x = np.sort(x)
    n = len(x)
    c = np.clip(_CDF[name](x, params), 1e-9, 1 - 1e-9)
    i = np.arange(1, n + 1)
    return float(np.max(np.abs(c - (i - 0.5) / n)))


def affine_match(x: np.ndarray, mean: float, sd: float) -> np.ndarray:
    """Linear rescale so the sample reproduces mean and SD exactly, then clamp."""
    s = x.std(ddof=1)
    y = (sd / s) * (x - x.mean()) + mean if s > 1e-9 else np.full_like(x, mean)
    y = np.clip(y, FLOOR, None)
    return y + (mean - y.mean())


@dataclass
class Marginal:
    family: Family
    mean: float
    sd: float
    p_dnb: float = 0.0

    def sample(self, n: int, rng) -> np.ndarray:
        if self.p_dnb <= 0:
            return affine_match(self.family.raw(n, rng), self.mean, self.sd)
        mask = rng.random(n) < self.p_dnb
        low = rng.gamma(1.4, max(self.sd * 0.35, 1.0) / 1.4, n) + 3.0
        raw = self.family.raw(n, rng)
        mix = np.where(mask, np.clip(low, FLOOR, None), raw)
        return affine_match(mix, self.mean, self.sd)


def cohort_families(history_points: dict) -> dict:
    return {k: Family.fit_best(v) for k, v in history_points.items()
            if len(v) >= MIN_COHORT}


def window_of(mean: float) -> int:
    edges = settings().model.window_edges
    for lo, hi in zip(edges, edges[1:]):
        if lo <= mean < hi:
            return lo
    return edges[0]


def _path():
    return settings().artifacts / "families.pkl"


def save(fams: dict) -> None:
    settings().ensure_dirs()
    with open(_path(), "wb") as fh:
        pickle.dump(fams, fh)


def load() -> dict:
    p = _path()
    if not p.exists():
        return {}
    with open(p, "rb") as fh:
        return pickle.load(fh)
