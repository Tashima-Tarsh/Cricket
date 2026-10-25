"""
EdgeForge – Strict Pydantic data models.
Every entity carries provenance. No silent defaults that invent data.
"""
from __future__ import annotations
from pydantic import BaseModel, Field, field_validator, model_validator
from typing import List, Dict, Optional, Literal
from datetime import datetime, date
from enum import Enum


class Role(str, Enum):
    WK = "WK"
    BAT = "BAT"
    AR = "AR"
    BOWL = "BOWL"


class Archetype(str, Enum):
    ROAD = "ROAD_HIGHWAY"
    MINEFIELD = "MINEFIELD"
    MISMATCH = "MISMATCH"
    PARITY = "PARITY"


class DataProvenance(BaseModel):
    """Mandatory on every data object. Makes silent invention impossible."""
    source: Literal["cricsheet", "provider", "admin_fixture", "estimated", "unavailable"]
    provider_name: Optional[str] = None
    confidence: float = Field(ge=0.0, le=1.0, default=0.0)
    sample_size: int = Field(ge=0, default=0)
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    notes: Optional[str] = None

    @model_validator(mode="after")
    def reject_fake_high_confidence(self) -> "DataProvenance":
        if self.source == "estimated" and self.confidence > 0.6:
            raise ValueError("Estimated data cannot claim confidence > 0.6")
        if self.source == "unavailable" and self.confidence > 0.0:
            raise ValueError("Unavailable data must have confidence 0.0")
        return self


class Player(BaseModel):
    id: str
    name: str
    team: str
    role: Role
    credits: float = Field(ge=4.0, le=15.0)
    batting_hand: Literal["RHB", "LHB"] = "RHB"
    bowling_style: Optional[str] = None
    is_confirmed_xi: bool = False
    batting_order: Optional[int] = Field(default=None, ge=1, le=11)
    expected_overs: float = Field(default=0.0, ge=0.0, le=10.0)
    projected_ownership: Optional[float] = Field(default=None, ge=0.0, le=100.0)
    ownership_available: bool = False
    projected_points: Optional[float] = None
    ceiling: Optional[float] = None
    floor: Optional[float] = None
    provenance: DataProvenance


class Fixture(BaseModel):
    id: str
    title: str
    series: Optional[str] = None
    match_date: date
    venue: str
    format: Literal["T20", "ODI", "TEST"] = "T20"
    team_a: str
    team_b: str
    status: Literal["SCHEDULED", "TOSS", "LIVE", "COMPLETED", "ABANDONED"] = "SCHEDULED"
    archetype: Optional[Archetype] = None
    par_score: Optional[int] = None
    toss_winner: Optional[str] = None
    toss_decision: Optional[Literal["BAT", "BOWL"]] = None
    confirmed_xi_a: List[str] = Field(default_factory=list)
    confirmed_xi_b: List[str] = Field(default_factory=list)
    provenance: DataProvenance


class MatchupRecord(BaseModel):
    batter_id: str
    bowler_id: str
    balls: int = Field(ge=0)
    runs: int = Field(ge=0)
    dismissals: int = Field(ge=0)
    fours: int = 0
    sixes: int = 0
    dots: int = 0
    provenance: DataProvenance


class Lineup(BaseModel):
    fixture_id: str
    players: List[Player]
    captain_id: str
    vice_captain_id: str
    total_credits: float
    unspent_credits: float
    csp: Optional[float] = None
    projected_mean: Optional[float] = None
    projected_ceiling: Optional[float] = None
    uniqueness_score: Optional[float] = None
    game_script_tag: Optional[str] = None
    rationale: str = ""
    provenance: DataProvenance

    @model_validator(mode="after")
    def validate_lineup_size(self) -> "Lineup":
        if len(self.players) != 11:
            raise ValueError(f"Lineup must contain exactly 11 players, got {len(self.players)}")
        ids = {p.id for p in self.players}
        if self.captain_id not in ids or self.vice_captain_id not in ids:
            raise ValueError("Captain and Vice-Captain must be in the lineup")
        if self.captain_id == self.vice_captain_id:
            raise ValueError("Captain and Vice-Captain must be different players")
        return self
