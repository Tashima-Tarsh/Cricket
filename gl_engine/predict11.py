"""Predict-11 Fantasy Cricket Application Foundation.
Implements Dream11 contest rules, squad formation constraints, official T20 fantasy points scoring,
roster validation, portfolio evaluation, and multi-format lineup exporters.
"""

from typing import List, Dict, Any, Optional, Tuple
from pydantic import BaseModel, Field
import pandas as pd


class Dream11Rules:
    """Official Dream11 Fantasy Cricket Rules & Constraints."""
    TOTAL_PLAYERS: int = 11
    MAX_CREDITS: float = 100.0
    
    # Modern Dream11 rules allow up to 10 players from a single team; classic allows 7
    MAX_PLAYERS_PER_TEAM: int = 10
    MIN_PLAYERS_PER_TEAM: int = 1
    
    # Position limits (Modern flexible rules: 1-8 for each category)
    MIN_WK: int = 1
    MAX_WK: int = 8
    MIN_BAT: int = 1
    MAX_BAT: int = 8
    MIN_AR: int = 1
    MAX_AR: int = 8
    MIN_BOWL: int = 1
    MAX_BOWL: int = 8

    # Multipliers
    CAPTAIN_MULTIPLIER: float = 2.0
    VICE_CAPTAIN_MULTIPLIER: float = 1.5


class ValidationResult(BaseModel):
    is_valid: bool
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    credits_used: float = 0.0
    role_counts: Dict[str, int] = Field(default_factory=dict)
    team_counts: Dict[str, int] = Field(default_factory=dict)


class Predict11Foundation:
    def __init__(self, rules: Dream11Rules = Dream11Rules()):
        self.rules = rules

    def validate_lineup(
        self,
        players: List[Dict[str, Any]],
        captain_id: str,
        vice_captain_id: str
    ) -> ValidationResult:
        """Validates whether a lineup complies with all Dream11 fantasy rules."""
        errors = []
        warnings = []

        # 1. Total players count
        if len(players) != self.rules.TOTAL_PLAYERS:
            errors.append(f"Lineup must contain exactly {self.rules.TOTAL_PLAYERS} players; received {len(players)}.")

        # 2. Duplicate players
        player_ids = [p.get("id") or p.get("name") for p in players]
        if len(set(player_ids)) != len(players):
            errors.append("Lineup contains duplicate players.")

        # 3. Credits check
        total_credits = sum(float(p.get("credits", 0.0)) for p in players)
        if total_credits > self.rules.MAX_CREDITS:
            errors.append(f"Total credits ({total_credits:.1f}) exceeds salary budget of {self.rules.MAX_CREDITS}.")

        # 4. Role limits
        role_counts = {"WK": 0, "BAT": 0, "AR": 0, "BOWL": 0}
        team_counts: Dict[str, int] = {}

        for p in players:
            role = p.get("role", "BAT")
            role_counts[role] = role_counts.get(role, 0) + 1
            team = p.get("team", "Unknown")
            team_counts[team] = team_counts.get(team, 0) + 1

        if not (self.rules.MIN_WK <= role_counts.get("WK", 0) <= self.rules.MAX_WK):
            errors.append(f"Wicketkeepers ({role_counts.get('WK', 0)}) must be between {self.rules.MIN_WK} and {self.rules.MAX_WK}.")
        if not (self.rules.MIN_BAT <= role_counts.get("BAT", 0) <= self.rules.MAX_BAT):
            errors.append(f"Batters ({role_counts.get('BAT', 0)}) must be between {self.rules.MIN_BAT} and {self.rules.MAX_BAT}.")
        if not (self.rules.MIN_AR <= role_counts.get("AR", 0) <= self.rules.MAX_AR):
            errors.append(f"All-rounders ({role_counts.get('AR', 0)}) must be between {self.rules.MIN_AR} and {self.rules.MAX_AR}.")
        if not (self.rules.MIN_BOWL <= role_counts.get("BOWL", 0) <= self.rules.MAX_BOWL):
            errors.append(f"Bowlers ({role_counts.get('BOWL', 0)}) must be between {self.rules.MIN_BOWL} and {self.rules.MAX_BOWL}.")

        # 5. Team distribution limits
        for team, count in team_counts.items():
            if count > self.rules.MAX_PLAYERS_PER_TEAM:
                errors.append(f"Team {team} has {count} players; maximum allowed is {self.rules.MAX_PLAYERS_PER_TEAM}.")
            if count < self.rules.MIN_PLAYERS_PER_TEAM:
                errors.append(f"Team {team} must have at least {self.rules.MIN_PLAYERS_PER_TEAM} player.")

        # 6. Captain & Vice Captain
        if not captain_id or captain_id not in player_ids:
            errors.append(f"Captain '{captain_id}' is not in the selected 11.")
        if not vice_captain_id or vice_captain_id not in player_ids:
            errors.append(f"Vice-Captain '{vice_captain_id}' is not in the selected 11.")
        if captain_id == vice_captain_id:
            errors.append("Captain and Vice-Captain cannot be the same player.")

        return ValidationResult(
            is_valid=(len(errors) == 0),
            errors=errors,
            warnings=warnings,
            credits_used=round(total_credits, 1),
            role_counts=role_counts,
            team_counts=team_counts
        )

    def calculate_lineup_fantasy_score(
        self,
        players: List[Dict[str, Any]],
        captain_id: str,
        vice_captain_id: str,
        points_key: str = "projected_points"
    ) -> float:
        """Calculates total fantasy points for a lineup with 2x Captain and 1.5x Vice-Captain."""
        total = 0.0
        for p in players:
            pid = p.get("id") or p.get("name")
            base = float(p.get(points_key, 0.0))
            if pid == captain_id:
                total += base * self.rules.CAPTAIN_MULTIPLIER
            elif pid == vice_captain_id:
                total += base * self.rules.VICE_CAPTAIN_MULTIPLIER
            else:
                total += base
        return round(total, 1)

    def compute_portfolio_overlap(self, lineups: List[Dict[str, Any]]) -> pd.DataFrame:
        """Calculates pairwise player overlap between all generated lineups."""
        n = len(lineups)
        overlap_matrix = [[0] * n for _ in range(n)]

        for i in range(n):
            set_i = set(p.get("id") or p.get("name") for p in lineups[i]["players"])
            for j in range(n):
                set_j = set(p.get("id") or p.get("name") for p in lineups[j]["players"])
                overlap_matrix[i][j] = len(set_i.intersection(set_j))

        team_names = [(l.get("team_name") if isinstance(l, dict) else l.team_name) for l in lineups]
        return pd.DataFrame(overlap_matrix, index=team_names, columns=team_names)

    def export_lineups_to_csv(self, lineups: List[Any], output_path: str) -> str:
        """Exports multiple lineups to standard CSV format suitable for Dream11 upload."""
        rows = []
        for idx, item in enumerate(lineups):
            lineup = item.model_dump() if hasattr(item, "model_dump") else item
            team_num = idx + 1
            cap = lineup.get("captain", {}).get("name", "Unknown")
            vc = lineup.get("vice_captain", {}).get("name", "Unknown")
            player_names = [p.get("name", "") for p in lineup.get("players", [])]

            rows.append({
                "Team": f"T{team_num}",
                "Captain": cap,
                "Vice_Captain": vc,
                "Total_Credits": lineup.get("total_credits", 0.0),
                "Projected_Points": lineup.get("projected_points", 0.0),
                "Ceiling": lineup.get("simulated_ceiling", 0.0),
                "Players": ", ".join(player_names)
            })

        df = pd.DataFrame(rows)
        df.to_csv(output_path, index=False)
        return output_path

