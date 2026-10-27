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
        lineups: List[Lineup] = []
        previous_team_player_indices: List[List[int]] = []
        player_usage_counts: Dict[str, int] = {}
        locked_set = set(locked_player_ids or [])
        excluded_set = set(excluded_player_ids or [])

        if overs < 20:
            self.players = RainReducedOversEngine.adjust_player_projections(self.players, overs, venue_conditions)
            self.player_map = {p.id: p for p in self.players}
            rain_scenarios = RainReducedOversEngine.get_rain_scenarios(overs)
            base_scenarios = custom_scenarios or rain_scenarios or self._get_default_scenarios()
        else:
            base_scenarios = custom_scenarios or self._get_default_scenarios()

        scenarios = [dict(s, risk_mode=risk_mode) for s in base_scenarios]

        effective_diffs = min_differentials_per_team
        if risk_mode == "DIFFERENTIAL_HEAVY":
            effective_diffs = max(effective_diffs, 4)
        if spots >= 1500000:
            effective_diffs = max(effective_diffs, 3)
        elif spots >= 700000:
            effective_diffs = max(effective_diffs, 3)

        if min_credits is not None and max_credits is not None:
            eff_min_cr = float(min_credits)
            eff_max_cr = float(max_credits)
        elif credit_strategy == "79-85":
            eff_min_cr, eff_max_cr = 79.0, 85.0
        elif credit_strategy == "87-89":
            eff_min_cr, eff_max_cr = 87.0, 89.0
        elif credit_strategy == "90-95":
            eff_min_cr, eff_max_cr = 90.0, 95.0
        else:
            eff_min_cr, eff_max_cr = 79.0, 85.0

        # Permanent zero-exposure exclusions
        if player_exposure_limits:
            for p_id, max_pct in player_exposure_limits.items():
                if max_pct is not None and max_pct <= 0:
                    excluded_set.add(p_id)

        for idx in range(num_teams):
            scenario = scenarios[idx % len(scenarios)]
            current_excluded = set(excluded_set)
            if player_exposure_limits:
                for p_id, max_pct in player_exposure_limits.items():
                    if max_pct is None or max_pct <= 0:
                        continue
                    used = player_usage_counts.get(p_id, 0)
                    if num_teams > 0 and (used / float(num_teams)) * 100.0 >= max_pct:
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
        """Full CP-SAT solve adapted from verified e07a baseline."""
        model = cp_model.CpModel()
        n = len(self.players)
        if n < 11:
            return None

        x = [model.NewBoolVar(f"x_{i}") for i in range(n)]
        c = [model.NewBoolVar(f"c_{i}") for i in range(n)]
        v = [model.NewBoolVar(f"v_{i}") for i in range(n)]

        model.Add(sum(x[i] for i in range(n)) == 11)
        model.Add(sum(c[i] for i in range(n)) == 1)
        model.Add(sum(v[i] for i in range(n)) == 1)
        for i in range(n):
            model.Add(c[i] + v[i] <= x[i])

        credit_scaled = [int(round(float(p.credits) * 10)) for p in self.players]
        model.Add(sum(x[i] * credit_scaled[i] for i in range(n)) >= int(round(min_credits * 10)))
        model.Add(sum(x[i] * credit_scaled[i] for i in range(n)) <= int(round(max_credits * 10)))

        role_indices = {"WK": [], "BAT": [], "AR": [], "BOWL": []}
        for i, p in enumerate(self.players):
            role_indices.setdefault(p.role, []).append(i)
        for role, idxs in role_indices.items():
            # An unavailable mandatory role is infeasible, not optional.
            lo = getattr(self.constraints, f"min_{role.lower()}", 1)
            hi = getattr(self.constraints, f"max_{role.lower()}", 8)
            model.Add(sum(x[i] for i in idxs) >= lo)
            model.Add(sum(x[i] for i in idxs) <= hi)

        team_indices: Dict[str, List[int]] = {}
        for i, p in enumerate(self.players):
            team_indices.setdefault(p.team, []).append(i)
        teams = list(team_indices.keys())
        for idxs in team_indices.values():
            model.Add(sum(x[i] for i in idxs) >= self.constraints.min_players_per_team)
            model.Add(sum(x[i] for i in idxs) <= self.constraints.max_players_per_team)

        ownership_available = all(getattr(p, "ownership_available", True) for p in self.players)
        if ownership_available and min_diffs > 0:
            diff_idx = [i for i, p in enumerate(self.players) if (p.projected_ownership or 100.0) < 35.0]
            model.Add(sum(x[i] for i in diff_idx) >= min_diffs)

        for prev in previous_selections:
            model.Add(sum(x[i] for i in prev) <= max_overlap)

        for i, p in enumerate(self.players):
            if p.id in locked_player_ids:
                model.Add(x[i] == 1)
            if p.id in excluded_player_ids:
                model.Add(x[i] == 0)

        pref_c = scenario.get("preferred_c") or scenario.get("preferred_c_id")
        pref_vc = scenario.get("preferred_vc") or scenario.get("preferred_vc_id")
        if pref_c:
            ci = next((i for i, p in enumerate(self.players) if p.id == pref_c), None)
            if ci is not None:
                model.Add(c[ci] == 1)
        if pref_vc:
            vi = next((i for i, p in enumerate(self.players) if p.id == pref_vc), None)
            if vi is not None:
                model.Add(v[vi] == 1)

        if overs <= 14 and not pref_c:
            for i, p in enumerate(self.players):
                order = p.batting_order_projected or 5
                exp_ov = p.expected_overs or 0.0
                if order > 3 and exp_ov < 3.0 and p.role != "BOWL":
                    model.Add(c[i] == 0)

        team_a_bias = float(scenario.get("team_a_bias") or scenario.get("ind_bias") or 1.0)
        team_b_bias = float(scenario.get("team_b_bias") or scenario.get("wi_bias") or 1.0)
        team_a = teams[0] if teams else None
        team_b = teams[1] if len(teams) > 1 else team_a

        scale = 10
        terms = []
        for i, p in enumerate(self.players):
            base = float(p.projected_points or 0.0)
            if p.team == team_a:
                base *= team_a_bias
            elif p.team == team_b:
                base *= team_b_bias
            pts = int(round(base * scale))
            terms.append(x[i] * pts)
            terms.append(c[i] * pts)
            terms.append(v[i] * int(round(pts * 0.5)))
        model.Maximize(sum(terms))

        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = 12.0
        status = solver.Solve(model)
        if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
            return None

        selected = [i for i in range(n) if solver.Value(x[i]) == 1]
        cap_i = next(i for i in range(n) if solver.Value(c[i]) == 1)
        vc_i = next(i for i in range(n) if solver.Value(v[i]) == 1)
        selected_players = [self.players[i] for i in selected]
        # Defense in depth: check solver outputs against the active contract.
        if len(selected) != 11 or len({p.id for p in selected_players}) != 11:
            return None
        if any(p.id in excluded_player_ids for p in selected_players):
            return None
        if not locked_player_ids.issubset({p.id for p in selected_players}):
            return None
        if any(not (getattr(self.constraints, f"min_{role.lower()}") <=
                    sum(p.role == role for p in selected_players) <=
                    getattr(self.constraints, f"max_{role.lower()}"))
               for role in ("WK", "BAT", "AR", "BOWL")):
            return None
        if any(not (self.constraints.min_players_per_team <=
                    sum(p.team == team for p in selected_players) <=
                    self.constraints.max_players_per_team)
               for team in team_indices):
            return None
        if not (min_credits <= sum(p.credits for p in selected_players) <= max_credits):
            return None
        if cap_i == vc_i or cap_i not in selected or vc_i not in selected:
            return None
        captain = self.players[cap_i]
        vice_captain = self.players[vc_i]
        total_credits = round(sum(p.credits for p in selected_players), 1)
        projected_pts = round(
            sum((p.projected_points or 0) for p in selected_players)
            + (captain.projected_points or 0)
            + 0.5 * (vice_captain.projected_points or 0),
            1,
        )
        simulated_ceiling = round(projected_pts * 1.15, 1)
        total_ownership = round(sum((p.projected_ownership or 0) for p in selected_players), 1)
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
        """Player-agnostic templates; preferred_c/vc are None (resolved dynamically if needed)."""
        return [
            {"tag": "EXPRESS_PACE_CARNAGE", "name": "Express Pace & Seam Emphasis", "ind_bias": 1.05, "wi_bias": 1.05,
             "preferred_c": None, "preferred_vc": None, "gl_potential": "High-Ceiling Leverage",
             "rationale": "Damp or overcast conditions amplify early seam. Prioritise frontline pace and top-order anchors."},
            {"tag": "TEAM_B_COUNTER", "name": "Underdog Counter-Punch", "ind_bias": 0.85, "wi_bias": 1.30,
             "preferred_c": None, "preferred_vc": None, "gl_potential": "High Volatility",
             "rationale": "Leverage underdog volume via top-order batters and two-way all-rounders."},
            {"tag": "MIDDLE_ORDER_REBUILD", "name": "Middle-Overs Recovery", "ind_bias": 1.15, "wi_bias": 0.95,
             "preferred_c": None, "preferred_vc": None, "gl_potential": "Elite Floor + Ceiling",
             "rationale": "Early wickets favour middle-order anchors and bowling all-rounders."},
            {"tag": "DEATH_OVERS_BLITZ", "name": "Death Overs Boundary Emphasis", "ind_bias": 0.95, "wi_bias": 1.20,
             "preferred_c": None, "preferred_vc": None, "gl_potential": "Contrarian Multiplier",
             "rationale": "Finishers and death bowlers drive ceiling in slog-phase scripts."},
            {"tag": "TOP_ORDER_STACK", "name": "Top-Order Concentration", "ind_bias": 1.10, "wi_bias": 1.10,
             "preferred_c": None, "preferred_vc": None, "gl_potential": "High Aggregate Ceiling",
             "rationale": "Concentrate volume on top-3 batters who face the majority of deliveries."},
            {"tag": "SPIN_CHOKE", "name": "Spin / Grip Surface", "ind_bias": 1.05, "wi_bias": 1.05,
             "preferred_c": None, "preferred_vc": None, "gl_potential": "Dot-Ball Accumulator",
             "rationale": "Gripping surfaces elevate spinner and cutter value."},
            {"tag": "PACE_STRANGLE", "name": "Dual Pace Strangle", "ind_bias": 1.08, "wi_bias": 1.08,
             "preferred_c": None, "preferred_vc": None, "gl_potential": "Wicket Multiplier",
             "rationale": "Two frontline pacers who keep full quotas remove top orders early."},
            {"tag": "ANTI_CHALK_LEVERAGE", "name": "Anti-Chalk Leverage Portfolio", "ind_bias": 1.00, "wi_bias": 1.10,
             "preferred_c": None, "preferred_vc": None, "gl_potential": "Low-Duplication Portfolio",
             "rationale": "Prefer lower-ownership ceiling plays; leave credits unspent for uniqueness. Not a Rank guarantee."},
        ]
