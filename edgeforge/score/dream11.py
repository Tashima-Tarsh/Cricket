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
        # One scoring implementation for all engines; this adapter retains
        # the EdgeForge return type and configurable point weights.
        from gl_engine.capabilities.c11_fantasy_scoring import CricketFantasyScoring
        from gl_engine.config import FantasyScoringConfig
        cfg = self.config
        rules = FantasyScoringConfig(
            run=cfg.run, boundary_four=cfg.boundary_four,
            boundary_six=cfg.boundary_six, duck=cfg.duck,
            runs_30_bonus=cfg.t20_30_bonus, runs_50_bonus=cfg.t20_50_bonus,
            runs_100_bonus=cfg.t20_100_bonus,
            t10_30_bonus=cfg.t10_30_bonus, t10_50_bonus=cfg.t10_50_bonus,
            odi_50_bonus=cfg.odi_50_bonus, odi_100_bonus=cfg.odi_100_bonus,
            odi_150_bonus=cfg.odi_150_bonus,
            wicket=cfg.wicket, odi_wicket=cfg.odi_wicket,
            bowled_lbw_bonus=cfg.bowled_lbw_bonus,
            maiden_over=cfg.maiden_t20, maiden_odi=cfg.maiden_odi,
            dot_ball=cfg.dot_ball, three_wickets_bonus=cfg.three_wickets,
            four_wickets_bonus=cfg.four_wickets,
            five_wickets_bonus=cfg.five_wickets,
            catch=cfg.catch, stumping=cfg.stumping,
            run_out_direct=cfg.run_out_direct,
            run_out_thrower_catcher=cfg.run_out_indirect,
            three_catch_bonus=cfg.three_catch_bonus,
            in_starting_11=cfg.in_starting_11,
        )
        scored = CricketFantasyScoring(rules).calculate_player_points(
            runs=runs, fours=fours, sixes=sixes, balls_faced=balls_faced,
            wickets=wickets, bowled_lbw=bowled_lbw, overs_bowled=overs_bowled,
            runs_conceded=runs_conceded, maidens=maidens, dots=dots,
            catches=catches, stumpings=stumpings,
            run_outs_direct=run_outs_direct, run_outs_indirect=run_outs_indirect,
            is_playing=is_playing, match_format=match_format,
            is_womens=is_womens, is_captain=is_captain,
            is_vice_captain=is_vice_captain,
        )
        return ScoringResult(
            total=scored["total_points"], breakdown=scored["breakdown"],
            format=scored["format"]
        )
