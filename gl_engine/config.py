"""Configuration settings for Fantasy Cricket Grand League Engine.
Implements Dream11-style scoring rules for T20, ODI and T10 (men & women)
and roster constraints.

INVARIANTS:
- Single source of truth for point values.
- Format-aware thresholds live in the scorer, not scattered callers.
"""
import os
from typing import Dict, Optional
from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()

class FantasyScoringConfig(BaseModel):
    # Batting Points
    run: float = 1.0
    boundary_four: float = 1.0   # +1 extra on top of 4 runs
    boundary_six: float = 2.0    # +2 extra on top of 6 runs
    duck: float = -2.0

    # T20 milestone bonuses (Dream11-style)
    runs_30_bonus: float = 4.0
    runs_50_bonus: float = 8.0
    runs_100_bonus: float = 16.0

    # Additional format rule parameters (legacy-v3 compatibility profile)
    t10_30_bonus: float = 8.0
    t10_50_bonus: float = 16.0
    odi_50_bonus: float = 4.0
    odi_100_bonus: float = 8.0
    odi_150_bonus: float = 16.0
    odi_wicket: float = 25.0
    maiden_odi: float = 4.0

    # Strike Rate Bonus/Penalty (min balls depend on format — applied in scorer)
    strike_rate_bonuses: Dict[str, float] = Field(default_factory=lambda: {
        "over_170": 6.0,
        "150_to_170": 4.0,
        "130_to_150": 2.0,
        "70_to_130": 0.0,
        "60_to_70": -2.0,
        "50_to_59": -4.0,
        "under_50": -6.0
    })

    # Bowling Points (T20 defaults; ODI/T10 override wicket/maiden in scorer)
    wicket: float = 30.0
    dot_ball: float = 1.0
    bowled_lbw_bonus: float = 8.0
    maiden_over: float = 12.0
    three_wickets_bonus: float = 4.0
    four_wickets_bonus: float = 8.0
    five_wickets_bonus: float = 16.0

    # Economy Rate Bonus/Penalty (min overs depend on format)
    economy_bonuses: Dict[str, float] = Field(default_factory=lambda: {
        "under_5": 6.0,
        "5_to_6": 4.0,
        "6_to_7": 2.0,
        "7_to_10": 0.0,
        "10_to_11": -2.0,
        "11_to_12": -4.0,
        "over_12": -6.0
    })

    # Fielding Points
    catch: float = 8.0
    three_catch_bonus: float = 4.0
    stumping: float = 12.0
    run_out_direct: float = 12.0
    run_out_thrower_catcher: float = 6.0

    # Multipliers
    captain_multiplier: float = 2.0
    vice_captain_multiplier: float = 1.5
    in_starting_11: float = 4.0


class LineupConstraints(BaseModel):
    total_players: int = 11
    min_credits: float = 79.0
    max_credits: float = 100.0
    max_players_per_team: int = 10
    min_players_per_team: int = 1
    min_wk: int = 1
    max_wk: int = 8
    min_bat: int = 1
    max_bat: int = 8
    min_ar: int = 1
    max_ar: int = 8
    min_bowl: int = 1
    max_bowl: int = 8
    min_bowling_options: int = 5


DEFAULT_SCORING = FantasyScoringConfig()
DEFAULT_CONSTRAINTS = LineupConstraints()
