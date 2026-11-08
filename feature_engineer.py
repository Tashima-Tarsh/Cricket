"""
Feature engineering for cricket fantasy prediction.
Converts raw ball-by-ball data into per-player-per-match features used by the
LightGBM predictor:
  - skill_rating
  - recent_form_last_5
  - opposition_strength
  - phase_strike_rate
  - economy_rate
  - fantasy_points (target)
"""
import logging
from typing import List, Dict, Optional

import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)

# Fantasy points scoring (Dream11-style)
SCORING = {
    "run": 1.0,
    "half_century_bonus": 4.0,
    "century_bonus": 8.0,
    "wicket": 25.0,
    "three_wicket_bonus": 4.0,
    "four_wicket_bonus": 8.0,
    "five_wicket_bonus": 16.0,
    "catch": 4.0,
    "stumping": 4.0,
    "run_out_direct": 6.0,
    "run_out_indirect": 4.0,
    "economy_under_5_bonus": 6.0,
    "economy_5_to_6_bonus": 4.0,
    "strike_rate_170_plus": 4.0,
    "strike_rate_150_to_169": 2.0,
    "duck_penalty": -2.0,
}

ROLE_MAP = {
    "BAT": "BAT",
    "BOWL": "BOWL",
    "AR": "AR",
    "WK": "WK",
    "ALLROUNDER": "AR",
    "BATSMAN": "BAT",
    "BOWLER": "BOWL",
    "WICKETKEEPER": "WK",
}


class FantasyFeatureEngineer:
    """Builds per-player-per-match fantasy features from ball-by-ball data."""

    def __init__(self, scoring: Optional[Dict[str, float]] = None):
        self.scoring = scoring or SCORING

    def aggregate_match_stats(self, balls_df: pd.DataFrame) -> pd.DataFrame:
        """Aggregate ball-by-ball records into per-player match statistics."""
        if balls_df.empty:
            return pd.DataFrame()

        df = balls_df.copy()

        # Normalize column names: synthetic data may use 'player' instead of 'batter'
        if "batter" not in df.columns and "player" in df.columns:
            df = df.rename(columns={"player": "batter"})
        if "bowler" not in df.columns and "bowler_name" in df.columns:
            df = df.rename(columns={"bowler_name": "bowler"})
        if "fielder" not in df.columns and "fielders" in df.columns:
            df = df.rename(columns={"fielders": "fielder"})

        required = {"batter", "bowler", "match_id", "runs_batter", "runs_total", "is_wicket"}
        missing = required - set(df.columns)
        if missing:
            raise KeyError(f"Missing required columns: {missing}")

        # Batting aggregation per player per match per innings
        batting = (
            df[df["batter"].notna() & (df["batter"] != "")]
            .groupby(["match_id", "batting_team", "batter"], as_index=False)
            .agg(
                runs=("runs_batter", "sum"),
                balls_faced=("runs_batter", "size"),
                fours=("runs_batter", lambda s: (s == 4).sum()),
                sixes=("runs_batter", lambda s: (s == 6).sum()),
            )
        )
        batting = batting.rename(columns={"batter": "player"})

        # Wickets taken by bowler per match per innings
        bowling = (
            df[df["bowler"].notna() & (df["bowler"] != "")]
            .groupby(["match_id", "bowling_team", "bowler"], as_index=False)
            .agg(
                wickets=("is_wicket", "sum"),
                runs_conceded=("runs_total", "sum"),
                balls_bowled=("runs_total", "size"),
            )
        )
        bowling = bowling.rename(columns={"bowler": "player"})

        # Fielding: catches/stumpings/run-outs attributed to fielder
        fielding = (
            df[df["fielder"].notna() & (df["fielder"] != "")]
            .groupby(["match_id", "fielder"], as_index=False)
            .size()
            .rename(columns={"size": "fielding_actions", "fielder": "player"})
        )

        # Merge batting + bowling
        stats = batting.merge(bowling, on=["match_id", "player"], how="outer")
        stats = stats.merge(fielding, on=["match_id", "player"], how="left")

        # Fill missing
        numeric_cols = [
            "runs", "balls_faced", "fours", "sixes",
            "wickets", "runs_conceded", "balls_bowled", "fielding_actions",
        ]
        for col in numeric_cols:
            if col in stats.columns:
                stats[col] = stats[col].fillna(0)

        # Batting team / bowling team for each player
        if "batting_team_x" in stats.columns:
            stats["team"] = stats["batting_team_x"].fillna(stats.get("bowling_team", ""))
        elif "batting_team" in stats.columns:
            stats["team"] = stats["batting_team"]
        else:
            stats["team"] = stats.get("bowling_team", "")

        # Derived metrics
        stats["strike_rate"] = np.where(
            stats["balls_faced"] > 0,
            stats["runs"] / stats["balls_faced"] * 100,
            0.0,
        )
        stats["economy_rate"] = np.where(
            stats["balls_bowled"] > 0,
            stats["runs_conceded"] / (stats["balls_bowled"] / 6.0),
            0.0,
        )

        stats["fantasy_points"] = stats.apply(self._compute_fantasy_points, axis=1)

        # Date from match records (first occurrence per match)
        if "date" in df.columns:
            match_dates = df.groupby("match_id")["date"].first().reset_index()
            stats = stats.merge(match_dates, on="match_id", how="left")

        stats = stats.sort_values(["date", "match_id", "player"], na_position="last")
        return stats.reset_index(drop=True)

    def _compute_fantasy_points(self, row: pd.Series) -> float:
        """Compute fantasy points for a single player-match row."""
        pts = 0.0

        runs = float(row.get("runs", 0) or 0)
        wickets = float(row.get("wickets", 0) or 0)
        catches = float(row.get("fielding_actions", 0) or 0)

        # Batting base
        pts += runs * self.scoring["run"]

        # Batting milestones
        if runs >= 100:
            pts += self.scoring["century_bonus"]
        elif runs >= 50:
            pts += self.scoring["half_century_bonus"]

        # Bowling
        pts += wickets * self.scoring["wicket"]
        if wickets >= 5:
            pts += self.scoring["five_wicket_bonus"]
        elif wickets >= 4:
            pts += self.scoring["four_wicket_bonus"]
        elif wickets >= 3:
            pts += self.scoring["three_wicket_bonus"]

        # Fielding
        pts += catches * self.scoring["catch"]

        # Strike rate bonuses (batters only, if they faced balls)
        balls_faced = float(row.get("balls_faced", 0) or 0)
        sr = float(row.get("strike_rate", 0) or 0)
        if balls_faced > 0:
            if sr >= 170:
                pts += self.scoring["strike_rate_170_plus"]
            elif sr >= 150:
                pts += self.scoring["strike_rate_150_to_169"]

        # Economy rate bonuses (bowlers only, if they bowled)
        balls_bowled = float(row.get("balls_bowled", 0) or 0)
        econ = float(row.get("economy_rate", 0) or 0)
        if balls_bowled > 0:
            if econ < 5.0:
                pts += self.scoring["economy_under_5_bonus"]
            elif econ <= 6.0:
                pts += self.scoring["economy_5_to_6_bonus"]

        # Duck penalty
        if runs == 0 and balls_faced > 0:
            pts += self.scoring["duck_penalty"]

        return round(pts, 2)

    def build_player_features(
        self, stats_df: pd.DataFrame, lookback_matches: int = 5
    ) -> pd.DataFrame:
        """Build ML-ready features per player for their most recent match."""
        if stats_df.empty:
            return pd.DataFrame()

        df = stats_df.copy()
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        df = df.sort_values(["player", "date"])

        # Role inference: if a player bowls > 0 balls in >30% of matches -> AR/BOWL
        role_inference = (
            df.groupby("player")
            .agg(
                matches=("match_id", "nunique"),
                matches_bowled=("balls_bowled", lambda s: (s > 0).sum()),
                total_wickets=("wickets", "sum"),
                total_catches=("fielding_actions", "sum"),
            )
            .reset_index()
        )
        role_inference["bowl_pct"] = (
            role_inference["matches_bowled"] / role_inference["matches"]
        )
        role_inference["role"] = np.where(
            role_inference["bowl_pct"] > 0.3,
            np.where(role_inference["total_wickets"] > 5, "BOWL", "AR"),
            np.where(role_inference["total_catches"] > 5, "WK", "BAT"),
        )

        # Latest match per player (the upcoming prediction target)
        latest = df.sort_values("date").groupby("player").tail(1).copy()
        latest = latest.merge(role_inference[["player", "role"]], on="player", how="left")

        # Recent form: mean fantasy points over last N matches (excluding current)
        form_rows = []
        for player, group in df.groupby("player"):
            group = group.sort_values("date")
            for i in range(len(group)):
                window = group.iloc[max(0, i - lookback_matches):i]
                form_rows.append({
                    "player": player,
                    "date": group.iloc[i]["date"],
                    "recent_form_last_5": window["fantasy_points"].mean()
                    if len(window) > 0 else 50.0,
                })
        form_df = pd.DataFrame(form_rows)
        latest = latest.merge(form_df, on=["player", "date"], how="left")
        latest["recent_form_last_5"] = latest["recent_form_last_5"].fillna(50.0)

        # Opposition strength: average fantasy points allowed to this player's role by opp team
        opp_strength = (
            df.groupby(["date", "team"])["fantasy_points"]
            .mean()
            .reset_index(name="opposition_strength")
        )
        latest = latest.merge(
            opp_strength,
            left_on=["date", "team"],
            right_on=["date", "team"],
            how="left",
        )
        latest["opposition_strength"] = latest["opposition_strength"].fillna(65.0)

        # Skill rating: career average fantasy points scaled to 0-100
        career_avg = df.groupby("player")["fantasy_points"].mean().reset_index(name="career_avg")
        latest = latest.merge(career_avg, on="player", how="left")
        latest["skill_rating"] = np.clip(latest["career_avg"] / 100.0 * 100, 40, 95).round(1)

        # Phase strike rate: use overall strike rate as proxy (death-overs detail not in CSV)
        latest["phase_strike_rate"] = latest["strike_rate"].fillna(130.0).round(1)

        # Economy rate (for bowlers; 0 for batters)
        latest["economy_rate"] = latest["economy_rate"].fillna(9.0).round(2)

        # Output columns matching predictor.FEATURE_COLS + metadata
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
            "fantasy_points": latest["fantasy_points"],
        })

        return out.sort_values("date", na_position="last").reset_index(drop=True)

    def build_training_frame(
        self, balls_df: pd.DataFrame, lookback_matches: int = 5
    ) -> pd.DataFrame:
        """Full pipeline: raw balls -> per-match stats -> ML features."""
        stats = self.aggregate_match_stats(balls_df)
        return self.build_player_features(stats, lookback_matches=lookback_matches)

    def predict_upcoming_features(
        self, upcoming_players: List[Dict], history_df: pd.DataFrame
    ) -> pd.DataFrame:
        """Build feature rows for upcoming-match players using historical context."""
        role_defaults = {
            "BAT":  {"skill_rating": 85, "recent_form_last_5": 70.0, "opposition_strength": 70.0, "phase_strike_rate": 140.0, "economy_rate": 9.5},
            "BOWL": {"skill_rating": 85, "recent_form_last_5": 70.0, "opposition_strength": 70.0, "phase_strike_rate": 110.0, "economy_rate": 8.0},
            "AR":   {"skill_rating": 82, "recent_form_last_5": 70.0, "opposition_strength": 70.0, "phase_strike_rate": 130.0, "economy_rate": 8.5},
            "WK":   {"skill_rating": 80, "recent_form_last_5": 70.0, "opposition_strength": 70.0, "phase_strike_rate": 135.0, "economy_rate": 9.5},
        }

        out_rows = []
        for p in upcoming_players:
            role = p["role"]
            base = {
                "match_id": p.get("match_id", "upcoming"),
                "player": p["name"],
                "role": role,
                "team": p["team"],
                "credit": p.get("credit", 8.0),
                "projected_sel_pct": p.get("projected_sel_pct", 50.0),
            }

            if not history_df.empty:
                player_hist = history_df[history_df["player"] == p["name"]]
                if not player_hist.empty:
                    latest = player_hist.sort_values("date").iloc[-1]
                    row = {
                        **base,
                        "skill_rating": latest["skill_rating"],
                        "recent_form_last_5": latest["recent_form_last_5"],
                        "opposition_strength": latest["opposition_strength"],
                        "phase_strike_rate": latest["phase_strike_rate"],
                        "economy_rate": latest["economy_rate"],
                    }
                else:
                    row = {**base, **role_defaults.get(role, role_defaults["BAT"])}
            else:
                row = {**base, **role_defaults.get(role, role_defaults["BAT"])}

            out_rows.append(row)

        return pd.DataFrame(out_rows)
