from __future__ import annotations

import duckdb

from .config import settings

SCHEMA = """
CREATE TABLE IF NOT EXISTS matches (
  match_id TEXT PRIMARY KEY, series_id TEXT, fmt TEXT, venue TEXT,
  team_a TEXT, team_b TEXT, start_utc TIMESTAMP, status TEXT,
  toss_winner TEXT, toss_decision TEXT, pitch_class TEXT, par_score INT,
  updated_at TIMESTAMP DEFAULT now());

CREATE TABLE IF NOT EXISTS players (
  player_id TEXT PRIMARY KEY, name TEXT, short_name TEXT, team TEXT,
  role TEXT, bat_pos INT, overseas BOOL, credit DOUBLE,
  is_xi BOOL DEFAULT FALSE);

CREATE TABLE IF NOT EXISTS player_alias (alias TEXT PRIMARY KEY, player_id TEXT);

CREATE TABLE IF NOT EXISTS ownership (
  match_id TEXT, player_id TEXT, own_pct DOUBLE, captured_at TIMESTAMP,
  PRIMARY KEY (match_id, player_id));

CREATE TABLE IF NOT EXISTS ball_by_ball (
  match_id TEXT, innings INT, over INT, ball INT, batter_id TEXT,
  bowler_id TEXT, bat_style TEXT, bowl_style TEXT, runs INT,
  outcome TEXT, phase TEXT, venue TEXT, fmt TEXT, match_date DATE,
  PRIMARY KEY (match_id, innings, over, ball));

CREATE TABLE IF NOT EXISTS scorecards (
  match_id TEXT, player_id TEXT, venue TEXT, role TEXT,
  runs INT, balls INT, fours INT, sixes INT, out BOOL, batted BOOL,
  balls_bowled INT, runs_conceded INT, wickets INT, lbw_bowled INT,
  maidens INT, catches INT, stumpings INT, runout_direct INT,
  runout_indirect INT, points DOUBLE,
  PRIMARY KEY (match_id, player_id));

CREATE TABLE IF NOT EXISTS projections (
  match_id TEXT, player_id TEXT, proj DOUBLE, sd DOUBLE, boom DOUBLE,
  bust DOUBLE, own_pct DOUBLE, leverage DOUBLE, generated_at TIMESTAMP,
  PRIMARY KEY (match_id, player_id));

CREATE TABLE IF NOT EXISTS lineups (
  match_id TEXT, portfolio TEXT, lineup_id INT, players JSON, captain TEXT,
  vice TEXT, p_rank1 DOUBLE, p_top10 DOUBLE, p_top100 DOUBLE,
  avg_rank DOUBLE, created_at TIMESTAMP DEFAULT now(),
  PRIMARY KEY (match_id, portfolio, lineup_id));

CREATE TABLE IF NOT EXISTS results (
  match_id TEXT, player_id TEXT, actual_points DOUBLE,
  PRIMARY KEY (match_id, player_id));
"""


def connect(read_only: bool = False):
    settings().ensure_dirs()
    con = duckdb.connect(str(settings().db_path), read_only=read_only)
    con.execute("PRAGMA threads=4")
    return con


def init():
    con = connect()
    con.execute(SCHEMA)
    con.close()
    return settings().db_path


def upsert(con, table: str, df):
    if df is None or len(df) == 0:
        return 0
    con.register("_tmp", df)
    cols = ", ".join(df.columns)
    con.execute(f"INSERT OR REPLACE INTO {table} ({cols}) SELECT {cols} FROM _tmp")
    con.unregister("_tmp")
    return len(df)
