"""Fit empirical distribution families from Cricsheet historical deliveries."""
from pathlib import Path
import sys
import numpy as np
import pandas as pd
import duckdb

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from edge.config import settings
from edge.model import distributions as D
from edge.score import BatLine, BowlLine, FieldLine, points


def fit_and_save_families():
    db_path = settings().data_dir / "cricsheet_wt20.duckdb"
    if not db_path.exists():
        alt = ROOT.parent / "data" / "cricsheet_wt20.duckdb"
        if alt.exists():
            db_path = alt
    
    con = duckdb.connect(str(db_path), read_only=True)
    df = con.execute("""
        SELECT match_id, innings, over, ball,
               batter, non_striker, bowler,
               runs_batter, runs_extras, runs_total,
               is_wicket, wicket_type, player_dismissed, fielder
        FROM deliveries
    """).df()
    con.close()

    print(f"Loaded {len(df)} deliveries from {db_path.name}")

    # Aggregate by match and player
    # 1. Batting
    bat = df.groupby(["match_id", "batter"]).agg(
        runs=("runs_batter", "sum"),
        balls=("runs_batter", "count"),
        fours=("runs_batter", lambda s: (s == 4).sum()),
        sixes=("runs_batter", lambda s: (s == 6).sum())
    ).reset_index().rename(columns={"batter": "player"})

    dismissals = df[df["is_wicket"] == True].groupby(["match_id", "player_dismissed"]).size().reset_index(name="outs").rename(columns={"player_dismissed": "player"})
    bat = bat.merge(dismissals, on=["match_id", "player"], how="left")
    bat["out"] = bat["outs"].fillna(0) > 0

    # 2. Bowling
    bowl = df.groupby(["match_id", "bowler"]).agg(
        balls=("ball", "count"),
        runs=("runs_total", "sum"),
        wickets=("is_wicket", lambda s: s.sum()),
        lbw_bowled=("wicket_type", lambda s: s.isin(["bowled", "lbw"]).sum()),
        dots=("runs_total", lambda s: (s == 0).sum())
    ).reset_index().rename(columns={"bowler": "player"})

    # 3. Fielding
    catches = df[df["wicket_type"] == "caught"].groupby(["match_id", "fielder"]).size().reset_index(name="catches").rename(columns={"fielder": "player"})
    stumpings = df[df["wicket_type"] == "stumped"].groupby(["match_id", "fielder"]).size().reset_index(name="stumpings").rename(columns={"fielder": "player"})
    runouts = df[df["wicket_type"] == "run out"].groupby(["match_id", "fielder"]).size().reset_index(name="runouts").rename(columns={"fielder": "player"})

    # Combine into player-match records
    all_players = set(zip(df["match_id"], df["batter"])).union(set(zip(df["match_id"], df["bowler"])))
    pm_df = pd.DataFrame(list(all_players), columns=["match_id", "player"])

    pm_df = pm_df.merge(bat, on=["match_id", "player"], how="left")
    pm_df = pm_df.merge(bowl, on=["match_id", "player"], how="left")
    pm_df = pm_df.merge(catches, on=["match_id", "player"], how="left")
    pm_df = pm_df.merge(stumpings, on=["match_id", "player"], how="left")
    pm_df = pm_df.merge(runouts, on=["match_id", "player"], how="left")

    pm_df = pm_df.fillna(0)

    # Compute official fantasy points per player-match
    scores = []
    roles = []
    for row in pm_df.itertuples():
        b_balls = int(getattr(row, "balls_x", 0))
        b_runs = int(getattr(row, "runs_x", 0))
        w_balls = int(getattr(row, "balls_y", 0))
        w_runs = int(getattr(row, "runs_y", 0))
        fours = int(getattr(row, "fours", 0))
        sixes = int(getattr(row, "sixes", 0))
        is_out = bool(getattr(row, "out", False))
        wickets = int(getattr(row, "wickets", 0))
        lbw_bowled = int(getattr(row, "lbw_bowled", 0))
        dots = int(getattr(row, "dots", 0))
        catches_count = int(getattr(row, "catches", 0))
        stumpings_count = int(getattr(row, "stumpings", 0))
        runouts_count = int(getattr(row, "runouts", 0))
        
        bat_line = BatLine(runs=b_runs, balls=b_balls, fours=fours, sixes=sixes, out=is_out, batted=(b_balls > 0))
        bowl_line = BowlLine(balls=w_balls, runs=w_runs, wickets=wickets, lbw_bowled=lbw_bowled, dots=dots)
        fld_line = FieldLine(catches=catches_count, stumpings=stumpings_count, runout_direct=runouts_count)
        
        pts = points(bat_line, bowl_line, fld_line, is_xi=True)
        scores.append(pts)

        # Role heuristic
        if int(row.stumpings) > 0:
            role = "WK"
        elif w_balls >= 12 and b_balls >= 10:
            role = "AR"
        elif w_balls >= 12:
            role = "BOWL"
        else:
            role = "BAT"
        roles.append(role)

    pm_df["score"] = scores
    pm_df["role"] = roles

    # Fit empirical distributions by (role, window)
    families = {}
    edges = settings().model.window_edges
    roles_list = ["BAT", "BOWL", "AR", "WK"]

    for r in roles_list:
        sub = pm_df[pm_df["role"] == r]
        if len(sub) == 0:
            sub = pm_df
        for lo, hi in zip(edges, edges[1:]):
            cohort = sub[(sub["score"] >= lo) & (sub["score"] < hi)]["score"].values
            if len(cohort) < D.MIN_COHORT:
                # Expand slightly to fit a credible empirical family
                cohort = sub["score"].values
            fam = D.Family.fit_best(cohort)
            families[(r, lo)] = fam
            print(f"Fitted (Role={r:4s}, Window={lo:3d}): Family={fam.name:10s}, KS={fam.ks:.4f}, Sample Size={len(cohort)}")

    # Save to artifacts/families.pkl
    D.save(families)
    print(f"Successfully saved {len(families)} empirical families to {D._path()}")


if __name__ == "__main__":
    fit_and_save_families()
