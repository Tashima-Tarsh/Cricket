import urllib.request
import json

res = urllib.request.urlopen('http://127.0.0.1:8000/api/rain/simulate?overs=12')
data = json.loads(res.read().decode('utf-8'))

print("=== 12-OVER RAIN REDUCED MATCH SIMULATION ===")
c = data['constraints']
print(f"Overs: {c['overs']} | Powerplay: {c['powerplay_overs']} ov | Max Bowler Quota: {c['max_bowler_quota']} ov")
print(f"Projected Par Score (DLS): {c['projected_par']} runs | Chasing Win Equity: {c['chasing_win_prob']}%")

print("\n=== TOP SHORTENED-MATCH FANTASY PICKS ===")
for p in data['top_picks'][:6]:
    print(f"• {p['name']} ({p['team']} - {p['role']}): Order {p['batting_order']} | Proj: {p['projected_points']} pts | Reason: {p['reason']}")

print("\n=== DEDICATED SHORT-FORMAT GRAND LEAGUE SCENARIOS ===")
for s in data['rain_scenarios']:
    print(f"• {s['name']}: C={s['preferred_c']} | VC={s['preferred_vc']} -> {s['rationale']}")

