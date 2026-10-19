import os
import glob
import json
import time
import duckdb

db_path = "d:/cricket/data/cricsheet_wt20.duckdb"
json_dir = "d:/cricket/data/cricsheet/t20s_female"

print(f"Initializing DuckDB at {db_path}...", flush=True)
con = duckdb.connect(db_path)

# Create schema
con.execute("""
CREATE TABLE IF NOT EXISTS matches (
    match_id VARCHAR PRIMARY KEY,
    match_date DATE,
    venue VARCHAR,
    city VARCHAR,
    team1 VARCHAR,
    team2 VARCHAR,
    toss_winner VARCHAR,
    toss_decision VARCHAR,
    winner VARCHAR,
    win_by_runs INTEGER,
    win_by_wickets INTEGER,
    player_of_match VARCHAR
);

CREATE TABLE IF NOT EXISTS deliveries (
    match_id VARCHAR,
    innings INTEGER,
    over INTEGER,
    ball INTEGER,
    batter VARCHAR,
    non_striker VARCHAR,
    bowler VARCHAR,
    runs_batter INTEGER,
    runs_extras INTEGER,
    runs_total INTEGER,
    is_wicket BOOLEAN,
    wicket_type VARCHAR,
    player_dismissed VARCHAR,
    fielder VARCHAR,
    batting_team VARCHAR,
    bowling_team VARCHAR,
    match_date DATE,
    venue VARCHAR
);

CREATE INDEX IF NOT EXISTS idx_deliv_batter ON deliveries(batter);
CREATE INDEX IF NOT EXISTS idx_deliv_bowler ON deliveries(bowler);
CREATE INDEX IF NOT EXISTS idx_deliv_match ON deliveries(match_id);
""")

json_files = glob.glob(os.path.join(json_dir, "*.json"))
print(f"Found {len(json_files)} match files to index...", flush=True)

t0 = time.time()
match_rows = []
delivery_rows = []
batch_size = 200

# Clear existing
con.execute("DELETE FROM deliveries;")
con.execute("DELETE FROM matches;")

for idx, fpath in enumerate(json_files):
    try:
        with open(fpath, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        info = data.get("info", {})
        match_id = os.path.splitext(os.path.basename(fpath))[0]
        
        dates = info.get("dates", [])
        m_date = dates[0] if dates else "2020-01-01"
        venue = info.get("venue", "Unknown Venue")
        city = info.get("city", "")
        teams = info.get("teams", ["Team A", "Team B"])
        team1 = teams[0] if len(teams) > 0 else "Team A"
        team2 = teams[1] if len(teams) > 1 else "Team B"
        toss = info.get("toss", {})
        toss_winner = toss.get("winner", "")
        toss_decision = toss.get("decision", "")
        outcome = info.get("outcome", {})
        winner = outcome.get("winner", "")
        win_by_runs = outcome.get("by", {}).get("runs", 0)
        win_by_wickets = outcome.get("by", {}).get("wickets", 0)
        pom = (info.get("player_of_match") or [""])[0] if info.get("player_of_match") else ""

        match_rows.append((
            match_id, m_date, venue, city, team1, team2,
            toss_winner, toss_decision, winner, win_by_runs, win_by_wickets, pom
        ))

        # Innings
        innings_list = data.get("innings", [])
        for inn_idx, inn in enumerate(innings_list):
            batting_team = inn.get("team", "")
            bowling_team = team2 if batting_team == team1 else team1
            overs = inn.get("overs", [])
            for over_obj in overs:
                over_num = over_obj.get("over", 0)
                deliveries = over_obj.get("deliveries", [])
                for b_idx, d in enumerate(deliveries):
                    batter = d.get("batter", "")
                    non_striker = d.get("non_striker", "")
                    bowler = d.get("bowler", "")
                    runs_obj = d.get("runs", {})
                    r_bat = runs_obj.get("batter", 0)
                    r_ext = runs_obj.get("extras", 0)
                    r_tot = runs_obj.get("total", 0)
                    
                    wickets = d.get("wickets", [])
                    is_wkt = len(wickets) > 0
                    w_type = wickets[0].get("kind", "") if is_wkt else ""
                    p_dism = wickets[0].get("player_out", "") if is_wkt else ""
                    fielders = wickets[0].get("fielders", []) if is_wkt else []
                    f_name = fielders[0].get("name", "") if fielders else ""

                    delivery_rows.append((
                        match_id, inn_idx + 1, over_num, b_idx + 1,
                        batter, non_striker, bowler, r_bat, r_ext, r_tot,
                        is_wkt, w_type, p_dism, f_name,
                        batting_team, bowling_team, m_date, venue
                    ))

        if len(match_rows) >= batch_size:
            con.executemany("INSERT INTO matches VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", match_rows)
            con.executemany("INSERT INTO deliveries VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", delivery_rows)
            match_rows.clear()
            delivery_rows.clear()
            print(f"Processed {idx+1}/{len(json_files)} matches...", flush=True)

    except Exception as e:
        pass

if match_rows:
    con.executemany("INSERT INTO matches VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", match_rows)
    con.executemany("INSERT INTO deliveries VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", delivery_rows)

tot_matches = con.execute("SELECT count(*) FROM matches").fetchone()[0]
tot_deliveries = con.execute("SELECT count(*) FROM deliveries").fetchone()[0]
print(f"DuckDB Build Complete in {time.time()-t0:.1f}s!", flush=True)
print(f"Indexed {tot_matches} Women's T20 matches, {tot_deliveries} ball-by-ball deliveries!", flush=True)
con.close()

