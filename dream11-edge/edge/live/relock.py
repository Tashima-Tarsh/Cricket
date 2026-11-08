from __future__ import annotations
from datetime import datetime, timedelta
from ..config import settings

METRIC = "p_top001"


def should_relock(held, cand, deadline):
    cfg = settings().relock
    if deadline and (deadline - datetime.now(deadline.tzinfo)) < timedelta(minutes=cfg.freeze_minutes):
        return False
    base = max(held.get(METRIC, 0.0), 1e-9)
    return (cand.get(METRIC, 0.0) - base) / base > cfg.min_edge


def diff(held, cand):
    return dict(
        out=sorted(set(held["squad"]) - set(cand["squad"])),
        in_=sorted(set(cand["squad"]) - set(held["squad"])),
        cap_change=held["cap"] != cand["cap"],
        vic_change=held["vic"] != cand["vic"],
    )
