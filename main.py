"""
BBL/WBBL Grand League Engine — orchestrator.
End-to-end pipeline:
  1. Load historical ball-by-ball data (Cricsheet + synthetic fallback)
  2. Build correlation matrix (bowler-batter rivalries + partnerships)
  3. Feature engineer (venue quirks, travel fatigue, phase matchups)
  4. Train dual LightGBM (mean + variance)
  5. Predict upcoming players
  6. Apply Chaos Intelligence adjustments (weather, umpire, pitch, form, venue, toss,
     crowd, travel, importance)
  7. Generate Grand League teams via OR-Tools CP-SAT
"""
import logging
import sys
from typing import Dict, List

import pandas as pd

sys.stdout.reconfigure(encoding="utf-8")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("bbl_wbbl_engine")

from chaos_intelligence import ChaosIntelligence  # noqa: E402
from config import SCENARIOS  # noqa: E402
from correlation_matrix import CorrelationMatrix  # noqa: E402
from data_loader import load_bbl_data  # noqa: E402
from feature_engineer import BBLFeatureEngineer  # noqa: E402
from optimizer import GrandLeagueOptimizer  # noqa: E402
from predictor import CricketPredictor  # noqa: E402
import scenario_generator  # noqa: E402

N_TEAMS_TOTAL = 20


def load_upcoming_bbl_players() -> List[dict]:
    """Return the upcoming match squad with credits and projected selection %."""
    return [
        {"name": "Steve_Smith", "role": "BAT", "team": "Sydney Sixers", "credit": 11.0, "projected_sel_pct": 85.0,
         "expected_points": 50.0, "variance_score": 0.5, "bowling_style": "", "lbw_dismissal_rate": 0.2,
         "edge_rate": 0.1, "caught_behind_rate": 0.2, "false_shot_percentage": 0.1, "balls_per_wicket": 30,
         "recent_form_variance": 0.3, "batting_order": 2, "bowling_phase": "middle", "bowling_innings": 1,
         "experience_years": 8},
        {"name": "David_Warner", "role": "BAT", "team": "Sydney Thunder", "credit": 10.5, "projected_sel_pct": 78.0,
         "expected_points": 52.0, "variance_score": 0.4, "bowling_style": "", "lbw_dismissal_rate": 0.15,
         "edge_rate": 0.08, "caught_behind_rate": 0.15, "false_shot_percentage": 0.1, "balls_per_wicket": 30,
         "recent_form_variance": 0.25, "batting_order": 1, "bowling_phase": "middle", "bowling_innings": 1,
         "experience_years": 10},
        {"name": "Glenn_Maxwell", "role": "AR", "team": "Melbourne Stars", "credit": 10.0, "projected_sel_pct": 72.0,
         "expected_points": 48.0, "variance_score": 0.6, "bowling_style": "off_spin", "lbw_dismissal_rate": 0.18,
         "edge_rate": 0.12, "caught_behind_rate": 0.22, "false_shot_percentage": 0.15, "balls_per_wicket": 25,
         "recent_form_variance": 0.4, "batting_order": 4, "bowling_phase": "middle", "bowling_innings": 1,
         "experience_years": 9},
        {"name": "Marcus_Stoinis", "role": "AR", "team": "Melbourne Stars", "credit": 9.5, "projected_sel_pct": 65.0,
         "expected_points": 44.0, "variance_score": 0.5, "bowling_style": "pace", "lbw_dismissal_rate": 0.2,
         "edge_rate": 0.11, "caught_behind_rate": 0.18, "false_shot_percentage": 0.14, "balls_per_wicket": 28,
         "recent_form_variance": 0.35, "batting_order": 6, "bowling_phase": "death", "bowling_innings": 1,
         "experience_years": 7},
        {"name": "Rashid_Khan", "role": "BOWL", "team": "Adelaide Strikers", "credit": 10.5, "projected_sel_pct": 88.0,
         "expected_points": 55.0, "variance_score": 0.55, "bowling_style": "leg_spin", "lbw_dismissal_rate": 0.1,
         "edge_rate": 0.05, "caught_behind_rate": 0.05, "false_shot_percentage": 0.05, "balls_per_wicket": 20,
         "recent_form_variance": 0.2, "batting_order": 10, "bowling_phase": "death", "bowling_innings": 1,
         "experience_years": 6},
        {"name": "Pat_Cummins", "role": "BOWL", "team": "Sydney Thunder", "credit": 10.0, "projected_sel_pct": 82.0,
         "expected_points": 51.0, "variance_score": 0.45, "bowling_style": "pace", "lbw_dismissal_rate": 0.12,
         "edge_rate": 0.06, "caught_behind_rate": 0.08, "false_shot_percentage": 0.08, "balls_per_wicket": 24,
         "recent_form_variance": 0.25, "batting_order": 9, "bowling_phase": "death", "bowling_innings": 1,
         "experience_years": 8},
        {"name": "Josh_Hazlewood", "role": "BOWL", "team": "Sydney Sixers", "credit": 9.5, "projected_sel_pct": 70.0,
         "expected_points": 49.0, "variance_score": 0.4, "bowling_style": "pace", "lbw_dismissal_rate": 0.1,
         "edge_rate": 0.05, "caught_behind_rate": 0.05, "false_shot_percentage": 0.06, "balls_per_wicket": 26,
         "recent_form_variance": 0.22, "batting_order": 11, "bowling_phase": "powerplay", "bowling_innings": 1,
         "experience_years": 8},
        {"name": "Adam_Zampa", "role": "BOWL", "team": "Sydney Sixers", "credit": 9.0, "projected_sel_pct": 60.0,
         "expected_points": 46.0, "variance_score": 0.5, "bowling_style": "leg_spin", "lbw_dismissal_rate": 0.08,
         "edge_rate": 0.04, "caught_behind_rate": 0.04, "false_shot_percentage": 0.04, "balls_per_wicket": 23,
         "recent_form_variance": 0.28, "batting_order": 10, "bowling_phase": "middle", "bowling_innings": 1,
         "experience_years": 6},
        {"name": "Matthew_Wade", "role": "WK", "team": "Hobart Hurricanes", "credit": 9.0, "projected_sel_pct": 50.0,
         "expected_points": 42.0, "variance_score": 0.45, "bowling_style": "", "lbw_dismissal_rate": 0.22,
         "edge_rate": 0.13, "caught_behind_rate": 0.24, "false_shot_percentage": 0.13, "balls_per_wicket": 30,
         "recent_form_variance": 0.32, "batting_order": 5, "bowling_phase": "middle", "bowling_innings": 1,
         "experience_years": 7},
        {"name": "Alex_Carey", "role": "WK", "team": "Adelaide Strikers", "credit": 8.5, "projected_sel_pct": 40.0,
         "expected_points": 40.0, "variance_score": 0.42, "bowling_style": "", "lbw_dismissal_rate": 0.2,
         "edge_rate": 0.12, "caught_behind_rate": 0.22, "false_shot_percentage": 0.12, "balls_per_wicket": 30,
         "recent_form_variance": 0.3, "batting_order": 6, "bowling_phase": "middle", "bowling_innings": 1,
         "experience_years": 6},
        {"name": "Nick_Madron", "role": "WK", "team": "Perth Scorchers", "credit": 8.5, "projected_sel_pct": 35.0,
         "expected_points": 39.0, "variance_score": 0.4, "bowling_style": "", "lbw_dismissal_rate": 0.18,
         "edge_rate": 0.11, "caught_behind_rate": 0.21, "false_shot_percentage": 0.11, "balls_per_wicket": 30,
         "recent_form_variance": 0.29, "batting_order": 7, "bowling_phase": "middle", "bowling_innings": 1,
         "experience_years": 5},
        {"name": "Tim_David", "role": "BAT", "team": "Perth Scorchers", "credit": 8.5, "projected_sel_pct": 30.0,
         "expected_points": 38.0, "variance_score": 0.55, "bowling_style": "", "lbw_dismissal_rate": 0.15,
         "edge_rate": 0.09, "caught_behind_rate": 0.16, "false_shot_percentage": 0.1, "balls_per_wicket": 28,
         "recent_form_variance": 0.38, "batting_order": 7, "bowling_phase": "death", "bowling_innings": 1,
         "experience_years": 4},
        {"name": "Colin_Munro", "role": "BAT", "team": "Perth Scorchers", "credit": 8.0, "projected_sel_pct": 22.0,
         "expected_points": 36.0, "variance_score": 0.6, "bowling_style": "", "lbw_dismissal_rate": 0.18,
         "edge_rate": 0.14, "caught_behind_rate": 0.2, "false_shot_percentage": 0.14, "balls_per_wicket": 26,
         "recent_form_variance": 0.42, "batting_order": 3, "bowling_phase": "powerplay", "bowling_innings": 1,
         "experience_years": 6},  # differential
        {"name": "Chris_Lynn", "role": "BAT", "team": "Brisbane Heat", "credit": 8.0, "projected_sel_pct": 18.0,
         "expected_points": 34.0, "variance_score": 0.62, "bowling_style": "", "lbw_dismissal_rate": 0.2,
         "edge_rate": 0.16, "caught_behind_rate": 0.25, "false_shot_percentage": 0.16, "balls_per_wicket": 25,
         "recent_form_variance": 0.45, "batting_order": 2, "bowling_phase": "powerplay", "bowling_innings": 1,
         "experience_years": 7},  # differential
        {"name": "Ben_McDermott", "role": "BAT", "team": "Hobart Hurricanes", "credit": 8.0, "projected_sel_pct": 25.0,
         "expected_points": 35.0, "variance_score": 0.5, "bowling_style": "", "lbw_dismissal_rate": 0.19,
         "edge_rate": 0.13, "caught_behind_rate": 0.2, "false_shot_percentage": 0.13, "balls_per_wicket": 27,
         "recent_form_variance": 0.36, "batting_order": 4, "bowling_phase": "middle", "bowling_innings": 1,
         "experience_years": 6},
        {"name": "D'Arcy_Short", "role": "AR", "team": "Hobart Hurricanes", "credit": 8.0, "projected_sel_pct": 15.0,
         "expected_points": 33.0, "variance_score": 0.58, "bowling_style": "left_arm_spin", "lbw_dismissal_rate": 0.17,
         "edge_rate": 0.12, "caught_behind_rate": 0.19, "false_shot_percentage": 0.12, "balls_per_wicket": 24,
         "recent_form_variance": 0.4, "batting_order": 5, "bowling_phase": "middle", "bowling_innings": 1,
         "experience_years": 5},
        {"name": "Ashton_Turner", "role": "AR", "team": "Perth Scorchers", "credit": 8.0, "projected_sel_pct": 10.0,
         "expected_points": 31.0, "variance_score": 0.6, "bowling_style": "off_spin", "lbw_dismissal_rate": 0.16,
         "edge_rate": 0.11, "caught_behind_rate": 0.18, "false_shot_percentage": 0.11, "balls_per_wicket": 26,
         "recent_form_variance": 0.41, "batting_order": 8, "bowling_phase": "death", "bowling_innings": 1,
         "experience_years": 4},  # differential
        {"name": "Nathan_Coulter_Nile", "role": "BOWL", "team": "Melbourne Stars", "credit": 8.5,
         "projected_sel_pct": 12.0, "expected_points": 41.0, "variance_score": 0.48, "bowling_style": "pace",
         "lbw_dismissal_rate": 0.11, "edge_rate": 0.07, "caught_behind_rate": 0.09, "false_shot_percentage": 0.07,
         "balls_per_wicket": 25, "recent_form_variance": 0.31, "batting_order": 10, "bowling_phase": "middle",
         "bowling_innings": 1, "experience_years": 7},
        {"name": "Jason_Behrendorff", "role": "BOWL", "team": "Perth Scorchers", "credit": 8.0,
         "projected_sel_pct": 8.0, "expected_points": 39.0, "variance_score": 0.52, "bowling_style": "pace",
         "lbw_dismissal_rate": 0.1, "edge_rate": 0.06, "caught_behind_rate": 0.08, "false_shot_percentage": 0.06,
         "balls_per_wicket": 23, "recent_form_variance": 0.34, "batting_order": 11, "bowling_phase": "death",
         "bowling_innings": 1, "experience_years": 6},  # differential
        {"name": "Kane_Richardson", "role": "BOWL", "team": "Melbourne Renegades", "credit": 8.0,
         "projected_sel_pct": 9.0, "expected_points": 40.0, "variance_score": 0.49, "bowling_style": "pace",
         "lbw_dismissal_rate": 0.1, "edge_rate": 0.06, "caught_behind_rate": 0.07, "false_shot_percentage": 0.06,
         "balls_per_wicket": 24, "recent_form_variance": 0.33, "batting_order": 11, "bowling_phase": "death",
         "bowling_innings": 1, "experience_years": 7},  # differential
    ]


def build_match_context() -> Dict:
    """Build match context with all chaos factors for the upcoming fixture."""
    return {
        "venue": "MCG",
        "rain_prob": 35,
        "humidity": 78,
        "wind_speed": 18,
        "cloud_cover": 60,
        "temperature": 22,
        "dew_factor": "HIGH",
        "is_night_match": True,
        "umpires": [
            {"strictness_index": 0.75, "lbw_given_rate": 0.6, "drs_overturn_rate": 0.45},
            {"strictness_index": 0.65, "lbw_given_rate": 0.5, "drs_overturn_rate": 0.35},
        ],
        "pitch_type": "slow",
        "pace_friendly": False,
        "spin_friendly": True,
        "wear_rate": 0.65,
        "cracks": True,
        "grass_cover": "medium",
        "players": load_upcoming_bbl_players(),
        "travel_distance_km": 2500,
        "days_since_last_match": 2,
        "timezone_changes": 1,
        "is_knockout": True,
        "rivalry_factor": 0.8,
        "home_crowd_pct": 85,
        "match_importance": "playoff",
        "boundary_size": "medium",
        "crowd_noise": "high",
        "home_advantage": 0.6,
        "toss_winner": "Sydney Sixers",
        "toss_decision": "bowl",
        "venue_upset_rate": 0.45,
        "head_to_head_chaos": 0.5,
        "recent_upsets": 3,
        "average_margin": 18,
        "margin_variance": 25,
        "chasing_win_rate": 0.55,
        "pitch_wear_rate": 0.65,
    }


def run_pipeline(use_cricsheet: bool = True, max_matches: int = 100):
    logger.info("=" * 70)
    logger.info("🏏 BBL/WBBL GRAND LEAGUE ENGINE")
    logger.info("=" * 70)

    # ---- 1. Load historical data ----
    logger.info("\n[1/7] Loading BBL/WBBL ball-by-ball data...")
    balls_df = load_bbl_data(max_matches=max_matches, use_synthetic_fallback=True)
    logger.info("      Loaded %d ball-by-ball records", len(balls_df))

    # ---- 2. Correlation matrix ----
    logger.info("\n[2/7] Building correlation matrix...")
    correlation = CorrelationMatrix(balls_df)
    summary = correlation.summary()
    logger.info(
        "      %d bowler-batter rivalries | %d partnerships",
        summary["bowler_batter_rivalries"], summary["partnerships"],
    )

    # ---- 3. Feature engineering ----
    logger.info("\n[3/7] Engineering features...")
    engineer = BBLFeatureEngineer()
    upcoming_players = load_upcoming_bbl_players()
    train_df = engineer.build_ml_features(balls_df, upcoming_players)
    logger.info("      Built %d feature rows", len(train_df))

    # ---- 4. Train predictor ----
    logger.info("\n[4/7] Training dual LightGBM (mean + variance)...")
    predictor = CricketPredictor()
    train_rows = train_df[train_df["match_id"] != "upcoming"]
    if not train_rows.empty:
        metrics = predictor.train(train_rows)
        logger.info("      val_rmse=%.4f n_train=%d", metrics["val_rmse"], metrics["n_train"])
        predictor.save("models/")
    else:
        logger.warning("No training rows; skipping training")

    # ---- 5. Predict upcoming ----
    logger.info("\n[5/7] Predicting upcoming players...")
    upcoming_df = train_df[train_df["match_id"] == "upcoming"].copy()
    if upcoming_df.empty:
        upcoming_df = engineer._default_features(upcoming_players)
    pred_df = predictor.predict(upcoming_df)
    logger.info("      Predicted %d players", len(pred_df))

    # ---- 6. Chaos Intelligence ----
    logger.info("\n[6/7] Applying Chaos Intelligence adjustments...")
    match_context = build_match_context()
    chaos = ChaosIntelligence()
    all_factors = chaos.load_all_factors(match_context)
    chaos_summary = chaos.get_match_chaos_summary(all_factors)
    logger.info(
        "      Match Chaos Level: %s (score %.2f)",
        chaos_summary["chaos_level"], chaos_summary["total_chaos_score"],
    )
    logger.info("      Key Factors: %s", ", ".join(chaos_summary["key_factors"]))
    logger.info("      Strategy: %s", chaos_summary["recommended_strategy"])

    # Map predicted players by name for chaos adjustment
    player_map = {row["player"]: row.to_dict() for _, row in pred_df.iterrows()}

    # Build match context players with prediction data merged in
    context_players = match_context["players"]
    for ctx_player in context_players:
        pname = ctx_player["name"]
        if pname in player_map:
            pred = player_map[pname]
            # Start from model prediction, then apply chaos
            ctx_player["expected_points"] = float(pred["expected_points"])
            ctx_player["variance_score"] = float(pred["variance_score"])

    # Apply chaos adjustments to all players
    adjusted_players = []
    for ctx_player in context_players:
        adjusted = chaos.apply_chaos_to_player(ctx_player, all_factors)
        adjusted_players.append(adjusted)

    logger.info(
      "      Applied chaos adjustments to %d players", len(adjusted_players),
    )

    # Build chaos-adjusted DataFrame for the optimizer
    adjusted_df = pd.DataFrame(adjusted_players)
    # Ensure required optimizer columns exist
    if "player" not in adjusted_df.columns and "name" in adjusted_df.columns:
        adjusted_df["player"] = adjusted_df["name"]

    # ---- 7. Optimize ----
    logger.info("\n[7/7] Generating Grand League teams via OR-Tools CP-SAT...")
    optimizer = GrandLeagueOptimizer(adjusted_df, correlation)
    all_teams: List[Dict] = []
    for sc in SCENARIOS:
        n = scenario_generator.teams_for_scenario(sc)
        teams = optimizer.optimize(n_teams=n, scenario=sc)
        all_teams.extend(teams)

    all_teams.sort(key=lambda t: -t["projected_points"])

    logger.info("\n✅ Generated %d teams. TOP 5:", len(all_teams))
    for team in all_teams[:5]:
        _print_team(team)

    logger.info("\n%s", "=" * 70)
    logger.info("📊 PORTFOLIO SUMMARY")
    logger.info("=" * 70)
    logger.info("Total teams: %d", len(all_teams))
    if all_teams:
        logger.info("Best projected points:  %s", all_teams[0]["projected_points"])
        logger.info("Worst projected points: %s", all_teams[-1]["projected_points"])
        avg_diff = sum(t["n_differentials"] for t in all_teams) / len(all_teams)
        logger.info("Avg differentials per team: %.1f", avg_diff)
    logger.info("=" * 70)

    return all_teams


def _print_team(team: Dict) -> None:
    print(f"\n{'='*70}")
    print(f"TEAM #{team['team_id']}  |  Scenario: {team['scenario']}")
    print(f"Projected Points: {team['projected_points']}  |  Credits: {team['total_credits']}/100")
    print(f"Avg Selection %: {team['avg_selection_pct']}  |  Differentials: {team['n_differentials']}")
    print(f"{'='*70}")
    print(f"{'Player':<22} {'Role':<5} {'Team':<16} {'Cr':<5} {'Sel%':<6} {'ExpPts':<7} {'Var':<5} {'C/VC'}")
    print("-" * 70)
    for pl in sorted(team["players"], key=lambda x: -x.get("expected_points", 0)):
        cvc = "C" if pl.get("is_captain") else ("VC" if pl.get("is_vice_captain") else "")
        print(f"{pl.get('player', pl.get('name', 'Unknown')):<22} "
              f"{pl.get('role', ''):<5} {pl.get('team', ''):<16} "
              f"{pl.get('credit', 0):<5.1f} {pl.get('projected_sel_pct', 0):<6.1f} "
              f"{pl.get('expected_points', 0):<7.2f} {pl.get('variance_score', 0):<5.2f} {cvc}")


if __name__ == "__main__":
    # A multi-team, hardcoded men's roster is retained only as a regression demo.
    # It must never be presented as the current WBBL player pool.
    import os
    if os.getenv("CRICKET_DEMO_MODE") != "1":
        raise SystemExit(
            "Demo-only pipeline disabled by default. Set CRICKET_DEMO_MODE=1 "
            "for explicitly synthetic runs; use the verified fixture API for real matches."
        )
    run_pipeline()
