import duckdb
from pathlib import Path

db = Path(r"C:\Users\lenovo\.gemini\antigravity\scratch\Cricket\data\cricsheet_wt20.duckdb")
c = duckdb.connect(str(db), read_only=True)

print("=== Matches at Sharjah ===")
q = """
SELECT match_id, match_date, team1, team2, toss_winner, toss_decision, winner, win_by_runs, win_by_wickets, player_of_match
FROM matches
WHERE venue ILIKE '%Sharjah%'
ORDER BY match_date DESC
LIMIT 10
"""
for m in c.execute(q).fetchall():
    print(m)

print("\n=== Top Batters at Sharjah ===")
q_bat = """
SELECT batter, COUNT(DISTINCT d.match_id) as matches, SUM(runs_batter) as total_runs, 
       COUNT(1) as balls_faced, ROUND(SUM(runs_batter)*100.0/COUNT(1), 1) as strike_rate
FROM deliveries d
JOIN matches m ON d.match_id = m.match_id
WHERE m.venue ILIKE '%Sharjah%'
GROUP BY batter
ORDER BY total_runs DESC
LIMIT 10
"""
for b in c.execute(q_bat).fetchall():
    print(b)

print("\n=== Top Bowlers at Sharjah ===")
q_bowl = """
SELECT bowler, COUNT(DISTINCT d.match_id) as matches, COUNT(1)/6 as overs,
       SUM(CASE WHEN is_wicket = true AND wicket_type NOT IN ('run out', 'retired hurt') THEN 1 ELSE 0 END) as wickets,
       SUM(runs_total) as runs_conceded,
       ROUND(SUM(runs_total) / (COUNT(1)/6.0), 2) as economy
FROM deliveries d
JOIN matches m ON d.match_id = m.match_id
WHERE m.venue ILIKE '%Sharjah%'
GROUP BY bowler
ORDER BY wickets DESC
LIMIT 10
"""
for bw in c.execute(q_bowl).fetchall():
    print(bw)

