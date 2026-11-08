"""
Grand League optimizer using Google OR-Tools CP-SAT.
Incorporates explicit correlation constraints:
  - Negative correlation (Block): bowler-batter rivalries prevent
    mutually-exclusive C/VC pairings.
  - Positive correlation (Stack): objective bonuses for batting partnerships
    and all-rounder self-correlation.
All CP-SAT constraints use valid boolean reification (no OnlyEnforceIf on
linear expressions), so the model stays feasible.
"""
import logging
from typing import Dict, List

import pandas as pd
from ortools.sat.python import cp_model

from config import FEATURE_COLS, MAX_TEAM_PLAYERS, MIN_DIFFERENTIALS, ROLE_BOUNDS, TOTAL_CREDITS
from correlation_matrix import CorrelationMatrix

logger = logging.getLogger(__name__)


class GrandLeagueOptimizer:
    def __init__(self, players_df: pd.DataFrame, correlation_matrix: CorrelationMatrix):
        self.players = players_df.to_dict("records")
        self.n = len(self.players)
        self.correlation = correlation_matrix

    def optimize(self, n_teams: int = 20, scenario: str = "balanced") -> List[Dict]:
        teams: List[Dict] = []
        for i in range(n_teams):
            team = self._solve_single_team(scenario=scenario, seed=i)
            if team:
                teams.append(team)
        return teams

    # ------------------------------------------------------------------ #
    # Core solver
    # ------------------------------------------------------------------ #
    def _solve_single_team(self, scenario: str, seed: int) -> Dict:
        model = cp_model.CpModel()
        n = self.n
        p = self.players

        selected = [model.NewBoolVar(f"sel_{i}") for i in range(n)]
        captain = [model.NewBoolVar(f"cap_{i}") for i in range(n)]
        vice_cap = [model.NewBoolVar(f"vc_{i}") for i in range(n)]

        # ---- Hard constraints ----
        model.Add(sum(selected) == 11)
        model.Add(sum(captain) == 1)
        model.Add(sum(vice_cap) == 1)

        for i in range(n):
            model.Add(captain[i] <= selected[i])
            model.Add(vice_cap[i] <= selected[i])
            model.Add(captain[i] + vice_cap[i] <= 1)

        # Credit budget (<= 100)
        model.Add(
            sum(selected[i] * int(p[i].get("credit", 8.0) * 10) for i in range(n))
            <= int(TOTAL_CREDITS * 10)
        )

        # Max players per team
        for team_name in set(x["team"] for x in p):
            idx = [i for i, x in enumerate(p) if x["team"] == team_name]
            model.Add(sum(selected[i] for i in idx) <= MAX_TEAM_PLAYERS)

        # Role bounds
        for role, (lo, hi) in ROLE_BOUNDS.items():
            idx = [i for i, x in enumerate(p) if x["role"] == role]
            model.Add(sum(selected[i] for i in idx) >= lo)
            model.Add(sum(selected[i] for i in idx) <= hi)

        # ---- Correlation locks ----
        self._add_negative_correlation(model, selected, captain, vice_cap, p)
        self._add_scenario_constraints(model, selected, p, scenario)

        # ---- Objective: upside + correlation bonuses ----
        team_top_order: Dict[str, List[int]] = {}
        for i, pi in enumerate(p):
            if pi["role"] == "BAT" and pi.get("credit", 8.0) >= 9.0:
                team_top_order.setdefault(pi["team"], []).append(i)

        objective_terms = []
        for i in range(n):
            base_score = int(p[i].get("expected_points", 30.0) * 100)
            ownership_penalty = (100 - p[i].get("projected_sel_pct", 50.0)) / 100.0
            variance_bonus = int(p[i].get("variance_score", 0.0) * 5000 * ownership_penalty)
            total_score = base_score + variance_bonus

            # Positive correlation bonuses (constants added to objective)
            correlation_bonus = 0
            if p[i]["role"] == "AR":
                correlation_bonus += 1000  # all-rounder self-correlation
            if (
                p[i]["role"] in ("BAT", "AR")
                and p[i].get("credit", 8.0) < 9.0
                and len(team_top_order.get(p[i]["team"], [])) >= 2
            ):
                correlation_bonus += 800  # middle-order stack hint

            final_score = total_score + correlation_bonus

            objective_terms.append(selected[i] * final_score)
            objective_terms.append(captain[i] * final_score)          # 2x total
            objective_terms.append(vice_cap[i] * int(final_score * 0.5))  # 1.5x total

        model.Maximize(sum(objective_terms))

        # ---- Solve ----
        solver = cp_model.CpSolver()
        solver.parameters.random_seed = seed + 100
        solver.parameters.max_time_in_seconds = 10
        status = solver.Solve(model)

        if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
            logger.warning("Solver returned %s for seed %d scenario %s", status, seed, scenario)
            return None

        # ---- Extract ----
        team_players: List[Dict] = []
        for i in range(n):
            if solver.Value(selected[i]):
                entry = p[i].copy()
                entry["is_captain"] = bool(solver.Value(captain[i]))
                entry["is_vice_captain"] = bool(solver.Value(vice_cap[i]))
                team_players.append(entry)

        total_credits = sum(x.get("credit", 0.0) for x in team_players)
        total_proj_points = sum(
            x.get("expected_points", 0.0)
            * (2.0 if x["is_captain"] else 1.5 if x["is_vice_captain"] else 1.0)
            for x in team_players
        )
        avg_sel = sum(x.get("projected_sel_pct", 0.0) for x in team_players) / len(team_players)

        return {
            "team_id": seed + 1,
            "scenario": scenario,
            "players": team_players,
            "total_credits": round(total_credits, 1),
            "projected_points": round(total_proj_points, 2),
            "avg_selection_pct": round(avg_sel, 2),
            "n_differentials": sum(1 for x in team_players if x.get("projected_sel_pct", 100) < 15),
        }

    # ------------------------------------------------------------------ #
    # Negative correlation: bowler-batter rivalries
    # ------------------------------------------------------------------ #
    def _add_negative_correlation(
        self,
        model: cp_model.CpModel,
        selected: List,
        captain: List,
        vice_cap: List,
        players: List[Dict],
    ) -> None:
        """Block C/VC pairings where bowler dismisses batter (mutually exclusive success)."""
        for i, bowler in enumerate(players):
            if bowler["role"] != "BOWL":
                continue
            bname = bowler.get("name") or bowler.get("player", "")
            dismissed = self.correlation.get_negative_correlations(bname)
            for batter_name in dismissed:
                bat_idx = next(
                    (j for j, pl in enumerate(players)
                     if (pl.get("name") or pl.get("player", "")) == batter_name),
                    None,
                )
                if bat_idx is None or bat_idx == i:
                    continue
                # If bowler is Captain, batter cannot be Vice-Captain
                model.Add(captain[i] + vice_cap[bat_idx] <= 1)
                # If bowler is Vice-Captain, batter cannot be Captain
                model.Add(vice_cap[i] + captain[bat_idx] <= 1)

    # ------------------------------------------------------------------ #
    # Scenario forcing
    # ------------------------------------------------------------------ #
    def _add_scenario_constraints(
        self,
        model: cp_model.CpModel,
        selected: List,
        players: List[Dict],
        scenario: str,
    ) -> None:
        if scenario == "death_bowler_special":
            death_idx = [
                i for i, x in enumerate(players)
                if x.get("role") == "BOWL" or x.get("phase_strike_rate", 130) > 140
            ][:4]
            if len(death_idx) >= 2:
                model.Add(sum(selected[i] for i in death_idx) >= 2)

        elif scenario == "top_collapse":
            bowlers_idx = [i for i, x in enumerate(players) if x["role"] == "BOWL"][:4]
            model.Add(sum(selected[i] for i in bowlers_idx) >= 2)
            # Stack: opposing batters get collapse opportunity
            other_batters = [
                i for i, x in enumerate(players)
                if x["role"] == "BAT" and x["team"] != "Sydney Sixers"
            ]
            if other_batters:
                model.Add(sum(selected[i] for i in other_batters) >= 1)

        elif scenario == "high_scoring_chase":
            batters_idx = [i for i, x in enumerate(players) if x["role"] == "BAT"]
            model.Add(sum(selected[i] for i in batters_idx) >= 4)

        elif scenario == "spin_dominance":
            spinners = [
                i for i, x in enumerate(players)
                if x["role"] == "BOWL" and "spin" in str(x.get("bowling_style", "")).lower()
            ]
            if len(spinners) >= 2:
                model.Add(sum(selected[i] for i in spinners) >= 2)

        elif scenario == "pace_dominance":
            pacers = [
                i for i, x in enumerate(players)
                if x["role"] == "BOWL" and "pace" in str(x.get("bowling_style", "")).lower()
            ]
            if len(pacers) >= 2:
                model.Add(sum(selected[i] for i in pacers) >= 2)

        elif scenario == "balanced":
            # No extra forcing; rely on anti-chalk + objective
            pass
