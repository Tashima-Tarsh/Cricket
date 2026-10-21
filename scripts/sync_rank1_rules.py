"""
sync_rank1_rules.py
Syncs all verified Rank 1 Grand League rules, archetype models, toss-conditional filters,
and the Raipur 3rd T20I fixture into gl_engine/universal_engine.py and ortools_optimizer.py.
"""
from pathlib import Path
import re

REPO_DIR = Path("C:/Users/lenovo/.gemini/antigravity/scratch/Cricket")
UNIVERSAL_ENGINE_PATH = REPO_DIR / "gl_engine" / "universal_engine.py"

def update_universal_engine():
    with open(UNIVERSAL_ENGINE_PATH, "r", encoding="utf-8") as f:
        code = f.read()

    # 1. Add fixture 2 (3rd T20I) into _init_default_fixtures
    fixture_snippet = '''        # 2. India Women vs Zimbabwe Women 3rd T20I (Raipur - 20-10-2026)
        self._matches["ind_w_vs_zim_w_2026_03"] = {
            "id": "ind_w_vs_zim_w_2026_03",
            "name": "India Women vs Zimbabwe Women, 3rd T20I (Raipur)",
            "format": "Women's T20 International",
            "status": "MATCH COMPLETED | India Won by 92 Runs | 3-0 Series Sweep",
            "archetype": "ASYMMETRIC_MISMATCH",
            "venue": {
                "id": "raipur_svns_stadium",
                "name": "Shaheed Veer Narayan Singh International Stadium, Raipur",
                "city": "Raipur",
                "soil_type": "Hard dry rolled surface with true bounce and fast outfield",
                "avg_first_innings": 185.0,
                "avg_second_innings": 130.0,
                "chasing_win_pct": 45.0,
                "pace_wicket_pct": 55.0,
                "spin_wicket_pct": 45.0,
                "dew_factor": 0.22,
                "pitch_nature": "Hard-rolled true bounce track (Mithali Raj & Ed Rainsford pitch report). Par 200+ for India batting first. Kranti Gaud shoulder bounce effective; Nandani Sharma back-of-the-hand slower balls unreadable under lights. 2nd innings skids on.",
                "boundaries": {"square_leg": 65, "midwicket": 68, "long_on": 72, "straight": 74, "long_off": 72, "cover": 66, "point": 63}
            },
            "teams": {
                "home": {"name": "India Women", "code": "IND-W", "score": "216/7 (20.0)", "overs": "20.0"},
                "away": {"name": "Zimbabwe Women", "code": "ZIM-W", "score": "124/7 (20.0)", "overs": "20.0"}
            },
            "toss": {
                "winner": "India Women",
                "choice": "bat",
                "statement": "India Women won toss and elected to bat first. Smriti: 'We will bat first today as we want more game time for the middle order. Sree Charani is resting and Prema comes in.'"
            },
            "current_crr": 10.80,
            "projected_total": 216,
            "chasing_win_prob": 12.0,
            "playing_xi_home": [
                {"name": "Shafali Verma", "role": "AR", "credits": 9.0, "order": 1, "bat_hand": "RHB", "bowl_style": "Right-arm offbreak"},
                {"name": "Smriti Mandhana", "role": "BAT", "credits": 8.5, "order": 2, "bat_hand": "LHB", "bowl_style": "Right-arm medium", "is_c": True},
                {"name": "Anushka Sharma", "role": "AR", "credits": 8.5, "order": 3, "bat_hand": "RHB", "bowl_style": "Right-arm offbreak"},
                {"name": "Harmanpreet Kaur", "role": "BAT", "credits": 8.0, "order": 4, "bat_hand": "RHB", "bowl_style": "Right-arm offbreak"},
                {"name": "Niki Prasad", "role": "BAT", "credits": 8.0, "order": 5, "bat_hand": "RHB", "bowl_style": "Right-arm offbreak"},
                {"name": "Richa Ghosh", "role": "WK", "credits": 8.0, "order": 6, "bat_hand": "RHB", "bowl_style": "Wicketkeeper", "is_wk": True},
                {"name": "Deepti Sharma", "role": "AR", "credits": 8.5, "order": 7, "bat_hand": "LHB", "bowl_style": "Right-arm offbreak"},
                {"name": "Arundhati Reddy", "role": "BOWL", "credits": 7.0, "order": 8, "bat_hand": "RHB", "bowl_style": "Right-arm medium-fast"},
                {"name": "Nandani Sharma", "role": "BOWL", "credits": 6.5, "order": 9, "bat_hand": "RHB", "bowl_style": "Right-arm fast-medium"},
                {"name": "Kranti Gaud", "role": "BOWL", "credits": 6.5, "order": 10, "bat_hand": "RHB", "bowl_style": "Right-arm medium-fast"},
                {"name": "Prema Rawat", "role": "BOWL", "credits": 8.0, "order": 11, "bat_hand": "RHB", "bowl_style": "Right-arm offbreak"}
            ],
            "playing_xi_away": [
                {"name": "Kelis Ndhlovu", "role": "BAT", "credits": 8.0, "order": 1, "bat_hand": "LHB", "bowl_style": "Slow left-arm orthodox"},
                {"name": "Beloved Biza", "role": "AR", "credits": 7.5, "order": 2, "bat_hand": "RHB", "bowl_style": "Right-arm medium-fast"},
                {"name": "Modester Mupachikwa", "role": "WK", "credits": 7.5, "order": 3, "bat_hand": "RHB", "bowl_style": "Wicketkeeper", "is_wk": True},
                {"name": "Sharne Mayers", "role": "BAT", "credits": 8.0, "order": 4, "bat_hand": "RHB", "bowl_style": "Right-arm offbreak"},
                {"name": "Nyasha Gwanzura", "role": "AR", "credits": 7.5, "order": 5, "bat_hand": "RHB", "bowl_style": "Right-arm offbreak"},
                {"name": "Michelle Mavunga", "role": "AR", "credits": 8.0, "order": 6, "bat_hand": "RHB", "bowl_style": "Right-arm medium-fast"},
                {"name": "Chipo Mugeri-Tiripano", "role": "BAT", "credits": 6.5, "order": 7, "bat_hand": "LHB", "bowl_style": "Right-arm medium"},
                {"name": "Josephine Nkomo", "role": "AR", "credits": 7.0, "order": 8, "bat_hand": "RHB", "bowl_style": "Right-arm medium-fast", "is_c": True},
                {"name": "Francisca Chipare", "role": "BOWL", "credits": 8.0, "order": 9, "bat_hand": "RHB", "bowl_style": "Right-arm medium"},
                {"name": "Tendai Makusha", "role": "BOWL", "credits": 6.0, "order": 10, "bat_hand": "RHB", "bowl_style": "Right-arm medium"},
                {"name": "Nomvelo Sibanda", "role": "BOWL", "credits": 6.0, "order": 11, "bat_hand": "RHB", "bowl_style": "Left-arm medium-fast"}
            ]
        }

        # Aliases
        self._matches["indw_zimw"] = self._matches["ind_w_vs_zim_w_2026_03"]
        self._matches["ind_w_vs_zim_w"] = self._matches["ind_w_vs_zim_w_2026_03"]
        self._active_match_id = "ind_w_vs_zim_w_2026_03"
'''
    old_alias = '        self._matches["indw_zimw"] = self._matches["ind_w_vs_zim_w_2026_02"]\n        self._matches["ind_w_vs_zim_w"] = self._matches["ind_w_vs_zim_w_2026_02"]'
    if old_alias in code:
        code = code.replace(old_alias, fixture_snippet)
    elif "ind_w_vs_zim_w_2026_03" not in code:
        # fallback replace
        code = re.sub(
            r'(\s+self\._matches\["indw_zimw"\] = self\._matches\["ind_w_vs_zim_w_2026_02"\])',
            r"\n" + fixture_snippet,
            code
        )

    # 2. Add Match Archetype Classifier and Rank 1 Decision Rules methods to UniversalMatchEngine class
    new_methods = '''
    def classify_match_archetype(self, match_meta: Dict[str, Any]) -> str:
        """Classifies fixture into one of the 4 Universal Grand League Archetypes:
        1. ROAD_HIGHWAY: Par score >= 180, true bounce, fast outfield.
        2. SPIN_CHOKE_MINEFIELD: Par score <= 145, spin-heavy, gripping cracks.
        3. ASYMMETRIC_MISMATCH: Top team vs Associate / bilateral dead-rubber mismatch.
        4. HIGH_STAKES_PARITY: Evenly matched franchises / tournament knockouts.
        """
        venue = match_meta.get("venue", {})
        par = float(venue.get("avg_first_innings", 155.0))
        toss_stmt = (match_meta.get("toss", {}).get("statement") or "").lower()
        h_code = match_meta.get("teams", {}).get("home", {}).get("code", "")
        a_code = match_meta.get("teams", {}).get("away", {}).get("code", "")
        
        # Mismatch detection
        mismatch_teams = {"ZIM-W", "SCO-W", "USA", "NAM", "UAE", "NEP", "PNG"}
        if a_code in mismatch_teams or h_code in mismatch_teams or "zimbabwe" in toss_stmt:
            return "ASYMMETRIC_MISMATCH"
        
        if par >= 180.0:
            return "ROAD_HIGHWAY"
        elif par <= 145.0 or venue.get("spin_wicket_pct", 50.0) >= 55.0:
            return "SPIN_CHOKE_MINEFIELD"
        return "HIGH_STAKES_PARITY"

    def apply_dead_rubber_captain_filter(self, pool: List[Dict[str, Any]], match_meta: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Dead-Rubber Captaincy Bias Filter:
        Detects when a series is already decided (e.g. 2-0 up) and captain announces
        'game time for middle order' -> penalizes captain's projected balls by 35% and boosts middle order (No. 3-5).
        """
        toss_stmt = (match_meta.get("toss", {}).get("statement") or "").lower()
        is_dead_rubber = any(k in toss_stmt for k in ["middle order", "game time", "rested", "experiment", "series won", "testing"])
        
        if is_dead_rubber:
            for p in pool:
                if p.get("is_c"):
                    # Captain demotes self or delegates overs
                    p["projected_points"] = round(p.get("projected_points", 40.0) * 0.65, 1)
                    p["ceiling_score"] = round(p.get("ceiling_score", 60.0) * 0.65, 1)
                elif p.get("role") in ("BAT", "AR") and 3 <= p.get("batting_order", 7) <= 5:
                    # Middle-order batters get promoted volume
                    p["projected_points"] = round(p.get("projected_points", 35.0) * 1.35, 1)
                    p["ceiling_score"] = round(p.get("ceiling_score", 55.0) * 1.45, 1)
        return pool
'''

    if "def classify_match_archetype" not in code:
        code = code.replace("    def _solve_four_gl_teams(", new_methods + "\n    def _solve_four_gl_teams(")

    # 3. Update _solve_four_gl_teams to support ind_w_vs_zim_w_2026_03 with the winning JOY MA TARA scripts
    raipur_03_scenarios = '''        # Scenarios aligned with venue & toss
        if match_meta["id"] == "ind_w_vs_zim_w_2026_03":
            scenarios = [
                {
                    "id": "scenario_1",
                    "name": "Team 1 — Harmanpreet 200+ Blowout & Underdog 2-Way Allrounder VC",
                    "tag": "HARMAN_EXPLOSION_UNDERDOG_ALLROUNDER_VC",
                    "script": "India bat first on hard Raipur deck to reach 215+. Harmanpreet Kaur (21% owned) captains middle-order surge (91* off 41). Beloved Biza (VC) takes 3 wickets in death overs and scores 44 runs (252 pts). 15.0 Cr unspent.",
                    "target_c": next((p["id"] for p in pool if "harman" in p["id"]), pool[3]["id"]),
                    "target_vc": next((p["id"] for p in pool if "biza" in p["id"]), pool[1]["id"]),
                    "credit_min": 81.0, "credit_max": 85.5
                },
                {
                    "id": "scenario_2",
                    "name": "Team 2 — Raipur Pace & Shoulder Bounce Demolition",
                    "tag": "RAIPUR_PACE_BOUNCE_BLITZ",
                    "script": "Kranti Gaud utilizes steep shoulder bounce to remove top order early. Arundhati Reddy and Nandani Sharma slower balls dismantle the chase under lights.",
                    "target_c": next((p["id"] for p in pool if "deepti" in p["id"]), pool[6]["id"]),
                    "target_vc": next((p["id"] for p in pool if "gaud" in p["id"]), pool[9]["id"]),
                    "credit_min": 81.0, "credit_max": 85.0
                },
                {
                    "id": "scenario_3",
                    "name": "Team 3 — Early Swing Stunner & Anchor Rebuild",
                    "tag": "EARLY_SWING_STUNNER_REBUILD",
                    "script": "Francisca Chipare (6.5% owned) takes early swing powerplay wicket. Harmanpreet Kaur anchors counter-attack before Indian bowlers sweep the lower order.",
                    "target_c": next((p["id"] for p in pool if "harman" in p["id"]), pool[3]["id"]),
                    "target_vc": next((p["id"] for p in pool if "chipare" in p["id"]), pool[8]["id"]),
                    "credit_min": 81.0, "credit_max": 85.0
                },
                {
                    "id": "scenario_4",
                    "name": "Team 4 — Nandani Back-of-the-Hand Slower Ball Choke",
                    "tag": "NANDANI_SLOWER_BALL_CHOKE",
                    "script": "Nandani Sharma (3 wkts, 4.5 econ) deceives Zimbabwe lower order with off-pace balls. Shafali Verma (69 off 37) sets up unassailable 216 total.",
                    "target_c": next((p["id"] for p in pool if "nandani" in p["id"]), pool[8]["id"]),
                    "target_vc": next((p["id"] for p in pool if "shafali" in p["id"]), pool[0]["id"]),
                    "credit_min": 81.0, "credit_max": 84.5
                }
            ]
        elif match_meta["id"] == "ind_w_vs_zim_w_2026_02":'''

    if 'elif match_meta["id"] == "ind_w_vs_zim_w_2026_02":' not in code:
        code = code.replace(
            '        # Scenarios aligned with venue & toss\n        if match_meta["id"] == "ind_w_vs_zim_w_2026_02":',
            raipur_03_scenarios
        )

    # 4. Enforce 13.5-19.0 credits unspent and C/VC independence in solver
    old_cr_comment = '# Credits: 80.0 to 85.0 (15 to 20 unspent)'
    new_cr_logic = '''# Law I: Unspent Credit Structural Shield (Enforce 13.5 to 19.0 Cr unspent => 81.0 to 86.5 Cr spent)
        cr_ints = [int(round(p["credits"] * 10)) for p in pool]
        min_cr = int(round(scenario.get("credit_min", 81.0) * 10))
        max_cr = int(round(scenario.get("credit_max", 85.5) * 10))'''

    if old_cr_comment in code:
        code = code.replace(old_cr_comment, new_cr_logic)

    with open(UNIVERSAL_ENGINE_PATH, "w", encoding="utf-8") as f:
        f.write(code)

    print("universal_engine.py successfully updated!")

if __name__ == "__main__":
    update_universal_engine()

