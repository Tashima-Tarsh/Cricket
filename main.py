"""
BBL/WBBL Grand League Engine — orchestrator.
End-to-end pipeline:
  1. Load historical ball-by-ball data (Cricsheet + synthetic fallback)
  2. Build correlation matrix (bowler-batter rivalries + partnerships)
  3. Feature engineer (venue quirks, travel fatigue, phase matchups)
  4. Train dual LightGBM (mean + variance)
  5. Predict upcoming players
  6. Generate Grand League teams via OR-Tools CP-SAT
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
        {"name": "Steve_Smith", "role": "BAT", "team": "Sydney Sixers", "credit": 11.0, "projected_sel_pct": 85.0},
        {"name": "David_Warner", "role": "BAT", "team": "Sydney Thunder", "credit": 10.5, "projected_sel_pct": 78.0},
        {"name": "Glenn_Maxwell", "role": "AR", "team": "Melbourne Stars", "credit": 10.0, "projected_sel_pct": 72.0},
        {"name": "Marcus_Stoinis", "role": "AR", "team": "Melbourne Stars", "credit": 9.5, "projected_sel_pct": 65.0},
        {"name": "Rashid_Khan", "role": "BOWL", "team": "Adelaide Strikers", "credit": 10.5, "projected_sel_pct": 88.0},
        {"name": "Pat_Cummins", "role": "BOWL", "team": "Sydney Thunder", "credit": 10.0, "projected_sel_pct": 82.0},
        {"name": "Josh_Hazlewood", "role": "BOWL", "team": "Sydney Sixers", "credit": 9.5, "projected_sel_pct": 70.0},
        {"name": "Adam_Zampa", "role": "BOWL", "team": "Sydney Sixers", "credit": 9.0, "projected_sel_pct": 60.0},
        {"name": "Matthew_Wade", "role": "WK", "team": "Hobart Hurricanes", "credit": 9.0, "projected_sel_pct": 50.0},
        {"name": "Alex_Carey", "role": "WK", "team": "Adelaide Strikers", "credit": 8.5, "projected_sel_pct": 40.0},
        {"name": "Nick_Madron", "role": "WK", "team": "Perth Scorchers", "credit": 8.5, "projected_sel_pct": 35.0},
        {"name": "Tim_David", "role": "BAT", "team": "Perth Scorchers", "credit": 8.5, "projected_sel_pct": 30.0},
        {"name": "Colin_Munro", "role": "BAT", "team": "Perth Scorchers", "credit": 8.0, "projected_sel_pct": 22.0},  # differential
        {"name": "Chris_Lynn", "role": "BAT", "team": "Brisbane Heat", "credit": 8.0, "projected_sel_pct": 18.0},   # differential
        {"name": "Ben_McDermott", "role": "BAT", "team": "Hobart Hurricanes", "credit": 8.0, "projected_sel_pct": 25.0},
        {"name": "D'Arcy_Short", "role": "AR", "team": "Hobart Hurricanes", "credit": 8.0, "projected_sel_pct": 15.0},
        {"name": "Ashton_Turner", "role": "AR", "team": "Perth Scorchers", "credit": 8.0, "projected_sel_pct": 10.0},  # differential
        {"name": "Nathan_Coulter_Nile", "role": "BOWL", "team": "Melbourne Stars", "credit": 8.5, "projected_sel_pct": 12.0},
        {"name": "Jason_Behrendorff", "role": "BOWL", "team": "Perth Scorchers", "credit": 8.0, "projected_sel_pct": 8.0},   # differential
        {"name": "Kane_Richardson", "role": "BOWL", "team": "Melbourne Renegades", "credit": 8.0, "projected_sel_pct": 9.0},  # differential
    ]


def run_pipeline(use_cricsheet: bool = True, max_matches: int = 100):
    logger.info("=" * 70)
    logger.info("🏏 BBL/WBBL GRAND LEAGUE ENGINE")
    logger.info("=" * 70)

    # ---- 1. Load historical data ----
    logger.info("\n[1/6] Loading BBL/WBBL ball-by-ball data...")
    balls_df = load_bbl_data(max_matches=max_matches, use_synthetic_fallback=True)
    logger.info("      Loaded %d ball-by-ball records", len(balls_df))

    # ---- 2. Correlation matrix ----
    logger.info("\n[2/6] Building correlation matrix...")
    correlation = CorrelationMatrix(balls_df)
    summary = correlation.summary()
    logger.info(
        "      %d bowler-batter rivalries | %d partnerships",
        summary["bowler_batter_rivalries"], summary["partnerships"],
    )

    # ---- 3. Feature engineering ----
    logger.info("\n[3/6] Engineering features...")
    engineer = BBLFeatureEngineer()
    upcoming_players = load_upcoming_bbl_players()
    train_df = engineer.build_ml_features(balls_df, upcoming_players)
    logger.info("      Built %d feature rows", len(train_df))

    # ---- 4. Train predictor ----
    logger.info("\n[4/6] Training dual LightGBM (mean + variance)...")
    predictor = CricketPredictor()
    train_rows = train_df[train_df["match_id"] != "upcoming"]
    if not train_rows.empty:
        metrics = predictor.train(train_rows)
        logger.info("      val_rmse=%.4f n_train=%d", metrics["val_rmse"], metrics["n_train"])
        predictor.save("models/")
    else:
        logger.warning("No training rows; skipping training")

    # ---- 5. Predict upcoming ----
    logger.info("\n[5/6] Predicting upcoming players...")
    upcoming_df = train_df[train_df["match_id"] == "upcoming"].copy()
    if upcoming_df.empty:
        # Build fresh features for upcoming players only
        upcoming_df = engineer._default_features(upcoming_players)
    pred_df = predictor.predict(upcoming_df)
    logger.info("      Predicted %d players", len(pred_df))

    # ---- 6. Optimize ----
    logger.info("\n[6/6] Generating Grand League teams via OR-Tools CP-SAT...")
    optimizer = GrandLeagueOptimizer(pred_df, correlation)
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
    run_pipeline()
