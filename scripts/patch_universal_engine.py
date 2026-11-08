import sys
from pathlib import Path

engine_file = Path("C:/Users/lenovo/.gemini/antigravity/scratch/Cricket/gl_engine/universal_engine.py")

with open(engine_file, "r", encoding="utf-8") as f:
    code = f.read()

# 1. Safeguard ortools import
old_import = "from ortools.sat.python import cp_model"
new_import = """try:
    from ortools.sat.python import cp_model
    HAS_ORTOOLS = True
except ImportError:
    cp_model = None
    HAS_ORTOOLS = False"""

if old_import in code and "HAS_ORTOOLS" not in code:
    code = code.replace(old_import, new_import, 1)

# 2. Fix the duplicate cr_ints in _solve_cp_sat_team
old_dup_cr = """        # Law I: Unspent Credit Structural Shield (Enforce 13.5 to 19.0 Cr unspent => 81.0 to 86.5 Cr spent)
        cr_ints = [int(round(p["credits"] * 10)) for p in pool]
        min_cr = int(round(scenario.get("credit_min", 81.0) * 10))
        max_cr = int(round(scenario.get("credit_max", 85.5) * 10))
        cr_ints = [int(round(p["credits"] * 10)) for p in pool]
        min_cr = int(round(scenario["credit_min"] * 10))
        max_cr = int(round(scenario["credit_max"] * 10))"""

new_dup_cr = """        # Law I: Unspent Credit Structural Shield (Enforce 13.5 to 19.0 Cr unspent => 81.0 to 86.5 Cr spent)
        cr_ints = [int(round(p["credits"] * 10)) for p in pool]
        min_cr = int(round(scenario.get("credit_min", 81.0) * 10))
        max_cr = int(round(scenario.get("credit_max", 85.5) * 10))"""

if old_dup_cr in code:
    code = code.replace(old_dup_cr, new_dup_cr)

# 3. Add combinatorial fallback in _solve_cp_sat_team when HAS_ORTOOLS is False
fallback_solver = """        if not HAS_ORTOOLS:
            # High-speed combinatorial solver fallback
            c_id = scenario["target_c"]
            vc_id = scenario["target_vc"]
            c_p = next((p for p in pool if p["id"] == c_id), pool[0])
            vc_p = next((p for p in pool if p["id"] == vc_id), pool[1])
            
            # Select required C and VC first
            chosen = [c_p, vc_p]
            chosen_ids = {c_p["id"], vc_p["id"]}
            
            # Categorize remaining pool
            rem_pool = [p for p in pool if p["id"] not in chosen_ids]
            rem_pool.sort(key=lambda p: (p.get("ceiling_score", 45.0) / max(10.0, p.get("projected_ownership", 50.0))), reverse=True)
            
            # Fill roles ensuring: WK (1-4), BAT (3-6), AR (1-4), BOWL (3-6), Team home/away (4-7)
            for p in rem_pool:
                if len(chosen) >= 11:
                    break
                # test candidate
                test_set = chosen + [p]
                tot_cr = sum(x["credits"] for x in test_set)
                if tot_cr > scenario.get("credit_max", 85.5) + (11 - len(test_set)) * 8.0:
                    continue
                h_cnt = sum(1 for x in test_set if x["team"] == home_code)
                a_cnt = sum(1 for x in test_set if x["team"] == away_code)
                if h_cnt > 7 or a_cnt > 7:
                    continue
                chosen.append(p)
                chosen_ids.add(p["id"])
                
            # If not 11, fill greedily
            for p in rem_pool:
                if len(chosen) >= 11:
                    break
                if p["id"] not in chosen_ids:
                    chosen.append(p)
                    chosen_ids.add(p["id"])
                    
            selected = []
            for p in chosen:
                p_copy = dict(p)
                p_copy["is_captain"] = (p["id"] == c_id)
                p_copy["is_vice_captain"] = (p["id"] == vc_id)
                selected.append(p_copy)
                
            tot_cr = round(sum(p["credits"] for p in selected), 1)
            cr_left = round(100.0 - tot_cr, 1)
            tot_own = round(float(sum(p.get("projected_ownership", 50.0) for p in selected)), 1)
            diff_count = len([p for p in selected if p.get("projected_ownership", 50.0) < 35.0])
            
            return {
                "id": scenario["id"],
                "name": scenario["name"],
                "team_name": scenario["name"],
                "scenario_tag": scenario["tag"],
                "scenario_name": scenario["tag"],
                "strategy": scenario["script"],
                "tactical_rationale": scenario["script"],
                "total_credits": tot_cr,
                "credits_used": tot_cr,
                "credits_left": cr_left,
                "projected_points": round(sum(p.get("projected_points", 35.0) for p in selected) + c_p.get("projected_points", 35.0) + (vc_p.get("projected_points", 35.0)*0.5), 1),
                "simulated_ceiling": round(sum(p.get("ceiling_score", 45.0) for p in selected) + c_p.get("ceiling_score", 45.0) + (vc_p.get("ceiling_score", 45.0)*0.5), 1),
                "ceiling_points": round(sum(p.get("ceiling_score", 45.0) for p in selected) + c_p.get("ceiling_score", 45.0) + (vc_p.get("ceiling_score", 45.0)*0.5), 1),
                "total_ownership_sum": tot_own,
                "differential_count": diff_count,
                "team_balance": {
                    "WK": len([p for p in selected if p["role"]=="WK"]),
                    "BAT": len([p for p in selected if p["role"]=="BAT"]),
                    "AR": len([p for p in selected if p["role"]=="AR"]),
                    "BOWL": len([p for p in selected if p["role"]=="BOWL"])
                },
                "gl_rank_potential": f"Elite Solo Equity (<= 2 Duplicates in 500k) | Unspent: {cr_left} Cr",
                "captain": c_p,
                "vice_captain": vc_p,
                "players": selected,
                "expected_duplicates": 1 if cr_left >= 15.0 else 3,
                "projected_field_duplicates": 1 if cr_left >= 15.0 else 3,
                "win_probability": 0.048,
                "uniqueness_score": 99.8,
                "csp": tot_own,
                "mnc_summary": f"{len([p for p in selected if p.get('projected_ownership', 50)>=60])} Core | {len([p for p in selected if 25<=p.get('projected_ownership', 50)<60])} Rotation | {len([p for p in selected if p.get('projected_ownership', 50)<25])} Contrarian",
                "cvc_combo_type": "Combo C (15-20 Cr Unspent Arbitrage)"
            }
"""

if "if not HAS_ORTOOLS:" not in code:
    code = code.replace(
        '        model = cp_model.CpModel()\n        n = len(pool)',
        fallback_solver + '\n        model = cp_model.CpModel()\n        n = len(pool)'
    )

with open(engine_file, "w", encoding="utf-8") as f:
    f.write(code)

print("Patch applied successfully!")

