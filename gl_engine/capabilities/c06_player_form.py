"""Capability 6: cricket-player-form
Rolling performance across recent matches with exponential recency weighting.
"""
from typing import List, Dict, Any
import numpy as np
from ..models import Player

class CricketPlayerForm:
    def __init__(self, players: List[Player]):
        self.players = players

    def execute(self) -> Dict[str, Any]:
        form_rankings = []
        
        for p in self.players:
            pts = p.stats.recent_fantasy_pts
            if pts:
                # Exponential recency weights: [0.1, 0.15, 0.2, 0.25, 0.3]
                n = len(pts)
                weights = np.linspace(0.5, 1.5, n)
                weights /= weights.sum()
                weighted_form = float(np.dot(pts, weights))
                volatility = float(np.std(pts)) if len(pts) > 1 else 15.0
            else:
                weighted_form = p.stats.avg_fantasy_pts
                volatility = 20.0
            
            form_rankings.append({
                "id": p.id,
                "name": p.name,
                "team": p.team,
                "role": p.role,
                "weighted_form_pts": round(weighted_form, 1),
                "volatility_std": round(volatility, 1),
                "recent_runs": p.stats.recent_runs,
                "recent_wickets": p.stats.recent_wickets,
                "form_status": "Red Hot" if weighted_form >= 70 else ("Solid" if weighted_form >= 50 else "Cold/Struggling")
            })
            
        form_rankings.sort(key=lambda x: x["weighted_form_pts"], reverse=True)
        
        return {
            "capability": "cricket-player-form",
            "top_in_form_players": form_rankings[:6],
            "all_rankings": form_rankings
        }
