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
            winner="Home", decision="BOWL_FIRST", dew_impact=1.15, bat_first_advantage=0.92
        )
        
        # Analyze game scripts dynamically based on toss
        winner = scenario.winner or "Home"
        other_team = getattr(scenario, "loser", None) or ("Away" if winner == "Home" else "Opponent")
        chasing_team = winner if scenario.decision == "BOWL_FIRST" else other_team
        batting_first_team = other_team if chasing_team == winner else winner
        
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
        else:
            tactical_implications.append(
                f"{batting_first_team} electing to bat first aims to post an above-par total on dry surface."
            )
            tactical_implications.append(
                f"{batting_first_team} top-order anchors benefit from maximum ball-striking conditions before surface degradation."
            )
            tactical_implications.append(
                f"{chasing_team} will face scoreboard pressure in the chase against {batting_first_team} frontline spinners."
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
