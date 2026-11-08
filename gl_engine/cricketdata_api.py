"""CricketData.org Live Cricket API Integration.
Connects to CricketData / CricAPI endpoints to fetch live matches, squads, toss updates, and scorecards.
Unavailable external data returns an explicit unavailable result; no example scores.
"""

import os
import requests
from typing import Dict, Any, List, Optional


CRICKETDATA_BASE_URL = "https://api.cricapi.com/v1"


class CricketDataClient:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("CRICKETDATA_API_KEY")
        self.base_url = CRICKETDATA_BASE_URL
        self.is_live = bool(self.api_key and self.api_key.strip() and self.api_key != "MOCK_KEY")

    def _get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Performs authenticated GET request to CricketData API."""
        if not self.is_live:
            return {"status": "offline_mode", "data": None}

        params = params or {}
        params["apikey"] = self.api_key

        try:
            url = f"{self.base_url}/{endpoint}"
            res = requests.get(url, params=params, timeout=10)
            res.raise_for_status()
            data = res.json()
            if data.get("status") == "success":
                return data
            else:
                print(f"[CricketData Warning] API response error: {data.get('reason', data)}")
                return {"status": "api_error", "data": None, "error": data.get("reason")}
        except Exception as e:
            print(f"[CricketData Exception] Failed connecting to API: {e}")
            return {"status": "connection_error", "data": None, "error": str(e)}

    def get_current_matches(self) -> List[Dict[str, Any]]:
        """Fetches currently live, upcoming, and recent matches."""
        if self.is_live:
            res = self._get("cricScore")
            if res.get("status") == "success" and "data" in res:
                return res["data"]
            res2 = self._get("matches", {"offset": 0})
            if res2.get("status") == "success" and "data" in res2:
                return res2["data"]

        return []  # Do not forge live matches in offline mode

    def get_match_info(self, match_id: str) -> Dict[str, Any]:
        """Retrieves match status, toss results, venue, and teams."""
        if self.is_live:
            res = self._get("match_info", {"id": match_id})
            if res.get("status") == "success" and "data" in res:
                return res["data"]

        return {"status": "UNAVAILABLE", "data": None}

    def get_match_squad(self, match_id: str) -> Dict[str, Any]:
        """Retrieves playing 11 and bench players for both teams."""
        if self.is_live:
            res = self._get("match_squad", {"id": match_id})
            if res.get("status") == "success" and "data" in res:
                return res["data"]

        return {"status": "UNAVAILABLE", "data": None}

    def get_match_scorecard(self, match_id: str) -> Dict[str, Any]:
        """Retrieves live ball-by-ball / innings scorecard."""
        if self.is_live:
            res = self._get("match_scorecard", {"id": match_id})
            if res.get("status") == "success" and "data" in res:
                return res["data"]

        return {"status": "UNAVAILABLE", "data": None}
