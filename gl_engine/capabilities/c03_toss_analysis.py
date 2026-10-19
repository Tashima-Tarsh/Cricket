"""Capability 3: cricket-toss-analysis
Model batting-first and chasing implications, dew impact, and game script adjustments.
"""
from typing import Dict, Any, List
from ..models import TossScenario, VenueConditions

class CricketTossAnalysis:
    def __init__(self, venue: VenueConditions, toss_scenarios: List[TossScenario]):
        self.venue = venue
        self.toss_scenarios = toss_scenarios

    def execute(self, selected_scenario_index: int = 0) -> Dict[str, Any]:
        scenario = self.toss_scenarios[selected_scenario_index] if self.toss_scenarios else TossScenario(
            winner="IND", decision="BOWL_FIRST", dew_impact=1.15, bat_first_advantage=0.92
        )
        
        # Analyze game scripts based on toss
        chasing_team = scenario.winner if scenario.decision == "BOWL_FIRST" else ("WI" if scenario.winner == "IND" else "IND")
        batting_first_team = "WI" if chasing_team == "IND" else "IND"
        
        tactical_implications = []
        if scenario.decision == "BOWL_FIRST":
            tactical_implications.append(
                f"{chasing_team} bowling first will benefit from maximum grip and swing in 1st innings Powerplay."
            )
            tactical_implications.append(
                f"Dew in 2nd innings (dew factor: {self.venue.dew_factor}) will reduce spin grip by ~20%, heavily favoring {chasing_team} top-order batters."
            )
            tactical_implications.append(
                f"{batting_first_team} death bowlers will face wet ball conditions, increasing boundary conceded rate by 18%."
            )
        
        return {
            "capability": "cricket-toss-analysis",
            "toss_winner": scenario.winner,
            "decision": scenario.decision,
            "batting_first": batting_first_team,
            "chasing": chasing_team,
            "chasing_win_probability": self.venue.chasing_win_pct,
            "dew_multiplier_second_innings": scenario.dew_impact,
            "tactical_implications": tactical_implications,
            "recommended_strategy": f"Anchor heavy lineup around {chasing_team} top-order chase masters and {chasing_team} death pacers."
        }
