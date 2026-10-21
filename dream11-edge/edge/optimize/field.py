"""Simulate the opponent field.

The field COPIES - it does not sample independently. Modelling that is the
difference between an honest and a naive duplication estimate.
"""
from __future__ import annotations

import numpy as np

from .constraints import repair


def build_field(ctx, n: int, rng, own_scale: float = 1.0,
                cap_bias: float = 1.35) -> list:
    w = np.array([max(ctx.own.get(i, 1.0), 0.05) for i in ctx.ids]) ** own_scale
    w = w / w.sum()
    n_ids = len(ctx.ids)

    field = []
    guard = 0
    while len(field) < n and guard < n * 4:
        guard += 1
        picks = rng.choice(n_ids, size=11, replace=False, p=w)
        sq = [ctx.ids[k] for k in picks]
        sq = repair(sq, ctx, rng)
        if sq is None:
            continue
        cw = np.array([max(ctx.own.get(i, 1.0), 0.05) for i in sq]) ** cap_bias
        cw = cw / cw.sum()
        cap = sq[int(rng.choice(len(sq), p=cw))]
        field.append((sq, cap))
    return field


def field_scores(field: list, sims: np.ndarray, idx: dict) -> np.ndarray:
    """(n_field, n_sims) totals including the captain multiplier."""
    out = np.empty((len(field), sims.shape[0]))
    for f, (sq, cap) in enumerate(field):
        cols = [idx[i] for i in sq]
        out[f] = sims[:, cols].sum(1) + sims[:, idx[cap]]
    return out
