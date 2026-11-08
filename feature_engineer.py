"""
Advanced feature engineering for BBL/WBBL fantasy cricket.
Includes venue quirks, travel fatigue, and phase-specific matchups.
"""
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional

import numpy as np
import pandas as pd

from config import FEATURE_COLS, SCORING, TRAVEL_FATIGUE_PENALTY, VENUE_ADJUSTMENTS

logger = logging.getLogger(__name__)


class BBLFeatureEngineer:
    def __init__(self, venue_data_path: str | Path = "data/venues.json"):
        self.venue_data: Dict[str, dict] = {}
        p = Path(venue_data_path)
        if p.exists():
            with open(p, "r", encoding="utf-8") as f:
                self.venue_data = json.load(f)

    # ------------------------------------------------------------------ #
    # Venue quirks
    # ------------------------------------------------------------------ #
    def add_venue_quirks(self, df: pd.DataFrame) -> pd.DataFrame:
        """Adjust player projections based on venue characteristics."""
        if df.empty:
            return df

        df = df.copy()

        def adjust(row: pd.Series) -> pd.Series:
            venue = str(row.get("venue", "MCG"))
            info = self.venue_data.get(venue)
            if not info:
                return row

            adj = row.copy()

            # Boundary size effect on power hitters
            dims = info.get("boundary_dimensions", {})
            square = dims.get("square", 70)
            sr = float(row.get("strike_rate", 130) or 130)
            if row["role"] == "BAT":
                if square > 75 and sr > 150:
                    adj["fantasy_points"] = float(adj["fantasy_points"]) * 0.85
                elif square < 65 and sr > 150:
                    adj["fantasy_points"] = float(adj["fantasy_points"]) * 1.15

            # Pace/spin friendliness for bowlers
            if row["role"] == "BOWL":
                style = str(row.get("bowling_style", "pace")).lower()
                if "pace" in style or "fast" in style:
                    adj["fantasy_points"] = float(adj["fantasy_points"]) * float(info.get("pace_friendly", 1.0))
                elif "spin" in style:
                    adj["fantasy_points"] = float(adj["fantasy_points"]) * float(info.get("spin_friendly", 1.0))

            return adj

        return df.apply(adjust, axis=1)

    # ------------------------------------------------------------------ #
    # Travel fatigue
    # ------------------------------------------------------------------ #
    def add_travel_fatigue(
        self,
        df: pd.DataFrame,
        last_match_venue: str,
        current_venue: str,
    ) -> pd.DataFrame:
        """Penalize fast bowlers who traveled long distances between matches."""
        if df.empty:
            return df

        df = df.copy()
        distance_km = self._calculate_distance(last_match_venue, current_venue)

        if distance_km > 2000:
            for idx, row in df.iterrows():
                if row["role"] == "BOWL":
                    style = str(row.get("bowling_style", "pace")).lower()
                    if "pace" in style or "fast" in style:
                        df.at[idx, "fantasy_points"] = float(
                            df.at[idx, "fantasy_points"]
                        ) * (1.0 - TRAVEL_FATIGUE_PENALTY)

        return df

    @staticmethod
    def _calculate_distance(venue1: str, venue2: str) -> float:
        distances = {
            ("Perth_Stadium", "MCG"): 2700,
            ("Perth_Stadium", "Adelaide_Oval"): 2100,
            ("MCG", "Adelaide_Oval"): 650,
            ("MCG", "SCG"): 700,
            ("SCG", "Gabba"): 730,
        }
        key = (venue1, venue2) if (venue1, venue2) in distances else (venue2, venue1)
        return float(distances.get(key, 500))

    # ------------------------------------------------------------------ #
    # Phase matchups
    # ------------------------------------------------------------------ #
    def add_phase_matchups(self, df: pd.DataFrame, balls_df: pd.DataFrame) -> pd.DataFrame:
        """Calculate batter strike-rate in powerplay / middle / death overs."""
        if df.empty or balls_df.empty:
            return df

        df = df.copy()

        for idx, row in df.iterrows():
            batter = str(row["player"])
            batter_balls = balls_df[balls_df["batter"] == batter]
            if batter_balls.empty:
                continue

            pp = batter_balls[batter_balls["over"] < 6]
            if not pp.empty:
                df.at[idx, "powerplay_sr"] = (pp["runs_batter"].sum() / len(pp)) * 100

            mid = batter_balls[(batter_balls["over"] >= 6) & (batter_balls["over"] < 15)]
            if not mid.empty:
                df.at[idx, "middle_overs_sr"] = (mid["runs_batter"].sum() / len(mid)) * 100

            death = batter_balls[batter_balls["over"] >= 15]
            if not death.empty:
                df.at[idx, "death_overs_sr"] = (death["runs_batter"].sum() / len(death)) * 100

        return df

    # ------------------------------------------------------------------ #
    # ML feature frame
    # ------------------------------------------------------------------ #
    def build_ml_features(
        self,
        balls_df: pd.DataFrame,
        upcoming_players: List[dict],
        lookback_matches: int = 5,
    ) -> pd.DataFrame:
        """Build the full ML-ready feature frame for upcoming players."""
        if balls_df.empty:
            return self._default_features(upcoming_players)

        df = balls_df.copy()

        # Normalize columns: real iCSV data uses batter/bowler/batting_team;
        # synthetic data uses player/role/team/venue.
        if "player" not in df.columns:
            if "batter" in df.columns:
                df["player"] = df["batter"]
            elif "bowler" in df.columns:
                df["player"] = df["bowler"]
            else:
                df["player"] = "Unknown"

        if "team" not in df.columns:
            if "batting_team" in df.columns:
                df["team"] = df["batting_team"]
            else:
                df["team"] = "Unknown"

        if "role" not in df.columns:
            df["role"] = "BAT"

        if "venue" not in df.columns:
            df["venue"] = "MCG"

        if "fantasy_points" in df.columns:
            df["fantasy_points"] = pd.to_numeric(df["fantasy_points"], errors="coerce").fillna(0)
        else:
            df["fantasy_points"] = 0.0

        df["date"] = pd.to_datetime(df.get("date", "2026-01-01"), errors="coerce")

        # Compute fantasy_points per ball from SCORING rules (if not already present)
        if "fantasy_points" not in df.columns or df["fantasy_points"].sum() == 0:
            pts = pd.Series(0.0, index=df.index)
            runs = pd.to_numeric(df.get("runs_batter", 0), errors="coerce").fillna(0)
            wickets = pd.to_numeric(df.get("is_wicket", 0), errors="coerce").fillna(0)
            # Batting runs
            pts = pts + runs * SCORING["run"]
            # Wickets (credited to bowler)
            pts = pts + wickets * SCORING["wicket"]
            # Catches (fielder column non-empty)
            if "fielder" in df.columns:
                catches = df["fielder"].notna() & (df["fielder"].astype(str) != "")
                pts = pts + catches.astype(float) * SCORING["catch"]
            df["fantasy_points"] = pts

        df = df.sort_values(["player", "date"])

        # Per-player match aggregates
        group_cols = ["match_id", "player", "role", "team", "venue", "date"]
        stats = (
            df.groupby(group_cols)
            .agg(
                runs=("runs_batter", "sum"),
                wickets=("is_wicket", "sum"),
                balls_bowled=("runs_total", "size"),
                fantasy_points=("fantasy_points", "mean"),
            )
            .reset_index()
        )

        # Recent form (mean fantasy points over last N matches)
        form_rows: List[dict] = []
        for player, group in stats.groupby("player"):
            group = group.sort_values("date")
            for i in range(len(group)):
                window = group.iloc[max(0, i - lookback_matches):i]
                form_rows.append({
                    "player": player,
                    "date": group.iloc[i]["date"],
                    "recent_form_last_5": float(window["fantasy_points"].mean()) if len(window) > 0 else 50.0,
                })
        form_df = pd.DataFrame(form_rows)

        latest = stats.sort_values("date").groupby("player").tail(1).copy()
        latest = latest.merge(form_df, on=["player", "date"], how="left")
        latest["recent_form_last_5"] = latest["recent_form_last_5"].fillna(50.0)

        # Skill rating = career avg fantasy points scaled to 0-100
        career_avg = stats.groupby("player")["fantasy_points"].mean().reset_index(name="career_avg")
        latest = latest.merge(career_avg, on="player", how="left")
        latest["skill_rating"] = np.clip(latest["career_avg"] / 100.0 * 100, 40, 95).round(1)

        # Venue factor
        latest["venue_factor"] = latest["venue"].apply(
            lambda v: VENUE_ADJUSTMENTS.get(str(v), {}).get("avg_first_innings", 160) / 160.0
        )

        # Travel fatigue (default neutral)
        latest["travel_fatigue"] = 0.0

        # Phase strike rate proxy
        if "strike_rate" in latest.columns:
            latest["phase_strike_rate"] = latest["strike_rate"].fillna(130).round(1)
        else:
            latest["phase_strike_rate"] = 130.0

        # Economy rate
        if "economy_rate" in latest.columns:
            latest["economy_rate"] = latest["economy_rate"].fillna(9.0).round(2)
        else:
            latest["economy_rate"] = 9.0

        # Opposition strength
        if "opposition_strength" in latest.columns:
            latest["opposition_strength"] = latest["opposition_strength"].fillna(65.0).round(1)
        else:
            latest["opposition_strength"] = 65.0

        out = pd.DataFrame({
            "match_id": latest["match_id"],
            "player": latest["player"],
            "role": latest["role"],
            "team": latest["team"],
            "date": latest["date"],
            "skill_rating": latest["skill_rating"],
            "recent_form_last_5": latest["recent_form_last_5"],
            "opposition_strength": latest["opposition_strength"],
            "phase_strike_rate": latest["phase_strike_rate"],
            "economy_rate": latest["economy_rate"],
            "venue_factor": latest["venue_factor"],
            "travel_fatigue": latest["travel_fatigue"],
            "fantasy_points": latest["fantasy_points"],
        })

        # Append upcoming players with defaults
        upcoming_df = self._default_features(upcoming_players)
        out = pd.concat([out, upcoming_df], ignore_index=True)
        return out.sort_values("date", na_position="last").reset_index(drop=True)

    def _default_features(self, upcoming_players: List[dict]) -> pd.DataFrame:
        rows: List[dict] = []
        for p in upcoming_players:
            role = p["role"]
            defaults = {
                "BAT": {"skill_rating": 85, "recent_form_last_5": 70.0, "opposition_strength": 70.0,
                        "phase_strike_rate": 140.0, "economy_rate": 9.5, "venue_factor": 1.0, "travel_fatigue": 0.0},
                "BOWL": {"skill_rating": 85, "recent_form_last_5": 70.0, "opposition_strength": 70.0,
                         "phase_strike_rate": 110.0, "economy_rate": 8.0, "venue_factor": 1.0, "travel_fatigue": 0.0},
                "AR": {"skill_rating": 82, "recent_form_last_5": 70.0, "opposition_strength": 70.0,
                       "phase_strike_rate": 130.0, "economy_rate": 8.5, "venue_factor": 1.0, "travel_fatigue": 0.0},
                "WK": {"skill_rating": 80, "recent_form_last_5": 70.0, "opposition_strength": 70.0,
                       "phase_strike_rate": 135.0, "economy_rate": 9.5, "venue_factor": 1.0, "travel_fatigue": 0.0},
            }
            d = defaults.get(role, defaults["BAT"])
            rows.append({
                "match_id": "upcoming",
                "player": p["name"],
                "role": role,
                "team": p["team"],
                "date": pd.NaT,
                "credit": p.get("credit", 8.0),
                "projected_sel_pct": p.get("projected_sel_pct", 50.0),
                **d,
                "fantasy_points": 0.0,
            })
        return pd.DataFrame(rows)
