from __future__ import annotations
import numpy as np
from .constraints import repair


def build_field(ctx, n, rng, cap_bias=1.35):
    """Simulate the opponent field. The field COPIES - it does not sample independently."""
    w = np.array([max(ctx.own.get(i, 1.0), 0.05) for i in ctx.ids])
    w = w / w.sum()
    n_ids = len(ctx.ids)

    # Sample a realistic pool of unique archetypes
    n_archetypes = min(n, 1200)
    archetypes = []
    seen = set()
    guard = 0
    while len(archetypes) < n_archetypes and guard < n_archetypes * 4:
        guard += 1
        picks = tuple(sorted(rng.choice(n_ids, size=11, replace=False, p=w).tolist()))
        if picks in seen:
            continue
        seen.add(picks)
        sq = repair([ctx.ids[k] for k in picks], ctx, rng)
        if sq is None:
            continue
        archetypes.append(sq)

    if not archetypes:
        sq0 = repair(ctx.ids[:11], ctx, rng)
        archetypes = [sq0] if sq0 else []

    arch_weights = np.array([sum(ctx.own.get(i, 1.0) for i in sq) for sq in archetypes], dtype=float)
    arch_weights = arch_weights / arch_weights.sum()

    chosen_idx = rng.choice(len(archetypes), size=n, p=arch_weights)
    field = []
    cap_cache = {}
    for idx in chosen_idx:
        sq = archetypes[idx]
        sq_tuple = tuple(sq)
        if sq_tuple not in cap_cache:
            cw = np.array([max(ctx.own.get(i, 1.0), 0.05) for i in sq]) ** cap_bias
            cw = cw / cw.sum()
            cap_cache[sq_tuple] = (cw, [sq[k] for k in range(len(sq))])
        cw, players_list = cap_cache[sq_tuple]
        cap = players_list[int(rng.choice(len(players_list), p=cw))]
        field.append((sq, cap))
    return field


def field_scores(field, sims, idx):
    out = np.empty((len(field), sims.shape[0]), dtype=np.float32)
    cache = {}
    for f, (sq, cap) in enumerate(field):
        key = (tuple(sorted(sq)), cap)
        if key in cache:
            out[f] = cache[key]
        else:
            score = sims[:, [idx[i] for i in sq]].sum(1) + sims[:, idx[cap]]
            cache[key] = score
            out[f] = score
    return out
