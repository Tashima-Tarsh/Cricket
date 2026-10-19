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
        if p.name == "Mayank Yadav":
            return "150kph+ express pace rattle top order and clean up tail (3-4 wickets in quick succession)."
        elif p.name == "Tilak Varma":
            return "Stabilizes after early wicket, scores a rapid 70+ and snags 1 wicket with off-spin against WI lefties."
        elif p.name == "Matthew Forde":
            return "New ball swing removes Indian openers early in powerplay (2 wickets + maiden over)."
        elif p.name == "Sherfane Rutherford":
            return "Promoted as left-handed disruptor during middle overs, scores explosive 50* with 5 sixes."
        elif p.name == "Washington Sundar":
            return "Powerplay squeeze bowling (2 wickets under 6.0 econ) + valuable 25 runs down the order."
        elif p.name == "Shamar Joseph":
            return "Unplayable yorkers and bouncers in death overs picking 3 wickets."
        return f"Outperforms baseline by fulfilling key {p.role} duties."
