"""Ball-by-ball match engine.

Optional. The marginal path is faster and is the default. Use this when
you want realistic tails and genuinely joint structure at the ball level.
"""
from __future__ import annotations

import numpy as np

from ..score import BatLine, BowlLine, FieldLine, points

MAX_OVERS = 20
OVERS_PER_BOWLER = 4


def simulate_match(batting_orders: dict, bowl_plans: dict, probs_fn,
                   fielders: dict, keepers: dict, rng, n_sims: int,
                   ids: list) -> np.ndarray:
    """
    batting_orders: {0: [pid, ...], 1: [...]}
    bowl_plans:     {0: [pid, ...], 1: [...]}   bowlers for that innings
    fielders:       {0: [pid, ...], 1: [...]}   fielding side for that innings
    keepers:        {0: pid, 1: pid}
    """
    idx = {p: i for i, p in enumerate(ids)}
    n = len(ids)
    out = np.zeros((n_sims, n))

    for s in range(n_sims):
        bat = np.zeros((n, 6))   # runs balls fours sixes out batted
        bowl = np.zeros((n, 5))  # balls runs wkts lbw maidens
        fld = np.zeros((n, 4))   # catches stumpings ro_direct ro_indirect

        for innings in (0, 1):
            _innings(batting_orders[innings], bowl_plans[innings],
                     fielders[innings], keepers[innings], probs_fn, rng,
                     bat, bowl, fld, idx)

        for i in range(n):
            if bat[i, 1] == 0 and bowl[i, 0] == 0:
                continue
            out[s, i] = points(
                BatLine(int(bat[i, 0]), int(bat[i, 1]), int(bat[i, 2]),
                        int(bat[i, 3]), bool(bat[i, 4]), bool(bat[i, 5])),
                BowlLine(int(bowl[i, 0]), int(bowl[i, 1]), int(bowl[i, 2]),
                         int(bowl[i, 3]), int(bowl[i, 4])),
                FieldLine(int(fld[i, 0]), int(fld[i, 1]), int(fld[i, 2]), int(fld[i, 3])),
            )
    return out


def _innings(order, bowlers, fielders, keeper, probs_fn, rng,
             bat, bowl, fld, idx) -> None:
    if len(order) < 2 or not bowlers:
        return

    striker, non, nxt = 0, 1, 2
    bat[idx[order[0]], 5] = 1
    bat[idx[order[1]], 5] = 1

    wkts, legal = 0, 0
    runs = 0
    while legal < MAX_OVERS * 6 and wkts < 10 and nxt <= len(order):
        over = legal // 6
        phase = "pp" if over < 6 else "mid" if over < 16 else "death"
        bowl_pid = bowlers[over % len(bowlers)]
        bidx, widx = idx[order[striker]], idx[bowl_pid]
        bat[bidx, 5] = 1

        p = probs_fn(order[striker], bowl_pid, phase,
                     int(bat[bidx, 1]), 10 - wkts)
        o = int(rng.choice(9, p=p))

        if o == 7:                                    # wide
            bowl[widx, 1] += 1
            runs += 1
            continue
        if o == 8:                                    # no ball
            bowl[widx, 1] += 1
            bat[bidx, 0] += 1
            runs += 1
            continue

        legal += 1
        bat[bidx, 1] += 1
        bowl[widx, 0] += 1

        if o == 6:                                    # wicket
            bat[bidx, 4] = 1
            bowl[widx, 2] += 1
            r = rng.random()
            if r < 0.55:
                bowl[widx, 3] += 1                    # bowled / lbw
            elif r < 0.78:
                fld[idx[fielders[int(rng.integers(len(fielders)))]], 0] += 1
            elif r < 0.86:
                fld[idx[keeper], 1] += 1
            else:
                fld[idx[fielders[int(rng.integers(len(fielders)))]], 3] += 1
            wkts += 1
            if nxt < len(order):
                striker = nxt
                nxt += 1
                bat[idx[order[striker]], 5] = 1
            else:
                break
            continue

        r = int(_RUNS[o])
        bat[bidx, 0] += r
        bowl[widx, 1] += r
        runs += r
        if r == 4:
            bat[bidx, 2] += 1
        elif r == 6:
            bat[bidx, 3] += 1
        if r % 2 == 1:
            striker, non = non, striker

        if legal % 6 == 0:                            # end of over
            striker, non = non, striker


_RUNS = np.array([0, 1, 2, 3, 4, 6, 0, 0, 0])


def build_probs_fn(model, fallback, batter_quality: dict, bowler_quality: dict):
    """Blend a trained model with empirical base rates.

    If no model is available, shift the empirical phase vector by the
    batter/bowler quality differential so the sim is not quality-blind.
    """
    def fn(batter_id, bowler_id, phase, balls_faced, wkts_left):
        base = fallback.probs(phase).copy()
        if model is not None:
            return base
        q = (batter_quality.get(batter_id, 0.0) - bowler_quality.get(bowler_id, 0.0))
        # positive q: more boundaries, fewer dots and wickets
        base[0] *= max(0.55, 1 - 0.35 * q)
        base[4] *= 1 + 0.55 * q
        base[5] *= 1 + 0.65 * q
        base[6] *= max(0.6, 1 - 0.30 * q)
        base = np.clip(base, 1e-6, None)
        return base / base.sum()

    return fn
