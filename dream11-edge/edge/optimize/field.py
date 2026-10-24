from __future__ import annotations
import numpy as np
from .constraints import repair


def build_field(ctx, n, rng, cap_bias=1.35):
    """Simulate the opponent field with full Captain (2x) and Vice-Captain (1.5x) selections."""
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
    for idx_val in chosen_idx:
        sq = archetypes[idx_val]
        sq_tuple = tuple(sq)
        if sq_tuple not in cap_cache:
            cw = np.array([max(ctx.own.get(i, 1.0), 0.05) for i in sq]) ** cap_bias
            cw = cw / cw.sum()
            cap_cache[sq_tuple] = (cw, [sq[k] for k in range(len(sq))])
        cw, players_list = cap_cache[sq_tuple]
        
        # Pick Captain
        c_choice = int(rng.choice(len(players_list), p=cw))
        cap = players_list[c_choice]
        
        # Pick Vice-Captain from remaining players (1.5x multiplier)
        remaining_indices = [k for k in range(len(players_list)) if k != c_choice]
        vw = np.array([cw[k] for k in remaining_indices])
        vw = vw / vw.sum()
        v_choice = int(rng.choice(len(remaining_indices), p=vw))
        vic = players_list[remaining_indices[v_choice]]
        
        field.append((sq, cap, vic))
    return field


def field_scores(field, sims, idx):
    """Computes total simulated scores for field opponents including 2.0x Captain and 1.5x Vice-Captain."""
    out = np.empty((len(field), sims.shape[0]), dtype=np.float32)
    cache = {}
    for f, entry in enumerate(field):
        if len(entry) == 3:
            sq, cap, vic = entry
        else:
            sq, cap = entry
            vic = None
        key = (tuple(sorted(sq)), cap, vic)
        if key in cache:
            out[f] = cache[key]
        else:
            score = sims[:, [idx[i] for i in sq]].sum(1) + sims[:, idx[cap]]
            if vic is not None and vic in idx:
                score = score + 0.5 * sims[:, idx[vic]]
            cache[key] = score
            out[f] = score
    return out
