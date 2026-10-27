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
from collections import Counter
from math import isfinite
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

from .provenance import DataProvenance
from .models import Player
from .roster_safety import validate_confirmed_xi


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
    provider_xi_evidence: bool = False

    def evaluate(self) -> bool:
        self.optimization_ready = (
            self.fixture_discovered
            and self.roster_available
            and self.official_xi_confirmed
            and self.fantasy_credits_available
            and self.provider_xi_evidence
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

    _ALLOWED_TRANSITIONS = {
        MatchState.DISCOVERED: {MatchState.ROSTER_PENDING, MatchState.ROSTER_AVAILABLE},
        MatchState.ROSTER_PENDING: {MatchState.ROSTER_PENDING, MatchState.ROSTER_AVAILABLE},
        MatchState.ROSTER_AVAILABLE: {MatchState.TOSS_PENDING, MatchState.XI_PENDING, MatchState.XI_CONFIRMED},
        MatchState.TOSS_PENDING: {MatchState.XI_PENDING, MatchState.XI_CONFIRMED},
        MatchState.XI_PENDING: {MatchState.XI_CONFIRMED},
        MatchState.XI_CONFIRMED: {MatchState.ANALYSIS_READY},
        MatchState.ANALYSIS_READY: {MatchState.LOCKED},
        MatchState.LOCKED: {MatchState.LIVE},
        MatchState.LIVE: {MatchState.COMPLETED},
        MatchState.COMPLETED: set(),
    }

    def transition_to(self, new_state: MatchState, evidence_source: str, details: Optional[str] = None):
        """Reject backwards/invalid lifecycle transitions and untraceable changes."""
        if not isinstance(evidence_source, str) or not evidence_source.strip():
            raise ValueError("Lifecycle transition requires a nonempty evidence source")
        if new_state not in self._ALLOWED_TRANSITIONS[self.current_state]:
            raise ValueError(f"Illegal match transition: {self.current_state.value} -> {new_state.value}")
        record = StateTransitionRecord(
            from_state=self.current_state, to_state=new_state,
            evidence_source=evidence_source, details=details
        )
        self.history.append(record)
        self.current_state = new_state

    @staticmethod
    def _identity_check(players: List[Player], *, require_exact_xi: bool):
        if require_exact_xi:
            validate_confirmed_xi(players)
        else:
            if len(players) < 22:
                raise ValueError("Two full teams are needed for the roster")
        ids = [p.id for p in players]
        if len(set(ids)) != len(ids):
            raise ValueError("Duplicate player IDs are not allowed")
        names = [p.name.casefold().strip() for p in players]
        if len(set(names)) != len(names):
            raise ValueError("Duplicate player names are not allowed")
        by_team = Counter(p.team for p in players)
        if len(by_team) != 2 or (require_exact_xi and sorted(by_team.values()) != [11, 11]):
            raise ValueError("A playing XI must have two teams of eleven")
        if any(not p.team or not p.name.strip() or not p.id.strip() for p in players):
            raise ValueError("Roster contains incomplete player identities")

    def set_roster(self, players: List[Player], evidence_source: str):
        if not players or len(players) < 22:
            self.transition_to(MatchState.ROSTER_PENDING, evidence_source, f"Incomplete player count: {len(players) if players else 0}")
            self.readiness.roster_available = False
            self.readiness.evaluate()
            return
        self._identity_check(players, require_exact_xi=False)
        self.transition_to(MatchState.ROSTER_AVAILABLE, evidence_source, f"Loaded {len(players)} unique players")
        self.players = players
        self.readiness.roster_available = True
        self.readiness.fantasy_credits_available = all(isfinite(p.credits) and 0 < p.credits <= 20 for p in players)
        self.readiness.evaluate()

    def register_toss(self, winner: str, decision: str, evidence_source: str):
        teams = {p.team for p in self.players}
        if winner not in teams or decision not in {"bat", "bowl"}:
            raise ValueError("Toss must identify one roster team and a bat/bowl decision")
        self.transition_to(MatchState.TOSS_PENDING, evidence_source, f"Toss reported for {winner}")
        self.toss_info = {
            "winner": winner, "decision": decision,
            "verification_status": "UNVERIFIED_SOURCE",
            "registered_at_utc": datetime.now(timezone.utc).isoformat(),
        }

    def confirm_lineup(self, confirmed_22: List[Player], evidence_source: str,
                       corroboration: Optional[Dict[str, Any]] = None):
        """Only a fixture-bound, cross-provider XI report can assert confirmation.

        A manually supplied roster can be used as unverified research data, but
        cannot set the official-XI flag by merely passing 22 names.
        The corroboration report must originate from the trusted verifier,
        not an untrusted browser-provided field.
        """
        if not self.readiness.roster_available:
            raise ValueError("Load a real two-team roster before confirming its XI")
        self._identity_check(confirmed_22, require_exact_xi=True)
        prior_ids = {p.id for p in self.players}
        if not {p.id for p in confirmed_22} <= prior_ids:
            raise ValueError("XI introduces unknown player IDs")
        if not isinstance(corroboration, dict) or corroboration.get("status") != "CROSS_PROVIDER_CORROBORATED":
            raise ValueError("Cross-provider XI corroboration required; user attestation alone is not official")
        if corroboration.get("fixture_id") != self.match_id:
            raise ValueError("XI evidence is for another fixture")
        provider_ids = corroboration.get("provider_fixture_ids") or {}
        if not all(isinstance(provider_ids.get(key), str) and provider_ids[key].strip()
                   for key in ("sportmonks", "cricketdata")):
            raise ValueError("XI evidence is missing independent provider fixture IDs")
        if set(corroboration.get("sources", [])) != {"sportmonks_live", "cricketdata_live"}:
            raise ValueError("XI corroboration requires two independent known provider sources")
        if corroboration.get("count") != 22:
            raise ValueError("XI evidence does not contain 22 players")
        report_teams = corroboration.get("teams")
        if not isinstance(report_teams, list) or len(report_teams) != 2:
            raise ValueError("Invalid XI report team identities")
        expected = {t: {p.name.casefold().strip() for p in confirmed_22 if p.team == t}
                    for t in {p.team for p in confirmed_22}}
        observed = {}
        for team in report_teams:
            key = str(team.get("name", "")).strip()
            if key in observed:
                raise ValueError("Duplicate corroborated team")
            observed[key] = {str(n).casefold().strip() for n in team.get("players", [])}
        if observed != expected:
            raise ValueError("Corroborated team/player identities do not match this fixture's XI")
        checked_at = corroboration.get("checked_at_utc")
        try:
            verified_at = datetime.fromisoformat(checked_at)
        except (TypeError, ValueError) as exc:
            raise ValueError("XI corroboration requires a verification timestamp") from exc
        now = datetime.now(timezone.utc)
        if verified_at.tzinfo is None or not 0 <= (now - verified_at).total_seconds() <= 900:
            raise ValueError("XI verification is stale, future-dated or not timezone-aware")
        self.transition_to(MatchState.XI_CONFIRMED, evidence_source,
                           "22 fixture-identical players corroborated by two independent feeds")
        self.players = confirmed_22
        self.readiness.official_xi_confirmed = True
        self.readiness.provider_xi_evidence = True
        self.readiness.fantasy_credits_available = all(isfinite(p.credits) and 0 < p.credits <= 20 for p in confirmed_22)
        self.readiness.evaluate()

    def _validate_lineup_export(self, lineup_players: List[Player], captain: Player, vice_captain: Player):
        """Validate standard 11-player constrained fantasy export before CSV/JSON."""
        if not self.readiness.optimization_ready:
            raise ValueError("A source-confirmed XI and credits are required before official lineup export")
        if len(lineup_players) != 11:
            raise ValueError(f"Lineup requires exactly 11 players, received {len(lineup_players)}")
        ids = [p.id for p in lineup_players]
        if len(set(ids)) != 11:
            raise ValueError("Duplicate fantasy player IDs")
        if captain.id == vice_captain.id or captain.id not in ids or vice_captain.id not in ids:
            raise ValueError("Captain and vice-captain must be distinct members of the lineup")
        if not set(ids) <= {p.id for p in self.players}:
            raise ValueError("Lineup contains players outside the confirmed match XI")
        by_team = Counter(p.team for p in lineup_players)
        if len(by_team) != 2 or max(by_team.values()) > 7:
            raise ValueError("Fantasy XI must use both teams and at most seven players from either")
        by_role = Counter(p.role for p in lineup_players)
        required_ranges = {"WK": (1, 4), "BAT": (3, 6), "AR": (1, 4), "BOWL": (3, 6)}
        if any(not lo <= by_role[role] <= hi for role, (lo, hi) in required_ranges.items()):
            raise ValueError("Fantasy XI violates position limits")
        credits = sum(p.credits for p in lineup_players)
        if not isfinite(credits) or credits > 100:
            raise ValueError("Fantasy XI exceeds the 100-credit cap")
        return credits

    def export_lineup_json(
        self,
        lineup_players: List[Player],
        captain: Player,
        vice_captain: Player,
        scenario_label: str = "balanced"
    ) -> Dict[str, Any]:
        """Produces validated, provenance-rich JSON export."""
        tot_credits = self._validate_lineup_export(lineup_players, captain, vice_captain)
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
                verification_status="MODEL_ESTIMATE",
                notes="Source-confirmed XI membership does not verify projected lineup performance."
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
        self._validate_lineup_export(lineup_players, captain, vice_captain)

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

