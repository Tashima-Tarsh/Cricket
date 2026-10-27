"""Chronological retrospective evaluation of a *partial* score proxy.

Scores are batting runs, boundary bonuses, wickets, bowled/LBW bonuses and
dot balls observed in Cricsheet. Fielding, selection points and platform
rule versions are not present and are deliberately not inferred. This is
NOT a Dream11 competition rank backtest. Predictions use only strictly
earlier match dates; the target game's data is used ONLY to assess error.
"""
from __future__ import annotations

from collections import defaultdict
from math import sqrt
from pathlib import Path
from typing import Dict, Any, Optional
import duckdb

_SCORE_PROXY_SQL = """
WITH partial_events AS (
    SELECT m.match_id, CAST(m.date AS DATE) AS game_date,
           d.batter AS player,
           SUM(d.runs_batter +
               CASE WHEN d.runs_batter = 4 THEN 1 ELSE 0 END +
               CASE WHEN d.runs_batter = 6 THEN 2 ELSE 0 END) AS partial_points
    FROM deliveries d JOIN matches m ON m.match_id = d.match_id
    WHERE m.date IS NOT NULL AND CAST(m.date AS DATE) <= CAST(? AS DATE)
    GROUP BY m.match_id, m.date, d.batter
    UNION ALL
    SELECT m.match_id, CAST(m.date AS DATE) AS game_date,
           d.bowler AS player,
           SUM(
               CASE WHEN d.is_wicket AND d.wicket_type NOT IN ('run out', 'retired hurt')
                    THEN 30 ELSE 0 END +
               CASE WHEN d.is_wicket AND d.wicket_type IN ('bowled', 'lbw')
                    THEN 8 ELSE 0 END +
               CASE WHEN d.runs_total = 0 THEN 1 ELSE 0 END) AS partial_points
    FROM deliveries d JOIN matches m ON m.match_id = d.match_id
    WHERE m.date IS NOT NULL AND CAST(m.date AS DATE) <= CAST(? AS DATE)
    GROUP BY m.match_id, m.date, d.bowler
)
SELECT match_id, game_date, player, SUM(partial_points) AS partial_points
FROM partial_events
WHERE player IS NOT NULL AND TRIM(player) <> ''
GROUP BY match_id, game_date, player
"""


def chronological_player_predictions(rows, target_match_id, target_date, min_history=3):
    """Pure holdout calculation; no target-date outcomes may inform forecasts."""
    history = defaultdict(list)
    actual = {}
    for match_id, game_date, name, score in sorted(rows, key=lambda x: (x[1], str(x[0]))):
        if game_date < target_date:
            history[name].append(float(score))
        elif match_id == target_match_id:
            actual[name] = float(score)
    predictions = {}
    for name, observed in actual.items():
        prior = history.get(name, [])
        if len(prior) >= min_history:
            predictions[name] = {
                "predicted_partial_points": round(sum(prior) / len(prior), 3),
                "observed_partial_points": round(observed, 3),
                "prior_matches": len(prior),
            }
    return predictions, len(actual)


class CricketBacktesting:
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = Path(db_path) if db_path else Path(__file__).resolve().parents[2] / "t20.duckdb"

    def replay_match_from_duckdb(self, match_id: str) -> Optional[Dict[str, Any]]:
        if not self.db_path.exists():
            return None
        try:
            with duckdb.connect(str(self.db_path), read_only=True) as con:
                meta = con.execute(
                    "SELECT match_id, CAST(date AS DATE), team_a, team_b, venue_name "
                    "FROM matches WHERE match_id = ?", [match_id]
                ).fetchone()
                if not meta or meta[1] is None:
                    return None
                rows = con.execute(_SCORE_PROXY_SQL, [meta[1], meta[1]]).fetchall()
        except (duckdb.Error, OSError, TypeError, ValueError):
            return None

        forecasts, actual_count = chronological_player_predictions(rows, match_id, meta[1])
        errors = [entry["predicted_partial_points"] - entry["observed_partial_points"]
                  for entry in forecasts.values()]
        coverage = len(forecasts) / actual_count if actual_count else 0.0
        return {
            "match_id": match_id,
            "match": f"{meta[2]} vs {meta[3]}",
            "venue": meta[4],
            "holdout_date": meta[1].isoformat(),
            "status": "EVALUATED_PARTIAL_PROXY" if errors else "INSUFFICIENT_PRIOR_HISTORY",
            "evaluation_scope": "conditional_on_observed_participants; NOT verified pre-match XI",
            "scoring_scope": "PARTIAL_PROXY_RUNS_BOUNDARIES_WICKETS_DOTS_ONLY",
            "selection_policy": "No target-date data used for projection; >=3 prior matches required",
            "rank_in_grand_league": None,
            "contest_probability": None,
            "coverage_ratio": round(coverage, 3),
            "players_evaluated": len(errors),
            "players_observed": actual_count,
            "mae_partial_points": round(sum(abs(e) for e in errors) / len(errors), 3) if errors else None,
            "rmse_partial_points": round(sqrt(sum(e * e for e in errors) / len(errors)), 3) if errors else None,
            "predictions": forecasts,
            "provenance": {
                "source": "CRICSHEET_DUCKDB_PRIOR_DATE_REPLAY",
                "verification_status": "UNVERIFIED",
                "notes": "Historical records; scoring only partial and model not independently calibrated."
            },
        }

    def execute(self) -> Dict[str, Any]:
        if not self.db_path.exists():
            return {"capability": "cricket-backtesting", "status": "DATA_UNAVAILABLE",
                    "validation_matches": [], "average_efficiency_pct": None}
        try:
            with duckdb.connect(str(self.db_path), read_only=True) as con:
                ids = [row[0] for row in con.execute(
                    "SELECT match_id FROM matches WHERE date IS NOT NULL "
                    "ORDER BY date DESC, match_id DESC LIMIT 10"
                ).fetchall()]
        except (duckdb.Error, OSError):
            ids = []

        evaluations = [self.replay_match_from_duckdb(mid) for mid in ids]
        evaluations = [r for r in evaluations if r is not None]
        eligible = [r for r in evaluations if r["mae_partial_points"] is not None]
        return {
            "capability": "cricket-backtesting",
            "status": "PARTIAL_HOLDOUT_EVALUATION" if eligible else "INSUFFICIENT_PRIOR_HISTORY",
            "validation_matches": evaluations,
            "mean_mae_partial_points": (
                round(sum(r["mae_partial_points"] for r in eligible) / len(eligible), 3)
                if eligible else None
            ),
            "average_efficiency_pct": None,
            "contest_ranks_available": False,
            "data_provenance": "HISTORICAL_PARTIAL_PROXY_UNVERIFIED",
            "note": "No post-match lineup selection, artificial efficiency percentage, or curated benchmark ranks.",
        }
