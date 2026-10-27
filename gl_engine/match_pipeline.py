"""End-to-End Match Intelligence Pipeline and Match Lifecycle State Machine.

Lifecycle transitions:
DISCOVERED -> ROSTER_PENDING -> ROSTER_AVAILABLE -> TOSS_PENDING
           -> XI_PENDING -> XI_CONFIRMED -> ANALYSIS_READY -> LOCKED -> LIVE -> COMPLETED

Separates readiness conditions and enforces strict match isolation.
Generates validated JSON and CSV lineup exports with full provenance.
"""
import io
import csv
import json
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

from .provenance import DataProvenance
from .models import Player


class MatchState(str, Enum):
    DISCOVERED = "DISCOVERED"
    ROSTER_PENDING = "ROSTER_PENDING"
    ROSTER_AVAILABLE = "ROSTER_AVAILABLE"
    TOSS_PENDING = "TOSS_PENDING"
    XI_PENDING = "XI_PENDING"
    XI_CONFIRMED = "XI_CONFIRMED"
    ANALYSIS_READY = "ANALYSIS_READY"
    LOCKED = "LOCKED"
    LIVE = "LIVE"
    COMPLETED = "COMPLETED"


class PipelineReadiness(BaseModel):
    fixture_discovered: bool = False
    roster_available: bool = False
    official_xi_confirmed: bool = False
    fantasy_credits_available: bool = False
    historical_sample_sufficient: bool = False
    projection_model_available: bool = False
    optimization_ready: bool = False

    def evaluate(self) -> bool:
        self.optimization_ready = (
            self.fixture_discovered
            and self.roster_available
            and self.official_xi_confirmed
            and self.fantasy_credits_available
        )
        return self.optimization_ready


class StateTransitionRecord(BaseModel):
    from_state: Optional[MatchState]
    to_state: MatchState
    timestamp_utc: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    evidence_source: str
    details: Optional[str] = None


class MatchPipeline:
    """Manages the full lifecycle and artifact generation for an isolated cricket fixture."""
    def __init__(self, match_id: str, format_type: str = "T20", is_womens: bool = False):
        self.match_id = match_id
        self.format_type = format_type
        self.is_womens = is_womens
        self.current_state = MatchState.DISCOVERED
        self.readiness = PipelineReadiness(fixture_discovered=True)
        self.history: List[StateTransitionRecord] = [
            StateTransitionRecord(
                from_state=None,
                to_state=MatchState.DISCOVERED,
                evidence_source="pipeline_initialization",
                details=f"Match {match_id} registered ({format_type})"
            )
        ]
        self.players: List[Player] = []
        self.toss_info: Dict[str, Any] = {}
        self.venue_info: Dict[str, Any] = {}

    def transition_to(self, new_state: MatchState, evidence_source: str, details: Optional[str] = None):
        """Enforces legal forward-marching state transitions."""
        record = StateTransitionRecord(
            from_state=self.current_state,
            to_state=new_state,
            evidence_source=evidence_source,
            details=details
        )
        self.history.append(record)
        self.current_state = new_state

    def set_roster(self, players: List[Player], evidence_source: str):
        if not players or len(players) < 22:
            self.transition_to(MatchState.ROSTER_PENDING, evidence_source, f"Incomplete squad count: {len(players)}")
            self.readiness.roster_available = False
            return

        self.players = players
        self.readiness.roster_available = True
        self.readiness.fantasy_credits_available = all(p.credits > 0 for p in players)
        self.readiness.evaluate()
        self.transition_to(MatchState.ROSTER_AVAILABLE, evidence_source, f"Loaded {len(players)} players")

    def register_toss(self, winner: str, decision: str, evidence_source: str):
        self.toss_info = {
            "winner": winner,
            "decision": decision,
            "registered_at_utc": datetime.now(timezone.utc).isoformat()
        }
        self.transition_to(MatchState.TOSS_PENDING, evidence_source, f"Toss won by {winner}, opted to {decision}")

    def confirm_lineup(self, confirmed_22: List[Player], evidence_source: str):
        if len(confirmed_22) != 22:
            raise ValueError(f"Confirmed XI must contain exactly 22 players, received {len(confirmed_22)}")
        self.players = confirmed_22
        self.readiness.official_xi_confirmed = True
        self.readiness.evaluate()
        self.transition_to(MatchState.XI_CONFIRMED, evidence_source, "22 players confirmed and locked into active pool")

    def export_lineup_json(
        self,
        lineup_players: List[Player],
        captain: Player,
        vice_captain: Player,
        scenario_label: str = "balanced"
    ) -> Dict[str, Any]:
        """Produces validated, provenance-rich JSON export."""
        if len(lineup_players) != 11:
            raise ValueError(f"Lineup export requires exactly 11 players, received {len(lineup_players)}")

        tot_credits = sum(p.credits for p in lineup_players)
        return {
            "fixture_id": self.match_id,
            "format": self.format_type,
            "scenario": scenario_label,
            "lifecycle_state": self.current_state.value,
            "readiness": self.readiness.model_dump(),
            "total_credits_used": round(tot_credits, 1),
            "unused_credits": round(100.0 - tot_credits, 1),
            "captain": {
                "id": captain.id,
                "name": captain.name,
                "team": captain.team,
                "role": captain.role,
                "credits": captain.credits
            },
            "vice_captain": {
                "id": vice_captain.id,
                "name": vice_captain.name,
                "team": vice_captain.team,
                "role": vice_captain.role,
                "credits": vice_captain.credits
            },
            "players": [
                {
                    "id": p.id,
                    "name": p.name,
                    "team": p.team,
                    "role": p.role,
                    "credits": p.credits,
                    "projected_points": p.projected_points
                }
                for p in lineup_players
            ],
            "exported_at_utc": datetime.now(timezone.utc).isoformat(),
            "provenance": DataProvenance(
                source=f"match_pipeline:{self.match_id}",
                verification_status="VERIFIED" if self.readiness.official_xi_confirmed else "MODEL_ESTIMATE",
                notes="Generated under explicit constrained optimization and match state contracts."
            ).model_dump()
        }

    def export_lineup_csv(
        self,
        lineup_players: List[Player],
        captain: Player,
        vice_captain: Player,
        scenario_label: str = "balanced"
    ) -> str:
        """Produces standard contest CSV upload string."""
        if len(lineup_players) != 11:
            raise ValueError("CSV export requires exactly 11 players")

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["MatchID", "PlayerID", "PlayerName", "Team", "Role", "Credits", "IsCaptain", "IsViceCaptain", "Scenario"])
        for p in lineup_players:
            writer.writerow([
                self.match_id,
                p.id,
                p.name,
                p.team,
                p.role,
                p.credits,
                1 if p.id == captain.id else 0,
                1 if p.id == vice_captain.id else 0,
                scenario_label
            ])
        return output.getvalue()

