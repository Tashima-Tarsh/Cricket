"""Versioned, conservative API facade for the consolidated cricket workspace.

The three pre-existing engines remain available as libraries. This router
exposes a stable identity/roster/scoring/evaluation contract without silently
moving users across fixtures or promising calibrated predictions.
"""
from typing import Literal, Optional
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, ConfigDict, Field

from .capabilities.c11_fantasy_scoring import CricketFantasyScoring
from .official_scoring import RULE_VERSION, SOURCE_URL, score_official
from .roster_safety import validate_roster
from .admin_auth import require_admin
from .live_xi_verification import verify_live_xi

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


@router.get("/readiness")
def research_readiness():
    """Measured local readiness, never an assertion of provider-verified XI or ROI."""
    import os
    from .universal_engine import get_universal_engine
    from .providers.sportmonks_api import SportmonksCricketClient
    from .cricketdata_api import CricketDataClient
    engine = get_universal_engine()
    return {
        "service": "RESEARCH_MODE",
        "available_connected_fixtures": len(engine.list_available_matches()),
        "playing_xi_verification": "MANUAL_ATTESTATION_ONLY",
        "provider_configured_not_probed": {
            "sportmonks": bool(SportmonksCricketClient().is_live),
            "cricketdata": bool(CricketDataClient().is_live),
        },
        "manual_ingestion_enabled": bool(os.getenv("CRICKET_ADMIN_TOKEN")),
        "official_fantasy_scoring_rule_version": RULE_VERSION,
        "model_calibrated_rank1_probabilities": False,
        "validated_real_world_profitability": False,
        "limitations": [
            "No licensed live-XI agreement guarantees",
            "No calibrated contest-field or Rank-1 distribution",
            "Request-time heavy work requires ingress quotas in production",
        ],
    }


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


class LiveXIRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    fixture_id: str = Field(min_length=1, max_length=128)
    sportmonks_fixture_id: str = Field(min_length=1, max_length=128)
    cricketdata_match_id: str = Field(min_length=1, max_length=128)


@router.post("/live/verify-xi")
def verified_live_xi(request: LiveXIRequest, _admin: None = Depends(require_admin)):
    result = verify_live_xi(
        sportmonks_fixture_id=request.sportmonks_fixture_id,
        cricketdata_match_id=request.cricketdata_match_id,
    )
    return {"fixture_id": request.fixture_id, **result}


@router.get("/live/providers")
def live_provider_readiness():
    from .providers.sportmonks_api import SportmonksCricketClient
    from .cricketdata_api import CricketDataClient
    return {
        "sportmonks": "CONFIGURED_NOT_PROBED" if SportmonksCricketClient().is_live else "NOT_CONFIGURED",
        "cricketdata": "CONFIGURED_NOT_PROBED" if CricketDataClient().is_live else "NOT_CONFIGURED",
        "cricbuzz": "REFERENCE_ONLY_NO_AUTOMATED_SCRAPING",
        "confirmed_xi": "REQUIRES_2_AGREEING_LIVE_FEEDS",
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


@router.get("/evaluation/model")
def out_of_time_model_evaluation():
    from .model_validation import audit_database
    return audit_database()


@router.get("/evaluation")
def evaluation():
    from .capabilities.c19_backtesting import CricketBacktesting
    return CricketBacktesting().execute()
