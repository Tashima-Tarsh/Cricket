"""Capability 17: cricket-multi-team-optimizer
Generate diverse valid fantasy lineups using Google OR-Tools CP-SAT (with SciPy MILP fallback)
across distinct Grand League game scripts.
Guarantees roster constraints, credit budget, role balance, and pairwise lineup diversity.
"""
from typing import List, Dict, Any, Optional
from ..models import Player, Lineup
from ..config import LineupConstraints, DEFAULT_CONSTRAINTS
from ..ortools_optimizer import ORToolsCricketOptimizer


class CricketMultiTeamOptimizer:
    def __init__(
        self,
        players: List[Player],
        constraints: LineupConstraints = DEFAULT_CONSTRAINTS
    ):
        self.players = players
        self.constraints = constraints
        self.or_tools_optimizer = ORToolsCricketOptimizer(players, constraints)

    def generate_grand_league_portfolio(
        self,
        num_teams: int = 10,
        min_differentials_per_team: int = 2,
        max_overlap_between_teams: int = 8
    ) -> List[Lineup]:
        """Generates diverse Grand League lineups using Google OR-Tools CP-SAT."""
        return self.or_tools_optimizer.generate_grand_league_portfolio(
            num_teams=num_teams,
            min_differentials_per_team=min_differentials_per_team,
            max_overlap_between_teams=max_overlap_between_teams
        )
