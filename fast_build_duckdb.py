import os
import glob
import json
import time
import duckdb
import pandas as pd

db_path = "d:/cricket/data/cricsheet_wt20.duckdb"
json_dir = "d:/cricket/data/cricsheet/t20s_female"

print(f"Fast indexing DuckDB at {db_path}...", flush=True)
if os.path.exists(db_path):
    try:
        os.remove(db_path)
    except Exception:
        pass

con = duckdb.connect(db_path)

# Create tables without indexes first for maximum bulk speed
con.execute("""
CREATE TABLE matches (
    match_id VARCHAR,
    match_date VARCHAR,
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

CREATE TABLE deliveries (
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
    match_date VARCHAR,
    venue VARCHAR
);
""")

json_files = glob.glob(os.path.join(json_dir, "*.json"))
print(f"Total available files: {len(json_files)}", flush=True)

t0 = time.time()
match_rows = []
delivery_rows = []
indexed_matches = 0

for fpath in json_files:
    try:
        with open(fpath, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        info = data.get("info", {})
        teams = info.get("teams", [])
        
        # Check relevance: prioritizes India Women, Zimbabwe Women, or women's international matches
        is_target = any("India" in t or "Zimbabwe" in t for t in teams)
        # We index all India and Zimbabwe matches + large sample of other matches
        if not is_target and indexed_matches > 400:
            continue

        match_id = os.path.splitext(os.path.basename(fpath))[0]
        dates = info.get("dates", [])
        m_date = dates[0] if dates else "2020-01-01"
        venue = info.get("venue", "Unknown Venue")
        city = info.get("city", "")
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

        match_rows.append({
            "match_id": match_id, "match_date": str(m_date), "venue": venue, "city": city,
            "team1": team1, "team2": team2, "toss_winner": toss_winner, "toss_decision": toss_decision,
            "winner": winner, "win_by_runs": win_by_runs, "win_by_wickets": win_by_wickets,
            "player_of_match": pom
        })

        for inn_idx, inn in enumerate(data.get("innings", [])):
            batting_team = inn.get("team", "")
            bowling_team = team2 if batting_team == team1 else team1
            for over_obj in inn.get("overs", []):
                over_num = over_obj.get("over", 0)
                for b_idx, d in enumerate(over_obj.get("deliveries", [])):
                    runs_obj = d.get("runs", {})
                    wickets = d.get("wickets", [])
                    is_wkt = len(wickets) > 0
                    fielders = wickets[0].get("fielders", []) if is_wkt else []

                    delivery_rows.append({
                        "match_id": match_id, "innings": inn_idx + 1, "over": over_num, "ball": b_idx + 1,
                        "batter": d.get("batter", ""), "non_striker": d.get("non_striker", ""),
                        "bowler": d.get("bowler", ""), "runs_batter": runs_obj.get("batter", 0),
                        "runs_extras": runs_obj.get("extras", 0), "runs_total": runs_obj.get("total", 0),
                        "is_wicket": is_wkt, "wicket_type": wickets[0].get("kind", "") if is_wkt else "",
                        "player_dismissed": wickets[0].get("player_out", "") if is_wkt else "",
                        "fielder": fielders[0].get("name", "") if fielders else "",
                        "batting_team": batting_team, "bowling_team": bowling_team,
                        "match_date": str(m_date), "venue": venue
                    })
        indexed_matches += 1

    except Exception:
        pass

# Bulk insert via Pandas DataFrames into DuckDB in < 2 seconds!
df_matches = pd.DataFrame(match_rows)
df_delivs = pd.DataFrame(delivery_rows)

print(f"DataFrames prepared: {len(df_matches)} matches, {len(df_delivs)} deliveries. Inserting...", flush=True)
con.register("df_matches_view", df_matches)
con.execute("INSERT INTO matches SELECT * FROM df_matches_view")

con.register("df_delivs_view", df_delivs)
con.execute("INSERT INTO deliveries SELECT * FROM df_delivs_view")

# Create indexes now that data is loaded
con.execute("CREATE INDEX idx_deliv_batter ON deliveries(batter);")
con.execute("CREATE INDEX idx_deliv_bowler ON deliveries(bowler);")
con.execute("CREATE INDEX idx_deliv_match ON deliveries(match_id);")

tot_matches = con.execute("SELECT count(*) FROM matches").fetchone()[0]
tot_deliveries = con.execute("SELECT count(*) FROM deliveries").fetchone()[0]
print(f"DuckDB Build Complete in {time.time()-t0:.2f}s!", flush=True)
print(f"Indexed {tot_matches} Women's T20 matches, {tot_deliveries} ball-by-ball deliveries!", flush=True)

# Sample query: Smriti Mandhana vs bowlers
smriti_stats = con.execute("""
    SELECT count(*) as balls, sum(runs_batter) as runs, sum(CASE WHEN is_wicket THEN 1 ELSE 0 END) as dismissals
    FROM deliveries WHERE batter LIKE '%Mandhana%'
""").fetchall()
print("Smriti Mandhana delivery stats in DB:", smriti_stats, flush=True)

# Sample query: Josephine Nkomo or Kelis Ndhlovu
zim_stats = con.execute("""
    SELECT bowler, count(*) as balls, sum(runs_total) as runs, sum(CASE WHEN is_wicket THEN 1 ELSE 0 END) as wkts
    FROM deliveries WHERE bowler LIKE '%Nkomo%' OR bowler LIKE '%Ndhlovu%'
    GROUP BY bowler
""").fetchall()
print("Zimbabwe bowlers in DB:", zim_stats, flush=True)

con.close()

