"""Capability 18: cricket-opponent-simulator
Model plausible competing field lineups, calculate duplication risk, and assess leverage.
"""
from typing import List, Dict, Any
from ..models import Lineup

class CricketOpponentSimulator:
    def __init__(self, lineups: List[Lineup], pool_size: int = 1000000):
        self.lineups = lineups
        self.pool_size = pool_size

    def execute(self) -> Dict[str, Any]:
        evaluations = []

        for lineup in self.lineups:
            # Estimate probability of an opponent generating this exact lineup
            # Based on product of player ownerships normalized
            prod_prob = 1.0
            for p in lineup.players:
                prod_prob *= (p.projected_ownership / 100.0)
            
            # Captain & Vice Captain ownership correlation
            c_factor = (lineup.captain.projected_ownership / 100.0) * 0.4
            vc_factor = (lineup.vice_captain.projected_ownership / 100.0) * 0.3
            
            lineup_rarity_index = prod_prob * c_factor * vc_factor
            
            # Projected duplicates in a 1M user contest
            # Chalk lineups (>650 cumulative ownership) have 500 - 5000 duplicates
            # Contrarian lineups (<450 cumulative ownership) have 0 - 5 duplicates
            cum_own = lineup.total_ownership_sum
            if cum_own > 650:
                expected_duplicates = int(max(40, (cum_own - 650) ** 1.8 + 10))
                duplication_risk = "Severe (1st prize would be split among dozens)"
            elif cum_own > 520:
                expected_duplicates = int(max(5, (cum_own - 500) * 0.4))
                duplication_risk = "Moderate (A few duplicate lineups expected)"
            else:
                expected_duplicates = 0  # Unique or near unique
                duplication_risk = "Negligible / Solitary Win Potential (Max Prize Payout)"

            leverage_score = round(lineup.simulated_ceiling / max(1, expected_duplicates + 1), 1)

            evaluations.append({
                "team_name": lineup.team_name,
                "cumulative_ownership": cum_own,
                "differentials_count": lineup.differential_count,
                "expected_duplicates_in_1M_field": expected_duplicates,
                "duplication_risk_level": duplication_risk,
                "grand_league_leverage_score": leverage_score,
                "calibration_status": "HEURISTIC_COMBINATORIC_ESTIMATE",
                "uniqueness_rating": "⭐️⭐️⭐️⭐️⭐️" if expected_duplicates == 0 else (
                    "⭐️⭐️⭐️⭐️" if expected_duplicates < 10 else "⭐️⭐️"
                )
            })

        return {
            "capability": "cricket-opponent-simulator",
            "field_pool_size": self.pool_size,
            "lineup_evaluations": evaluations,
            "tactical_rule": "Avoid cumulative ownership > 620 in massive GPP contests; target 420-540 cumulative ownership for solo 1st rank equity."
        }
