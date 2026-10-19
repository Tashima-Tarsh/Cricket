import sys
import json
import numpy as np
from typing import List, Dict, Any
from ortools.sat.python import cp_model

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

with open('gl_engine/data/ind_wi_match.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

players = data['players']
n = len(players)

def solve_lineup(
    weights: List[float],
    min_credits: float = 75.0,
    max_credits: float = 100.0,
    min_diffs: int = 0,
    c_weights: List[float] = None,
    vc_weights: List[float] = None,
    force_players: List[str] = None,
    exclude_players: List[str] = None,
    ind_min: int = 1,
    ind_max: int = 10
):
    model = cp_model.CpModel()
    x = [model.NewBoolVar(f"x_{i}") for i in range(n)]
    c = [model.NewBoolVar(f"c_{i}") for i in range(n)]
    v = [model.NewBoolVar(f"v_{i}") for i in range(n)]

    # 1. Total players == 11
    model.Add(sum(x) == 11)

    # 2. Credits
    credit_ints = [int(round(p['credits'] * 10)) for p in players]
    model.Add(sum(credit_ints[i] * x[i] for i in range(n)) <= int(round(max_credits * 10)))
    model.Add(sum(credit_ints[i] * x[i] for i in range(n)) >= int(round(min_credits * 10)))

    # 3. Roles
    wk = [i for i, p in enumerate(players) if p['role'] == 'WK']
    bat = [i for i, p in enumerate(players) if p['role'] == 'BAT']
    ar = [i for i, p in enumerate(players) if p['role'] == 'AR']
    bowl = [i for i, p in enumerate(players) if p['role'] == 'BOWL']

    model.Add(sum(x[i] for i in wk) >= 1)
    model.Add(sum(x[i] for i in wk) <= 8)
    model.Add(sum(x[i] for i in bat) >= 1)
    model.Add(sum(x[i] for i in bat) <= 8)
    model.Add(sum(x[i] for i in ar) >= 1)
    model.Add(sum(x[i] for i in ar) <= 8)
    model.Add(sum(x[i] for i in bowl) >= 1)
    model.Add(sum(x[i] for i in bowl) <= 8)

    # 4. Team balance
    ind = [i for i, p in enumerate(players) if p['team'] == 'IND']
    wi = [i for i, p in enumerate(players) if p['team'] == 'WI']
    model.Add(sum(x[i] for i in ind) >= ind_min)
    model.Add(sum(x[i] for i in ind) <= ind_max)
    model.Add(sum(x[i] for i in wi) >= 1)
    model.Add(sum(x[i] for i in wi) <= 10)

    # 5. Differentials
    if min_diffs > 0:
        diffs = [i for i, p in enumerate(players) if p['projected_ownership'] < 35.0]
        model.Add(sum(x[i] for i in diffs) >= min_diffs)

    # 6. Captain & VC
    model.Add(sum(c) == 1)
    model.Add(sum(v) == 1)
    for i in range(n):
        model.Add(c[i] <= x[i])
        model.Add(v[i] <= x[i])
        model.Add(c[i] + v[i] <= 1)

    if force_players:
        for fp in force_players:
            idx = next((i for i, p in enumerate(players) if p['id'] == fp or p['name'] == fp), None)
            if idx is not None:
                model.Add(x[idx] == 1)

    if exclude_players:
        for ep in exclude_players:
            idx = next((i for i, p in enumerate(players) if p['id'] == ep or p['name'] == ep), None)
            if idx is not None:
                model.Add(x[idx] == 0)

    cw = c_weights if c_weights is not None else weights
    vw = vc_weights if vc_weights is not None else weights

    obj = []
    for i in range(n):
        base_val = int(round(weights[i] * 100))
        cap_val = int(round(cw[i] * 100))
        vc_val = int(round(vw[i] * 50))
        obj.append(base_val * x[i] + cap_val * c[i] + vc_val * v[i])

    model.Maximize(sum(obj))

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 2.0
    status = solver.Solve(model)

    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        sel_players = [players[i] for i in range(n) if solver.Value(x[i]) == 1]
        c_p = next(players[i] for i in range(n) if solver.Value(c[i]) == 1)
        vc_p = next(players[i] for i in range(n) if solver.Value(v[i]) == 1)
        tot_cr = sum(p['credits'] for p in sel_players)
        return {
            'players': sel_players,
            'captain': c_p,
            'vice_captain': vc_p,
            'total_credits': round(tot_cr, 1)
        }
    return None

# Base projections
p_points = [p.get('projected_points', p['stats']['avg_fantasy_pts']) for p in players]
p_ceil = [p.get('ceiling_score', p['stats']['avg_fantasy_pts'] * 1.5) for p in players]
p_own = [p['projected_ownership'] for p in players]
p_c_own = [p.get('captain_percentage', 1.0) for p in players]
p_dt = [p.get('dream_team_percentage', 30.0) for p in players]

scenarios = {}

# 1. Team 1: Highest Expected Fantasy Points (Pure Mean, No budget restriction up to 100)
scenarios['Team 1: Highest Projected Expected Fantasy Points'] = solve_lineup(
    weights=[p['stats']['avg_fantasy_pts'] for p in players],
    min_credits=75.0,
    max_credits=100.0,
    min_diffs=0
)

# 2. Team 2: Highest 1st-Place Probability (79-85 Cr Anti-Chalk, sub-35% diffs, C leverage)
w2 = []
cw2 = []
for p in players:
    w = p.get('ceiling_score', 100.0)
    if p['projected_ownership'] < 25.0:
        w *= 1.35
    elif p['projected_ownership'] > 75.0:
        w *= 0.85
    w2.append(w)
    
    # Captain weight
    c_mult = 1.0
    if p.get('captain_percentage', 1.0) > 20.0:
        c_mult = 0.70
    elif p.get('captain_percentage', 1.0) < 3.0 and p.get('dream_team_percentage', 0) >= 40:
        c_mult = 1.40
    cw2.append(w * c_mult)

scenarios['Team 2: Highest Estimated Single-Entry First-Place Probability'] = solve_lineup(
    weights=w2,
    c_weights=cw2,
    min_credits=79.0,
    max_credits=85.0,
    min_diffs=3
)

# 3. Team 3: High-Scoring Match Upside (200+ Par, top order & power hitters)
w3 = []
for p in players:
    w = p.get('ceiling_score', 100.0)
    if p['role'] in ['BAT', 'WK'] or p['stats']['strike_rate'] >= 160:
        w *= 1.30
    if p['role'] == 'BOWL' and getattr(p['stats'], 'economy', 8.0) > 9.0:
        w *= 0.80
    w3.append(w)

scenarios['Team 3: Strongest Upside Under High-Scoring Match Scenario'] = solve_lineup(
    weights=w3,
    min_credits=79.0,
    max_credits=90.0,
    min_diffs=2
)

# 4. Team 4: Low-Scoring Match Upside (140-150 Par, Bowlers & Bowling ARs)
w4 = []
for p in players:
    w = p.get('projected_points', 50.0)
    if p['role'] in ['BOWL', 'AR']:
        w *= 1.35
    if p['role'] in ['BAT', 'WK'] and p['stats']['batting_avg'] < 30:
        w *= 0.75
    w4.append(w)

scenarios['Team 4: Strongest Upside Under Low-Scoring Match Scenario'] = solve_lineup(
    weights=w4,
    min_credits=75.0,
    max_credits=85.0,
    min_diffs=3
)

# 5. Team 5: Pace-Dominant Match (59.6% Pacer Wickets, Overcast Seam)
w5 = []
cw5 = []
for p in players:
    w = p.get('ceiling_score', 100.0)
    b_style = (p.get('bowling_style') or '').lower()
    if any(k in b_style for k in ['fast', 'pace', 'medium']):
        w *= 1.45
    elif 'spin' in b_style or 'slow' in b_style or 'orthodox' in b_style:
        w *= 0.80
    w5.append(w)
    
    # Fast bowler captain boost
    if any(k in b_style for k in ['fast', 'pace']) and p['projected_ownership'] < 30.0:
        cw5.append(w * 1.50)
    else:
        cw5.append(w)

scenarios['Team 5: Strongest Lineup for a Pace-Dominant Match'] = solve_lineup(
    weights=w5,
    c_weights=cw5,
    min_credits=79.0,
    max_credits=86.0,
    min_diffs=3
)

# 6. Team 6: Spin-Dominant Match (Middle Overs Choke)
w6 = []
for p in players:
    w = p.get('ceiling_score', 100.0)
    b_style = (p.get('bowling_style') or '').lower()
    if 'spin' in b_style or 'slow' in b_style or 'orthodox' in b_style:
        w *= 1.45
    w6.append(w)

scenarios['Team 6: Strongest Lineup for a Spin-Dominant Match'] = solve_lineup(
    weights=w6,
    min_credits=75.0,
    max_credits=88.0,
    min_diffs=2
)

# 7. Team 7: India Bats First (Heavy IND Top-4 + IND Death Bowlers + WI Chasing Finishers)
w7 = []
for p in players:
    w = p.get('projected_points', 50.0)
    if p['team'] == 'IND':
        if p['batting_order_projected'] <= 4:
            w *= 1.25
        if p['role'] == 'BOWL':
            w *= 1.20
    elif p['team'] == 'WI':
        if p['role'] == 'AR' or p['batting_order_projected'] >= 5:
            w *= 1.15
    w7.append(w)

scenarios['Team 7: Strongest Lineup if India Bats First'] = solve_lineup(
    weights=w7,
    ind_min=6,
    ind_max=8,
    min_credits=79.0,
    max_credits=88.0,
    min_diffs=2
)

# 8. Team 8: West Indies Bats First (WI Top-4 & Power Finishers + IND Chasing Anchors)
w8 = []
for p in players:
    w = p.get('projected_points', 50.0)
    if p['team'] == 'WI':
        w *= 1.25
    elif p['team'] == 'IND':
        if p['batting_order_projected'] <= 3:
            w *= 1.20
    w8.append(w)

scenarios['Team 8: Strongest Lineup if West Indies Bats First'] = solve_lineup(
    weights=w8,
    ind_min=4,
    ind_max=6,
    min_credits=79.0,
    max_credits=88.0,
    min_diffs=3
)

# 9. Team 9: Shortened Match (10-12 Overs DLS Rain Reduction: Top 3 Batters + Death Bowlers Only)
w9 = []
for p in players:
    w = p.get('projected_points', 50.0)
    # In shortened matches, lower order batters get 0 balls!
    if p['batting_order_projected'] > 4 and p['expected_overs'] < 2.0:
        w *= 0.30
    elif p['batting_order_projected'] <= 3:
        w *= 1.40
    if p['role'] in ['BOWL', 'AR'] and p['expected_overs'] >= 2.0:
        w *= 1.30
    w9.append(w)

scenarios['Team 9: Strongest Lineup for a Shortened Match (DLS)'] = solve_lineup(
    weights=w9,
    min_credits=75.0,
    max_credits=85.0,
    min_diffs=2
)

# 10. Team 10: Differentiated Lineup (Maximum Ownership Leverage, strictly sub-85 credits)
w10 = []
cw10 = []
for p in players:
    # Inverse ownership weighting
    own_inv = 100.0 - p['projected_ownership']
    w = p.get('ceiling_score', 100.0) * (own_inv / 50.0)
    w10.append(w)
    
    # Captain strictly from sub-5% captaincy
    c_inv = 10.0 / max(0.2, p.get('captain_percentage', 1.0))
    cw10.append(w * c_inv)

scenarios['Team 10: Strongest Differentiated Lineup (Anti-Chalk Leverage)'] = solve_lineup(
    weights=w10,
    c_weights=cw10,
    min_credits=78.0,
    max_credits=84.0,
    min_diffs=4
)

# Print Summary of 10 Lineups
print("=== 10 SOLVED LINEUPS SUMMARY ===")
for name, res in scenarios.items():
    if res:
        print(f"\n{name}:")
        print(f"  Credits: {res['total_credits']} Cr | C: {res['captain']['name']} | VC: {res['vice_captain']['name']}")
        p_str = ', '.join([p['name'] + ' (' + str(p['credits']) + ')' for p in res['players']])
        print("  Players: " + p_str)

# Save to json for exact markdown reporting
with open('gl_engine/data/ten_scenarios.json', 'w', encoding='utf-8') as f:
    json.dump(scenarios, f, indent=2)
print('\nSaved ten_scenarios.json successfully!')
