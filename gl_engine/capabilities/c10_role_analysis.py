"""Capability 10: cricket-role-analysis
Batting order, expected overs, multi-category floor, and role stability.
"""
from typing import List, Dict, Any
from ..models import Player

class CricketRoleAnalysis:
    def __init__(self, players: List[Player]):
        self.players = players

    def execute(self) -> Dict[str, Any]:
        dual_threat_allrounders = []
        specialist_batsmen = []
        specialist_bowlers = []
        wicketkeepers = []

        for p in self.players:
            # Dual threat: Bats top 7 AND bowls at least 2.5 overs
            if p.batting_order_projected <= 7 and p.expected_overs >= 2.5:
                dual_threat_allrounders.append({
                    "name": p.name,
                    "team": p.team,
                    "bat_order": p.batting_order_projected,
                    "overs": p.expected_overs,
                    "floor_rating": "Very High",
                    "reason": "Points from both batting crease and bowling spells make them essential cash/safe picks."
                })
            elif p.role == "WK":
                wicketkeepers.append({
                    "name": p.name,
                    "team": p.team,
                    "bat_order": p.batting_order_projected,
                    "dismissal_equity": "Expected 1-2 catches/stumpings"
                })
            elif p.expected_overs >= 3.0:
                specialist_bowlers.append({
                    "name": p.name,
                    "team": p.team,
                    "overs": p.expected_overs,
                    "death_presence": p.stats.death_overs_rate > 0.3
                })
            else:
                specialist_batsmen.append({
                    "name": p.name,
                    "team": p.team,
                    "bat_order": p.batting_order_projected,
                    "strike_rate": p.stats.strike_rate
                })

        return {
            "capability": "cricket-role-analysis",
            "dual_threat_allrounders": dual_threat_allrounders,
            "wicketkeepers": wicketkeepers,
            "specialist_bowlers": specialist_bowlers,
            "specialist_batsmen": specialist_batsmen,
            "tactical_guideline": "In Grand Leagues, maximize high-ceiling specialist hitters and death pacers rather than just stacking floor-safe all-rounders."
        }
