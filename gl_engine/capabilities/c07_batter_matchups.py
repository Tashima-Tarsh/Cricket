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
                    "sample_size": m.balls,
                    "confidence_label": ("HIGH" if m.balls >= 40 else ("MODERATE" if m.balls >= 20 else "SHRUNK_TOWARD_PRIOR")),
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
                    "sample_size": m.balls,
                    "confidence_label": ("HIGH" if m.balls >= 40 else ("MODERATE" if m.balls >= 20 else "SHRUNK_TOWARD_PRIOR")),
                    "tactical_note": f"{m.batter_name} dominates {m.bowler_name} striking at {m.strike_rate}."
                })

        style_insights = []
        for danger in key_danger_zones[:2]:
            style_insights.append(danger["tactical_note"])
        for adv in key_advantages[:2]:
            style_insights.append(adv["tactical_note"])

        if self.players:
            lhb_count = sum(1 for p in self.players if "LHB" in (p.batting_style or "").upper() or "LEFT" in (p.batting_style or "").upper())
            off_spinners = [p.name for p in self.players if "OFF" in (p.bowling_style or "").upper() or "OB" in (p.bowling_style or "").upper()]
            if lhb_count > 0 and off_spinners:
                style_insights.append(
                    f"Lineup tactical matchup: {lhb_count} left-handed batter(s) in active squads face off-spin threats ({', '.join(off_spinners[:2])}) in powerplay and middle overs."
                )

        if not style_insights:
            style_insights.append(
                "Head-to-head delivery sample is limited for this fixture. Matchup assessments rely on role priors and venue pace/spin distribution."
            )

        return {
            "capability": "cricket-batter-matchups",
            "key_danger_zones": key_danger_zones,
            "key_batter_advantages": key_advantages,
            "tactical_style_insights": style_insights,
            "all_h2h_records": [m.model_dump() for m in self.matchups]
        }
