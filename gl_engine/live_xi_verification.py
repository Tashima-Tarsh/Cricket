"""Live XI corroboration: two independently licensed, explicit provider XIs.

A Cricbuzz scorecard URL can be retained as a human-readable reference but
Cricbuzz is not scraped: their Terms of Use prohibit automated extraction
without permission (https://www.cricbuzz.com/info/terms).
"""
from datetime import datetime, timezone
from typing import Any
from fastapi import HTTPException

from .providers.sportmonks_api import SportmonksCricketClient
from .cricketdata_api import CricketDataClient


def _norm(value: Any) -> str:
    return " ".join(str(value or "").casefold().split())


def _normalise_sportmonks(data: dict) -> dict:
    if data.get("status") != "LIVE_PROVIDER_RESPONSE":
        raise ValueError("Sportmonks data unavailable; demo sources are prohibited")
    home, away = _norm(data.get("home_team")), _norm(data.get("away_team"))
    if not home or not away or home == away:
        raise ValueError("Sportmonks fixture has unknown or identical teams")
    xi = data.get("playing_xi") or {}
    def names(players):
        if not isinstance(players, list) or len(players) != 11:
            raise ValueError("Sportmonks must explicitly confirm eleven per team")
        if any(p.get("lineup_status") is not True for p in players):
            raise ValueError("Sportmonks squad entries are not confirmed XI")
        found = [_norm(p.get("name")) for p in players]
        if any(not x or x == "unknown" for x in found) or len(set(found)) != 11:
            raise ValueError("Sportmonks XI contains duplicate or unknown players")
        return found
    return {home: names(xi.get("home")), away: names(xi.get("away"))}


def _normalise_cricketdata(data: dict) -> dict:
    # Providers often return SQUADS. Accept only a separately declared XI;
    # generic players lists cannot be promoted to match confirmation.
    if data.get("status") in ("UNAVAILABLE", "api_error", "connection_error"):
        raise ValueError("CricketData live XI unavailable")
    teams = data.get("teams")
    if not isinstance(teams, dict) or len(teams) != 2:
        raise ValueError("CricketData match_squad has no explicit team-separated XI")
    output = {}
    for name, record in teams.items():
        key = _norm(name)
        if not key or not isinstance(record, dict) or "playing_xi" not in record:
            raise ValueError("CricketData returned squad, not playing XI")
        raw = record["playing_xi"]
        if not isinstance(raw, list) or len(raw) != 11:
            raise ValueError("CricketData XI must contain eleven per team")
        names = [_norm(p.get("name")) for p in raw if isinstance(p, dict)]
        if len(names) != 11 or any(not n for n in names) or len(set(names)) != 11:
            raise ValueError("CricketData XI identities incomplete")
        output[key] = names
    return output


def compare_independent_xis(sportmonks: dict, cricketdata: dict) -> dict:
    a = _normalise_sportmonks(sportmonks)
    b = _normalise_cricketdata(cricketdata)
    # Provider team-name aliases MUST be mapped explicitly by licensed
    # provider fixture metadata. For now require exact team names.
    if set(a) != set(b):
        raise ValueError("Provider team identities differ; alias mapping not verified")
    for team in a:
        if set(a[team]) != set(b[team]):
            raise ValueError(f"Playing XI mismatch between independent feeds for {team}")
    all_players = [p for names in a.values() for p in names]
    if len(all_players) != 22 or len(set(all_players)) != 22:
        raise ValueError("Verified XI has duplicate players across teams")
    return {
        "status": "CROSS_PROVIDER_CORROBORATED",
        "teams": [{"name": name, "players": sorted(a[name])} for name in sorted(a)],
        "count": 22,
        "sources": ["sportmonks_live", "cricketdata_live"],
        "checked_at_utc": datetime.now(timezone.utc).isoformat(),
        "observation_type": "fresh API responses; source publication time not supplied",
        "caveat": "Providers agree on a named XI; fantasy credits and lock cutoff still require fixture checks",
    }


def verify_live_xi(*, sportmonks_fixture_id: str, cricketdata_match_id: str) -> dict:
    sm = SportmonksCricketClient()
    cd = CricketDataClient()
    if not sm.is_live or not cd.is_live:
        raise HTTPException(503, "Two licensed provider credentials required; Cricbuzz scraping is not an alternative")
    try:
        a = sm.get_lineup(sportmonks_fixture_id)
        b = cd.get_match_squad(cricketdata_match_id)
        result = compare_independent_xis(a, b)
        result["provider_fixture_ids"] = {
            "sportmonks": str(sportmonks_fixture_id),
            "cricketdata": str(cricketdata_match_id),
        }
        return result
    except (ValueError, KeyError, TypeError) as exc:
        raise HTTPException(409, str(exc)) from exc
