"""Versioned, conservative API facade for the consolidated cricket workspace.

The three pre-existing engines remain available as libraries. This router
exposes a stable identity/roster/scoring/evaluation contract without silently
moving users across fixtures or promising calibrated predictions.
"""
from typing import Literal, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, ConfigDict, Field

from .capabilities.c11_fantasy_scoring import CricketFantasyScoring
from .official_scoring import RULE_VERSION, SOURCE_URL, score_official
from .roster_safety import validate_roster

router = APIRouter(prefix="/api/v1", tags=["stable-research-api"])


class ScoreRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    rule_version: Literal["legacy_v3", "dream11_published_2026_10_27"] = "legacy_v3"
    was_dismissed: bool = False
    match_format: Literal["T20", "ODI", "T10"] = "T20"
    runs: int = Field(default=0, ge=0)
    fours: int = Field(default=0, ge=0)
    sixes: int = Field(default=0, ge=0)
    balls_faced: int = Field(default=0, ge=0)
    wickets: int = Field(default=0, ge=0)
    bowled_lbw: int = Field(default=0, ge=0)
    overs_bowled: float = Field(default=0, ge=0)
    runs_conceded: int = Field(default=0, ge=0)
    maidens: int = Field(default=0, ge=0)
    dots: int = Field(default=0, ge=0)
    catches: int = Field(default=0, ge=0)
    stumpings: int = Field(default=0, ge=0)
    run_outs_direct: int = Field(default=0, ge=0)
    run_outs_indirect: int = Field(default=0, ge=0)
    is_playing: bool = True
    is_womens: bool = False
    is_captain: bool = False
    is_vice_captain: bool = False


class OptimizeRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    fixture_id: str = Field(min_length=1, max_length=128)
    teams: int = Field(default=1, ge=1, le=5)
    max_overlap: int = Field(default=8, ge=0, le=11)


@router.get("/engines")
def list_engines():
    return {
        "status": "RESEARCH_UNVERIFIED",
        "api_version": "v1",
        "primary": "gl_engine",
        "adapters": ["edgeforge", "dream11-edge"],
        "scoring": "gl_engine.capabilities.c11_fantasy_scoring",
        "scoring_rule_version": "legacy_v3",
        "live_provider_verification": "NOT_PROBED",
        "calibrated_contest_probabilities": False,
    }


@router.get("/fixtures")
def list_fixtures():
    from .universal_engine import get_universal_engine
    return {
        "fixtures": get_universal_engine().list_available_matches(),
        "verification_status": "UNVERIFIED",
    }


@router.get("/fixtures/{fixture_id}/roster")
def fixture_roster(fixture_id: str):
    from .universal_engine import get_universal_engine
    state = get_universal_engine().get_unified_state(fixture_id)
    players = state.get("players", [])
    validate_roster(players)
    return {
        "fixture_id": fixture_id,
        "players": players,
        "verification_status": state.get("match", {}).get(
            "data_provenance", "UNVERIFIED"
        ),
    }


@router.post("/score")
def score(request: ScoreRequest):
    data = request.model_dump(exclude={"rule_version"})
    if request.rule_version == RULE_VERSION:
        return {"rule_version": RULE_VERSION, "data": score_official(**data)}
    data.pop("was_dismissed")
    return {
        "rule_version": request.rule_version,
        "current_official_rule_verification": "LEGACY_ARCHIVAL_PROFILE",
        "data": CricketFantasyScoring().calculate_player_points(**data),
    }


@router.get("/scoring/rules")
def scoring_rules():
    return {
        "published_version": RULE_VERSION,
        "published_source": SOURCE_URL,
        "reviewed_on": "2026-10-27",
        "formats": ["T20", "ODI", "T10"],
        "legacy_profile_available": "legacy_v3",
        "selection_required": True,
        "caveat": "Published 2026 rules are not retroactive to historical contests.",
    }


@router.post("/optimize")
def optimize(request: OptimizeRequest):
    # Delegate to the existing validated CP-SAT route instead of creating
    # another independent solver or selecting an unrelated default fixture.
    from .web_app import get_ortools_lineups
    result = get_ortools_lineups(
        teams=request.teams,
        max_overlap=request.max_overlap,
        match_id=request.fixture_id,
    )
    return {
        "api_version": "v1",
        "fixture_id": request.fixture_id,
        "status": result.get("status", "UNAVAILABLE"),
        "lineups": result.get("lineups", []),
        "calibrated_contest_probabilities": False,
    }


@router.get("/evaluation")
def evaluation():
    from .capabilities.c19_backtesting import CricketBacktesting
    return CricketBacktesting().execute()
