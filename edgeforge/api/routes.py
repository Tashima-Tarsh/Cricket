"""
EdgeForge – Clean FastAPI routes.
Replaces hardcoded portal endpoints. Zero fabricated players.
"""
from __future__ import annotations
from typing import List, Optional, Dict, Any
from datetime import datetime, date
from fastapi import APIRouter, HTTPException, Query, Body, Depends
from pydantic import BaseModel, Field

from edgeforge.models.schemas import (
    Player, Fixture, DataProvenance, Role, Archetype, Lineup
)
from edgeforge.ingest.roster import RosterResolver, RosterNotFoundError
from edgeforge.ingest.store import InMemoryFixtureStore, InMemoryPlayerStore
from edgeforge.score.dream11 import Dream11Scorer
from edgeforge.optimize.rank_optimizer import RankOptimizer, OptimizerConfig
from edgeforge.model.simulator import MatchSimulator
from gl_engine.admin_auth import require_admin

router = APIRouter(prefix="/edge", tags=["edgeforge"])

fixture_store = InMemoryFixtureStore()
player_store = InMemoryPlayerStore()
resolver = RosterResolver(fixture_store, player_store)
scorer = Dream11Scorer()


class ScoreRequest(BaseModel):
    runs: int = 0
    balls_faced: int = 0
    fours: int = 0
    sixes: int = 0
    wickets: int = 0
    overs_bowled: float = 0.0
    runs_conceded: int = 0
    maidens: int = 0
    dots: int = 0
    catches: int = 0
    stumpings: int = 0
    run_outs_direct: int = 0
    is_playing: bool = True
    match_format: str = "T20"


class OptimizeRequest(BaseModel):
    fixture_id: str
    archetype: Optional[str] = None
    n_portfolios: int = Field(default=10, ge=1, le=50)
    n_sims: int = Field(default=3000, ge=500, le=20000)
    min_unspent: float = 13.0
    max_unspent: float = 19.0
    min_differentials: int = 2


class PlayerIn(BaseModel):
    id: str
    name: str
    team: str
    role: str
    credits: float
    batting_hand: str = "RHB"
    bowling_style: Optional[str] = None
    is_confirmed_xi: bool = False
    projected_ownership: Optional[float] = None
    projected_points: Optional[float] = None


class FixtureIn(BaseModel):
    id: str
    title: str
    match_date: date
    venue: str
    format: str = "T20"
    team_a: str
    team_b: str
    players: List[PlayerIn]
 

@router.get("/health")
def health():
    return {
        "status": "ok",
        "service": "edgeforge",
        "version": "0.1.0",
        "timestamp": datetime.utcnow().isoformat(),
        "fixtures_loaded": len(fixture_store.list_ids()),
    }


@router.get("/roster/{fixture_id}")
def get_roster(fixture_id: str):
    try:
        fixture, players = resolver.get_roster(fixture_id)
    except RosterNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

    return {
        "status": "success",
        "fixture": {
            "id": fixture.id,
            "title": fixture.title,
            "team_a": fixture.team_a,
            "team_b": fixture.team_b,
            "format": fixture.format,
            "status": fixture.status,
            "archetype": fixture.archetype.value if fixture.archetype else None,
            "provenance": fixture.provenance.model_dump(),
        },
        "roster": [
            {
                "id": p.id,
                "name": p.name,
                "team": p.team,
                "role": p.role.value,
                "credits": p.credits,
                "is_confirmed_xi": p.is_confirmed_xi,
                "projected_ownership": p.projected_ownership,
                "ownership_available": p.ownership_available,
                "projected_points": p.projected_points,
                "provenance": p.provenance.model_dump(),
            }
            for p in players
        ],
        "total_players": len(players),
    }


@router.post("/score")
def score_performance(req: ScoreRequest):
    result = scorer.calculate(
        runs=req.runs,
        balls_faced=req.balls_faced,
        fours=req.fours,
        sixes=req.sixes,
        wickets=req.wickets,
        overs_bowled=req.overs_bowled,
        runs_conceded=req.runs_conceded,
        maidens=req.maidens,
        dots=req.dots,
        catches=req.catches,
        stumpings=req.stumpings,
        run_outs_direct=req.run_outs_direct,
        is_playing=req.is_playing,
        match_format=req.match_format.upper() if req.match_format else "T20",
    )
    return {"status": "success", **result.to_dict()}


@router.post("/optimize")
def optimize_portfolio(req: OptimizeRequest):
    try:
        fixture, players = resolver.get_roster(req.fixture_id)
    except RosterNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

    arch = Archetype.PARITY
    if req.archetype:
        try:
            arch = Archetype(req.archetype.upper())
        except ValueError:
            pass
    elif fixture.archetype:
        arch = fixture.archetype

    cfg = OptimizerConfig(
        n_portfolios=req.n_portfolios,
        n_sims=req.n_sims,
        min_unspent=req.min_unspent,
        max_unspent=req.max_unspent,
        min_differentials=req.min_differentials,
    )

    try:
        optimizer = RankOptimizer(config=cfg)
        result = optimizer.optimize(players, archetype=arch, fixture_id=req.fixture_id)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Optimizer failed: {exc}")

    return {
        "status": "success",
        "fixture_id": req.fixture_id,
        "archetype": arch.value,
        "simulation_valid": result.simulation_valid,
        "n_lineups": len(result.lineups),
        "lineups": result.lineups,
        "notes": result.notes,
    }


@router.post("/fixtures")
def load_fixture(body: FixtureIn, _authorized: None = Depends(require_admin)):
    prov = DataProvenance(
        source="admin_fixture",
        confidence=0.95,
        sample_size=len(body.players),
        last_updated=datetime.utcnow(),
        notes="Loaded via /edge/fixtures",
    )

    fixture = Fixture(
        id=body.id,
        title=body.title,
        match_date=body.match_date,
        venue=body.venue,
        format=body.format.upper() if body.format else "T20",
        team_a=body.team_a,
        team_b=body.team_b,
        status="SCHEDULED",
        provenance=prov,
    )
    fixture_store.put(fixture)

    players = []
    for p in body.players:
        try:
            role = Role(p.role.upper())
        except ValueError:
            role = Role.BAT
        players.append(
            Player(
                id=p.id,
                name=p.name,
                team=p.team,
                role=role,
                credits=p.credits,
                batting_hand=p.batting_hand if p.batting_hand in ("RHB", "LHB") else "RHB",
                bowling_style=p.bowling_style,
                is_confirmed_xi=p.is_confirmed_xi,
                projected_ownership=p.projected_ownership,
                ownership_available=p.projected_ownership is not None,
                projected_points=p.projected_points,
                provenance=prov,
            )
        )
    player_store.put_players(body.id, players)

    return {
        "status": "success",
        "fixture_id": body.id,
        "players_loaded": len(players),
        "message": "Fixture and roster stored. Ready for /edge/roster and /edge/optimize.",
    }


@router.get("/fixtures")
def list_fixtures():
    ids = fixture_store.list_ids()
    return {"status": "success", "fixture_ids": ids, "count": len(ids)}
