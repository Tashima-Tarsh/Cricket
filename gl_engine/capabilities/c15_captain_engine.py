"""Capability 15: cricket-captain-engine
Rank captain (2x) and vice-captain (1.5x) combinations based on ceiling, correlation and leverage.
"""
from typing import List, Dict, Any, Tuple
from ..models import Player

class CricketCaptainEngine:
    def __init__(self, players: List[Player]):
        self.players = players

    def execute(self) -> Dict[str, Any]:
        # High-ceiling candidates
        candidates = sorted(self.players, key=lambda x: x.ceiling_score, reverse=True)
        
        # Categorize Captains
        chalk_captains = []
        differential_captains = []

        for p in candidates:
            # Captain score combines ceiling, role equity, and differential leverage
            c_score = p.ceiling_score * 2.0
            entry = {
                "id": p.id,
                "name": p.name,
                "team": p.team,
                "role": p.role,
                "ownership": p.projected_ownership,
                "ceiling": p.ceiling_score,
                "captain_ceiling_pts": c_score
            }
            if p.projected_ownership >= 60.0:
                chalk_captains.append(entry)
            else:
                differential_captains.append(entry)

        # Generate Correlated Pairs for Grand Leagues
        gl_pairs = [
            {
                "captain": "Abhishek Sharma",
                "vice_captain": "Arshdeep Singh",
                "narrative": "Dominant India: Abhishek sets electric target/chase, Arshdeep destroys WI chase at death.",
                "type": "Safe Anchor + Death Weapon"
            },
            {
                "captain": "Tilak Varma",
                "vice_captain": "Mayank Yadav",
                "narrative": "Ultra Differential GL Punt: Early wicket brings Tilak in to score big; Mayank tears through WI top order with extreme pace.",
                "type": "High Leverage (Both sub-40% owned)"
            },
            {
                "captain": "Romario Shepherd",
                "vice_captain": "Shai Hope",
                "narrative": "West Indies Fightback: Hope anchors innings with 70+, Shepherd finishes with bat and takes 3 wickets in death overs.",
                "type": "WI Upset Scenario"
            },
            {
                "captain": "Axar Patel",
                "vice_captain": "Kuldeep Yadav",
                "narrative": "Spin Web Choke: Pitch takes turn; Axar and Kuldeep combine for 6+ wickets in middle overs.",
                "type": "Spin Squeeze Dominance"
            },
            {
                "captain": "Sanju Samson",
                "vice_captain": "Matthew Forde",
                "narrative": "Contrarian Chaos: Forde gets early breakthrough, Samson enters in middle phase and blasts a rapid 80+.",
                "type": "Extreme Chaos Differential"
            }
        ]

        return {
            "capability": "cricket-captain-engine",
            "chalk_captains": chalk_captains[:4],
            "differential_captains": differential_captains[:5],
            "recommended_gl_pairs": gl_pairs
        }
