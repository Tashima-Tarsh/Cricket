"""Sportmonks Cricket API v2.0 Client.
Documentation: https://docs.sportmonks.com/v2/cricket-api
Endpoints:
- GET /livescores
- GET /fixtures
- GET /fixtures/{id}?include=lineup,bowling,batting,scoreboards,runs,balls
- GET /venues/{id}
- GET /teams/{id}
- GET /players/{id}
Best Use: Live matches, comprehensive scorecards, playing XI lineups, bowling & batting breakdowns.
"""

import os
import requests
from typing import Dict, Any, List, Optional


SPORTMONKS_BASE_URL = "https://cricket.sportmonks.com/api/v2.0"


class SportmonksCricketClient:
    def __init__(self, api_token: Optional[str] = None):
        self.api_token = api_token or os.getenv("SPORTMONKS_API_TOKEN")
        self.base_url = SPORTMONKS_BASE_URL
        self.is_live = bool(self.api_token and self.api_token.strip() and self.api_token != "MOCK_TOKEN")

    def _get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Sends authenticated request to Sportmonks Cricket API v2.0."""
        if not self.is_live:
            return {"status": "offline_mode", "data": None}

        params = params or {}
        params["api_token"] = self.api_token

        try:
            url = f"{self.base_url}/{endpoint.lstrip('/')}"
            res = requests.get(url, params=params, timeout=12)
            res.raise_for_status()
            return res.json()
        except Exception as e:
            print(f"[Sportmonks API Exception] {endpoint}: {e}")
            return {"status": "error", "error": str(e), "data": None}

    def get_livescores(self) -> List[Dict[str, Any]]:
        """Retrieves currently live matches."""
        if self.is_live:
            res = self._get("livescores", {"include": "localteam,visitorteam,runs"})
            if "data" in res and res["data"] is not None:
                return res["data"]
        return []  # Never expose illustrative fixtures as live

    def get_fixture_details(self, fixture_id: int or str, include: str = "lineup,bowling,batting,scoreboards,venue") -> Dict[str, Any]:
        """Retrieves full fixture details with batting, bowling, lineup, and venue."""
        if self.is_live:
            res = self._get(f"fixtures/{fixture_id}", {"include": include})
            if "data" in res and res["data"] is not None:
                return res["data"]
        return {}  # No licensed connection / remote result

    def get_lineup(self, fixture_id: int or str) -> Dict[str, Any]:
        """Extracts confirmed Playing 11 and bench players from fixture."""
        fixture = self.get_fixture_details(fixture_id, include="lineup,localteam,visitorteam")
        lineup_raw = fixture.get("lineup", [])
        
        home_team_id = fixture.get("localteam_id")
        away_team_id = fixture.get("visitorteam_id")

        playing_xi = {"home": [], "away": []}
        bench = {"home": [], "away": []}

        if not isinstance(lineup_raw, list) or not home_team_id or not away_team_id:
            return {"status": "UNVERIFIED", "fixture_id": fixture_id,
                    "playing_xi": {"home": [], "away": []},
                    "home_team": None, "away_team": None}
        for p in lineup_raw:
            if p.get("team_id") not in (home_team_id, away_team_id):
                continue
            p_data = {
                "player_id": p.get("id"),
                "name": p.get("fullname", p.get("name", "Unknown")),
                "role": self._map_role(p.get("position", {}).get("name", "")),
                "lineup_status": p.get("lineup", {}).get("lineup", False)
            }
            is_home = (p.get("team_id") == home_team_id)
            target = playing_xi if p_data["lineup_status"] else bench
            if is_home:
                target["home"].append(p_data)
            else:
                target["away"].append(p_data)

        return {
            "status": "LIVE_PROVIDER_RESPONSE",
            "fixture_id": fixture_id,
            "home_team": fixture.get("localteam", {}).get("name"),
            "away_team": fixture.get("visitorteam", {}).get("name"),
            "playing_xi": playing_xi,
            "bench": bench
        }

    def get_detailed_scorecard(self, fixture_id: int or str) -> Dict[str, Any]:
        """Extracts detailed batting cards, bowling figures, and fall of wickets."""
        fixture = self.get_fixture_details(fixture_id, include="batting,bowling,scoreboards")
        return {
            "fixture_id": fixture_id,
            "status": fixture.get("status", "Finished"),
            "batting": fixture.get("batting", []),
            "bowling": fixture.get("bowling", []),
            "scoreboards": fixture.get("scoreboards", [])
        }

    def _map_role(self, role_str: str) -> str:
        r = role_str.lower()
        if "wicket" in r or "keeper" in r:
            return "WK"
        elif "allrounder" in r or "all-rounder" in r:
            return "AR"
        elif "bowler" in r:
            return "BOWL"
        return "BAT"
