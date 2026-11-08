"""
daily_match_sync.py
Automated Daily Match Sync, Live Commentary Ingest, and AI Intelligence Pipeline.

Features:
1. Daily Fixture Discovery: Pulls all current, live, upcoming, and completed matches.
2. Real-Time Telemetry & Commentary Ingest: Scrapes live ball-by-ball, pitch reports, and toss quotes.
3. Automated DuckDB Warehouse Sync: Persists match results and deliveries into local DuckDB.
4. AI Archetype & Strategy Recommender: Runs the 4 Universal Match Archetypes on any newly discovered match.
"""

from typing import List, Dict, Any, Optional
import urllib.request
import json
import re
import time
from datetime import datetime, timezone
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)
CACHE_FILE = DATA_DIR / "daily_sync_cache.json"

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"

class DailyMatchSyncEngine:
    def __init__(self):
        self._cached_matches: List[Dict[str, Any]] = []
        self._last_sync_time: float = 0.0

    def discover_daily_matches(self, force_refresh: bool = False) -> List[Dict[str, Any]]:
        """Pulls comprehensive list of matches: Live, Upcoming, and Completed today."""
        now = time.time()
        if not force_refresh and self._cached_matches and (now - self._last_sync_time < 300.0):
            return self._cached_matches

        matches = []
        
        # 1. Try Cricdata SDK / ESPNcricinfo
        try:
            from .live_feed import _fetch_from_cricdata_sdk
            sdk_matches = _fetch_from_cricdata_sdk()
            if sdk_matches:
                matches.extend(sdk_matches)
        except Exception as e:
            pass

        # Third-party scraping disabled. ESPN references do not establish a verified XI.

        # 3. Enrich with AI Archetype Classification
        for m in matches:
            m["ai_archetype"] = self._classify_archetype(m)
            m["recommended_strategy"] = self._get_archetype_strategy(m["ai_archetype"])

        self._cached_matches = matches
        self._last_sync_time = now
        
        # Save cache
        try:
            with open(CACHE_FILE, "w", encoding="utf-8") as f:
                json.dump({"timestamp": now, "count": len(matches), "matches": matches}, f, indent=2)
        except Exception:
            pass

        return matches

    def _fetch_cricbuzz_fixtures(self) -> List[Dict[str, Any]]:
        """Removed unlicensed HTML scraping and URL-based verified-live guesses."""
        return []

    def fetch_live_commentary_and_scorecard(self, match_id: str) -> Dict[str, Any]:
        """Only licensed adapters may provide verified ball-by-ball observations."""
        return {"status": "UNAVAILABLE", "match_id": match_id,
                "reason": "Licensed scorecard/commentary provider not configured",
                "pitch_report": None, "toss": None, "scorecard": None, "key_events": []}

    def _classify_archetype(self, match: Dict[str, Any]) -> str:
        """Classifies match into one of the 4 Universal Match Archetypes."""
        title = (match.get("title") or "").lower()
        fmt = (match.get("format") or "").upper()
        cat = (match.get("category") or "").upper()
        
        # Mismatch
        if any(w in title for w in ["zimbabwe", "scotland", "namibia", "uae", "nepal", "usa"]):
            return "ASYMMETRIC_MISMATCH"
        
        # Venue checks
        venue = (match.get("venue") or "").lower()
        if any(w in venue for w in ["chinnaswamy", "wankhede", "raipur", "hyderabad", "rawalpindi"]):
            return "ROAD_HIGHWAY"
        elif any(w in venue for w in ["chepauk", "chennai", "ekana", "lucknow", "mirpur", "dhaka"]):
            return "SPIN_CHOKE_MINEFIELD"

        return "HIGH_STAKES_PARITY"

    def _get_archetype_strategy(self, archetype: str) -> Dict[str, str]:
        """Returns the quantitative Grand League rules for this archetype."""
        if archetype == "ROAD_HIGHWAY":
            return {
                "archetype": "ROAD_HIGHWAY (Par 195-230)",
                "batting_rule": "Top-order stack (Openers + No. 3). They face 70% of deliveries.",
                "bowling_rule": "Fade powerplay specialist bowlers. Target 2nd-innings death-overs wickets.",
                "captaincy": "Top-3 Batter or Death Finisher (70+ run milestone bonus).",
                "credit_shield": "Leave 13.5 to 17.0 credits unspent."
            }
        elif archetype == "SPIN_CHOKE_MINEFIELD":
            return {
                "archetype": "SPIN_CHOKE_MINEFIELD (Par 125-145)",
                "batting_rule": "Fade boundary-reliant openers. Pick technical spin-anchors only.",
                "bowling_rule": "Stack 5 to 6 Bowlers/All-Rounders (bowlers outscore batters 2:1).",
                "captaincy": "Mystery Spinner or Change-of-Pace Seamer (3 wkts + low econ).",
                "credit_shield": "Leave 14.0 to 18.0 credits unspent."
            }
        elif archetype == "ASYMMETRIC_MISMATCH":
            return {
                "archetype": "ASYMMETRIC_MISMATCH (Powerhouse vs Underdog)",
                "batting_rule": "Watch for dead-rubber captaincy demotions; lock middle order No. 4/5.",
                "bowling_rule": "Favorite team strike pace/spin choke against forced aggressive chase.",
                "captaincy": "Middle-order powerhouse (C) + Underdog 2-Way All-Rounder (VC).",
                "credit_shield": "Leave 15.0 to 19.0 credits unspent."
            }
        else:
            return {
                "archetype": "HIGH_STAKES_PARITY (Even Derby / Knockout)",
                "batting_rule": "Balanced 6-5 split. Target left-arm pace / off-spin micro matchups.",
                "bowling_rule": "Balanced powerplay + death overs coverage.",
                "captaincy": "Dual-threat all-rounder (bats top 5 + bowls 3-4 overs).",
                "credit_shield": "Leave 12.0 to 15.5 credits unspent."
            }

_DAILY_SYNC_INSTANCE: Optional[DailyMatchSyncEngine] = None

def get_daily_match_sync_engine() -> DailyMatchSyncEngine:
    global _DAILY_SYNC_INSTANCE
    if _DAILY_SYNC_INSTANCE is None:
        _DAILY_SYNC_INSTANCE = DailyMatchSyncEngine()
    return _DAILY_SYNC_INSTANCE

if __name__ == "__main__":
    engine = get_daily_match_sync_engine()
    print("Discovering daily fixtures...")
    fixtures = engine.discover_daily_matches(force_refresh=True)
    print(f"Total Fixtures Synced: {len(fixtures)}\n")
    for f in fixtures[:8]:
        print(f"[{f['state']}] {f['title']} ({f['format']})")
        print(f"   Archetype: {f['ai_archetype']}")
        print(f"   Strategy: {f['recommended_strategy']['captaincy']}\n")

