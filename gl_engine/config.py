"""Configuration settings for Fantasy Cricket Grand League Engine.
Implements Dream11 & Standard T20 fantasy scoring rules and roster constraints.
"""
import os
from typing import Dict, Optional
from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()

class FantasyScoringConfig(BaseModel):
    # Batting Points
    run: float = 1.0
    boundary_four: float = 1.0  # +1 extra bonus on top of 4 runs scored
    boundary_six: float = 2.0   # +2 extra bonus on top of 6 runs scored
    duck: float = -2.0          # (except bowlers batting 8+)
    runs_30_bonus: float = 4.0
    runs_50_bonus: float = 8.0
    runs_100_bonus: float = 16.0
    # T10 Milestones
    t10_30_bonus: float = 8.0
    t10_50_bonus: float = 16.0
    # ODI Milestones
    odi_50_bonus: float = 4.0
    odi_100_bonus: float = 8.0
    odi_150_bonus: float = 16.0
    
    # Strike Rate Bonus/Penalty (min 10 balls faced)
    strike_rate_bonuses: Dict[str, float] = Field(default_factory=lambda: {
        "over_170": 6.0,
        "150_to_170": 4.0,
        "130_to_150": 2.0,
        "70_to_130": 0.0,
        "60_to_70": -2.0,
        "50_to_59": -4.0,
        "under_50": -6.0
    })

    # Bowling Points
    wicket: float = 30.0        # Official Dream11 T20 wicket = 30 pts (updated from 25)
    dot_ball: float = 1.0       # Official Dream11 T20 dot ball = +1 pt
    bowled_lbw_bonus: float = 8.0
    maiden_over: float = 12.0
    three_wickets_bonus: float = 4.0
    four_wickets_bonus: float = 8.0
    five_wickets_bonus: float = 16.0
    
    # Economy Rate Bonus/Penalty (min 2 overs / 12 balls bowled)
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
    min_credits: float = 79.0       # Minimum team credit sum (e.g. 79.0 or 87.0)
    max_credits: float = 85.0       # Maximum team credit sum (e.g. 85.0 or 89.0)
    max_players_per_team: int = 10  # Modern Dream11 allows up to 10 from one side (or 7 in classic)
    min_players_per_team: int = 1
    min_wk: int = 1
    max_wk: int = 8
    min_bat: int = 1
    max_bat: int = 8
    min_ar: int = 1
    max_ar: int = 8
    min_bowl: int = 1
    max_bowl: int = 8
    min_bowling_options: int = 5    # Lineup should have at least 5 credible bowling options


DEFAULT_SCORING = FantasyScoringConfig()
DEFAULT_CONSTRAINTS = LineupConstraints()
