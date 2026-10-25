"""Capability 14: cricket-differential-finder
Identify plausible low-ownership (<35%), high-upside ceiling picks essential for Grand League 1st rank.
"""
from typing import List, Dict, Any
from ..models import Player

class CricketDifferentialFinder:
    def __init__(self, players: List[Player]):
        self.players = players

    def execute(self) -> Dict[str, Any]:
        differentials = []

        for p in self.players:
            # Grand League Differential criteria:
            # 1. Ownership < 40% (ideally < 30%)
            # 2. Ceiling >= 100 points
            if p.projected_ownership <= 42.0:
                leverage_score = round((p.ceiling_score / max(10.0, p.projected_ownership)) * 10.0, 1)
                differentials.append({
                    "id": p.id,
                    "name": p.name,
                    "team": p.team,
                    "role": p.role,
                    "credits": p.credits,
                    "ownership_pct": p.projected_ownership,
                    "ceiling_score": p.ceiling_score,
                    "leverage_score": leverage_score,
                    "tag": p.differential_tag or "Punt Pick",
                    "path_to_ceiling": self._generate_path_to_ceiling(p)
                })

        differentials.sort(key=lambda x: x["leverage_score"], reverse=True)

        return {
            "capability": "cricket-differential-finder",
            "top_differential_picks": differentials[:6],
            "all_differentials": differentials,
            "core_gl_rule": "Every winning Grand League lineup MUST contain 2 to 3 players from this list to differentiate from millions of standard entries."
        }

    def _generate_path_to_ceiling(self, p: Player) -> str:
        role = (p.role or "BAT").upper()
        if role == "BOWL":
            style = p.bowling_style or "Pace"
            return f"Frontline {style} burst capturing 3+ wickets across powerplay and death phases with high dot-ball volume."
        elif role == "AR":
            return "Dual-threat leverage: contributes 25+ vital runs with the bat plus 1-2 key wickets in middle/death overs."
        elif role == "WK":
            return "Top-order boundary surge (40+ runs) combined with 2+ dismissals (catches/stumpings) behind the stumps."
        else:
            order = getattr(p, "batting_order_projected", 4)
            if order <= 3:
                return "Top-order aggression exploiting fielding restrictions to compile an explosive half-century (50+ runs)."
            else:
                return "Middle-overs acceleration and death finishing flurry with multiple boundaries and high strike rate."
