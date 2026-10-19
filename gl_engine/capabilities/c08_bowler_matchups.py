"""Capability 8: cricket-bowler-matchups
Wicket probabilities against batting positions (powerplay strikes vs death bursts).
"""
from typing import List, Dict, Any
from ..models import Player

class CricketBowlerMatchups:
    def __init__(self, players: List[Player]):
        self.players = players

    def execute(self) -> Dict[str, Any]:
        bowler_profiles = []
        for p in self.players:
            if p.expected_overs >= 2.0:
                # Calculate strike index
                pp_weight = p.stats.powerplay_overs_rate
                death_weight = p.stats.death_overs_rate
                base_sr = p.stats.bowling_strike_rate if p.stats.bowling_strike_rate > 0 else 18.0
                
                # Death overs have ~2.2x higher wicket probability per ball than middle overs
                wicket_burst_index = round((pp_weight * 1.3 + death_weight * 2.2 + (24.0 / base_sr)), 2)
                
                target_victims = []
                if death_weight > 0.3:
                    target_victims.append("Overs 16-20 finishers looking for boundaries")
                if pp_weight > 0.3:
                    target_victims.append("Overs 1-6 openers attacking early swing/skid")
                if pp_weight <= 0.2 and death_weight <= 0.2:
                    target_victims.append("Middle-order consolidating batters (overs 7-15)")
                
                bowler_profiles.append({
                    "bowler_id": p.id,
                    "name": p.name,
                    "team": p.team,
                    "overs": p.expected_overs,
                    "economy": p.stats.economy,
                    "powerplay_rate": p.stats.powerplay_overs_rate,
                    "death_rate": p.stats.death_overs_rate,
                    "wicket_burst_index": wicket_burst_index,
                    "primary_target_zones": target_victims
                })
        
        bowler_profiles.sort(key=lambda x: x["wicket_burst_index"], reverse=True)
        
        return {
            "capability": "cricket-bowler-matchups",
            "top_strike_threats": bowler_profiles[:5],
            "all_bowler_profiles": bowler_profiles,
            "death_overs_enforcers": [b["name"] for b in bowler_profiles if b["death_rate"] >= 0.3],
            "powerplay_swing_merchants": [b["name"] for b in bowler_profiles if b["powerplay_rate"] >= 0.4]
        }
