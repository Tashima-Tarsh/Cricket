"""Solve 3 Grand League teams with strict 6:5 split and ONLY high-performing players."""
import numpy as np
from scipy.optimize import milp, LinearConstraint, Bounds
import json
from pathlib import Path

# ONLY THE 15 PLAYERS PREDICTED TO PERFORM (ZERO GENERIC / FLOP FILLERS)
performers = [
    # INDIA (9 viable performers)
    {"id": "ind_samson", "name": "Sanju Samson", "team": "IND", "role": "WK", "credits": 8.5, "ownership": 58.0, "ceiling": 175.0, "projected_points": 78.0, "expected_overs": 0.0},
    {"id": "ind_abhishek", "name": "Abhishek Sharma", "team": "IND", "role": "BAT", "credits": 9.0, "ownership": 88.0, "ceiling": 150.0, "projected_points": 75.0, "expected_overs": 1.0},
    {"id": "ind_ishan", "name": "Ishan Kishan", "team": "IND", "role": "WK", "credits": 8.5, "ownership": 69.0, "ceiling": 130.0, "projected_points": 65.0, "expected_overs": 0.0},
    {"id": "ind_shreyas", "name": "Shreyas Iyer", "team": "IND", "role": "BAT", "credits": 9.0, "ownership": 62.0, "ceiling": 115.0, "projected_points": 55.0, "expected_overs": 0.0},
    {"id": "ind_tilak", "name": "Tilak Varma", "team": "IND", "role": "BAT", "credits": 8.5, "ownership": 44.0, "ceiling": 160.0, "projected_points": 76.0, "expected_overs": 1.5},
    {"id": "ind_reddy", "name": "Nitish Kumar Reddy", "team": "IND", "role": "AR", "credits": 8.0, "ownership": 32.0, "ceiling": 135.0, "projected_points": 62.0, "expected_overs": 2.5},
    {"id": "ind_axar", "name": "Axar Patel", "team": "IND", "role": "AR", "credits": 9.0, "ownership": 79.0, "ceiling": 125.0, "projected_points": 68.0, "expected_overs": 4.0},
    {"id": "ind_arshdeep", "name": "Arshdeep Singh", "team": "IND", "role": "BOWL", "credits": 9.0, "ownership": 86.0, "ceiling": 130.0, "projected_points": 74.0, "expected_overs": 4.0},
    {"id": "ind_mayank", "name": "Mayank Yadav", "team": "IND", "role": "BOWL", "credits": 8.0, "ownership": 28.5, "ceiling": 140.0, "projected_points": 70.0, "expected_overs": 4.0},

    # WEST INDIES (6 viable performers)
    {"id": "wi_hope", "name": "Shai Hope", "team": "WI", "role": "WK", "credits": 9.0, "ownership": 76.0, "ceiling": 115.0, "projected_points": 60.0, "expected_overs": 0.0},
    {"id": "wi_rutherford", "name": "Sherfane Rutherford", "team": "WI", "role": "BAT", "credits": 8.0, "ownership": 29.0, "ceiling": 120.0, "projected_points": 56.0, "expected_overs": 0.5},
    {"id": "wi_shepherd", "name": "Romario Shepherd", "team": "WI", "role": "AR", "credits": 8.5, "ownership": 71.0, "ceiling": 145.0, "projected_points": 82.0, "expected_overs": 4.0},
    {"id": "wi_chase", "name": "Roston Chase", "team": "WI", "role": "AR", "credits": 8.5, "ownership": 64.0, "ceiling": 120.0, "projected_points": 64.0, "expected_overs": 4.0},
    {"id": "wi_paul", "name": "Keemo Paul", "team": "WI", "role": "AR", "credits": 8.0, "ownership": 24.0, "ceiling": 115.0, "projected_points": 52.0, "expected_overs": 3.0},
    {"id": "wi_joseph", "name": "Shamar Joseph", "team": "WI", "role": "BOWL", "credits": 8.5, "ownership": 36.0, "ceiling": 135.0, "projected_points": 62.0, "expected_overs": 4.0}
]

N = len(performers)

def solve_team(c_id, vc_id, ind_count, wi_count, diff_weight=1.2, excluded_ids=[], forced_ids=[]):
    weights = np.zeros(N)
    for i, p in enumerate(performers):
        w = p["ceiling"] * 0.6 + p["projected_points"] * 0.4
        if p["id"] == c_id:
            w *= 2.0
        elif p["id"] == vc_id:
            w *= 1.5
        if p["ownership"] <= 35.0:
            w *= diff_weight
        weights[i] = w

    c = -1.0 * weights
    A_rows, lhs, rhs = [], [], []

    # 1. Total players == 11
    A_rows.append(np.ones(N)); lhs.append(11.0); rhs.append(11.0)
    # 2. Credits <= 100
    A_rows.append(np.array([p["credits"] for p in performers])); lhs.append(0.0); rhs.append(100.0)
    # 3. Exact Team split: IND == ind_count, WI == wi_count
    A_rows.append(np.array([1.0 if p["team"] == "IND" else 0.0 for p in performers])); lhs.append(float(ind_count)); rhs.append(float(ind_count))
    A_rows.append(np.array([1.0 if p["team"] == "WI" else 0.0 for p in performers])); lhs.append(float(wi_count)); rhs.append(float(wi_count))
    
    # 4. Roles: WK 1-4, BAT 2-6, AR 1-5, BOWL 2-6
    for role, min_r, max_r in [('WK', 1, 4), ('BAT', 2, 6), ('AR', 1, 5), ('BOWL', 2, 6)]:
        A_rows.append(np.array([1.0 if p["role"] == role else 0.0 for p in performers])); lhs.append(float(min_r)); rhs.append(float(max_r))
    
    # 5. Min 5 bowling options
    A_rows.append(np.array([1.0 if p["expected_overs"] >= 1.0 else 0.0 for p in performers])); lhs.append(5.0); rhs.append(11.0)

    # 6. Force C and VC
    c_idx = next(i for i, p in enumerate(performers) if p["id"] == c_id)
    vc_idx = next(i for i, p in enumerate(performers) if p["id"] == vc_id)
    c_row = np.zeros(N); c_row[c_idx] = 1.0; A_rows.append(c_row); lhs.append(1.0); rhs.append(1.0)
    vc_row = np.zeros(N); vc_row[vc_idx] = 1.0; A_rows.append(vc_row); lhs.append(1.0); rhs.append(1.0)

    # 7. Excluded / Forced
    for p_id in excluded_ids:
        idx = next(i for i, p in enumerate(performers) if p["id"] == p_id)
        row = np.zeros(N); row[idx] = 1.0; A_rows.append(row); lhs.append(0.0); rhs.append(0.0)
    for p_id in forced_ids:
        idx = next(i for i, p in enumerate(performers) if p["id"] == p_id)
        row = np.zeros(N); row[idx] = 1.0; A_rows.append(row); lhs.append(1.0); rhs.append(1.0)

    A = np.array(A_rows)
    constraints = LinearConstraint(A, lhs, rhs)
    integrality = np.ones(N)
    bounds = Bounds(0, 1)

    res = milp(c=c, constraints=constraints, integrality=integrality, bounds=bounds)
    if not res.success:
        raise ValueError(f"MILP Failed for C={c_id}, VC={vc_id}")

    sel = [performers[i] for i in range(N) if res.x[i] > 0.5]
    tot_credits = sum(p["credits"] for p in sel)
    tot_own = sum(p["ownership"] for p in sel)
    diffs = [p for p in sel if p["ownership"] <= 35.0]
    ind_sel = [p for p in sel if p["team"] == "IND"]
    wi_sel = [p for p in sel if p["team"] == "WI"]

    return sel, tot_credits, tot_own, diffs, len(ind_sel), len(wi_sel)

# Solve Team 1: Strict 6 IND : 5 WI (India Dew Chasing Dominance)
# C: Tilak Varma, VC: Sanju Samson
t1_sel, t1_cr, t1_own, t1_diffs, t1_ind, t1_wi = solve_team(
    c_id="ind_tilak", vc_id="ind_samson", ind_count=6, wi_count=5, diff_weight=1.1,
    forced_ids=["ind_mayank", "wi_shepherd", "wi_rutherford", "wi_joseph"]
)

# Solve Team 2: Strict 5 IND : 6 WI (West Indies 1st Innings Power Explosion)
# C: Romario Shepherd, VC: Ishan Kishan
t2_sel, t2_cr, t2_own, t2_diffs, t2_ind, t2_wi = solve_team(
    c_id="wi_shepherd", vc_id="ind_ishan", ind_count=5, wi_count=6, diff_weight=1.2,
    forced_ids=["ind_samson", "ind_tilak", "ind_mayank", "wi_rutherford", "wi_joseph"]
)

# Solve Team 3: Strict 6 IND : 5 WI (80% Red Soil 150kph Pace Carnage - Contrarian)
# C: Mayank Yadav, VC: Shamar Joseph
t3_sel, t3_cr, t3_own, t3_diffs, t3_ind, t3_wi = solve_team(
    c_id="ind_mayank", vc_id="wi_joseph", ind_count=6, wi_count=5, diff_weight=1.4,
    forced_ids=["ind_reddy", "wi_rutherford", "wi_paul"]
)

print("="*60)
print(f"TEAM 1 (Split {t1_ind}:{t1_wi}): Credits {t1_cr}/100 | Ownership {t1_own:.1f}% | Wild Cards: {len(t1_diffs)}")
for p in t1_sel:
    badge = " [C]" if p['id']=='ind_tilak' else (" [VC]" if p['id']=='ind_samson' else (" [DIFF]" if p['ownership']<=35 else ""))
    print(f"  {p['name']:<20} ({p['team']} | {p['role']:<4} | {p['credits']}cr){badge}")

print("="*60)
print(f"TEAM 2 (Split {t2_ind}:{t2_wi}): Credits {t2_cr}/100 | Ownership {t2_own:.1f}% | Wild Cards: {len(t2_diffs)}")
for p in t2_sel:
    badge = " [C]" if p['id']=='wi_shepherd' else (" [VC]" if p['id']=='ind_ishan' else (" [DIFF]" if p['ownership']<=35 else ""))
    print(f"  {p['name']:<20} ({p['team']} | {p['role']:<4} | {p['credits']}cr){badge}")

print("="*60)
print(f"TEAM 3 (Split {t3_ind}:{t3_wi}): Credits {t3_cr}/100 | Ownership {t3_own:.1f}% | Wild Cards: {len(t3_diffs)}")
for p in t3_sel:
    badge = " [C]" if p['id']=='ind_mayank' else (" [VC]" if p['id']=='wi_joseph' else (" [DIFF]" if p['ownership']<=35 else ""))
    print(f"  {p['name']:<20} ({p['team']} | {p['role']:<4} | {p['credits']}cr){badge}")
