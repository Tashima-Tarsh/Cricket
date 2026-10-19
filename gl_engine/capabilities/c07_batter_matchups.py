"""Capability 7: cricket-batter-matchups
Batter versus individual bowlers and bowling styles (head-to-head records and angle vulnerabilities),
augmented with PlayerBattlesMCPEngine.
"""
from typing import List, Dict, Any
from ..models import MatchupDetail, Player
from ..player_battles_mcp import PlayerBattlesMCPEngine


class CricketBatterMatchups:
    def __init__(self, matchups: List[MatchupDetail], players: List[Player]):
        self.matchups = matchups
        self.players = players
        self.engine = PlayerBattlesMCPEngine([
            {
                "batter": m.batter_name,
                "bowler": m.bowler_name,
                "balls": m.balls,
                "runs": m.runs,
                "dismissals": m.dismissals
            }
            for m in matchups
        ])

    def execute(self) -> Dict[str, Any]:
        matchup_matrix = []
        key_advantages = []
        key_danger_zones = []

        for m in self.matchups:
            h2h = self.engine.query_h2h_battle(m.batter_name, m.bowler_name)
            if m.dismissals >= 2 and m.strike_rate < 120.0:
                key_danger_zones.append({
                    "batter": m.batter_name,
                    "nemesis_bowler": m.bowler_name,
                    "balls": m.balls,
                    "runs": m.runs,
                    "dismissals": m.dismissals,
                    "strike_rate": m.strike_rate,
                    "advantage": h2h.tactical_advantage if h2h else "Bowler Dominant",
                    "tactical_note": f"{m.bowler_name} has dismissed {m.batter_name} {m.dismissals} times in {m.balls} balls at SR {m.strike_rate}."
                })
            elif m.strike_rate >= 155.0 and m.dismissals <= 1:
                key_advantages.append({
                    "batter": m.batter_name,
                    "exploited_bowler": m.bowler_name,
                    "balls": m.balls,
                    "runs": m.runs,
                    "dismissals": m.dismissals,
                    "strike_rate": m.strike_rate,
                    "advantage": h2h.tactical_advantage if h2h else "Batter Dominant",
                    "tactical_note": f"{m.batter_name} dominates {m.bowler_name} striking at {m.strike_rate}."
                })

        style_insights = [
            "India's Top 5 contains 3 Left-Handers (Abhishek, Ishan, Tilak): Roston Chase (offbreak) will be utilized in powerplay & middle overs.",
            "Shivam Dube strikes at 209+ against left-arm orthodox spinners (Akeal Hosein / Motie). Dube is a major matchup counter-pick.",
            "Kuldeep Yadav's chinaman/googly historically troubles West Indies middle-order power hitters (Powell, Rutherford strike <95 against Kuldeep with high dismissal rates)."
        ]

        return {
            "capability": "cricket-batter-matchups",
            "key_danger_zones": key_danger_zones,
            "key_batter_advantages": key_advantages,
            "tactical_style_insights": style_insights,
            "all_h2h_records": [m.model_dump() for m in self.matchups]
        }
