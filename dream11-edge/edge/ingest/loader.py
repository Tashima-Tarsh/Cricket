"""Push ingested data into DuckDB. Idempotent."""
from __future__ import annotations
import pandas as pd
from .. import db


def load_balls(df: pd.DataFrame) -> int:
    if df is None or not len(df):
        return 0
    con = db.connect()
    n = db.upsert(con, "ball_by_ball", df)
    con.close()
    return n


def load_matches(df: pd.DataFrame) -> int:
    if df is None or not len(df):
        return 0
    con = db.connect()
    n = db.upsert(con, "matches", df)
    con.close()
    return n


def history(limit: int = 200000) -> pd.DataFrame:
    con = db.connect()
    try:
        return con.execute(
            f"SELECT * FROM ball_by_ball ORDER BY match_date DESC LIMIT {limit}").df()
    except Exception:
        return pd.DataFrame()
    finally:
        con.close()


def scorecard_history() -> pd.DataFrame:
    con = db.connect()
    try:
        return con.execute("SELECT * FROM scorecards").df()
    except Exception:
        return pd.DataFrame()
    finally:
        con.close()

