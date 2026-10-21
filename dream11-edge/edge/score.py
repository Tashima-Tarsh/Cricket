"""Exact Dream11 T20 scoring.

Single source of truth. The simulator, the backtester and the validator
all call this - nothing re-implements the table.
"""
from __future__ import annotations

from dataclasses import dataclass

MIN_BALLS_SR = 10
MIN_BALLS_ECO = 12
FLOOR = -6.0


@dataclass
class BatLine:
    runs: int = 0
    balls: int = 0
    fours: int = 0
    sixes: int = 0
    out: bool = False
    batted: bool = True


@dataclass
class BowlLine:
    balls: int = 0
    runs: int = 0
    wickets: int = 0
    lbw_bowled: int = 0
    maidens: int = 0


@dataclass
class FieldLine:
    catches: int = 0
    stumpings: int = 0
    runout_direct: int = 0
    runout_indirect: int = 0


def sr_bonus(runs: int, balls: int) -> float:
    if balls < MIN_BALLS_SR:
        return 0.0
    sr = 100.0 * runs / balls
    if sr > 170:
        return 6.0
    if sr > 150:
        return 4.0
    if sr >= 130:
        return 2.0
    if sr >= 60:
        return -2.0
    if sr >= 50:
        return -4.0
    return -6.0


def eco_bonus(runs: int, balls: int) -> float:
    if balls < MIN_BALLS_ECO:
        return 0.0
    eco = runs / (balls / 6.0)
    if eco <= 5:
        return 6.0
    if eco < 6:
        return 4.0
    if eco < 7:
        return 2.0
    if eco <= 10:
        return 0.0
    if eco <= 11:
        return -2.0
    if eco <= 12:
        return -4.0
    return -6.0


def points(bat: BatLine, bowl: BowlLine, fld: FieldLine) -> float:
    p = 0.0
    if bat.batted:
        p += bat.runs + bat.fours + 2 * bat.sixes
        p += sr_bonus(bat.runs, bat.balls)
        if bat.out and bat.runs == 0:
            p -= 2.0
        if bat.runs >= 100:
            p += 16.0
        elif bat.runs >= 50:
            p += 8.0
        elif bat.runs >= 30:
            p += 4.0
    p += 30.0 * bowl.wickets + 8.0 * bowl.lbw_bowled + 12.0 * bowl.maidens
    if bowl.wickets >= 5:
        p += 12.0
    elif bowl.wickets >= 4:
        p += 8.0
    elif bowl.wickets >= 3:
        p += 4.0
    p += eco_bonus(bowl.runs, bowl.balls)
    p += 8.0 * fld.catches + 12.0 * fld.stumpings
    p += 12.0 * fld.runout_direct + 6.0 * fld.runout_indirect
    if fld.catches >= 3:
        p += 4.0
    return max(p, FLOOR)


def score_lineup(squad_points: dict, captain: str, vice: str) -> float:
    total = 0.0
    for pid, pts in squad_points.items():
        if pid == captain:
            total += 2.0 * pts
        elif pid == vice:
            total += 1.5 * pts
        else:
            total += pts
    return total
