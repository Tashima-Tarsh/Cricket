import numpy as np

from edge.optimize.constraints import Ctx, is_legal, repair


def test_repair_produces_legal(roster):
    ctx = Ctx.from_frame(roster)
    rng = np.random.default_rng(0)
    sq = repair(list(rng.choice(ctx.ids, 11, replace=False)), ctx, rng)
    assert sq is not None and is_legal(sq, ctx)


def test_repair_success_rate(roster):
    ctx = Ctx.from_frame(roster)
    rng = np.random.default_rng(9)
    ok = 0
    for _ in range(200):
        sq = repair(list(rng.choice(ctx.ids, 11, replace=False)), ctx, rng)
        if sq and is_legal(sq, ctx):
            ok += 1
    assert ok > 180


def test_credit_cap_enforced(roster):
    ctx = Ctx.from_frame(roster)
    rng = np.random.default_rng(3)
    for _ in range(50):
        sq = repair(list(rng.choice(ctx.ids, 11, replace=False)), ctx, rng)
        if sq:
            assert sum(ctx.credit[i] for i in sq) <= 100 + 1e-6


def test_overseas_cap_enforced(roster):
    ctx = Ctx.from_frame(roster)
    rng = np.random.default_rng(4)
    for _ in range(50):
        sq = repair(list(rng.choice(ctx.ids, 11, replace=False)), ctx, rng)
        if sq:
            assert sum(1 for i in sq if i in ctx.overseas) <= 4
