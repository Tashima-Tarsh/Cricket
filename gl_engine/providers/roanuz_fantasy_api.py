"""Roanuz Fantasy Cricket API v5 Client.
Documentation: https://sports.dev.roanuz.com/v5/docs/fantasy-match-points-rest-api
Endpoints:
- GET /v5/cricket/{project_key}/fantasy-match-points/{match_key}/
- GET /v5/cricket/{project_key}/fantasy-match-credits/{match_key}/
Best Use: Real-time fantasy scoring calculation, dynamic fantasy leaderboards, and official credit valuations.
"""

import os
import requests
from typing import Dict, Any, List, Optional


ROANUZ_BASE_URL = "https://api.sports.roanuz.com/v5/cricket"


class RoanuzFantasyClient:
    def __init__(self, project_key: Optional[str] = None, api_key: Optional[str] = None):
        self.project_key = project_key or os.getenv("ROANUZ_PROJECT_KEY", "fantasy_app")
        self.api_key = api_key or os.getenv("ROANUZ_API_KEY")
        self.base_url = f"{ROANUZ_BASE_URL}/{self.project_key}"
        self.is_live = bool(self.api_key and self.api_key.strip() and self.api_key != "MOCK_KEY")

    def _headers(self) -> Dict[str, str]:
        return {
            "rs-token": self.api_key or "",
            "Content-Type": "application/json"
        }

    def _get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Sends authenticated request to Roanuz Fantasy API."""
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
            print(f"[Roanuz Fantasy API Exception] {endpoint}: {e}")
            return {"status": "error", "error": str(e), "data": None}

    def get_fantasy_match_points(self, match_key: str, rule_set: str = "standard_t20") -> Dict[str, Any]:
        """Retrieves real-time official fantasy points computed for every player in the match."""
        if self.is_live:
            res = self._get(f"fantasy-match-points/{match_key}/", {"rule_set": rule_set})
            if res:
                return res
        return self._mock_fantasy_match_points(match_key)

    def get_fantasy_match_credits(self, match_key: str) -> Dict[str, Any]:
        """Retrieves player credit pricing and official fantasy role assignments."""
        if self.is_live:
            res = self._get(f"fantasy-match-credits/{match_key}/")
            if res:
                return res
        return self._mock_fantasy_match_credits(match_key)

    # --- Realistic Mock Fallback ---
    def _mock_fantasy_match_points(self, match_key: str) -> Dict[str, Any]:
        return {
            "match_key": match_key,
            "status": "in_play",
            "rule_set": "dream11_standard_t20",
            "points": {
                "ind_abhishek": {
                    "player_name": "Abhishek Sharma",
                    "total_points": 88.0,
                    "breakdown": {
                        "starting_xi": 4.0,
                        "runs": 58.0,
                        "fours": 6.0,
                        "sixes": 6.0,
                        "half_century_bonus": 8.0,
                        "strike_rate_bonus": 6.0
                    }
                },
                "ind_samson": {
                    "player_name": "Sanju Samson",
                    "total_points": 50.0,
                    "breakdown": {
                        "starting_xi": 4.0,
                        "runs": 34.0,
                        "fours": 4.0,
                        "sixes": 4.0,
                        "thirty_runs_bonus": 4.0
                    }
                },
                "wi_joseph": {
                    "player_name": "Alzarri Joseph",
                    "total_points": 29.0,
                    "breakdown": {
                        "starting_xi": 4.0,
                        "wickets": 25.0
                    }
                },
                "wi_motie": {
                    "player_name": "Gudakesh Motie",
                    "total_points": 29.0,
                    "breakdown": {
                        "starting_xi": 4.0,
                        "wickets": 25.0
                    }
                }
            }
        }

    def _mock_fantasy_match_credits(self, match_key: str) -> Dict[str, Any]:
        return {
            "match_key": match_key,
            "credits": {
                "ind_samson": {"name": "Sanju Samson", "role": "WK", "credits": 8.5},
                "ind_abhishek": {"name": "Abhishek Sharma", "role": "BAT", "credits": 9.0},
                "ind_surya": {"name": "Suryakumar Yadav", "role": "BAT", "credits": 9.0},
                "ind_tilak": {"name": "Tilak Varma", "role": "BAT", "credits": 8.5},
                "ind_axar": {"name": "Axar Patel", "role": "AR", "credits": 9.0},
                "ind_arshdeep": {"name": "Arshdeep Singh", "role": "BOWL", "credits": 9.0},
                "ind_mayank": {"name": "Mayank Yadav", "role": "BOWL", "credits": 8.0},
                "wi_hope": {"name": "Shai Hope", "role": "WK", "credits": 9.0},
                "wi_pooran": {"name": "Nicholas Pooran", "role": "WK", "credits": 9.0},
                "wi_powell": {"name": "Rovman Powell", "role": "BAT", "credits": 8.5},
                "wi_shepherd": {"name": "Romario Shepherd", "role": "AR", "credits": 8.5},
                "wi_joseph": {"name": "Alzarri Joseph", "role": "BOWL", "credits": 8.5}
            }
        }

