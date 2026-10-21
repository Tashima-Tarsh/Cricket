from __future__ import annotations
from dataclasses import dataclass, field
from ..config import settings


@dataclass
class Ctx:
    ids: list
    team: dict
    role: dict
    credit: dict
    overseas: set
    proj: dict
    boom: dict = field(default_factory=dict)
    own: dict = field(default_factory=dict)
    by_team: dict = field(default_factory=dict)
    by_role: dict = field(default_factory=dict)

    @classmethod
    def from_frame(cls, df):
        ctx = cls(
            ids=list(df.player_id),
            team=dict(zip(df.player_id, df.team)),
            role=dict(zip(df.player_id, df.role)),
            credit=dict(zip(df.player_id, df.credit.astype(float))),
            overseas=set(df[df.overseas].player_id),
            proj=dict(zip(df.player_id, df.proj.astype(float))),
            boom=dict(zip(df.player_id, df.get("boom", [0.0] * len(df)))),
            own=dict(zip(df.player_id, df.get("own_pct", [1.0] * len(df)))),
        )
        for i in ctx.ids:
            ctx.by_team.setdefault(ctx.team[i], []).append(i)
            ctx.by_role.setdefault(ctx.role[i], []).append(i)
        return ctx

    def rules(self):
        return settings().rules["t20"]


def is_legal(squad, ctx: Ctx) -> bool:
    r = ctx.rules()
    sq = list(squad)
    if len(set(sq)) != r["squad"]:
        return False
    if sum(ctx.credit[i] for i in sq) > r["credits"] + 1e-6:
        return False
    for m in ctx.by_team.values():
        if sum(1 for i in sq if i in m) > r["per_team_max"]:
            return False
    if sum(1 for i in sq if i in ctx.overseas) > r["overseas_max"]:
        return False
    for role, (lo, hi) in r["roles"].items():
        n = sum(1 for i in sq if ctx.role[i] == role)
        if not (lo <= n <= hi):
            return False
    return True


def repair(squad, ctx: Ctx, rng, max_iter: int = 600):
    r = ctx.rules()
    sq = list(dict.fromkeys(squad))

    def can_add(p, current_sq):
        if p in current_sq:
            return False
        if sum(1 for x in current_sq if ctx.team[x] == ctx.team[p]) >= r["per_team_max"]:
            return False
        if p in ctx.overseas and sum(1 for x in current_sq if x in ctx.overseas) >= r["overseas_max"]:
            return False
        lo, hi = r["roles"][ctx.role[p]]
        if sum(1 for x in current_sq if ctx.role[x] == ctx.role[p]) >= hi:
            return False
        return True

    for it in range(max_iter):
        if is_legal(sq, ctx):
            return sq

        if it > 40 and it % 15 == 0 and len(sq) > 4:
            sq.pop(rng.integers(len(sq)))
            continue

        team_violation = False
        for tm, members in ctx.by_team.items():
            tm_in_sq = [p for p in sq if p in members]
            if len(tm_in_sq) > r["per_team_max"]:
                worst = min(tm_in_sq, key=lambda p: ctx.proj[p])
                sq.remove(worst)
                team_violation = True
                break
        if team_violation:
            continue

        os_in_sq = [p for p in sq if p in ctx.overseas]
        if len(os_in_sq) > r["overseas_max"]:
            worst = min(os_in_sq, key=lambda p: ctx.proj[p])
            sq.remove(worst)
            continue

        role_high = False
        for role, (lo, hi) in r["roles"].items():
            members = [p for p in sq if ctx.role[p] == role]
            if len(members) > hi:
                worst = min(members, key=lambda p: ctx.proj[p])
                sq.remove(worst)
                role_high = True
                break
        if role_high:
            continue

        role_low = False
        for role, (lo, hi) in r["roles"].items():
            members = [p for p in sq if ctx.role[p] == role]
            if len(members) < lo:
                cands = [p for p in ctx.by_role.get(role, []) if can_add(p, sq)]
                if cands:
                    cur_cost = sum(ctx.credit[p] for p in sq)
                    cands.sort(
                        key=lambda p: (
                            cur_cost + ctx.credit[p] <= r["credits"],
                            -ctx.credit[p] if cur_cost > r["credits"] else ctx.proj[p],
                        ),
                        reverse=True,
                    )
                    sq.append(cands[0])
                else:
                    droppable = [
                        p
                        for p in sq
                        if sum(1 for x in sq if ctx.role[x] == ctx.role[p])
                        > r["roles"][ctx.role[p]][0]
                    ]
                    if droppable:
                        sq.remove(min(droppable, key=lambda p: ctx.proj[p]))
                    elif sq:
                        sq.pop(rng.integers(len(sq)))
                role_low = True
                break
        if role_low:
            continue

        cur_cost = sum(ctx.credit[p] for p in sq)
        if cur_cost > r["credits"]:
            droppable = [
                p
                for p in sq
                if sum(1 for x in sq if ctx.role[x] == ctx.role[p])
                > r["roles"][ctx.role[p]][0]
            ]
            if not droppable:
                droppable = sq
            worst = max(droppable, key=lambda p: ctx.credit[p])
            sq.remove(worst)
            continue

        if len(sq) > r["squad"]:
            droppable = [
                p
                for p in sq
                if sum(1 for x in sq if ctx.role[x] == ctx.role[p])
                > r["roles"][ctx.role[p]][0]
            ]
            if not droppable:
                droppable = sq
            sq.remove(min(droppable, key=lambda p: ctx.proj[p]))
            continue

        if len(sq) < r["squad"]:
            cands = [p for p in ctx.ids if can_add(p, sq)]
            cur_cost = sum(ctx.credit[p] for p in sq)
            rem_slots = r["squad"] - len(sq)
            if cands:
                viable = [
                    p
                    for p in cands
                    if cur_cost + ctx.credit[p] <= r["credits"] - (rem_slots - 1) * 7.5
                ]
                pool = viable if viable else cands
                pool.sort(key=lambda p: ctx.proj[p], reverse=True)
                sq.append(pool[0])
            else:
                if sq:
                    sq.pop(rng.integers(len(sq)))
            continue

    return sq if is_legal(sq, ctx) else None
