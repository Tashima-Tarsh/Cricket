"""Conservative relock.

Only swap if the new lineup beats the held one by more than min_edge, and
stop churning inside the freeze window. Chasing noise at T-2m wrecks good
portfolios.
"""
from __future__ import annotations

from datetime import datetime, timedelta

from ..config import settings

METRIC = "p_top001"


def should_relock(held: dict, candidate: dict, deadline: datetime | None) -> bool:
    cfg = settings().relock
    if deadline is not None:
        remaining = deadline - datetime.now(deadline.tzinfo)
        if remaining < timedelta(minutes=cfg.freeze_minutes):
            return False
    base = max(held.get(METRIC, 0.0), 1e-9)
    return (candidate.get(METRIC, 0.0) - base) / base > cfg.min_edge


def diff(held: dict, candidate: dict) -> dict:
    return dict(
        out=sorted(set(held["squad"]) - set(candidate["squad"])),
        in_=sorted(set(candidate["squad"]) - set(held["squad"])),
        cap_change=held["cap"] != candidate["cap"],
        vic_change=held["vic"] != candidate["vic"],
    )
