"""Update exact confirmed 22 players and solve 3 final Grand League teams for 430,000 contest."""
import json
from pathlib import Path
import numpy as np
from scipy.optimize import milp, LinearConstraint, Bounds

# Confirmed 22 players with official credits and ownership estimates
confirmed_players = [
    # INDIA (11) - Bowling First, Chasing Under Dew
    {"id": "ind_samson", "name": "Sanju Samson", "team": "IND", "role": "WK", "credits": 8.5, "ownership": 58.0, "ceiling": 175.0, "projected_points": 72.0, "expected_overs": 0.0},
    {"id": "ind_abhishek", "name": "Abhishek Sharma", "team": "IND", "role": "BAT", "credits": 9.0, "ownership": 88.0, "ceiling": 150.0, "projected_points": 78.0, "expected_overs": 1.0},
    {"id": "ind_ishan", "name": "Ishan Kishan", "team": "IND", "role": "WK", "credits": 8.5, "ownership": 69.0, "ceiling": 130.0, "projected_points": 65.0, "expected_overs": 0.0},
    {"id": "ind_shreyas", "name": "Shreyas Iyer", "team": "IND", "role": "BAT", "credits": 9.0, "ownership": 62.0, "ceiling": 115.0, "projected_points": 60.0, "expected_overs": 0.0},
    {"id": "ind_tilak", "name": "Tilak Varma", "team": "IND", "role": "BAT", "credits": 8.5, "ownership": 44.0, "ceiling": 160.0, "projected_points": 70.0, "expected_overs": 1.5},
    {"id": "ind_dhir", "name": "Naman Dhir", "team": "IND", "role": "BAT", "credits": 7.5, "ownership": 18.0, "ceiling": 105.0, "projected_points": 38.0, "expected_overs": 1.0},
    {"id": "ind_reddy", "name": "Nitish Kumar Reddy", "team": "IND", "role": "AR", "credits": 8.0, "ownership": 32.0, "ceiling": 135.0, "projected_points": 58.0, "expected_overs": 2.5},
    {"id": "ind_axar", "name": "Axar Patel", "team": "IND", "role": "AR", "credits": 9.0, "ownership": 79.0, "ceiling": 125.0, "projected_points": 74.0, "expected_overs": 4.0},
    {"id": "ind_arshdeep", "name": "Arshdeep Singh", "team": "IND", "role": "BOWL", "credits": 9.0, "ownership": 86.0, "ceiling": 130.0, "projected_points": 72.0, "expected_overs": 4.0},
    {"id": "ind_prince", "name": "Prince Yadav", "team": "IND", "role": "BOWL", "credits": 7.5, "ownership": 14.0, "ceiling": 85.0, "projected_points": 32.0, "expected_overs": 3.0},
    {"id": "ind_mayank", "name": "Mayank Yadav", "team": "IND", "role": "BOWL", "credits": 8.0, "ownership": 28.5, "ceiling": 140.0, "projected_points": 62.0, "expected_overs": 4.0},

    # WEST INDIES (11) - Batting First
    {"id": "wi_hope", "name": "Shai Hope", "team": "WI", "role": "WK", "credits": 9.0, "ownership": 76.0, "ceiling": 115.0, "projected_points": 64.0, "expected_overs": 0.0},
    {"id": "wi_andrew", "name": "Jewel Andrew", "team": "WI", "role": "WK", "credits": 7.5, "ownership": 15.0, "ceiling": 95.0, "projected_points": 35.0, "expected_overs": 0.0},
    {"id": "wi_hetmyer", "name": "Shimron Hetmyer", "team": "WI", "role": "BAT", "credits": 8.5, "ownership": 51.0, "ceiling": 135.0, "projected_points": 48.0, "expected_overs": 0.0},
    {"id": "wi_powell", "name": "Rovman Powell", "team": "WI", "role": "BAT", "credits": 8.5, "ownership": 55.0, "ceiling": 130.0, "projected_points": 52.0, "expected_overs": 1.0},
    {"id": "wi_rutherford", "name": "Sherfane Rutherford", "team": "WI", "role": "BAT", "credits": 8.0, "ownership": 29.0, "ceiling": 120.0, "projected_points": 50.0, "expected_overs": 0.5},
    {"id": "wi_shepherd", "name": "Romario Shepherd", "team": "WI", "role": "AR", "credits": 8.5, "ownership": 71.0, "ceiling": 145.0, "projected_points": 76.0, "expected_overs": 4.0},
    {"id": "wi_chase", "name": "Roston Chase", "team": "WI", "role": "AR", "credits": 8.5, "ownership": 64.0, "ceiling": 120.0, "projected_points": 66.0, "expected_overs": 4.0},
    {"id": "wi_paul", "name": "Keemo Paul", "team": "WI", "role": "AR", "credits": 8.0, "ownership": 24.0, "ceiling": 115.0, "projected_points": 48.0, "expected_overs": 3.0},
    {"id": "wi_springer", "name": "Shamar Springer", "team": "WI", "role": "AR", "credits": 7.5, "ownership": 16.0, "ceiling": 95.0, "projected_points": 42.0, "expected_overs": 2.5},
    {"id": "wi_motie", "name": "Gudakesh Motie", "team": "WI", "role": "BOWL", "credits": 8.0, "ownership": 42.0, "ceiling": 110.0, "projected_points": 52.0, "expected_overs": 4.0},
    {"id": "wi_joseph", "name": "Shamar Joseph", "team": "WI", "role": "BOWL", "credits": 8.5, "ownership": 36.0, "ceiling": 135.0, "projected_points": 54.0, "expected_overs": 4.0}
]

N = len(confirmed_players)
player_map = {p["id"]: p for p in confirmed_players}

def solve_exact(c_id, vc_id, ind_bias, wi_bias, diff_mult, prev_indices=[]):
    weights = np.zeros(N)
    for i, p in enumerate(confirmed_players):
        w = p["ceiling"] * 0.6 + p["projected_points"] * 0.4
        if p["team"] == "IND":
            w *= ind_bias
        else:
            w *= wi_bias
        if p["id"] == c_id:
            w *= 2.0
        elif p["id"] == vc_id:
            w *= 1.6
        if p["ownership"] <= 35.0:
            w *= diff_mult
        weights[i] = w

    c = -1.0 * weights
    A_rows, lhs, rhs = [], [], []

    # 1. Total players == 11
    A_rows.append(np.ones(N)); lhs.append(11.0); rhs.append(11.0)
    # 2. Credits <= 100
    A_rows.append(np.array([p["credits"] for p in confirmed_players])); lhs.append(0.0); rhs.append(100.0)
    # 3. IND count (min 1, max 10)
    A_rows.append(np.array([1.0 if p["team"] == "IND" else 0.0 for p in confirmed_players])); lhs.append(1.0); rhs.append(10.0)
    # 4. WI count (min 1, max 10)
    A_rows.append(np.array([1.0 if p["team"] == "WI" else 0.0 for p in confirmed_players])); lhs.append(1.0); rhs.append(10.0)
    # 5. Role constraints: WK 1-4, BAT 2-6, AR 1-5, BOWL 2-6
    for role, min_r, max_r in [('WK', 1, 4), ('BAT', 2, 6), ('AR', 1, 5), ('BOWL', 2, 6)]:
        A_rows.append(np.array([1.0 if p["role"] == role else 0.0 for p in confirmed_players])); lhs.append(float(min_r)); rhs.append(float(max_r))
    # 6. Min 5 bowling options
    A_rows.append(np.array([1.0 if p["expected_overs"] >= 1.0 else 0.0 for p in confirmed_players])); lhs.append(5.0); rhs.append(11.0)
    # 7. Force C and VC
    c_idx = next(i for i, p in enumerate(confirmed_players) if p["id"] == c_id)
    vc_idx = next(i for i, p in enumerate(confirmed_players) if p["id"] == vc_id)
    c_row = np.zeros(N); c_row[c_idx] = 1.0; A_rows.append(c_row); lhs.append(1.0); rhs.append(1.0)
    vc_row = np.zeros(N); vc_row[vc_idx] = 1.0; A_rows.append(vc_row); lhs.append(1.0); rhs.append(1.0)

    # 8. Overlap constraint with previous team
    for prev in prev_indices:
        o_row = np.zeros(N)
        for idx in prev: o_row[idx] = 1.0
        A_rows.append(o_row); lhs.append(0.0); rhs.append(8.0)

    A = np.array(A_rows)
    res = milp(c=c, integrality=np.ones(N), bounds=Bounds(0, 1), constraints=LinearConstraint(A, lhs, rhs))
    sol = np.round(res.x).astype(int)
    selected = [confirmed_players[i] for i in range(N) if sol[i] == 1]
    
    total_credits = sum(p["credits"] for p in selected)
    cum_own = sum(p["ownership"] for p in selected)
    diffs = [p for p in selected if p["ownership"] <= 35.0]
    indices = [i for i in range(N) if sol[i] == 1]
    
    return selected, total_credits, cum_own, diffs, indices

# Team 1: Live Toss Optimal -> India Dew Chasing Masterclass (IND Bowl 1st, WI Bat 1st)
t1_sel, t1_cr, t1_own, t1_diffs, t1_idx = solve_exact("ind_tilak", "ind_samson", 1.25, 0.85, 1.25, [])

# Team 2: WI 1st Innings Power Surge -> Shepherd & Rutherford Explosion + Ishan Dew Chase
t2_sel, t2_cr, t2_own, t2_diffs, t2_idx = solve_exact("wi_shepherd", "ind_ishan", 0.9, 1.3, 1.2, [t1_idx])

# Team 3: 80% Red Soil Cracked Pitch 150kph Pace Carnage (Mayank C + Shamar Joseph VC)
t3_sel, t3_cr, t3_own, t3_diffs, t3_idx = solve_exact("ind_mayank", "wi_joseph", 1.05, 1.05, 1.35, [t1_idx, t2_idx])

print("Solved 3 Teams successfully with confirmed 22 players!")
print(f"Team 1: Credits {t1_cr}, Ownership {t1_own:.1f}%, Diffs: {len(t1_diffs)}")
print(f"Team 2: Credits {t2_cr}, Ownership {t2_own:.1f}%, Diffs: {len(t2_diffs)}")
print(f"Team 3: Credits {t3_cr}, Ownership {t3_own:.1f}%, Diffs: {len(t3_diffs)}")
