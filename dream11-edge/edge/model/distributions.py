"""Family fitting + affine matching + cricket hurdle.

Stage 1 fit empirical families per (role, window), select by KS
Stage 2 affine-transform so mean and SD match the player exactly
Stage 3 cricket hurdle for the near-zero spike (batter out early / didn't bat)
"""
from __future__ import annotations
import pickle
from dataclasses import dataclass
import numpy as np
from scipy import stats
from ..config import settings

FAMILIES = ("gamma", "lognormal", "weibull", "skewnorm", "exgaussian")
_FIT = {"gamma": lambda x: stats.gamma.fit(x, floc=0),
        "lognormal": lambda x: stats.lognorm.fit(x, floc=0),
        "weibull": lambda x: stats.weibull_min.fit(x, floc=0),
        "skewnorm": lambda x: stats.skewnorm.fit(x),
        "exgaussian": lambda x: stats.exponnorm.fit(x)}
_RVS = {"gamma": lambda p, n, r: stats.gamma.rvs(*p, size=n, random_state=r),
        "lognormal": lambda p, n, r: stats.lognorm.rvs(*p, size=n, random_state=r),
        "weibull": lambda p, n, r: stats.weibull_min.rvs(*p, size=n, random_state=r),
        "skewnorm": lambda p, n, r: stats.skewnorm.rvs(*p, size=n, random_state=r),
        "exgaussian": lambda p, n, r: stats.exponnorm.rvs(*p, size=n, random_state=r)}
_CDF = {"gamma": lambda v, p: stats.gamma.cdf(v, *p),
        "lognormal": lambda v, p: stats.lognorm.cdf(v, *p),
        "weibull": lambda v, p: stats.weibull_min.cdf(v, *p),
        "skewnorm": lambda v, p: stats.skewnorm.cdf(v, *p),
        "exgaussian": lambda v, p: stats.exponnorm.cdf(v, *p)}

FLOOR, MIN_COHORT = -6.0, 40


@dataclass
class Family:
    name: str
    params: tuple
    ks: float = 1.0

    @classmethod
    def fit_best(cls, x):
        x = np.abs(np.asarray(x, float))
        x = x[np.isfinite(x)]
        if len(x) < MIN_COHORT:
            return cls("gamma", _FIT["gamma"](x + 1e-6), 1.0)
        best, bk = None, np.inf
        for nm in FAMILIES:
            try:
                p = _FIT[nm](x + 1e-6)
                k = _ks(nm, p, x)
                if k < bk:
                    best, bk = cls(nm, p, k), k
            except Exception:
                continue
        return best or cls("gamma", _FIT["gamma"](x + 1e-6), 1.0)

    def raw(self, n, rng):
        return _RVS[self.name](self.params, n, rng)


def _ks(name, params, x):
    x = np.sort(x)
    n = len(x)
    c = np.clip(_CDF[name](x, params), 1e-9, 1 - 1e-9)
    return float(np.max(np.abs(c - (np.arange(1, n + 1) - 0.5) / n)))


def affine_match(x, mean, sd):
    s = x.std(ddof=1)
    y = (sd / s) * (x - x.mean()) + mean if s > 1e-9 else np.full_like(x, mean)
    for _ in range(4):
        y = np.clip(y, FLOOR, None)
        sy = y.std(ddof=1)
        if sy > 1e-9:
            y = (sd / sy) * (y - y.mean()) + mean
    return y + (mean - y.mean())


@dataclass
class Marginal:
    family: Family
    mean: float
    sd: float
    p_dnb: float = 0.0

    def sample(self, n, rng):
        raw = self.family.raw(n, rng)
        if self.p_dnb <= 0:
            return affine_match(raw, self.mean, self.sd)
        mask = rng.random(n) < self.p_dnb
        low = rng.gamma(1.4, max(self.sd * 0.35, 1.0) / 1.4, n) + 3.0
        mix = np.where(mask, np.clip(low, FLOOR, None), raw)
        return affine_match(mix, self.mean, self.sd)


def window_of(mean):
    e = settings().model.window_edges
    for lo, hi in zip(e, e[1:]):
        if lo <= mean < hi:
            return lo
    return e[0]


def _path():
    return settings().artifacts / "families.pkl"


def save(f):
    settings().ensure_dirs()
    with open(_path(), "wb") as fh:
        pickle.dump(f, fh)


def load():
    p = _path()
    return pickle.load(open(p, "rb")) if p.exists() else {}
