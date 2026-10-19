"""Cricsheet DuckDB High-Performance Loader and Parquet Engine.
Loads Cricsheet JSON archives (e.g. ipl_json.zip, t20s_json.zip) directly into DuckDB tables:
- matches
- deliveries
- canonical_players
"""

import sys
import os
import json
import zipfile
from pathlib import Path
from typing import Dict, Any, List, Optional
import duckdb
import polars as pl

if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

DB_PATH = Path(__file__).parent / "t20.duckdb"

def init_duckdb_schema(con: duckdb.DuckDBPyConnection):
    """Initializes normalized relational schema matching the blueprint."""
    con.execute("""
        CREATE TABLE IF NOT EXISTS matches (
            match_id VARCHAR PRIMARY KEY,
            date VARCHAR,
            season VARCHAR,
            match_type VARCHAR,
            gender VARCHAR,
            event VARCHAR,
            venue_id VARCHAR,
            venue_name VARCHAR,
            city VARCHAR,
            team_a VARCHAR,
            team_b VARCHAR,
            toss_winner VARCHAR,
            toss_decision VARCHAR,
            winner VARCHAR,
            win_by_runs INTEGER,
            win_by_wickets INTEGER,
            balls_per_over INTEGER DEFAULT 6
        );

        CREATE TABLE IF NOT EXISTS deliveries (
            match_id VARCHAR,
            innings INTEGER,
            over INTEGER,
            ball INTEGER,
            batter VARCHAR,
            bowler VARCHAR,
            non_striker VARCHAR,
            runs_batter INTEGER,
            runs_extras INTEGER,
            runs_total INTEGER,
            is_wicket BOOLEAN,
            wicket_type VARCHAR,
            player_dismissed VARCHAR,
            phase VARCHAR, -- Powerplay (1-6), Middle (7-15), Death (16-20)
            PRIMARY KEY (match_id, innings, over, ball)
        );

        CREATE TABLE IF NOT EXISTS canonical_players (
            canonical_name VARCHAR PRIMARY KEY,
            cricsheet_id VARCHAR,
            batting_style VARCHAR,
            bowling_style VARCHAR,
            primary_role VARCHAR,
            gender VARCHAR
        );
    """)

def load_zip_into_duckdb(zip_path: str, max_matches: Optional[int] = None) -> Dict[str, int]:
    """Ingests match and delivery records from a Cricsheet JSON zip file."""
    zpath = Path(zip_path)
    if not zpath.exists():
        raise FileNotFoundError(f"Zip file not found: {zpath}")

    con = duckdb.connect(str(DB_PATH))
    init_duckdb_schema(con)

    existing_matches = set(r[0] for r in con.execute("SELECT match_id FROM matches").fetchall())

    matches_to_insert = []
    deliveries_to_insert = []

    print(f"Reading Cricsheet zip: {zpath.name}...")
    with zipfile.ZipFile(zpath, "r") as z:
        file_list = [f for f in z.namelist() if f.endswith(".json") and not f.startswith("__")]
        if max_matches:
            file_list = file_list[:max_matches]

        for idx, filename in enumerate(file_list):
            match_id = Path(filename).stem
            if match_id in existing_matches:
                continue

            try:
                raw_bytes = z.read(filename)
                data = json.loads(raw_bytes.decode("utf-8"))
            except Exception as e:
                continue

            info = data.get("info", {})
            event_name = info.get("event", {}).get("name", "T20 Match") if isinstance(info.get("event"), dict) else str(info.get("event", "T20 Match"))
            teams = info.get("teams", ["Team A", "Team B"])
            toss = info.get("toss", {})
            outcome = info.get("outcome", {})
            dates = info.get("dates", ["2026-01-01"])
            venue = info.get("venue", "Unknown Venue")
            city = info.get("city", "Unknown City")
            season = str(info.get("season", "2026"))
            match_type = info.get("match_type", "T20")
            gender = info.get("gender", "male")

            winner = outcome.get("winner", None)
            by_runs = outcome.get("by", {}).get("runs", None)
            by_wickets = outcome.get("by", {}).get("wickets", None)

            matches_to_insert.append((
                match_id,
                dates[0] if dates else "2026-01-01",
                season,
                match_type,
                gender,
                event_name,
                venue.lower().replace(" ", "_"),
                venue,
                city,
                teams[0] if len(teams) > 0 else "Team A",
                teams[1] if len(teams) > 1 else "Team B",
                toss.get("winner", ""),
                toss.get("decision", ""),
                winner,
                by_runs,
                by_wickets,
                info.get("balls_per_over", 6)
            ))

            # Deliveries
            for inn_idx, innings in enumerate(data.get("innings", []), 1):
                overs = innings.get("overs", [])
                for over_data in overs:
                    over_num = over_data.get("over", 0) + 1  # 1 to 20
                    # Phase classification
                    if over_num <= 6:
                        phase = "Powerplay"
                    elif over_num <= 15:
                        phase = "Middle"
                    else:
                        phase = "Death"

                    for ball_idx, deliv in enumerate(over_data.get("deliveries", []), 1):
                        batter = deliv.get("batter", "")
                        bowler = deliv.get("bowler", "")
                        non_striker = deliv.get("non_striker", "")
                        runs = deliv.get("runs", {})
                        runs_bat = runs.get("batter", 0)
                        runs_extras = runs.get("extras", 0)
                        runs_total = runs.get("total", runs_bat + runs_extras)

                        wickets = deliv.get("wickets", [])
                        is_wicket = len(wickets) > 0
                        wicket_type = wickets[0].get("kind", None) if is_wicket else None
                        player_dismissed = wickets[0].get("player_out", None) if is_wicket else None

                        deliveries_to_insert.append((
                            match_id,
                            inn_idx,
                            over_num,
                            ball_idx,
                            batter,
                            bowler,
                            non_striker,
                            runs_bat,
                            runs_extras,
                            runs_total,
                            is_wicket,
                            wicket_type,
                            player_dismissed,
                            phase
                        ))

            if len(matches_to_insert) >= 500:
                con.executemany("INSERT OR IGNORE INTO matches VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", matches_to_insert)
                con.executemany("INSERT OR IGNORE INTO deliveries VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)", deliveries_to_insert)
                matches_to_insert.clear()
                deliveries_to_insert.clear()

        # Insert remaining
        if matches_to_insert:
            con.executemany("INSERT OR IGNORE INTO matches VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", matches_to_insert)
            matches_to_insert.clear()
        if deliveries_to_insert:
            con.executemany("INSERT OR IGNORE INTO deliveries VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)", deliveries_to_insert)
            deliveries_to_insert.clear()

    total_m = con.execute("SELECT count(*) FROM matches").fetchone()[0]
    total_d = con.execute("SELECT count(*) FROM deliveries").fetchone()[0]
    con.close()

    print(f"[OK] DuckDB Ingestion complete: {total_m} matches, {total_d} deliveries stored in {DB_PATH}.")
    return {"total_matches": total_m, "total_deliveries": total_d}

if __name__ == "__main__":
    target_zip = sys.argv[1] if len(sys.argv) > 1 else str(Path(__file__).parent / "data" / "cricsheet" / "ipl_json.zip")
    load_zip_into_duckdb(target_zip)
