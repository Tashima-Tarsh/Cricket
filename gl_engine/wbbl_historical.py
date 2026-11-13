"""Source-bound WBBL ball-by-ball historical features, no external API.

All numbers derive from observed Cricsheet deliveries. The local Cricsheet
warehouse does not store wide/no-ball flags, so delivery counts are explicitly
not legal-ball counts and no fantasy points, economy or bowling overs are inferred.
"""
from __future__ import annotations

from datetime import date
from pathlib import Path
import os
from typing import Optional
import duckdb


DB_DEFAULT = Path(os.getenv("CRICKET_WBBL_DB", str(Path(__file__).resolve().parents[1] / "data" / "cricsheet_wt20.duckdb")))
TEAMS = (
    "sydney sixers", "sydney thunder", "melbourne stars",
    "melbourne renegades", "brisbane heat", "perth scorchers",
    "adelaide strikers", "hobart hurricanes",
)
_TEAM_FILTER = """lower(trim(regexp_replace(m.team1, '( Women| Women''s)$', '', 'i'))) IN
    (SELECT unnest(?::VARCHAR[]))
    AND lower(trim(regexp_replace(m.team2, '( Women| Women''s)$', '', 'i'))) IN
    (SELECT unnest(?::VARCHAR[]))"""


def _validate(name: str, before: Optional[date]):
    if not isinstance(name, str) or not name.strip() or len(name) > 150:
        raise ValueError("An exact player name is required")
    if before is not None and not isinstance(before, date):
        raise ValueError("before must be an ISO date")


class WBBLHistorical:
    def __init__(self, db_path: str | Path | None = None):
        self.db_path = Path(db_path) if db_path else DB_DEFAULT

    def _query(self, sql: str, params: list):
        if not self.db_path.is_file():
            return None
        with duckdb.connect(str(self.db_path), read_only=True) as db:
            return db.execute(sql, params).fetchone()

    def player(self, name: str, before: date | None = None) -> dict:
        _validate(name, before)
        sql = f"""
            SELECT COUNT(DISTINCT d.match_id) AS matches,
                   COUNT(*) AS recorded_deliveries,
                   SUM(d.runs_batter) AS batting_runs,
                   SUM(CASE WHEN d.runs_batter=4 THEN 1 ELSE 0 END) AS fours,
                   SUM(CASE WHEN d.runs_batter=6 THEN 1 ELSE 0 END) AS sixes,
                   SUM(CASE WHEN d.is_wicket AND lower(trim(d.player_dismissed))=lower(trim(?))
                            THEN 1 ELSE 0 END) AS dismissals
            FROM deliveries d
            JOIN matches m ON d.match_id = m.match_id
            WHERE {_TEAM_FILTER}
                AND lower(trim(d.batter))=lower(trim(?))
                AND (?::DATE IS NULL OR CAST(m.match_date AS DATE) < ?::DATE)
        """
        params = [name, list(TEAMS), list(TEAMS), name,
                  str(before) if before else None, str(before) if before else None]
        row = self._query(sql, params)
        if row is None:
            return {"status": "DATA_UNAVAILABLE", "player": name}
        matches, balls, runs, fours, sixes, outs = row
        if not balls:
            return {"status": "NO_WBBL_HISTORY", "player": name,
                    "sample_matches": 0, "sample_recorded_deliveries": 0}
        return {
            "status": "OBSERVED_CRICSHEET_PARTIAL", "player": name,
            "sample_matches": int(matches), "sample_recorded_deliveries": int(balls),
            "batting_runs": int(runs or 0), "fours": int(fours or 0),
            "sixes": int(sixes or 0), "dismissals": int(outs or 0),
            "runs_per_recorded_delivery": round(float(runs or 0) / balls, 3),
            "cutoff_before": str(before) if before else None,
            "provenance": "LOCAL_WBBL_CRICSHEET_ONLY",
            "caveat": "Counts are recorded deliveries, including extras; not legal balls or fantasy points.",
        }

    def matchup(self, batter: str, bowler: str, before: date | None = None) -> dict:
        _validate(batter, before)
        _validate(bowler, before)
        sql = f"""
            SELECT COUNT(*) AS recorded_deliveries,
                   SUM(d.runs_batter) AS runs,
                   SUM(CASE WHEN d.is_wicket AND lower(trim(d.player_dismissed))=lower(trim(?))
                            THEN 1 ELSE 0 END) AS dismissals
            FROM deliveries d JOIN matches m ON d.match_id=m.match_id
            WHERE {_TEAM_FILTER}
              AND lower(trim(d.batter))=lower(trim(?))
              AND lower(trim(d.bowler))=lower(trim(?))
              AND (?::DATE IS NULL OR CAST(m.match_date AS DATE) < ?::DATE)
        """
        params=[batter,list(TEAMS),list(TEAMS),batter,bowler,
                str(before) if before else None,str(before) if before else None]
        row=self._query(sql,params)
        if row is None: return {"status":"DATA_UNAVAILABLE"}
        balls,runs,outs=row
        return {
            "status":"OBSERVED_CRICSHEET_H2H" if balls else "NO_OBSERVED_H2H",
            "batter":batter,"bowler":bowler,
            "recorded_deliveries":int(balls or 0),
            "batting_runs":int(runs or 0),"dismissals":int(outs or 0),
            "cutoff_before":str(before) if before else None,
            "provenance":"LOCAL_WBBL_CRICSHEET_ONLY",
            "caveat":"Sample may be sparse; not a calibrated win or wicket probability."
        }
