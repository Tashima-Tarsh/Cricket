"""Capability 15: cricket-captain-engine
Rank captain (2x) and vice-captain (1.5x) combinations based on ceiling, correlation and leverage.
Generates dynamic correlated pairs strictly from the active match roster.
"""
from typing import List, Dict, Any, Tuple
from ..models import Player

class CricketCaptainEngine:
    def __init__(self, players: List[Player]):
        self.players = players

    def execute(self) -> Dict[str, Any]:
        # High-ceiling candidates
        candidates = sorted(self.players, key=lambda x: x.ceiling_score, reverse=True)
        
        # Categorize Captains
        chalk_captains = []
        differential_captains = []

        for p in candidates:
            # Captain score combines ceiling, role equity, and differential leverage
            c_score = p.ceiling_score * 2.0
            entry = {
                "id": p.id,
                "name": p.name,
                "team": p.team,
                "role": p.role,
                "ownership": p.projected_ownership,
                "ceiling": p.ceiling_score,
                "captain_ceiling_pts": c_score
            }
            if p.projected_ownership >= 60.0:
                chalk_captains.append(entry)
            else:
                differential_captains.append(entry)

        # Generate Correlated Pairs for Grand Leagues dynamically from active roster
        gl_pairs = []
        if len(self.players) >= 2:
            teams = list(dict.fromkeys(p.team for p in self.players if p.team))
            team_a = teams[0] if len(teams) > 0 else "Team A"
            team_b = teams[1] if len(teams) > 1 else team_a

            team_a_players = [p for p in candidates if p.team == team_a]
            team_b_players = [p for p in candidates if p.team == team_b]

            # 1. Team A Dominance (Leading batter/AR + Primary Bowler/AR)
            t_a_bat = next((p for p in team_a_players if p.role in ["BAT", "WK", "AR"]), None)
            t_a_bowl = next((p for p in team_a_players if p.role in ["BOWL", "AR"] and p != t_a_bat), None)
            if t_a_bat and t_a_bowl:
                gl_pairs.append({
                    "captain": t_a_bat.name,
                    "vice_captain": t_a_bowl.name,
                    "narrative": f"Dominant {team_a}: {t_a_bat.name} anchors scoring; {t_a_bowl.name} attacks {team_b} with key wickets.",
                    "type": "Safe Anchor + Bowling Weapon"
                })

            # 2. High Leverage Differential Punt (Sub-50% ownership high-ceiling C + Top Bowler)
            diff_c = next((p for p in differential_captains if p["ceiling"] >= 50.0), None)
            if diff_c:
                vc_cand = next((p for p in candidates if p.id != diff_c["id"] and p.role in ["BOWL", "AR"]), None)
                if vc_cand:
                    gl_pairs.append({
                        "captain": diff_c["name"],
                        "vice_captain": vc_cand.name,
                        "narrative": f"High Leverage Differential Punt: {diff_c['name']} (sub-{diff_c['ownership']:.0f}% owned) outscores the chalk; {vc_cand.name} provides baseline volume.",
                        "type": "Leverage Surge"
                    })

            # 3. Team B Counter-Attack (Leading batter/AR from Team B + Team B Bowler)
            if team_b != team_a and team_b_players:
                t_b_bat = next((p for p in team_b_players if p.role in ["BAT", "WK", "AR"]), None)
                t_b_bowl = next((p for p in team_b_players if p.role in ["BOWL", "AR"] and p != t_b_bat), None)
                if t_b_bat and t_b_bowl:
                    gl_pairs.append({
                        "captain": t_b_bat.name,
                        "vice_captain": t_b_bowl.name,
                        "narrative": f"{team_b} Fightback / Upset: {t_b_bat.name} produces match-winning volume, paired with {t_b_bowl.name}'s bowling upside.",
                        "type": f"{team_b} Upset Scenario"
                    })

            # 4. Dual All-Rounder Floor/Ceiling Stack
            all_rounders = [p for p in candidates if p.role == "AR"]
            if len(all_rounders) >= 2:
                gl_pairs.append({
                    "captain": all_rounders[0].name,
                    "vice_captain": all_rounders[1].name,
                    "narrative": f"Dual All-Rounder High-Floor Strategy: {all_rounders[0].name} and {all_rounders[1].name} accumulate points across batting and bowling phases.",
                    "type": "All-Rounder Dominance"
                })

            # 5. Contrarian Top/Death Split
            if len(candidates) >= 4 and len(gl_pairs) < 5:
                c_pick = candidates[1] if candidates[1].name != (gl_pairs[0]["captain"] if gl_pairs else "") else candidates[0]
                vc_pick = candidates[3] if len(candidates) > 3 else candidates[-1]
                gl_pairs.append({
                    "captain": c_pick.name,
                    "vice_captain": vc_pick.name,
                    "narrative": f"Tournament Portfolio Pivot: {c_pick.name} provides ceiling leverage; {vc_pick.name} serves as a contrarian anchor.",
                    "type": "Contrarian Chaos Differential"
                })

        return {
            "capability": "cricket-captain-engine",
            "chalk_captains": chalk_captains[:4],
            "differential_captains": differential_captains[:5],
            "recommended_gl_pairs": gl_pairs
        }
