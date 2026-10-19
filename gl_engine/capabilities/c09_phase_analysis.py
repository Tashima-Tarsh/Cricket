"""Capability 9: cricket-phase-analysis
Powerplay (1-6), Middle-overs (7-15) and Death-overs (16-20) performance metrics.
"""
from typing import List, Dict, Any
from ..models import Player

class CricketPhaseAnalysis:
    def __init__(self, players: List[Player]):
        self.players = players

    def execute(self) -> Dict[str, Any]:
        powerplay_specialists = []
        middle_anchors_spinners = []
        death_finishers_pacers = []
        
        for p in self.players:
            # Batting categorization
            if p.batting_order_projected in [1, 2, 3]:
                powerplay_specialists.append(f"{p.name} ({p.team}) - PP Attacker")
            elif p.batting_order_projected in [4, 5]:
                middle_anchors_spinners.append(f"{p.name} ({p.team}) - Middle Spin Stabilizer")
            elif p.batting_order_projected in [6, 7]:
                death_finishers_pacers.append(f"{p.name} ({p.team}) - Death Finisher")
                
            # Bowling categorization
            if p.stats.powerplay_overs_rate >= 0.4:
                powerplay_specialists.append(f"{p.name} ({p.team}) - PP Ball Mover")
            if p.stats.powerplay_overs_rate < 0.3 and p.stats.death_overs_rate < 0.2 and p.expected_overs >= 3:
                middle_anchors_spinners.append(f"{p.name} ({p.team}) - Middle Choker/Spinner")
            if p.stats.death_overs_rate >= 0.3:
                death_finishers_pacers.append(f"{p.name} ({p.team}) - Death Wicket Specialist")

        return {
            "capability": "cricket-phase-analysis",
            "phase_breakdown": {
                "Powerplay (Overs 1-6)": {
                    "phase_par_score": "48-55 runs / 1.5 wickets",
                    "tactical_focal_point": "New ball swing vs aggressive boundary clearing",
                    "key_protagonists": powerplay_specialists
                },
                "Middle Overs (Overs 7-15)": {
                    "phase_par_score": "68-78 runs / 2.2 wickets",
                    "tactical_focal_point": "Spin squeeze vs boundary rotation and matchup exploitation",
                    "key_protagonists": middle_anchors_spinners
                },
                "Death Overs (Overs 16-20)": {
                    "phase_par_score": "52-65 runs / 3.4 wickets",
                    "tactical_focal_point": "Yorkers, slower cutters vs all-out maximum clearing. Highest fantasy point yield per over.",
                    "key_protagonists": death_finishers_pacers
                }
            }
        }
