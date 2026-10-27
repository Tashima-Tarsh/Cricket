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
from datetime import datetime


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

    # --- Realistic Mock Fallback ---
    def _mock_livescores(self) -> List[Dict[str, Any]]:
        return [{
            "id": 984512,
            "round": "4th T20I",
            "type": "T20I",
            "status": "1st Innings",
            "note": "India won the toss and elected to bat",
            "starting_at": datetime.now().isoformat(),
            "localteam": {"id": 101, "name": "India", "code": "IND"},
            "visitorteam": {"id": 202, "name": "West Indies", "code": "WI"},
            "runs": [
                {"team_id": 101, "inning": 1, "score": 118, "wickets": 2, "overs": 11.4}
            ]
        }]

    def _mock_fixture(self, fixture_id: Any) -> Dict[str, Any]:
        return {
            "id": fixture_id or 984512,
            "localteam_id": 101,
            "visitorteam_id": 202,
            "status": "In Progress",
            "localteam": {"id": 101, "name": "India", "code": "IND"},
            "visitorteam": {"id": 202, "name": "West Indies", "code": "WI"},
            "venue": {
                "name": "Rajiv Gandhi International Stadium",
                "city": "Hyderabad",
                "capacity": 55000
            },
            "lineup": [
                {"id": 1, "fullname": "Sanju Samson", "team_id": 101, "position": {"name": "Wicketkeeper"}, "lineup": {"lineup": True}},
                {"id": 2, "fullname": "Abhishek Sharma", "team_id": 101, "position": {"name": "Batsman"}, "lineup": {"lineup": True}},
                {"id": 3, "fullname": "Ishan Kishan", "team_id": 101, "position": {"name": "Wicketkeeper"}, "lineup": {"lineup": True}},
                {"id": 4, "fullname": "Suryakumar Yadav", "team_id": 101, "position": {"name": "Batsman"}, "lineup": {"lineup": True}},
                {"id": 5, "fullname": "Tilak Varma", "team_id": 101, "position": {"name": "Batsman"}, "lineup": {"lineup": True}},
                {"id": 6, "fullname": "Hardik Pandya", "team_id": 101, "position": {"name": "Allrounder"}, "lineup": {"lineup": True}},
                {"id": 7, "fullname": "Axar Patel", "team_id": 101, "position": {"name": "Allrounder"}, "lineup": {"lineup": True}},
                {"id": 8, "fullname": "Kuldeep Yadav", "team_id": 101, "position": {"name": "Bowler"}, "lineup": {"lineup": True}},
                {"id": 9, "fullname": "Arshdeep Singh", "team_id": 101, "position": {"name": "Bowler"}, "lineup": {"lineup": True}},
                {"id": 10, "fullname": "Jasprit Bumrah", "team_id": 101, "position": {"name": "Bowler"}, "lineup": {"lineup": True}},
                {"id": 11, "fullname": "Mayank Yadav", "team_id": 101, "position": {"name": "Bowler"}, "lineup": {"lineup": True}},
                {"id": 12, "fullname": "Brandon King", "team_id": 202, "position": {"name": "Batsman"}, "lineup": {"lineup": True}},
                {"id": 13, "fullname": "Shai Hope", "team_id": 202, "position": {"name": "Wicketkeeper"}, "lineup": {"lineup": True}},
                {"id": 14, "fullname": "Nicholas Pooran", "team_id": 202, "position": {"name": "Wicketkeeper"}, "lineup": {"lineup": True}},
                {"id": 15, "fullname": "Rovman Powell", "team_id": 202, "position": {"name": "Batsman"}, "lineup": {"lineup": True}},
                {"id": 16, "fullname": "Shimron Hetmyer", "team_id": 202, "position": {"name": "Batsman"}, "lineup": {"lineup": True}},
                {"id": 17, "fullname": "Sherfane Rutherford", "team_id": 202, "position": {"name": "Batsman"}, "lineup": {"lineup": True}},
                {"id": 18, "fullname": "Romario Shepherd", "team_id": 202, "position": {"name": "Allrounder"}, "lineup": {"lineup": True}},
                {"id": 19, "fullname": "Roston Chase", "team_id": 202, "position": {"name": "Allrounder"}, "lineup": {"lineup": True}},
                {"id": 20, "fullname": "Akeal Hosein", "team_id": 202, "position": {"name": "Bowler"}, "lineup": {"lineup": True}},
                {"id": 21, "fullname": "Gudakesh Motie", "team_id": 202, "position": {"name": "Bowler"}, "lineup": {"lineup": True}},
                {"id": 22, "fullname": "Alzarri Joseph", "team_id": 202, "position": {"name": "Bowler"}, "lineup": {"lineup": True}}
            ],
            "batting": [
                {"player_id": 1, "score": 34, "balls": 18, "four_x": 4, "six_x": 2, "strike_rate": 188.89},
                {"player_id": 2, "score": 58, "balls": 29, "four_x": 6, "six_x": 3, "strike_rate": 200.0}
            ],
            "bowling": [
                {"player_id": 20, "overs": 3.0, "medians": 0, "runs": 22, "wickets": 0, "rate": 7.33},
                {"player_id": 22, "overs": 3.0, "medians": 0, "runs": 32, "wickets": 1, "rate": 10.67}
            ]
        }

