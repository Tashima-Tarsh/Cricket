from __future__ import annotations
import pulp as pl
from .constraints import Ctx


def solve_core(ctx: Ctx, tail=False, locked=(), banned=(), exclude=(), risk=0.0):
    r = ctx.rules()
    p = pl.LpProblem("core", pl.LpMaximize)
    x = pl.LpVariable.dicts("x", ctx.ids, cat="Binary")
    c = pl.LpVariable.dicts("c", ctx.ids, cat="Binary")
    v = pl.LpVariable.dicts("v", ctx.ids, cat="Binary")

    obj = pl.lpSum(x[i] * ctx.proj[i] for i in ctx.ids)
    obj += pl.lpSum(c[i] * ctx.proj[i] for i in ctx.ids)
    obj += pl.lpSum(v[i] * 0.5 * ctx.proj[i] for i in ctx.ids)
    if tail:
        obj += pl.lpSum(x[i] * ctx.boom.get(i, 0.0) * 3.0 for i in ctx.ids)
    obj += pl.lpSum(x[i] * risk * (1.0 if ctx.own.get(i, 50.0) < 15.0 else 0.0) for i in ctx.ids)
    p += obj

    p += pl.lpSum(x[i] for i in ctx.ids) == r["squad"]
    p += pl.lpSum(x[i] * ctx.credit[i] for i in ctx.ids) <= r["credits"]
    p += pl.lpSum(c[i] for i in ctx.ids) == 1
    p += pl.lpSum(v[i] for i in ctx.ids) == 1
    for i in ctx.ids:
        p += c[i] <= x[i]
        p += v[i] <= x[i]
        p += c[i] + v[i] <= 1
    for m in ctx.by_team.values():
        p += pl.lpSum(x[i] for i in m) <= r["per_team_max"]
    p += pl.lpSum(x[i] for i in ctx.overseas) <= r["overseas_max"]
    for role, (lo, hi) in r["roles"].items():
        pool = ctx.by_role.get(role, [])
        p += pl.lpSum(x[i] for i in pool) >= lo
        p += pl.lpSum(x[i] for i in pool) <= hi
    for i in locked:
        p += x[i] == 1
    for i in banned:
        p += x[i] == 0
    for prev in exclude:
        p += pl.lpSum(x[i] for i in prev) <= len(prev) - 1

    p.solve(pl.PULP_CBC_CMD(msg=0, timeLimit=15))
    if pl.LpStatus[p.status] != "Optimal":
        return None
    squad = [i for i in ctx.ids if x[i].value() and x[i].value() > 0.5]
    if len(squad) != r["squad"]:
        return None
    cap = next((i for i in ctx.ids if c[i].value() and c[i].value() > 0.5), squad[0])
    vic = next((i for i in ctx.ids if v[i].value() and v[i].value() > 0.5), squad[1])
    if cap == vic:
        vic = next((i for i in squad if i != cap), squad[1])
    return squad, cap, vic
