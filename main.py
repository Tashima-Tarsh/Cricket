"""
Main entry point — Automated Fantasy Cricket Grand League Engine.

Pipeline:
  1. Load historical ball-by-ball data (Cricsheet, synthetic fallback)
  2. Feature-engineer into per-player ML frame
  3. Train / auto-retrain LightGBM mean + variance models (versioned registry)
  4. Build features for upcoming-match players
  5. Generate Grand League teams via OR-Tools CP-SAT
  6. Print top teams + portfolio summary
"""
import sys
import logging
import pandas as pd

sys.stdout.reconfigure(encoding="utf-8")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("fantasy_cricket")

from data_loader import load_upcoming_match_players
from cricsheet_loader import load_historical_cricsheet
from feature_engineer import FantasyFeatureEngineer
from model_pipeline import ModelPipeline
from optimizer import GrandLeagueOptimizer, print_team

N_TEAMS = 7
SCENARIOS = ["balanced", "top_collapse", "death_bowler_special"]


def run_pipeline(use_cricsheet: bool = True, max_matches: int | None = None):
    logger.info("=" * 70)
    logger.info("🏏 FANTASY CRICKET GRAND LEAGUE ENGINE (Automated Pipeline)")
    logger.info("=" * 70)

    # ---- STEP 1: Load historical data ----
    logger.info("\n[1/6] Loading historical ball-by-ball data...")
    if use_cricsheet:
        hist_balls = load_historical_cricsheet(
            source="international_men", max_matches=max_matches
        )
    else:
        from data_loader import generate_sample_historical_data
        hist_balls = generate_sample_historical_data(n_matches=50)

    # Synthetic data carries a fantasy_points column; real ball-by-ball does not.
    # Convert synthetic rows into ball-by-ball schema so the feature engine works uniformly.
    if "fantasy_points" in hist_balls.columns:
        hist_balls = _synthetic_to_balls(hist_balls)
    logger.info("      Loaded %d ball-by-ball records", len(hist_balls))

    # ---- STEP 2: Feature engineering ----
    logger.info("\n[2/6] Engineering per-player fantasy features...")
    engineer = FantasyFeatureEngineer()
    train_df = engineer.build_training_frame(hist_balls)
    logger.info("      Built %d player-match feature rows", len(train_df))

    # ---- STEP 3: Automated model training ----
    logger.info("\n[3/6] Training LightGBM predictor (automated pipeline)...")
    pipeline = ModelPipeline(model_dir="models")
    should, reason = pipeline.should_retrain(train_df, min_new_matches=5)
    logger.info("      Retrain decision: %s (%s)", should, reason)
    metrics = pipeline.train(train_df, force=True)
    logger.info("      Model v%s saved | val_rmse=%.4f | n_train=%d",
                metrics["version"], metrics["val_rmse"], metrics["n_train"])

    # ---- STEP 4: Load upcoming players + build features ----
    logger.info("\n[4/6] Loading upcoming match players...")
    upcoming_players = load_upcoming_match_players()
    upcoming_df = engineer.predict_upcoming_features(upcoming_players, train_df)
    logger.info("      Built features for %d upcoming players", len(upcoming_df))

    # ---- STEP 5: Predict expected points + variance ----
    logger.info("\n[5/6] Predicting expected points + variance...")
    pipeline.load_latest()  # ensure latest model loaded in-memory
    pred_df = pipeline.predictor.predict(upcoming_df)
    logger.info("      Predicted for %d players", len(pred_df))

    # ---- STEP 6: Generate Grand League teams ----
    logger.info("\n[6/6] Generating Grand League teams via OR-Tools CP-SAT...")
    optimizer = GrandLeagueOptimizer(pred_df)
    all_teams = []
    for sc in SCENARIOS:
        teams = optimizer.optimize(n_teams=N_TEAMS, scenario=sc)
        all_teams.extend(teams)

    all_teams.sort(key=lambda t: -t["projected_points"])

    logger.info("\n✅ Generated %d teams. Showing TOP 5:", len(all_teams))
    for team in all_teams[:5]:
        print_team(team)

    # Portfolio summary
    logger.info("\n%s", "=" * 70)
    logger.info("📊 PORTFOLIO SUMMARY")
    logger.info("=" * 70)
    logger.info("Total teams generated: %d", len(all_teams))
    logger.info("Best projected points:  %s", all_teams[0]["projected_points"])
    logger.info("Worst projected points: %s", all_teams[-1]["projected_points"])
    avg_diff = sum(t["n_differentials"] for t in all_teams) / len(all_teams)
    logger.info("Avg differentials per team: %.1f", avg_diff)
    logger.info("\n💡 Play ALL %d teams in the same Grand League.", len(all_teams))
    logger.info("=" * 70)

    return all_teams, metrics


def _synthetic_to_balls(df: pd.DataFrame) -> pd.DataFrame:
    """Convert synthetic player-match rows into ball-by-ball-like schema
    so the feature engineer can process them uniformly."""
    rows = []
    for _, r in df.iterrows():
        # Create ~3 balls per player-match to give the aggregator something to work with
        for ball_idx in range(3):
            rows.append({
                "match_id": r["match_id"],
                "date": "2024-01-01",
                "innings": 1,
                "over": float(ball_idx + 1),
                "ball": 1.0,
                "batter": r["player"],
                "non_striker": "",
                "bowler": r["player"],
                "fielder": "",
                "runs_batter": max(0, int(r["fantasy_points"]) // 3),
                "runs_extra": 0,
                "runs_total": max(0, int(r["fantasy_points"]) // 3),
                "is_wicket": 0,
                "wicket_type": "",
                "batting_team": r["team"],
                "bowling_team": "OPP",
            })
    return pd.DataFrame(rows)


if __name__ == "__main__":
    run_pipeline(use_cricsheet=True)
