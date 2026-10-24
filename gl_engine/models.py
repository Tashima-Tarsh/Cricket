"""Data models for cricket players, fixtures, conditions, and fantasy lineups."""
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Literal

RoleType = Literal["WK", "BAT", "AR", "BOWL"]
BattingStyle = Literal["RHB", "LHB"]
BowlingStyle = str

class PlayerStats(BaseModel):
    matches: int = 0
    recent_runs: List[int] = Field(default_factory=list)
    recent_wickets: List[int] = Field(default_factory=list)
    recent_fantasy_pts: List[float] = Field(default_factory=list)
    avg_fantasy_pts: float = 0.0
    strike_rate: float = 130.0
    batting_avg: float = 25.0
    economy: float = 8.0
    bowling_strike_rate: float = 18.0
    death_overs_rate: float = 0.0  # fraction of death overs bowled
    powerplay_overs_rate: float = 0.0

class Player(BaseModel):
    id: str
    name: str
    team: str  # "IND" or "WI"
    role: RoleType
    credits: float
    batting_style: BattingStyle
    bowling_style: Optional[BowlingStyle] = None
    batting_order_projected: int  # 1 to 11
    expected_overs: float = 0.0  # 0.0 to 4.0
    is_confirmed_xi: bool = True
    projected_ownership: float = 50.0  # 0 to 100%
    ownership_available: bool = True
    stats: PlayerStats = Field(default_factory=PlayerStats)
    ceiling_score: float = 0.0
    floor_score: float = 0.0
    projected_points: float = 0.0
    captain_percentage: float = 0.0
    dream_team_percentage: float = 0.0
    differential_tag: Optional[str] = None  # e.g., "High-Ceiling Pacer", "Death-Overs Finisher"

class MatchupDetail(BaseModel):
    batter_name: str
    bowler_name: str
    balls: int
    runs: int
    dismissals: int
    strike_rate: float
    dismissal_rate: float  # dismissals / balls

class VenueConditions(BaseModel):
    name: str
    city: str
    avg_first_innings_score: int = 175
    pace_wickets_pct: float = 62.0
    spin_wickets_pct: float = 38.0
    dew_factor: float = 0.35  # 0.0 (no dew) to 1.0 (extreme dew favoring chasing)
    pitch_nature: str = "True bounce, excellent for strokeplay, pacers get early carry"
    boundary_dimensions: str = "Square 65m, Straight 72m"
    chasing_win_pct: float = 56.0

class WeatherReport(BaseModel):
    temperature_c: float = 28.0
    humidity_pct: float = 75.0
    rain_probability_pct: float = 10.0
    dew_expected: bool = True
    wind_kmh: float = 14.0
    match_interruption_risk: str = "Low"

class TossScenario(BaseModel):
    winner: str  # "IND" or "WI"
    decision: Literal["BAT_FIRST", "BOWL_FIRST"]
    dew_impact: float = 1.0  # multiplier on 2nd innings batting
    bat_first_advantage: float = 1.0

class Lineup(BaseModel):
    team_name: str
    scenario_tag: str
    players: List[Player]
    captain: Player
    vice_captain: Player
    total_credits: float
    projected_points: float
    simulated_ceiling: float
    total_ownership_sum: float
    differential_count: int
    team_balance: Dict[str, int]
    gl_rank_potential: str  # "Elite Ceiling", "High Volatility", "Anchor Balanced"
    tactical_rationale: str
    csp: Optional[float] = None  # Cumulative Selection Percentage (Target: 500% to 650%)
    mnc_summary: Optional[str] = None  # e.g., "Core: 6 | Rotation: 3 | Contrarian: 2"
    cvc_combo_type: Optional[str] = None  # "Combo A (Safe)", "Combo B (Sweet Spot)", "Combo C (GL Killer)"
