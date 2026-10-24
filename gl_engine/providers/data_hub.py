"""Unified Multi-Provider Cricket Data Hub.
Coordinates, harmonizes, and queries all 5 industry-standard cricket data providers:
1. Cricsheet (Free historical ball-by-ball data)
2. CricketData / CricAPI (Live scores, squads, match info, fantasy points)
3. Sportmonks Cricket API (Live matches, detailed scorecards, lineups, bowling/batting)
4. Roanuz Cricket API (Real-time live match intelligence & ball-by-ball telemetry)
5. Roanuz Fantasy API (Real-time official fantasy scoring & player credit values)
"""

from typing import Dict, Any, List, Optional
from ..cricsheet import CricsheetDatabase
from ..cricketdata_api import CricketDataClient
from .sportmonks_api import SportmonksCricketClient
from .roanuz_match_api import RoanuzCricketClient
from .roanuz_fantasy_api import RoanuzFantasyClient


PROVIDER_METADATA = {
    "cricsheet": {
        "name": "Cricsheet",
        "documentation": "https://cricsheet.org/downloads/",
        "endpoints": ["/downloads/ipl_json.zip", "/downloads/t20s_json.zip", "/downloads/it20s_json.zip"],
        "best_use": "Free historical ball-by-ball data & ML training",
        "cost": "Free (Open Source)"
    },
    "cricketdata": {
        "name": "CricketData / CricAPI",
        "documentation": "https://cricketdata.org/python-code-samples/",
        "endpoints": ["/v1/cricScore", "/v1/matches", "/v1/match_info", "/v1/match_squad", "/v1/match_scorecard"],
        "best_use": "Live scores, squads, match information, fantasy points",
        "cost": "Freemium"
    },
    "sportmonks": {
        "name": "Sportmonks Cricket API",
        "documentation": "https://docs.sportmonks.com/v2/cricket-api",
        "endpoints": ["/v2.0/livescores", "/v2.0/fixtures/{id}?include=lineup,bowling,batting,scoreboards", "/v2.0/venues/{id}"],
        "best_use": "Live matches, scorecards, lineups, bowling and batting",
        "cost": "Paid Tier"
    },
    "roanuz_match": {
        "name": "Roanuz Cricket API",
        "documentation": "https://sports.prod.roanuz.com/v5/docs/match-rest-api",
        "endpoints": ["/v5/cricket/{project_key}/match/{match_key}/", "/v5/cricket/{project_key}/match/{match_key}/ball-by-ball/"],
        "best_use": "Live match intelligence, real-time micro-events, and toss tracking",
        "cost": "Commercial Subscription"
    },
    "roanuz_fantasy": {
        "name": "Roanuz Fantasy API",
        "documentation": "https://sports.dev.roanuz.com/v5/docs/fantasy-match-points-rest-api",
        "endpoints": ["/v5/cricket/{project_key}/fantasy-match-points/{match_key}/", "/v5/cricket/{project_key}/fantasy-match-credits/{match_key}/"],
        "best_use": "Real-time fantasy scoring and player credit valuations",
        "cost": "Commercial Subscription"
    },
    "cricdata": {
        "name": "cricdata (ESPNcricinfo SDK)",
        "documentation": "https://github.com/arnavbonigala/cricdata",
        "endpoints": ["client.live_matches()", "client.match_scorecard()", "client.ground_stats()", "client.series_fixtures()"],
        "best_use": "Direct zero-key live scorecards, ball-by-ball, grounds & rankings",
        "cost": "Free & Open Source (curl-cffi direct)"
    }
}


class UnifiedCricketDataHub:
    def __init__(
        self,
        cricketdata_api_key: Optional[str] = None,
        sportmonks_api_token: Optional[str] = None,
        roanuz_project_key: Optional[str] = None,
        roanuz_api_key: Optional[str] = None,
        cricsheet_data_dir: Optional[str] = None
    ):
        self.cricsheet = CricsheetDatabase(cricsheet_data_dir)
        self.cricketdata = CricketDataClient(cricketdata_api_key)
        self.sportmonks = SportmonksCricketClient(sportmonks_api_token)
        self.roanuz_match = RoanuzCricketClient(roanuz_project_key, roanuz_api_key)
        self.roanuz_fantasy = RoanuzFantasyClient(roanuz_project_key, roanuz_api_key)

    def get_providers_status(self) -> Dict[str, Any]:
        """Configuration plus measured local readiness; external services are not probed here."""
        import duckdb
        import time
        import importlib.util
        from pathlib import Path
        path = Path(__file__).parent.parent.parent / "t20.duckdb"
        local = {"active": False, "status": "UNAVAILABLE", "mode": "UNAVAILABLE",
                 "authenticated": None, "reachable": False, "freshly_synchronised": None,
                 "latency_ms": None, "records_indexed": None, "matches_cached": None,
                 "last_sync": None, "info": PROVIDER_METADATA["cricsheet"]}
        if path.exists():
            started = time.perf_counter()
            try:
                with duckdb.connect(str(path), read_only=True) as con:
                    matches = con.execute("SELECT count(*) FROM matches").fetchone()[0]
                    deliveries = con.execute("SELECT count(*) FROM deliveries").fetchone()[0]
                local.update(active=True, status="LOCAL_ARCHIVE_READY", mode="DUCKDB_COLUMNAR",
                             reachable=True, matches_cached=matches, records_indexed=deliveries,
                             latency_ms=round((time.perf_counter()-started)*1000, 2))
            except Exception:
                pass
        result = {"cricsheet": local}
        for pid, client in (("cricketdata", self.cricketdata), ("sportmonks", self.sportmonks),
                            ("roanuz_match", self.roanuz_match), ("roanuz_fantasy", self.roanuz_fantasy)):
            configured = bool(client.is_live)
            result[pid] = {"active": False, "configured": configured,
                           "status": "CONFIGURED_UNVERIFIED" if configured else "UNAVAILABLE",
                           "mode": "NOT_PROBED", "authenticated": None, "reachable": None,
                           "freshly_synchronised": None, "latency_ms": None,
                           "records_indexed": None, "last_sync": None, "info": PROVIDER_METADATA[pid]}
        result["cricdata"] = {"active": False, "configured": importlib.util.find_spec("cricdata") is not None,
                              "status": "NOT_PROBED", "mode": "NOT_PROBED", "authenticated": None,
                              "reachable": None, "freshly_synchronised": None, "latency_ms": None,
                              "records_indexed": None, "last_sync": None, "info": PROVIDER_METADATA["cricdata"]}
        return result

    def fetch_unified_live_match(self, match_id: str = "ind-vs-wi-t20i-2026") -> Dict[str, Any]:
        """Gathers and cross-references live match data across all available providers."""
        # 1. Match info & toss from Roanuz Match API
        roanuz_intel = self.roanuz_match.get_match_intelligence(match_id)
        
        # 2. Lineups & bowling from Sportmonks
        sportmonks_lineup = self.sportmonks.get_lineup(match_id)
        
        # 3. Overall scorecard from CricketData
        cricdata_score = self.cricketdata.get_match_scorecard(match_id)
        
        # 4. Live real-time fantasy points from Roanuz Fantasy API
        fantasy_pts = self.roanuz_fantasy.get_fantasy_match_points(match_id)

        return {
            "match_id": match_id,
            "status": roanuz_intel.get("status"),
            "toss": roanuz_intel.get("toss"),
            "lineup_source": "Sportmonks API v2.0",
            "lineup": sportmonks_lineup,
            "scorecard_source": "CricketData / CricAPI",
            "scorecard": cricdata_score,
            "fantasy_scoring_source": "Roanuz Fantasy API v5",
            "live_fantasy_points": fantasy_pts
        }

