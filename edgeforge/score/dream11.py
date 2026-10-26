"""
EdgeForge – Official Dream11 scoring (T20 + ODI).
This is the ONLY place points are calculated.
No hard-coded match-specific logic.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, Any, Literal
from enum import Enum


class Format(str, Enum):
    T20 = "T20"
    ODI = "ODI"
    T10 = "T10"


@dataclass(frozen=True)
class ScoringConfig:
    """Immutable scoring rules. Change here only when Dream11 changes rules."""
    # Batting
    run: float = 1.0
    boundary_four: float = 1.0
    boundary_six: float = 2.0
    duck: float = -2.0
    # T20 milestones
    t20_30_bonus: float = 4.0
    t20_50_bonus: float = 8.0
    t20_100_bonus: float = 16.0
    # T10 milestones
    t10_30_bonus: float = 8.0
    t10_50_bonus: float = 16.0
    # ODI milestones
    odi_50_bonus: float = 4.0
    odi_100_bonus: float = 8.0
    odi_150_bonus: float = 16.0
    # Bowling
    wicket: float = 30.0
    odi_wicket: float = 25.0
    bowled_lbw_bonus: float = 8.0
    maiden_t20: float = 12.0
    maiden_odi: float = 4.0
    dot_ball: float = 1.0
    # Wicket haul bonuses
    three_wickets: float = 4.0
    four_wickets: float = 8.0
    five_wickets: float = 16.0
    # Fielding
    catch: float = 8.0
    stumping: float = 12.0
    run_out_direct: float = 12.0
    run_out_indirect: float = 6.0
    three_catch_bonus: float = 4.0
    # Playing
    in_starting_11: float = 4.0


DEFAULT_CONFIG = ScoringConfig()


@dataclass
class ScoringResult:
    total: float
    breakdown: Dict[str, float] = field(default_factory=dict)
    format: str = "T20"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_points": round(self.total, 1),
            "breakdown": {k: round(v, 1) for k, v in self.breakdown.items()},
            "format": self.format,
        }


class Dream11Scorer:
    """
    Pure function scorer.
    Call calculate(...) with real performance numbers only.
    Never invents stats.
    """

    def __init__(self, config: ScoringConfig = DEFAULT_CONFIG):
        self.config = config

    def calculate(
        self,
        *,
        runs: int = 0,
        balls_faced: int = 0,
        fours: int = 0,
        sixes: int = 0,
        wickets: int = 0,
        overs_bowled: float = 0.0,
        runs_conceded: int = 0,
        maidens: int = 0,
        dots: int = 0,
        bowled_lbw: int = 0,
        catches: int = 0,
        stumpings: int = 0,
        run_outs_direct: int = 0,
        run_outs_indirect: int = 0,
        is_playing: bool = True,
        match_format: Literal["T20", "ODI", "T10"] = "T20",
        is_womens: bool = False,
        is_captain: bool = False,
        is_vice_captain: bool = False,
    ) -> ScoringResult:
        cfg = self.config
        fmt = match_format.upper()
        total = 0.0
        bd: Dict[str, float] = {}

        if is_playing:
            total += cfg.in_starting_11
            bd["starting_11"] = cfg.in_starting_11

        # Batting
        bat = (
            runs * cfg.run
            + fours * cfg.boundary_four
            + sixes * cfg.boundary_six
        )

        if fmt == "ODI":
            if runs >= 150:
                bat += cfg.odi_150_bonus
            elif runs >= 100:
                bat += cfg.odi_100_bonus
            elif runs >= 50:
                bat += cfg.odi_50_bonus
        elif fmt == "T10":
            if runs >= 50:
                bat += getattr(cfg, "t10_50_bonus", 16.0)
            elif runs >= 30:
                bat += getattr(cfg, "t10_30_bonus", 8.0)
        else:
            if runs >= 100:
                bat += cfg.t20_100_bonus
            elif runs >= 50:
                bat += cfg.t20_50_bonus
            elif runs >= 30:
                bat += cfg.t20_30_bonus

        if runs == 0 and balls_faced > 0:
            bat += cfg.duck

        if fmt == "ODI":
            min_balls = 20
        elif fmt == "T10":
            min_balls = 5
        else:
            min_balls = 10

        if balls_faced >= min_balls:
            sr = (runs / balls_faced) * 100.0
            if fmt == "ODI":
                if sr > 140:
                    bat += 6.0
                elif sr >= 120:
                    bat += 4.0
                elif sr >= 100:
                    bat += 2.0
                elif sr < 30:
                    bat -= 6.0
                elif sr < 40:
                    bat -= 4.0
                elif sr < 50:
                    bat -= 2.0
            elif fmt == "T10":
                if sr > 250.0:
                    bat += 6.0
                elif sr >= 200.0:
                    bat += 4.0
                elif sr >= 150.0:
                    bat += 2.0
                elif sr < 70.0:
                    bat -= 6.0
                elif sr < 80.0:
                    bat -= 4.0
                elif sr < 90.0:
                    bat -= 2.0
            else:
                if sr > 170:
                    bat += 6.0
                elif sr >= 150:
                    bat += 4.0
                elif sr >= 130:
                    bat += 2.0
                elif sr < 50:
                    bat -= 6.0
                elif sr < 60:
                    bat -= 4.0
                elif sr < 70:
                    bat -= 2.0

        total += bat
        bd["batting"] = bat

        # Bowling
        wicket_val = cfg.odi_wicket if fmt == "ODI" else cfg.wicket
        maiden_val = cfg.maiden_odi if fmt == "ODI" else cfg.maiden_t20

        bowl = (
            wickets * wicket_val
            + bowled_lbw * cfg.bowled_lbw_bonus
            + maidens * maiden_val
            + dots * cfg.dot_ball
        )

        if wickets >= 5:
            bowl += cfg.five_wickets
        elif wickets >= 4:
            bowl += cfg.four_wickets
        elif wickets >= 3:
            bowl += cfg.three_wickets

        if fmt == "ODI":
            min_overs = 5.0
        elif fmt == "T10":
            min_overs = 1.0
        else:
            min_overs = 2.0

        if overs_bowled >= min_overs:
            econ = runs_conceded / overs_bowled
            if fmt == "ODI":
                if econ < 3.5:
                    bowl += 6.0
                elif econ <= 4.5:
                    bowl += 4.0
                elif econ <= 5.5:
                    bowl += 2.0
                elif econ > 9.0:
                    bowl -= 6.0
                elif econ >= 8.0:
                    bowl -= 4.0
                elif econ >= 7.0:
                    bowl -= 2.0
            elif fmt == "T10":
                if econ < 6.0:
                    bowl += 6.0
                elif econ <= 7.0:
                    bowl += 4.0
                elif econ <= 8.0:
                    bowl += 2.0
                elif econ > 13.0:
                    bowl -= 6.0
                elif econ >= 12.0:
                    bowl -= 4.0
                elif econ >= 11.0:
                    bowl -= 2.0
            else:
                if econ < 5.0:
                    bowl += 6.0
                elif econ <= 6.0:
                    bowl += 4.0
                elif econ <= 7.0:
                    bowl += 2.0
                elif econ > 12.0:
                    bowl -= 6.0
                elif econ >= 11.0:
                    bowl -= 4.0
                elif econ >= 10.0:
                    bowl -= 2.0

        total += bowl
        bd["bowling"] = bowl
        bd["dot_balls"] = dots * cfg.dot_ball

        # Fielding
        field = (
            catches * cfg.catch
            + stumpings * cfg.stumping
            + run_outs_direct * cfg.run_out_direct
            + run_outs_indirect * cfg.run_out_indirect
        )
        if catches >= 3:
            field += cfg.three_catch_bonus

        total += field
        bd["fielding"] = field

        base_total = max(round(total, 1), -6.0)
        multiplier = 1.0
        if is_captain:
            multiplier = 2.0
        elif is_vice_captain:
            multiplier = 1.5

        final_total = round(base_total * multiplier, 1)

        return ScoringResult(total=final_total, breakdown=bd, format=fmt)
