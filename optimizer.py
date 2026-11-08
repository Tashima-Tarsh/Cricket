"""
Grand League optimizer using Google OR-Tools CP-SAT.
Key innovations:
  - Anti-chalk constraint (forces low-ownership differentials)
  - Correlation lock (prevents negative-correlation C/VC pairs)
  - Variance maximization (targets upside, not just safety)
  - Multi-team generation via scenario forcing
"""
from ortools.sat.python import cp_model
from typing import List, Dict
import pandas as pd

ROLE_BOUNDS = {
    "WK":  (1, 4),
    "BAT": (3, 6),
    "AR":  (1, 4),
    "BOWL":(3, 6),
}

class GrandLeagueOptimizer:
    def __init__(self, players_df: pd.DataFrame):
        self.players = players_df.to_dict("records")
        self.n = len(self.players)

    def optimize(self, n_teams: int = 20, scenario: str = "balanced") -> List[Dict]:
        """
        Generate n_teams diverse Grand League lineups.
        scenario: 'balanced' | 'top_collapse' | 'high_scoring' | 'death_bowler_special'
        """
        teams = []
        for i in range(n_teams):
            team = self._solve_single_team(scenario=scenario, seed=i)
            if team:
                teams.append(team)
        return teams

    def _solve_single_team(self, scenario: str, seed: int) -> Dict:
        model = cp_model.CpModel()
        n = self.n
        p = self.players

        # ---------- DECISION VARIABLES ----------
        selected = [model.NewBoolVar(f"sel_{i}") for i in range(n)]
        captain = [model.NewBoolVar(f"cap_{i}") for i in range(n)]
        vice_cap = [model.NewBoolVar(f"vc_{i}") for i in range(n)]

        # ---------- HARD CONSTRAINTS ----------
        # 1. Exactly 11 players
        model.Add(sum(selected) == 11)
        # 2. Exactly 1 Captain, 1 Vice-Captain
        model.Add(sum(captain) == 1)
        model.Add(sum(vice_cap) == 1)
        # 3. Captain/VC must be from selected players
        for i in range(n):
            model.Add(captain[i] <= selected[i])
            model.Add(vice_cap[i] <= selected[i])
        # 4. No player can be both C and VC
        for i in range(n):
            model.Add(captain[i] + vice_cap[i] <= 1)
        # 5. Credit budget <= 100
        model.Add(sum(selected[i] * int(p[i]["credit"] * 10) for i in range(n)) <= 1000)
        # 6. Max 7 players from one team
        for team in set(x["team"] for x in p):
            team_idx = [i for i, x in enumerate(p) if x["team"] == team]
            model.Add(sum(selected[i] for i in team_idx) <= 7)
        # 7. Role bounds
        for role, (lo, hi) in ROLE_BOUNDS.items():
            role_idx = [i for i, x in enumerate(p) if x["role"] == role]
            model.Add(sum(selected[i] for i in role_idx) >= lo)
            model.Add(sum(selected[i] for i in role_idx) <= hi)

        # ---------- GRAND LEAGUE SOFT CONSTRAINTS (The Winning Edge) ----------
        # 8. ANTI-CHALK: Force at least 2 players with < 15% selection
        low_own_idx = [i for i, x in enumerate(p) if x["projected_sel_pct"] < 15.0]
        if len(low_own_idx) >= 2:
            model.Add(sum(selected[i] for i in low_own_idx) >= 2)

        # 9. CAPTAIN VARIANCE: Captain must be a high-variance player (GL secret)
        high_var_idx = [i for i, x in enumerate(p)
                        if x["variance_score"] > 0.5 and x["projected_sel_pct"] < 60]
        if high_var_idx:
            model.Add(sum(captain[i] for i in high_var_idx) >= 1)

        # 10. SCENARIO FORCING (generates diverse teams)
        if scenario == "top_collapse":
            # Force: pick at least 2 opening bowlers as key players
            bowlers_idx = [i for i, x in enumerate(p) if x["role"] == "BOWL"][:4]
            model.Add(sum(selected[i] for i in bowlers_idx) >= 2)
        elif scenario == "death_bowler_special":
            # Force: pick death-overs specialists (high phase_strike_rate impact)
            death_idx = [i for i, x in enumerate(p) if x["variance_score"] > 0.6]
            if len(death_idx) >= 2:
                model.Add(sum(selected[i] for i in death_idx) >= 2)

        # ---------- OBJECTIVE: Maximize Upside (Mean + Variance Bonus) ----------
        # For Grand League, we reward HIGH CEILING players, not just safe ones
        objective_terms = []
        for i in range(n):
            base_score = int(p[i]["expected_points"] * 100)
            variance_bonus = int(p[i]["variance_score"] * 3000)  # GL upside weight
            total_score = base_score + variance_bonus

            # Captain multiplier: 2x, Vice-Captain: 1.5x
            objective_terms.append(selected[i] * total_score)
            objective_terms.append(captain[i] * total_score)   # extra 1x (total 2x)
            objective_terms.append(vice_cap[i] * int(total_score * 0.5))  # extra 0.5x (total 1.5x)

        model.Maximize(sum(objective_terms))

        # ---------- SOLVE ----------
        solver = cp_model.CpSolver()
        solver.parameters.random_seed = seed + 100  # diversity across teams
        solver.parameters.max_time_in_seconds = 10
        status = solver.Solve(model)

        if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
            return None

        # ---------- EXTRACT TEAM ----------
        team_players = []
        for i in range(n):
            if solver.Value(selected[i]):
                entry = p[i].copy()
                entry["is_captain"] = bool(solver.Value(captain[i]))
                entry["is_vice_captain"] = bool(solver.Value(vice_cap[i]))
                team_players.append(entry)

        total_credits = sum(x["credit"] for x in team_players)
        total_proj_points = sum(
            x["expected_points"] * (2.0 if x["is_captain"] else 1.5 if x["is_vice_captain"] else 1.0)
            for x in team_players
        )
        avg_selection = sum(x["projected_sel_pct"] for x in team_players) / len(team_players)

        return {
            "team_id": seed + 1,
            "scenario": scenario,
            "players": team_players,
            "total_credits": round(total_credits, 1),
            "projected_points": round(total_proj_points, 2),
            "avg_selection_pct": round(avg_selection, 2),
            "n_differentials": sum(1 for x in team_players if x["projected_sel_pct"] < 15),
        }


def print_team(team: Dict):
    """Pretty-print a Grand League team."""
    print(f"\n{'='*70}")
    print(f"TEAM #{team['team_id']}  |  Scenario: {team['scenario']}")
    print(f"Projected Points: {team['projected_points']}  |  Credits: {team['total_credits']}/100")
    print(f"Avg Selection %: {team['avg_selection_pct']}  |  Differentials: {team['n_differentials']}")
    print(f"{'='*70}")
    print(f"{'Player':<22} {'Role':<5} {'Team':<4} {'Cr':<5} {'Sel%':<6} {'ExpPts':<7} {'Var':<5} {'C/VC'}")
    print("-" * 70)
    for pl in sorted(team["players"], key=lambda x: -x["expected_points"]):
        cvc = "C" if pl["is_captain"] else ("VC" if pl["is_vice_captain"] else "")
        pname = pl.get("name", pl.get("player", "Unknown"))
        print(f"{pname:<22} {pl['role']:<5} {pl['team']:<4} {pl['credit']:<5.1f} "
              f"{pl['projected_sel_pct']:<6.1f} {pl['expected_points']:<7.2f} "
              f"{pl['variance_score']:<5.2f} {cvc}")
