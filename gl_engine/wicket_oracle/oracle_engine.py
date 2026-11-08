"""Fixture-neutral oracle interface. Never invent lines, probabilities or venue stats."""
from typing import Any, Dict, List, Optional

def compute_fractional_kelly(edge: float, implied_prob: float, fraction: float = 0.25) -> float:
    """
    Calculate Fractional Kelly Criterion stake sizing.
    Kelly formula: f* = (edge / (1 / implied_prob - 1)) * fraction * 100%
    """
    if implied_prob <= 0 or implied_prob >= 1.0 or edge <= 0:
        return 0.0
    odds_multiplier = (1.0 / implied_prob) - 1.0
    if odds_multiplier <= 0:
        return 0.0
    raw_kelly = (edge / odds_multiplier) * fraction * 100.0
    return round(max(0.0, min(raw_kelly, 10.0)), 1)  # Cap single bet at 10% of bankroll for safety


def convert_prob_to_american_odds(prob: float) -> str:
    """Convert decimal probability to American odds string (+120, -140)."""
    if prob <= 0 or prob >= 1:
        return "EVEN"
    if prob > 0.5:
        odds = round(-100.0 / ((1.0 / prob) - 1.0))
        return str(odds)
    else:
        odds = round(((1.0 / prob) - 1.0) * 100.0)
        return f"+{odds}"



class WicketOracleEngine:
    IPL_TEAMS: List[str] = []

    @classmethod
    def get_value_bets(cls, match_data: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        return []

    @classmethod
    def get_player_props(cls, players: List[Dict[str, Any]], match_id: Optional[str] = None) -> List[Dict[str, Any]]:
        return []

    @classmethod
    def get_team_phase_deep_dive(cls, team_name: str) -> Dict[str, Any]:
        return {"status": "UNAVAILABLE_NO_SOURCED_PHASE_DATA",
                "team": team_name, "overall_avg_score": None,
                "death_overs_economy": None, "powerplay_avg_runs": None,
                "phases": [], "venue_records": []}
