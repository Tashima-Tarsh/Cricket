"""Strict out-of-time, whole-date cricket prediction evaluation.

Target = observed PARTIAL run/4/6/wicket/dot scoring proxy, NOT Dream11
final fantasy points. The target fixture's participants are known only
retrospectively: no pre-toss availability or rank calibration is implied.
"""
from collections import defaultdict
from datetime import date
from pathlib import Path
from typing import Iterable, Optional
import argparse
import json
import math
import duckdb
import numpy as np

from .capabilities.c19_backtesting import _SCORE_PROXY_SQL


def build_historical_feature_rows(rows: Iterable[tuple], min_history: int = 3):
    """Only previous dates can contribute to feature vectors, even doubleheaders."""
    records = sorted(rows, key=lambda x: (x[1], str(x[0]), str(x[2])))
    history = defaultdict(list)
    output = []
    index = 0
    while index < len(records):
        date_of_game = records[index][1]
        day = []
        while index < len(records) and records[index][1] == date_of_game:
            day.append(records[index])
            index += 1
        for match_id, match_date, player, points in day:
            prior = history[player]
            if len(prior) < min_history:
                continue
            values = np.array([p for _, p in prior], dtype=float)
            recent = values[-5:]
            features = (
                float(np.mean(values)),
                float(np.mean(recent)),
                float(np.std(recent)),
                float(np.median(values)),
                float(len(prior)),
                float(min(365, max(0, (match_date - prior[-1][0]).days))),
            )
            output.append({
                "match_id": str(match_id), "date": match_date, "player": str(player),
                "features": features, "baseline": float(np.mean(recent)),
                "observed_partial_points": float(points),
                "history_count": len(prior),
                "latest_input_date": prior[-1][0],
            })
        # Crucial: no match on the same day is part of training for this day.
        for _, match_date, player, points in day:
            history[player].append((match_date, float(points)))
    return output


def _metrics(y, pred):
    residual = np.asarray(pred, dtype=float) - np.asarray(y, dtype=float)
    y = np.asarray(y, dtype=float)
    rmse = math.sqrt(float(np.mean(residual * residual)))
    var = float(np.sum((y - float(np.mean(y))) ** 2))
    return {"n": len(y), "mae": round(float(np.mean(np.abs(residual))), 4),
            "rmse": round(rmse, 4), "mean_signed_bias": round(float(np.mean(residual)), 4),
            "r2": round(1.0 - float(np.sum(residual * residual)) / var, 4) if var > 0 else None}


def evaluate_historical_rows(rows: Iterable[tuple], min_train: int = 300,
                             min_test: int = 100) -> dict:
    examples = build_historical_feature_rows(rows)
    dates = sorted({row["date"] for row in examples})
    if len(dates) < 12 or len(examples) < min_train + min_test * 2:
        return {"status": "INSUFFICIENT_HISTORY", "eligible_examples": len(examples),
                "unique_dates": len(dates), "contest_probability_calibrated": False}
    train_end = max(1, int(len(dates) * 0.65))
    calibration_end = max(train_end + 1, int(len(dates) * 0.80))
    train, cal, test = (
        [r for r in examples if r["date"] < dates[train_end]],
        [r for r in examples if dates[train_end] <= r["date"] < dates[calibration_end]],
        [r for r in examples if r["date"] >= dates[calibration_end]],
    )
    if len(train) < min_train or len(cal) < min_test or len(test) < min_test:
        return {"status": "INSUFFICIENT_SPLITS", "eligible_examples": len(examples),
                "train": len(train), "calibration": len(cal), "test": len(test),
                "contest_probability_calibrated": False}

    from xgboost import XGBRegressor
    model = XGBRegressor(
        n_estimators=120, max_depth=3, learning_rate=0.05,
        n_jobs=1, random_state=42, tree_method="hist",
        objective="reg:squarederror",
    )
    features = lambda group: np.asarray([r["features"] for r in group], dtype=float)
    outcomes = lambda group: np.asarray(
        [r["observed_partial_points"] for r in group], dtype=float
    )
    model.fit(features(train), outcomes(train))
    cal_pred = model.predict(features(cal))
    test_pred = model.predict(features(test))
    true_test = outcomes(test)
    # Calibration is fitted exclusively on held-out validation dates.
    # Test data do not inform interval width/centering.
    residuals = outcomes(cal) - cal_pred
    low, high = [float(q) for q in np.quantile(residuals, [0.05, 0.95])]
    coverage = float(np.mean(
        (true_test >= test_pred + low) & (true_test <= test_pred + high)
    ))
    benchmark = _metrics(true_test, [r["baseline"] for r in test])
    xgb = _metrics(true_test, test_pred)
    lift = ((benchmark["mae"] - xgb["mae"]) / benchmark["mae"]
            if benchmark["mae"] > 0 else 0)
    # Do not declare the model validated merely for having computed metrics.
    skill = (xgb["r2"] is not None and xgb["r2"] > 0.05 and lift > 0.02)
    return {
        "status": "OUT_OF_TIME_SKILL_ESTABLISHED_PARTIAL_PROXY" if skill
                  else "OUT_OF_TIME_SKILL_NOT_ESTABLISHED",
        "target": "CRICSHEET_PARTIAL_SCORE_PROXY_NOT_DREAM11_POINTS",
        "conditioning": "OBSERVED_PARTICIPANTS_NOT_VERIFIED_PREGAME_XI",
        "train_samples": len(train), "calibration_samples": len(cal),
        "unseen_test_samples": len(test),
        "last_train_date": str(train[-1]["date"]),
        "first_calibration_date": str(cal[0]["date"]),
        "first_unseen_test_date": str(test[0]["date"]),
        "last_unseen_test_date": str(test[-1]["date"]),
        "features": "strictly previous dates; no same-day results",
        "model": "XGBRegressor_120_depth3",
        "model_metrics_unseen": xgb,
        "last5_mean_baseline_unseen": benchmark,
        "mae_relative_gain_vs_baseline": round(lift, 4),
        "validation_interval_nominal_coverage": 0.90,
        "validation_interval_signed_error_quantiles": [round(low, 3), round(high, 3)],
        "unseen_test_interval_coverage": round(coverage, 4),
        "contest_probability_calibrated": False,
        "rank_1_probability_available": False,
        "current_deployed_model_validated": False,
        "source": "t20.duckdb + same-day-excluded Cricsheet partial_score",
        "scope": "Research evaluation only; no model was retrained or deployed",
    }


def audit_database(db_path: Optional[Path] = None) -> dict:
    path = Path(db_path) if db_path else Path(__file__).resolve().parent.parent / "t20.duckdb"
    if not path.is_file():
        return {"status": "DATA_UNAVAILABLE", "database": str(path),
                "contest_probability_calibrated": False}
    with duckdb.connect(str(path), read_only=True) as con:
        latest_date = con.execute(
            "SELECT MAX(CAST(date AS DATE)) FROM matches WHERE date IS NOT NULL"
        ).fetchone()[0]
        if latest_date is None:
            return {"status": "HISTORICAL_DATES_UNAVAILABLE",
                    "contest_probability_calibrated": False}
        rows = con.execute(_SCORE_PROXY_SQL, [latest_date, latest_date]).fetchall()
    result = evaluate_historical_rows(rows)
    result["fixture_rows_read"] = len(rows)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = audit_database()
    text = json.dumps(result, indent=2)
    print(text)
    if args.output:
        args.output.write_text(text + "\n", encoding="utf-8")
    if result["status"] in {"DATA_UNAVAILABLE", "HISTORICAL_DATES_UNAVAILABLE"}:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
