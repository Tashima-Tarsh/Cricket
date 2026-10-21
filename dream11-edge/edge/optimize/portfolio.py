"""Rank-optimized unique portfolio.

Maximises P(top alpha%), not E[score]. Diversifies on three axes at once:
projection jitter, structural pivots and a unique C/VC matrix.
"""
from __future__ import annotations

import numpy as np

from ..config import settings
from .constraints import is_legal
from .solver import solve_core


def evaluate(squad, cap, sims: np.ndarray, idx: dict, fsc: np.ndarray) -> dict:
    s = sims[:, [idx[i] for i in squad]].sum(1) + sims[:, idx[cap]]
    nf = fsc.shape[0]
    ranks = (fsc > s).sum(axis=0, dtype=np.int32) + 1
    return dict(
        p_rank1=float((ranks <= 1).mean()),
        p_top10=float((ranks <= 10).mean()),
        p_top100=float((ranks <= 100).mean()),
        p_top001=float((ranks <= max(1.0, nf * 0.0001)).mean()),
        avg_rank=float(ranks.mean()),
    )


def build(ctx, sims: np.ndarray, idx: dict, fsc: np.ndarray, n: int, rng) -> list:
    cfg = settings().portfolio
    pool, seen, cvc = [], [], set()
    attempts, max_attempts = 0, n * 40

    while len(pool) < n and attempts < max_attempts:
        attempts += 1
        base = dict(ctx.proj)
        ctx.proj = {i: base[i] + rng.normal(0, cfg.jitter * abs(base[i]) + 0.5)
                    for i in ctx.ids}
        res = solve_core(ctx, tail=True)
        ctx.proj = base
        if res is None:
            continue

        squad, cap, vic = res
        if not is_legal(squad, ctx):
            continue
        if any(len(set(squad) ^ set(p)) < cfg.min_swap for p in seen):
            continue
        if cfg.unique_cvc and (cap, vic) in cvc:
            continue

        pool.append(dict(squad=squad, cap=cap, vic=vic,
                         **evaluate(squad, cap, sims, idx, fsc)))
        seen.append(squad)
        cvc.add((cap, vic))

    pool.sort(key=lambda e: e["p_top001"], reverse=True)
    return enforce_exposure(pool, ctx, cfg.max_exposure)


def enforce_exposure(pool: list, ctx, cap: float) -> list:
    limit = max(1, int(len(pool) * cap))
    counts, kept = {}, []
    for e in pool:
        if any(counts.get(i, 0) >= limit for i in e["squad"]):
            continue
        for i in e["squad"]:
            counts[i] = counts.get(i, 0) + 1
        kept.append(e)
    return kept


def exposure_report(pool: list, ctx) -> list:
    n = max(len(pool), 1)
    c: dict = {}
    for e in pool:
        for i in e["squad"]:
            c[i] = c.get(i, 0) + 1
    return sorted(((i, v / n) for i, v in c.items()), key=lambda t: -t[1])
