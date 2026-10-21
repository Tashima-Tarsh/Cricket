"""Assemble marginals, build correlation, run the copula, emit summaries."""
from __future__ import annotations

import numpy as np
import pandas as pd

from . import distributions as D
from .copula import correlated_scores, verify
from .correlation import build as build_corr


def fit_marginals(roster: pd.DataFrame, history: dict, proj: pd.Series,
                  sd: pd.Series, p_dnb: pd.Series) -> dict:
    fams = D.load()
    if not fams and history:
        fams = D.cohort_families(history)
        D.save(fams)

    out = {}
    for i, r in enumerate(roster.itertuples()):
        key = (r.role, D.window_of(float(proj.iloc[i])))
        fam = (fams.get(key)
               or fams.get((r.role, 0))
               or D.Family.fit_best(
                   np.abs(np.random.default_rng(i).normal(20, 12, 400))))
        out[r.player_id] = D.Marginal(
            fam, float(proj.iloc[i]), float(sd.iloc[i]), float(p_dnb.iloc[i]))
    return out


def run(roster: pd.DataFrame, marginals: dict, pitch: str, n_sims: int,
        seed: int = 7):
    rng = np.random.default_rng(seed)
    corr = build_corr(list(roster.itertuples()), pitch)
    scores, ids = correlated_scores(marginals, corr, n_sims, rng)
    err = verify(scores, marginals, ids, corr)
    return scores, ids, corr, err


def summarise(scores: np.ndarray, ids: list, own: dict) -> pd.DataFrame:
    ev = scores.mean(0)
    sd = scores.std(0)
    boom = (scores > 60).mean(0)
    bust = (scores < 10).mean(0)
    p90 = np.percentile(scores, 90, axis=0)
    o = np.array([max(own.get(i, 1.0), 0.05) for i in ids])

    def z(v):
        s = v.std()
        return (v - v.mean()) / (s if s > 1e-9 else 1.0)

    leverage = z(ev) - z(o)
    return pd.DataFrame(dict(
        player_id=ids, proj=ev, sd=sd, boom=boom, bust=bust,
        p90=p90, own_pct=o, leverage=leverage,
    )).sort_values("leverage", ascending=False).reset_index(drop=True)
