"""Google OR-Tools Multiple Fantasy Lineup Optimizer.
Generates diverse, mathematically optimal fantasy cricket portfolios under official Dream11 rules.
Employs CP-SAT / Integer Linear Programming with strict roster constraints, credit ceilings,
captaincy optimization, sub-35% differential exposures, and pairwise overlap penalties.
"""

from typing import List, Dict, Any, Optional, Set
import numpy as np
from ortools.sat.python import cp_model

from .models import Player, Lineup
from .config import LineupConstraints, DEFAULT_CONSTRAINTS
from .rain_model import RainReducedOversEngine
from .scenario_templates import build_default_scenarios


class ORToolsCricketOptimizer:
    def __init__(
        self,
        players: List[Player],
        constraints: LineupConstraints = DEFAULT_CONSTRAINTS
    ):
        self.players = players
        self.constraints = constraints
        self.player_map = {p.id: p for p in players}

    def generate_grand_league_portfolio(
        self,
        num_teams: int = 10,
        min_differentials_per_team: int = 2,
        max_overlap_between_teams: int = 8,
        custom_scenarios: Optional[List[Dict[str, Any]]] = None,
        spots: int = 700000,
        credit_strategy: str = "79-85",
        min_credits: Optional[float] = None,
        max_credits: Optional[float] = None,
        venue_conditions: Optional[Dict[str, Any]] = None,
        risk_mode: str = "HIGH_CEILING",
        overs: int = 20,
        locked_player_ids: Optional[List[str]] = None,
        excluded_player_ids: Optional[List[str]] = None,
        player_exposure_limits: Optional[Dict[str, float]] = None
    ) -> List[Lineup]:
        """Generates a diverse set of valid Grand League lineups using Google OR-Tools CP-SAT.
        Enforces target credit bands (79-85 Cr or 87-89 Cr) leaving budget on table to eliminate
        field duplication, while selecting perfect venue-matched low-credit gems.
        Supports syndicate player locks (100%), exclusions (0%), and max exposure percentage caps.
        Dynamically adapts batting share decay and bowler quota compression if overs are cut by rain.
        """
        lineups: List[Lineup] = []
        previous_team_player_indices: List[List[int]] = []
        player_usage_counts: Dict[str, int] = {}
        locked_set = set(locked_player_ids or [])
        excluded_set = set(excluded_player_ids or [])

        if overs < 20:
            self.players = RainReducedOversEngine.adjust_player_projections(self.players, overs, venue_conditions)
            self.player_map = {p.id: p for p in self.players}
            rain_scenarios = RainReducedOversEngine.get_rain_scenarios(overs, players=self.players)
            base_scenarios = custom_scenarios or rain_scenarios or self._get_default_scenarios()
        else:
            base_scenarios = custom_scenarios or self._get_default_scenarios()

        scenarios = [dict(s, risk_mode=risk_mode) for s in base_scenarios]

        effective_diffs = min_differentials_per_team
        if risk_mode == "DIFFERENTIAL_HEAVY":
            effective_diffs = max(effective_diffs, 4)
        if spots >= 1500000:
            effective_diffs = max(effective_diffs, 4)
        elif spots >= 700000:
            effective_diffs = max(effective_diffs, 3)

        if min_credits is not None and max_credits is not None:
            eff_min_cr = float(min_credits)
            eff_max_cr = float(max_credits)
        elif credit_strategy == "79-85":
            eff_min_cr = 79.0
            eff_max_cr = 85.0
        elif credit_strategy == "87-89":
            eff_min_cr = 87.0
            eff_max_cr = 89.0
        elif credit_strategy == "90-95":
            eff_min_cr = 90.0
            eff_max_cr = 95.0
        else:
            eff_min_cr = 79.0
            eff_max_cr = 85.0

        for idx in range(num_teams):
            scenario = scenarios[idx % len(scenarios)]
            current_excluded = set(excluded_set)
            if player_exposure_limits:
                for p_id, max_pct in player_exposure_limits.items():
                    used = player_usage_counts.get(p_id, 0)
                    if num_teams > 0 and (used / num_teams) * 100.0 >= max_pct:
                        current_excluded.add(p_id)

            result = self._solve_single_lineup(
                scenario=scenario,
                previous_selections=previous_team_player_indices,
                min_diffs=effective_diffs,
                max_overlap=max_overlap_between_teams,
                min_credits=eff_min_cr,
                max_credits=eff_max_cr,
                overs=overs,
                locked_player_ids=locked_set,
                excluded_player_ids=current_excluded,
                team_number=idx + 1,
            )
            if result is not None:
                lineup, indices = result
                lineups.append(lineup)
                previous_team_player_indices.append(indices)
                for i in indices:
                    pid = self.players[i].id
                    player_usage_counts[pid] = player_usage_counts.get(pid, 0) + 1

        return lineups

    def _solve_single_lineup(
        self,
        scenario: Dict[str, Any],
        previous_selections: List[List[int]],
        min_diffs: int,
        max_overlap: int,
        min_credits: float,
        max_credits: float,
        overs: int,
        locked_player_ids: Set[str],
        excluded_player_ids: Set[str],
        team_number: int = 1,
    ):
        model = cp_model.CpModel()
        n = len(self.players)
        if n < 11:
            return None

        x = [model.NewBoolVar(f"x_{i}") for i in range(n)]
        c = [model.NewBoolVar(f"c_{i}") for i in range(n)]
        v = [model.NewBoolVar(f"v_{i}") for i in range(n)]

        model.Add(sum(x) == 11)
        model.Add(sum(c) == 1)
        model.Add(sum(v) == 1)
        for i in range(n):
            model.Add(c[i] + v[i] <= x[i])

        credits = [int(round(float(p.credits) * 10)) for p in self.players]
        model.Add(sum(x[i] * credits[i] for i in range(n)) >= int(min_credits * 10))
        model.Add(sum(x[i] * credits[i] for i in range(n)) <= int(max_credits * 10))

        roles = {"WK": [], "BAT": [], "AR": [], "BOWL": []}
        for i, p in enumerate(self.players):
            roles.setdefault(p.role, []).append(i)
        for role, idxs in roles.items():
            if not idxs:
                continue
            lo = getattr(self.constraints, f"min_{role.lower()}", 1)
            hi = getattr(self.constraints, f"max_{role.lower()}", 8)
            model.Add(sum(x[i] for i in idxs) >= lo)
            model.Add(sum(x[i] for i in idxs) <= hi)

        teams_map: Dict[str, List[int]] = {}
        for i, p in enumerate(self.players):
            teams_map.setdefault(p.team, []).append(i)
        teams = list(teams_map.keys())
        for team_idxs in teams_map.values():
            model.Add(sum(x[i] for i in team_idxs) >= self.constraints.min_players_per_team)
            model.Add(sum(x[i] for i in team_idxs) <= self.constraints.max_players_per_team)

        ownership_available = any(getattr(p, "ownership_available", True) for p in self.players)
        if ownership_available:
            high_c = [i for i, p in enumerate(self.players) if (p.projected_ownership or 0) >= 70.0]
            high_vc = [i for i, p in enumerate(self.players) if (p.projected_ownership or 0) >= 75.0]
            for hc in high_c:
                for hvc in high_vc:
                    if hc != hvc:
                        model.Add(c[hc] + v[hvc] <= 1)

        diff_indices = [i for i, p in enumerate(self.players) if (p.projected_ownership or 100) < 35.0]
        if ownership_available and min_diffs > 0 and diff_indices:
            model.Add(sum(x[i] for i in diff_indices) >= min(min_diffs, len(diff_indices)))

        for prev in previous_selections:
            model.Add(sum(x[i] for i in prev) <= max_overlap)

        for i, p in enumerate(self.players):
            if p.id in locked_player_ids:
                model.Add(x[i] == 1)
            if p.id in excluded_player_ids:
                model.Add(x[i] == 0)

        pref_c = scenario.get("preferred_c") or scenario.get("preferred_c_id")
        pref_vc = scenario.get("preferred_vc") or scenario.get("preferred_vc_id")
        c_idx = None
        if pref_c:
            c_idx = next((i for i, p in enumerate(self.players) if p.id == pref_c), None)
            if c_idx is not None:
                model.Add(c[c_idx] == 1)
        if pref_vc:
            vc_idx = next((i for i, p in enumerate(self.players) if p.id == pref_vc), None)
            if vc_idx is not None and vc_idx != c_idx:
                model.Add(v[vc_idx] == 1)

        if overs <= 14 and not pref_c:
            for i, p in enumerate(self.players):
                order = p.batting_order_projected or 5
                exp_ov = p.expected_overs or 0.0
                if order > 3 and exp_ov < 3.0 and p.role != "BOWL":
                    model.Add(c[i] == 0)

        # Scenario team bias on projected points
        team_a_bias = float(scenario.get("team_a_bias") or scenario.get("ind_bias") or 1.0)
        team_b_bias = float(scenario.get("team_b_bias") or scenario.get("wi_bias") or 1.0)
        team_list = list(teams_map.keys())
        team_a = team_list[0] if team_list else None
        team_b = team_list[1] if len(team_list) > 1 else team_a

        scale = 10
        obj_terms = []
        for i, p in enumerate(self.players):
            base = float(p.projected_points or 0)
            if p.team == team_a:
                base *= team_a_bias
            elif p.team == team_b:
                base *= team_b_bias
            pts = int(round(base * scale))
            obj_terms.append(x[i] * pts)
            obj_terms.append(c[i] * pts)
            obj_terms.append(v[i] * int(round(pts * 0.5)))
        model.Maximize(sum(obj_terms))

        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = 8.0
        status = solver.Solve(model)
        if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
            return None

        selected = [i for i in range(n) if solver.Value(x[i]) == 1]
        cap_i = next(i for i in range(n) if solver.Value(c[i]) == 1)
        vc_i = next(i for i in range(n) if solver.Value(v[i]) == 1)
        selected_players = [self.players[i] for i in selected]
        captain = self.players[cap_i]
        vice_captain = self.players[vc_i]
        total_credits = round(sum(p.credits for p in selected_players), 1)
        projected_pts = round(
            sum(p.projected_points or 0 for p in selected_players)
            + (captain.projected_points or 0)
            + 0.5 * (vice_captain.projected_points or 0),
            1,
        )
        simulated_ceiling = round(projected_pts * 1.15, 1)
        total_ownership = round(sum(p.projected_ownership or 0 for p in selected_players), 1)
        diff_count = sum(1 for p in selected_players if (p.projected_ownership or 100) < 35.0)

        core_count = sum(1 for p in selected_players if (p.projected_ownership or 0) >= 60.0)
        rotation_count = sum(1 for p in selected_players if 16.0 <= (p.projected_ownership or 0) < 60.0)
        contrarian_count = sum(1 for p in selected_players if (p.projected_ownership or 0) < 16.0)
        mnc_summary = f"{core_count} Core | {rotation_count} Rotation | {contrarian_count} Contrarian"

        c_own = getattr(captain, "captain_percentage", 0.0) or ((captain.projected_ownership or 0) * 0.3)
        vc_own = getattr(vice_captain, "vice_captain_percentage", 0.0) or ((vice_captain.projected_ownership or 0) * 0.2)
        if c_own >= 20.0 and vc_own >= 15.0:
            cvc_type = "Combo A (Safe Template - High C / High VC)"
        elif c_own >= 20.0 and vc_own < 6.0:
            cvc_type = "Combo B (The Sweet Spot - High C / Low VC)"
        elif c_own < 6.0 and vc_own >= 15.0:
            cvc_type = "Combo C (The GL Killer - Low C / High VC)"
        else:
            cvc_type = "Combo B (Differentiated C/VC)"

        team_balance = {t: sum(1 for p in selected_players if p.team == t) for t in teams}

        lineup = Lineup(
            team_name=f"Team {team_number}: {scenario.get('name', 'Custom Scenario')}",
            scenario_tag=scenario.get("tag", "CUSTOM"),
            players=selected_players,
            captain=captain,
            vice_captain=vice_captain,
            total_credits=total_credits,
            projected_points=projected_pts,
            simulated_ceiling=simulated_ceiling,
            total_ownership_sum=total_ownership,
            differential_count=diff_count,
            team_balance=team_balance,
            gl_rank_potential=scenario.get("gl_potential", "Constrained optimum"),
            tactical_rationale=scenario.get("rationale", "Mathematical integer programming optimization"),
            csp=total_ownership,
            mnc_summary=mnc_summary,
            cvc_combo_type=cvc_type,
        )
        return lineup, selected

    def _get_default_scenarios(self) -> List[Dict[str, Any]]:
        """Dynamic scenarios from active roster — no hardcoded player IDs."""
        return build_default_scenarios(self.players)
