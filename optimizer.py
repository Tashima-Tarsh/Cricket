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


def build_correlation_constraints(model, selected, captain, vice_cap, players):
    """
    Adds explicit positive and negative correlation constraints to the OR-Tools model.
    Uses clean linear constraints (no invalid OnlyEnforceIf on linear expressions)
    so the model stays feasible and solves reliably.
    """
    n = len(players)

    def get_idx(name):
        return next(
            (i for i, pl in enumerate(players)
             if pl.get("name") == name or pl.get("player") == name),
            None,
        )

    # ---------------------------------------------------------
    # 1. NEGATIVE CORRELATION (The "Cancel-Out" Prevention / "Block")
    # If an opposition bowler is Captain, the opposition's star opener
    # should NOT be Vice-Captain (and vice versa), because their
    # successes mutually exclude each other.
    # ---------------------------------------------------------
    rivalries = [
        ("Jasprit_Bumrah", "Virat_Kohli"),
        ("Rashid_Khan", "Rohit_Sharma"),
        ("Mohammed_Siraj", "Suryakumar_Yadav"),
    ]
    for bowler_name, batter_name in rivalries:
        b_idx = get_idx(bowler_name)
        bat_idx = get_idx(batter_name)
        if b_idx is None or bat_idx is None:
            continue
        # If bowler is Captain, batter cannot be Vice-Captain
        model.Add(captain[b_idx] + vice_cap[bat_idx] <= 1)
        # If bowler is Vice-Captain, batter cannot be Captain
        model.Add(vice_cap[b_idx] + captain[bat_idx] <= 1)

    # ---------------------------------------------------------
    # 2. POSITIVE CORRELATION (The "Stack")
    # Hinted via per-player objective bonuses below (middle-order
    # batters from teams with 2+ top-order batters get a stack hint),
    # plus explicit team-stacking in scenario forcing.
    # ---------------------------------------------------------
    return None


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

        # ---------- CORRELATION LOCKS (Negative + Positive) ----------
        build_correlation_constraints(model, selected, captain, vice_cap, p)

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
            # Positive correlation stack: if Team A's bowlers collapse the innings,
            # at least 1 batter from the opposing team faces the collapse opportunity
            other_team_batters = [i for i, x in enumerate(p)
                                  if x["role"] == "BAT" and x["team"] != "MI"]
            if len(other_team_batters) >= 1:
                model.Add(sum(selected[i] for i in other_team_batters) >= 1)
        elif scenario == "death_bowler_special":
            # Force: pick death-overs specialists (high phase_strike_rate impact)
            death_idx = [i for i, x in enumerate(p) if x["variance_score"] > 0.6]
            if len(death_idx) >= 2:
                model.Add(sum(selected[i] for i in death_idx) >= 2)
        elif scenario == "high_scoring_chase":
            # Force: batting-heavy lineup (team stacking = positive correlation)
            batters_idx = [i for i, x in enumerate(p) if x["role"] == "BAT"]
            model.Add(sum(selected[i] for i in batters_idx) >= 4)

        # ---------- OBJECTIVE: Maximize Upside WITH CORRELATION ----------
        # For Grand League, we reward HIGH CEILING players, not just safe ones.
        # Correlation-aware: negative-correlation pairs are hard-blocked above;
        # positive-correlation stacks are hinted via objective bonuses below.
        # (CP-SAT objective coefficients must be constants, so per-player bonuses
        # are used rather than multiplying two decision variables.)

        # Pre-compute per-team top-order / middle-order for stacking hints
        team_top_order = {}
        for i, pi in enumerate(p):
            if pi["team"] not in team_top_order:
                team_top_order[pi["team"]] = []
            if pi["role"] == "BAT" and pi["credit"] >= 9.0:
                team_top_order[pi["team"]].append(i)

        objective_terms = []
        for i in range(n):
            base_score = int(p[i]["expected_points"] * 100)

            # GL Secret: Exponentially reward high variance AND low ownership
            ownership_penalty = (100 - p[i]["projected_sel_pct"]) / 100.0
            variance_bonus = int(p[i]["variance_score"] * 5000 * ownership_penalty)

            total_score = base_score + variance_bonus

            # --- CORRELATION ADJUSTMENTS ---
            correlation_bonus = 0

            # 1. Positive Correlation: All-rounders are naturally self-correlated
            # (they contribute with both bat and ball), so boost their score.
            if p[i]["role"] == "AR":
                correlation_bonus += 1000

            # 2. Positive Correlation: Middle-order batter from a team with
            # 2+ top-order batters gets a stack hint (top order success = easier
            # runs for middle order; top order collapse = more balls for middle order).
            if (p[i]["role"] in ["BAT", "AR"]
                    and p[i]["credit"] < 9.0
                    and len(team_top_order.get(p[i]["team"], [])) >= 2):
                correlation_bonus += 800

            final_score = total_score + correlation_bonus

            # Captain multiplier: 2x, Vice-Captain: 1.5x
            objective_terms.append(selected[i] * final_score)
            objective_terms.append(captain[i] * final_score)   # extra 1x (total 2x)
            objective_terms.append(vice_cap[i] * int(final_score * 0.5))  # extra 0.5x (total 1.5x)

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
