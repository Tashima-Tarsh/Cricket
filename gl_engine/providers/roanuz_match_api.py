"""Roanuz Cricket Match API v5 Client.
Documentation: https://sports.prod.roanuz.com/v5/docs/match-rest-api
Endpoints:
- GET /v5/cricket/{project_key}/matches/
- GET /v5/cricket/{project_key}/match/{match_key}/
- GET /v5/cricket/{project_key}/match/{match_key}/ball-by-ball/
- GET /v5/cricket/{project_key}/tournament/{tournament_key}/fixtures/
Best Use: Real-time live match intelligence, micro ball-by-ball event telemetry, toss decisions, and venue status.
"""

import os
import requests
from typing import Dict, Any, List, Optional
from datetime import datetime


ROANUZ_BASE_URL = "https://api.sports.roanuz.com/v5/cricket"


class RoanuzCricketClient:
    def __init__(self, project_key: Optional[str] = None, api_key: Optional[str] = None):
        self.project_key = project_key or os.getenv("ROANUZ_PROJECT_KEY", "cricket_app")
        self.api_key = api_key or os.getenv("ROANUZ_API_KEY")
        self.base_url = f"{ROANUZ_BASE_URL}/{self.project_key}"
        self.is_live = bool(self.api_key and self.api_key.strip() and self.api_key != "MOCK_KEY")

    def _headers(self) -> Dict[str, str]:
        return {
            "rs-token": self.api_key or "",
            "Content-Type": "application/json"
        }

    def _get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Sends authenticated request to Roanuz Cricket API v5."""
        if not self.is_live:
            return {"status": "offline_mode", "data": None}

        try:
            url = f"{self.base_url}/{endpoint.lstrip('/')}"
            res = requests.get(url, headers=self._headers(), params=params, timeout=12)
            res.raise_for_status()
            data = res.json()
            if data.get("status_code") == 200:
                return data.get("data", {})
            return data
        except Exception as e:
            print(f"[Roanuz Match API Exception] {endpoint}: {e}")
            return {"status": "error", "error": str(e), "data": None}

    def get_matches(self) -> List[Dict[str, Any]]:
        """Retrieves list of tournament and live matches."""
        if self.is_live:
            res = self._get("matches/")
            if "matches" in res:
                return res["matches"]
        return self._mock_matches()

    def get_match_intelligence(self, match_key: str) -> Dict[str, Any]:
        """Retrieves real-time match state, toss, venue, and current over status."""
        if self.is_live:
            res = self._get(f"match/{match_key}/")
            if res:
                return res
        return self._mock_match_intelligence(match_key)

    def get_ball_by_ball(self, match_key: str, over_key: Optional[str] = None) -> Dict[str, Any]:
        """Retrieves real-time ball-by-ball micro telemetry."""
        if self.is_live:
            endpoint = f"match/{match_key}/ball-by-ball/"
            if over_key:
                endpoint += f"{over_key}/"
            res = self._get(endpoint)
            if res:
                return res
        return self._mock_ball_by_ball(match_key)

    # --- Realistic Mock Fallback ---
    def _mock_matches(self) -> List[Dict[str, Any]]:
        return [{
            "key": "ind_wi_t20_2026_m4",
            "name": "India vs West Indies",
            "short_name": "IND vs WI",
            "subtitle": "4th T20I",
            "format": "t20",
            "status": "started",
            "play_status": "in_play",
            "start_at": datetime.now().isoformat(),
            "teams": {
                "a": {"key": "ind", "name": "India", "code": "IND"},
                "b": {"key": "wi", "name": "West Indies", "code": "WI"}
            },
            "venue": {"name": "Rajiv Gandhi International Stadium", "city": "Hyderabad"}
        }]

    def _mock_match_intelligence(self, match_key: str) -> Dict[str, Any]:
        return {
            "key": match_key,
            "status": "started",
            "play_status": "in_play",
            "toss": {
                "won": "ind",
                "decision": "bat",
                "str": "India won the toss and elected to bat first"
            },
            "venue": {
                "name": "Rajiv Gandhi International Stadium",
                "city": "Hyderabad",
                "pitch": "Batting paradise with true carry, pacers dominant in early overs"
            },
            "play": {
                "live": {
                    "innings": "a_1",
                    "overs": [11, 4],
                    "score": {"runs": 118, "wickets": 2, "balls": 70},
                    "run_rate": 10.11,
                    "striker": {"name": "Abhishek Sharma", "runs": 58, "balls": 29},
                    "non_striker": {"name": "Tilak Varma", "runs": 8, "balls": 6},
                    "bowler": {"name": "Romario Shepherd", "overs": [2, 4], "runs": 36, "wickets": 0}
                }
            }
        }

    def _mock_ball_by_ball(self, match_key: str) -> Dict[str, Any]:
        return {
            "match_key": match_key,
            "current_over": 12,
            "recent_balls": [
                {"ball": "11.1", "runs": 1, "bowler": "Romario Shepherd", "batsman": "Abhishek Sharma"},
                {"ball": "11.2", "runs": 4, "bowler": "Romario Shepherd", "batsman": "Tilak Varma", "boundary": True},
                {"ball": "11.3", "runs": 1, "bowler": "Romario Shepherd", "batsman": "Tilak Varma"},
                {"ball": "11.4", "runs": 6, "bowler": "Romario Shepherd", "batsman": "Abhishek Sharma", "boundary": True}
            ]
        }

