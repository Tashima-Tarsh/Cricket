"""Rank-optimized unique portfolio. Objective is P(top alpha%), not E[score]."""
from __future__ import annotations
import numpy as np
from gl_engine.provenance import DataProvenance
from ..config import settings
from .constraints import is_legal
from .solver import solve_core


def evaluate(squad, cap, vic, sims, idx, fsc):
    """Evaluates lineup finish ranks against simulated field incorporating 2.0x Captain and 1.5x Vice-Captain."""
    s = sims[:, [idx[i] for i in squad]].sum(1) + sims[:, idx[cap]]
    if vic is not None and vic in idx:
        s = s + 0.5 * sims[:, idx[vic]]
    nf = fsc.shape[0]
    step = max(1, sims.shape[0] // 5000)
    fsc_sub = fsc[:, ::step]
    s_sub = s[::step]
    ranks = (fsc_sub > s_sub).sum(axis=0, dtype=np.int32) + 1
    return dict(p_rank1=float((ranks <= 1).mean()), p_top10=float((ranks <= 10).mean()),
                p_top100=float((ranks <= 100).mean()),
                p_top001=float((ranks <= max(1.0, nf * 1e-4)).mean()),
                avg_rank=float(ranks.mean()), med_rank=float(np.median(ranks)))


def build(ctx, sims, idx, fsc, n, rng, risk=0.0, locked=(), banned=()):
    cfg = settings().portfolio
    pool, seen, cvc = [], [], set()
    att = 0
    max_att = min(n * 4, 250)

    while len(pool) < n and att < max_att:
        att += 1
        base = dict(ctx.proj)
        scale = 3.5 + 2.0 * (att / max_att)
        ctx.proj = {i: base[i] + rng.normal(0, scale) for i in ctx.ids}
        res = solve_core(ctx, tail=True, risk=risk, locked=locked, banned=banned)
        ctx.proj = base
        if res is None:
            continue
        squad, cap, vic = res
        if not is_legal(squad, ctx):
            continue
        if any(len(set(squad) ^ set(p)) < cfg.min_swap for p in seen):
            continue
        if cfg.unique_cvc and (cap, vic) in cvc:
            cands = sorted(squad, key=lambda i: ctx.proj[i], reverse=True)[:5]
            found = False
            for c_cand in cands:
                for v_cand in cands:
                    if c_cand != v_cand and (c_cand, v_cand) not in cvc:
                        cap, vic = c_cand, v_cand
                        found = True
                        break
                if found:
                    break
            if not found:
                continue
        pool.append(dict(squad=squad, cap=cap, vic=vic, provenance=DataProvenance(
            source="estimated", verification_status="SIMULATION",
            notes="Uncalibrated simulated field; not an observed contest rank."
        ).model_dump(mode="json")))
        seen.append(squad)
        cvc.add((cap, vic))

    for e in pool:
        e.update(evaluate(e["squad"], e["cap"], e.get("vic"), sims, idx, fsc))

    pool.sort(key=lambda e: e["p_top001"], reverse=True)
    return enforce_exposure(pool, ctx, cfg.max_exposure)


def enforce_exposure(pool, ctx, cap):
    limit = max(1, int(len(pool) * cap))
    counts, kept = {}, []
    for e in pool:
        if any(counts.get(i, 0) >= limit for i in e["squad"]):
            continue
        for i in e["squad"]:
            counts[i] = counts.get(i, 0) + 1
        kept.append(e)
    return kept


def exposure_report(pool, ctx):
    n = max(len(pool), 1)
    c = {}
    for e in pool:
        for i in e["squad"]:
            c[i] = c.get(i, 0) + 1
    return sorted(((i, v / n) for i, v in c.items()), key=lambda t: -t[1])
