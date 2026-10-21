"""Assemble marginals -> correlation -> copula -> summaries."""
from __future__ import annotations
import numpy as np
import pandas as pd
from . import distributions as D
from .copula import correlated_scores, verify
from .correlation import build as build_corr


def fit_marginals(roster, proj=None, sd=None, p_dnb=None):
    if proj is None:
        proj = roster.proj
    if sd is None:
        sd = roster.sd
    if p_dnb is None:
        p_dnb = roster.p_dnb
    fams = D.load()
    out = {}
    for i, r in enumerate(roster.itertuples()):
        key = (r.role, D.window_of(float(proj.iloc[i])))
        fam = fams.get(key) or D.Family.fit_best(
            np.abs(np.random.default_rng(i).normal(20, 12, 400)))
        out[r.player_id] = D.Marginal(fam, float(proj.iloc[i]), float(sd.iloc[i]),
                                      float(p_dnb.iloc[i]))
    return out


def run(roster, marginals, pitch, n_sims, seed=7):
    rng = np.random.default_rng(seed)
    corr = build_corr(list(roster.itertuples()), pitch)
    scores, ids = correlated_scores(marginals, corr, n_sims, rng)
    return scores, ids, corr, verify(scores, marginals, ids, corr)


def summarise(scores, ids, own):
    ev, sd = scores.mean(0), scores.std(0)
    o = np.array([max(own.get(i, 1.0), 0.05) for i in ids])
    z = lambda v: (v - v.mean()) / (v.std() if v.std() > 1e-9 else 1.0)
    return pd.DataFrame(dict(
        player_id=ids, proj=ev, sd=sd, boom=(scores > 60).mean(0),
        bust=(scores < 10).mean(0), p90=np.percentile(scores, 90, axis=0),
        own_pct=o, leverage=z(ev) - z(o)))
