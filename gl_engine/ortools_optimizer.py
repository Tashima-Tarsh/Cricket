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

        # In shortened matches, apply mathematical volume transformations and specialized rain scripts
        if overs < 20:
            self.players = RainReducedOversEngine.adjust_player_projections(self.players, overs, venue_conditions)
            self.player_map = {p.id: p for p in self.players}
            rain_scenarios = RainReducedOversEngine.get_rain_scenarios(overs)
            base_scenarios = custom_scenarios or rain_scenarios or self._get_default_scenarios()
        else:
            base_scenarios = custom_scenarios or self._get_default_scenarios()

        scenarios = [dict(s, risk_mode=risk_mode) for s in base_scenarios]

        # Enforce mega contest rule: >= 7 Lakhs spots requires 3+ differentials for collision avoidance
        effective_diffs = min_differentials_per_team
        if risk_mode == "DIFFERENTIAL_HEAVY":
            effective_diffs = max(effective_diffs, 4)
        if spots >= 1500000:
            effective_diffs = max(effective_diffs, 4)
        elif spots >= 700000:
            effective_diffs = max(effective_diffs, 3)

        # Resolve credit budget band
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
            
            # Compute dynamic exclusions based on exposure limits
            current_excluded = set(excluded_set)
            if player_exposure_limits:
                for p_id, max_pct in player_exposure_limits.items():
                    # API exposure values are percentages, including 0 and 1.
                    max_allowed_teams = int(np.floor(max_pct / 100.0 * num_teams))
                    if player_usage_counts.get(p_id, 0) >= max_allowed_teams:
                        current_excluded.add(p_id)

            lineup = self._solve_single_lineup(
                scenario=scenario,
                min_diffs=effective_diffs,
                max_overlap=max_overlap_between_teams,
                previous_selections=previous_team_player_indices,
                team_number=idx + 1,
                spots=spots,
                min_credits=eff_min_cr,
                max_credits=eff_max_cr,
                venue_conditions=venue_conditions,
                overs=overs,
                locked_player_ids=locked_set,
                excluded_player_ids=current_excluded
            )
            if lineup:
                lineups.append(lineup)
                selected_indices = [
                    i for i, p in enumerate(self.players)
                    if any(lp.id == p.id for lp in lineup.players)
                ]
                previous_team_player_indices.append(selected_indices)
                for lp in lineup.players:
                    player_usage_counts[lp.id] = player_usage_counts.get(lp.id, 0) + 1

        # A partial portfolio must not inflate exposure percentages beyond the cap.
        if player_exposure_limits and len(lineups) != num_teams:
            return []
        return lineups

    def _solve_single_lineup(
        self,
        scenario: Dict[str, Any],
        min_diffs: int,
        max_overlap: int,
        previous_selections: List[List[int]],
        team_number: int,
        spots: int = 700000,
        min_credits: float = 79.0,
        max_credits: float = 85.0,
        venue_conditions: Optional[Dict[str, Any]] = None,
        risk_mode: str = "HIGH_CEILING",
        overs: int = 20,
        locked_player_ids: Optional[Set[str]] = None,
        excluded_player_ids: Optional[Set[str]] = None
    ) -> Optional[Lineup]:
        """Solves a single optimal lineup using Google OR-Tools CP-SAT solver."""
        model = cp_model.CpModel()
        n = len(self.players)

        # Decision Variables:
        x = [model.NewBoolVar(f"x_{i}") for i in range(n)]
        c = [model.NewBoolVar(f"c_{i}") for i in range(n)]
        v = [model.NewBoolVar(f"v_{i}") for i in range(n)]

        # 1. Total players == 11
        model.Add(sum(x) == self.constraints.total_players)

        # 2. Strict Credit Budget Band (e.g. 79.0 to 85.0 or 87.0 to 89.0 credits)
        # Scale by 10 for exact integer precision
        credit_ints = [int(round(p.credits * 10)) for p in self.players]
        model.Add(sum(credit_ints[i] * x[i] for i in range(n)) <= int(round(max_credits * 10)))
        model.Add(sum(credit_ints[i] * x[i] for i in range(n)) >= int(round(min_credits * 10)))

        # 3. Role Constraints (Adapted dynamically for shortened sprint matches)
        wk_indices = [i for i, p in enumerate(self.players) if p.role == "WK"]
        bat_indices = [i for i, p in enumerate(self.players) if p.role == "BAT"]
        ar_indices = [i for i, p in enumerate(self.players) if p.role == "AR"]
        bowl_indices = [i for i, p in enumerate(self.players) if p.role == "BOWL"]

        if overs <= 12:
            # Shortened sprint matches (5-12 overs):
            # Max 2 WKs (Sanju Samson, Shai Hope) - never 3 or 4 keepers!
            # Frontline bowlers bowl 2 overs each; batsmen must hit boundaries immediately.
            min_wk_val = max(1, self.constraints.min_wk)
            max_wk_val = min(2, self.constraints.max_wk)
            min_bat_val = 3
            max_bat_val = 5
            min_ar_val = 1
            max_ar_val = 3
            min_bowl_val = 3
            max_bowl_val = 5

            # Prune non-bowling tail-enders who will face 0 balls in 54-ball shootout
            for i, p in enumerate(self.players):
                ord_val = getattr(p, "batting_order_projected", 5)
                exp_ov = getattr(p, "expected_overs", 0.0)
                if ord_val >= 7 and exp_ov < 1.0:
                    model.Add(x[i] == 0)
        else:
            min_wk_val = self.constraints.min_wk
            max_wk_val = self.constraints.max_wk
            min_bat_val = self.constraints.min_bat
            max_bat_val = self.constraints.max_bat
            min_ar_val = self.constraints.min_ar
            max_ar_val = self.constraints.max_ar
            min_bowl_val = self.constraints.min_bowl
            max_bowl_val = self.constraints.max_bowl

        model.Add(sum(x[i] for i in wk_indices) >= min_wk_val)
        model.Add(sum(x[i] for i in wk_indices) <= max_wk_val)
        model.Add(sum(x[i] for i in bat_indices) >= min_bat_val)
        model.Add(sum(x[i] for i in bat_indices) <= max_bat_val)
        model.Add(sum(x[i] for i in ar_indices) >= min_ar_val)
        model.Add(sum(x[i] for i in ar_indices) <= max_ar_val)
        model.Add(sum(x[i] for i in bowl_indices) >= min_bowl_val)
        model.Add(sum(x[i] for i in bowl_indices) <= max_bowl_val)

        # 4. Team distribution
        teams = list(set(p.team for p in self.players))
        for t in teams:
            t_indices = [i for i, p in enumerate(self.players) if p.team == t]
            model.Add(sum(x[i] for i in t_indices) <= self.constraints.max_players_per_team)
            model.Add(sum(x[i] for i in t_indices) >= self.constraints.min_players_per_team)

        # 5. Captain and Vice Captain assignment
        model.Add(sum(c) == 1)
        model.Add(sum(v) == 1)
        for i in range(n):
            model.Add(c[i] <= x[i])  # Captain must be selected
            model.Add(v[i] <= x[i])  # Vice Captain must be selected
            model.Add(c[i] + v[i] <= 1)  # Cannot be both C and VC

        # 6. Cumulative Selection Percentage (CSP) Rule: Grand League sweet spot 480% - 650%
        # Prohibits dead "chalk" teams with CSP > 650% to prevent splitting 1st prize
        ownership_ints = [int(round(p.projected_ownership)) for p in self.players]
        max_csp = int(round(scenario.get("max_csp", 650)))
        min_csp = int(round(scenario.get("min_csp", 450)))
        ownership_available = all(p.ownership_available for p in self.players)
        if ownership_available:
            model.Add(sum(ownership_ints[i] * x[i] for i in range(n)) <= max_csp)
            model.Add(sum(ownership_ints[i] * x[i] for i in range(n)) >= min_csp)

        # 7. Contrarian X-Factor Pool Rule (<16% owned players)
        # Guarantees exactly 1 or 2 ultra-low ownership contrarians per team to win alone
        contrarian_indices = [i for i, p in enumerate(self.players) if p.projected_ownership < 16.0]
        if contrarian_indices:
            max_contra = scenario.get("max_contrarians", 2)
            min_contra = scenario.get("min_contrarians", 1)
            model.Add(sum(x[i] for i in contrarian_indices) >= min_contra)
            model.Add(sum(x[i] for i in contrarian_indices) <= max_contra)

        # 8. C/VC Combinatorics Matrix Rule:
        # Never pair #1 popular Captain with #2 popular Vice-Captain (avoids Combo A safe template in GL)
        allow_chalk_cvc = scenario.get("allow_chalk_cvc", False)
        if not allow_chalk_cvc:
            high_c_indices = [i for i, p in enumerate(self.players) if getattr(p, "captain_percentage", 0.0) >= 20.0 or p.projected_ownership >= 80.0]
            high_vc_indices = [i for i, p in enumerate(self.players) if getattr(p, "vice_captain_percentage", 0.0) >= 15.0 or p.projected_ownership >= 75.0]
            for hc in high_c_indices:
                for hvc in high_vc_indices:
                    if hc != hvc:
                        model.Add(c[hc] + v[hvc] <= 1)

        # 9. Differential requirement: sub-35% ownership picks
        diff_indices = [i for i, p in enumerate(self.players) if p.projected_ownership < 35.0]
        if ownership_available and min_diffs > 0:
            model.Add(sum(x[i] for i in diff_indices) >= min_diffs)

        # 10. Pairwise Overlap Constraint with previously generated lineups
        for prev in previous_selections:
            model.Add(sum(x[i] for i in prev) <= max_overlap)

        # 10b. Syndicate Player Locks (100% Exposure) & Exclusions (0% Exposure)
        if locked_player_ids:
            for i, p in enumerate(self.players):
                if p.id in locked_player_ids:
                    model.Add(x[i] == 1)

        if excluded_player_ids:
            for i, p in enumerate(self.players):
                if p.id in excluded_player_ids:
                    model.Add(x[i] == 0)

        # 11. Scenario preferred Captain / Vice-Captain soft or hard locks
        c_idx = None
        vc_idx = None
        pref_c = scenario.get("preferred_c")
        pref_vc = scenario.get("preferred_vc")
        if pref_c:
            c_idx = next((i for i, p in enumerate(self.players) if p.id == pref_c), None)
            if c_idx is not None:
                model.Add(c[c_idx] == 1)
        if pref_vc:
            vc_idx = next((i for i, p in enumerate(self.players) if p.id == pref_vc), None)
            if vc_idx is not None:
                if c_idx is not None and vc_idx == c_idx:
                    pass  # Cannot assign same player to both C and VC
                else:
                    model.Add(v[vc_idx] == 1)

        # Shortened Match Captaincy Rule:
        # In matches <= 14 overs, Captain MUST be either in batting top 3 (order <= 3)
        # OR a frontline strike bowler (expected_overs >= 3.0 or role == "BOWL").
        # Lower-order accumulators (orders 5-8 with <2.5 expected overs) are barred from C/VC.
        if overs <= 14 and not scenario.get("preferred_c"):
            for i, p in enumerate(self.players):
                order = p.batting_order_projected or 5
                exp_ov = p.expected_overs or 0.0
                if order > 3 and exp_ov < 2.5:
                    model.Add(c[i] == 0)

        # 9. Objective Function: Venue & Pitch Matchup Intelligence + Low-Credit Gem Efficiency
        venue = venue_conditions or {}
        pace_pct = venue.get("pace_wickets_pct", 64.0)

        objective_terms = []
        for i, p in enumerate(self.players):
            score = p.projected_points or (p.stats.avg_fantasy_pts * 0.85)

            if scenario.get("short_match"):
                score *= 1.3 if p.batting_order_projected <= 3 else 0.85
            if scenario.get("pace_boost") and any(style in (p.bowling_style or "").lower() for style in ("fast", "pace", "medium")):
                score *= scenario["pace_boost"]
            if p.role in {"BAT", "WK"}:
                score *= scenario.get("batting_boost", 1.0)
            if p.projected_ownership < 35:
                score *= scenario.get("ownership_boost", 1.0)
            # Scenario team bias (Dynamic for any fixture)
            if scenario.get("team_biases"):
                score *= scenario["team_biases"].get(p.team, 1.0)
            elif p.team == scenario.get("favored_team"):
                score *= scenario.get("team_bias", 1.15)
            elif p.team == "IND":
                score *= scenario.get("ind_bias", 1.0)
            elif p.team == "WI":
                score *= scenario.get("wi_bias", 1.0)

            # "Less Sold" (Ownership Inversion Curve for 7L+ Mega Contests)
            if p.projected_ownership < 20.0:
                score *= 1.35  # Extreme leverage (<20% own)
            elif p.projected_ownership < 35.0:
                score *= 1.22  # High leverage (<35% own)
            elif p.projected_ownership > 75.0:
                score *= 0.90  # Fade chalk to avoid field duplication collisions

            # Venue & Bowler Type Intelligence (59.6% Pacer wickets at Chinnaswamy):
            b_style = (p.bowling_style or "").lower()
            if p.role == "BOWL" or p.expected_overs >= 2.0:
                # Fast / express pace on pace-friendly / bouncy deck (59.6% pacer wickets)
                if pace_pct >= 55.0 and any(w in b_style for w in ["fast", "pace", "medium-fast", "medium"]):
                    score *= 1.24
                # Death overs specialist bonus
                if getattr(p.stats, "death_overs_rate", 0) > 0.3 or "death" in (p.differential_tag or "").lower():
                    score *= 1.16
            elif p.role == "BAT" or p.role == "WK":
                # High strike-rate power hitters & death finishers
                if p.stats.strike_rate >= 160.0:
                    score *= 1.18

            # Dream Team Appearance Consistency (Last 5 T20s)
            dt_pct = getattr(p, "dream_team_percentage", 0.0)
            if dt_pct >= 80.0:
                score *= 1.20  # Elite consistency (80% DT rate in last 5 matches)
            elif dt_pct >= 50.0:
                score *= 1.10

            # Low-Credit Value-per-Credit (VPC) Efficiency ("less less credit player")
            if p.credits <= 8.0:
                vpc = p.ceiling_score / max(1.0, p.credits)
                if vpc >= 14.0 or p.credits <= 7.0:
                    score *= 1.25  # Reward elite value-per-credit gems (6.0 - 7.5 Cr)

            # Ceiling component: For mega fields (>= 500,000 spots), prioritize 90th percentile ceiling (40% weight)
            ceil_weight = {"BALANCED": 0.20, "HIGH_CEILING": 0.55, "DIFFERENTIAL_HEAVY": 0.40}.get(scenario.get("risk_mode"), 0.40)
            c_score = p.ceiling_score or (score * 1.5)
            combined_base = int(round((score * (1.0 - ceil_weight) + c_score * ceil_weight) * 100))

            # Strategic Captaincy Leverage Factor:
            # Over 50% of the entire field Captains either Abhishek Sharma (26%) or Shai Hope (24%).
            # Boosting high-ceiling sub-5% differential Captains (e.g. Tilak Varma, Mayank Yadav, Rutherford, Shamar Joseph)
            c_pct = getattr(p, "captain_percentage", 0.0)
            c_mult = 1.0
            if c_pct > 20.0:
                c_mult = 0.88  # Chalk captain fade for solo GPP podium
            elif c_pct < 2.0 and (dt_pct >= 40.0 or p.credits <= 8.0):
                c_mult = 1.30  # Sub-2% Golden Differential Captain
            elif c_pct < 5.0 and dt_pct >= 40.0:
                c_mult = 1.18

            cap_extra = int(round(c_score * 1.0 * c_mult * 100))      # 1x extra for Captain
            vc_extra = int(round(c_score * 0.5 * (1.0 + (c_mult - 1.0)*0.5) * 100))  # 0.5x extra for VC

            objective_terms.append(combined_base * x[i] + cap_extra * c[i] + vc_extra * v[i])

        model.Maximize(sum(objective_terms))

        # Solve with CP-SAT
        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = 2.0
        solver.parameters.num_workers = 4
        status = solver.Solve(model)

        if status not in [cp_model.OPTIMAL, cp_model.FEASIBLE]:
            # Hard constraints must survive infeasibility. Never retry a different request.
            return None

        # Extract selected players
        selected_players = [self.players[i] for i in range(n) if solver.Value(x[i]) == 1]
        captain = next(self.players[i] for i in range(n) if solver.Value(c[i]) == 1)
        vice_captain = next(self.players[i] for i in range(n) if solver.Value(v[i]) == 1)

        total_credits = round(sum(p.credits for p in selected_players), 1)
        projected_pts = round(
            sum(
                p.projected_points * (2.0 if p.id == captain.id else (1.5 if p.id == vice_captain.id else 1.0))
                for p in selected_players
            ),
            1
        )
        simulated_ceiling = round(
            sum(
                p.ceiling_score * (2.0 if p.id == captain.id else (1.5 if p.id == vice_captain.id else 1.0))
                for p in selected_players
            ),
            1
        )
        total_ownership = round(sum(p.projected_ownership for p in selected_players), 1)
        diff_count = sum(1 for p in selected_players if p.projected_ownership < 35.0)

        # M-N-C (Must-have Core, Rotation, Contrarian) Classification
        core_count = sum(1 for p in selected_players if p.projected_ownership >= 60.0)
        rotation_count = sum(1 for p in selected_players if 16.0 <= p.projected_ownership < 60.0)
        contrarian_count = sum(1 for p in selected_players if p.projected_ownership < 16.0)
        mnc_summary = f"{core_count} Core | {rotation_count} Rotation | {contrarian_count} Contrarian"

        # C/VC Combinatorics Matrix classification
        c_own = getattr(captain, "captain_percentage", 0.0) or (captain.projected_ownership * 0.3)
        vc_own = getattr(vice_captain, "vice_captain_percentage", 0.0) or (vice_captain.projected_ownership * 0.2)
        if c_own >= 20.0 and vc_own >= 15.0:
            cvc_type = "Combo A (Safe Template - High C / High VC)"
        elif c_own >= 20.0 and vc_own < 6.0:
            cvc_type = "Combo B (The Sweet Spot - High C / Low VC)"
        elif c_own < 6.0 and vc_own >= 15.0:
            cvc_type = "Combo C (The GL Killer - Low C / High VC)"
        else:
            cvc_type = "Combo B (Differentiated C/VC)"

        team_balance = {
            t: sum(1 for p in selected_players if p.team == t)
            for t in teams
        }

        return Lineup(
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
            gl_rank_potential=scenario.get("gl_potential", "Elite Ceiling"),
            tactical_rationale=scenario.get("rationale", "Mathematical integer programming optimization"),
            csp=total_ownership,
            mnc_summary=mnc_summary,
            cvc_combo_type=cvc_type
        )

    def _get_default_scenarios(self) -> List[Dict[str, Any]]:
        return [
            {
                "tag": "EXPRESS_PACE_CARNIVAL",
                "name": "Express Pace & Seam Carnage",
                "ind_bias": 1.05, "wi_bias": 1.05,
                "preferred_c": "ind_mayank", "preferred_vc": "ind_tilak",
                "gl_potential": "Rank #1 Leverage",
                "rationale": "Overcast damp red-soil amplifies 150kph bounce and swing. Mayank Yadav tears through top order; Tilak Varma anchors."
            },
            {
                "tag": "WI_POWER_UPSET",
                "name": "West Indies Decider Counter-Punch",
                "ind_bias": 0.8, "wi_bias": 1.4,
                "preferred_c": "wi_shepherd", "preferred_vc": "wi_hope",
                "gl_potential": "High Volatility",
                "rationale": "Romario Shepherd's 250+ death SR and cutters exploit damp surface while Shai Hope anchors."
            },
            {
                "tag": "MIDDLE_ORDER_REBUILD",
                "name": "Middle-Overs Recovery Masterclass",
                "ind_bias": 1.20, "wi_bias": 0.90,
                "preferred_c": "ind_tilak", "preferred_vc": "ind_axar",
                "gl_potential": "Elite Floor + Ceiling",
                "rationale": "Early swing takes down aggressive openers; Tilak Varma (80% DT rate) and Axar Patel anchor the recovery and take wickets."
            },
            {
                "tag": "DEATH_OVERS_BLITZ",
                "name": "Death Overs Boundary Explosion",
                "ind_bias": 0.95, "wi_bias": 1.25,
                "preferred_c": "wi_rutherford", "preferred_vc": "ind_arshdeep",
                "gl_potential": "Contrarian Multiplier",
                "rationale": "Sherfane Rutherford (204.8 death SR) unleashes at death; Arshdeep Singh mops up lower order wickets with pinpoint yorkers."
            },
            {
                "tag": "RAIN_SHORTENED_SPRINT",
                "name": "Rain-Reduced Powerplay Sprint",
                "ind_bias": 1.25, "wi_bias": 0.85,
                "preferred_c": "ind_abhishek", "preferred_vc": "wi_joseph",
                "gl_potential": "High Ceiling Slugfest",
                "rationale": "Overcast skies trigger a shortened game scenario; Abhishek Sharma attacks from ball one while Alzarri Joseph strikes early."
            },
            {
                "tag": "CHASE_DEW_MASTERCLASS",
                "name": "Dew-Assisted Chasing Heavy",
                "ind_bias": 1.3, "wi_bias": 0.85,
                "preferred_c": "ind_ishan", "preferred_vc": "ind_shreyas",
                "gl_potential": "Anchor Balanced",
                "rationale": "Dew makes 2nd innings batting effortless for top 4 batters to finish the chase."
            },
            {
                "tag": "ALL_ROUNDER_MAXIMIZER",
                "name": "All-Rounder Multi-Category Floor",
                "ind_bias": 1.1, "wi_bias": 1.1,
                "preferred_c": "ind_axar", "preferred_vc": "wi_shepherd",
                "gl_potential": "Floor + Ceiling Hybrid",
                "rationale": "Maximizes points from dual-threat players contributing top-7 batting runs and 4 bowling overs."
            },
            {
                "tag": "WI_DEATH_SURGE",
                "name": "West Indies Death Overs Blitz",
                "ind_bias": 0.9, "wi_bias": 1.3,
                "preferred_c": "wi_powell", "preferred_vc": "wi_motie",
                "gl_potential": "High Volatility",
                "rationale": "Rovman Powell unleashes fireworks in overs 16-20 while Motie constricts scoring."
            },
            {
                "tag": "POWERPLAY_CHAOS_COLLAPSE",
                "name": "Both Sides Powerplay Collapse",
                "ind_bias": 1.0, "wi_bias": 1.0,
                "preferred_c": "wi_forde", "preferred_vc": "ind_arshdeep",
                "gl_potential": "Rank #1 Punt",
                "rationale": "New ball swing decimates top orders, making middle-order anchors and death bowlers king."
            },
            {
                "tag": "SAMSON_VOLATILITY_BURST",
                "name": "Sanju Samson High-Variance Burst",
                "ind_bias": 1.25, "wi_bias": 0.85,
                "preferred_c": "ind_samson", "preferred_vc": "ind_mayank",
                "gl_potential": "Ultra Ceiling",
                "rationale": "Samson strikes a thunderous 80+ at 180 SR while Mayank Yadav mops up lower order."
            },
            {
                "tag": "SPIN_CHOKE_MIDDLE",
                "name": "Spin Strangle & Boundary Starvation",
                "ind_bias": 1.15, "wi_bias": 0.95,
                "preferred_c": "ind_axar", "preferred_vc": "wi_hosein",
                "gl_potential": "Dot Ball Accumulator",
                "rationale": "Axar Patel and Akeal Hosein build extreme dot pressure across overs 7-15, forcing mistimed slogs."
            },
            {
                "tag": "OPENER_SHOOTOUT_200",
                "name": "Top-Order 200+ Boundary Shootout",
                "ind_bias": 1.10, "wi_bias": 1.10,
                "preferred_c": "ind_abhishek", "preferred_vc": "wi_hope",
                "gl_potential": "High Aggregate Score",
                "rationale": "Pure batting paradise: both opening pairs survive powerplay and produce 100+ opening stands."
            },
            {
                "tag": "WI_TOP_ORDER_PUNT",
                "name": "West Indies Top-Order Dominance",
                "ind_bias": 0.85, "wi_bias": 1.35,
                "preferred_c": "wi_hope", "preferred_vc": "wi_rutherford",
                "gl_potential": "Contrarian Solo",
                "rationale": "West Indies post 195+ with Hope and Rutherford dominating Indian spinners."
            },
            {
                "tag": "DEATH_SEAM_DUO",
                "name": "Death Over Wicket Cluster (Bowlers C/VC)",
                "ind_bias": 1.05, "wi_bias": 1.05,
                "preferred_c": "ind_arshdeep", "preferred_vc": "wi_joseph",
                "gl_potential": "Wicket Multiplier",
                "rationale": "Arshdeep Singh and Alzarri Joseph deliver 8 wickets between overs 16-20 as batters swing wildly."
            },
            {
                "tag": "LOW_SCORING_GRIND",
                "name": "Low-Scoring 145 Pitch Dogfight",
                "ind_bias": 1.0, "wi_bias": 1.0,
                "preferred_c": "ind_tilak", "preferred_vc": "wi_shepherd",
                "gl_potential": "Attrition Specialist",
                "rationale": "Dry abrasive soil slows down the ball; anchors and seam cutters decide a tight low-scoring thriller."
            },
            {
                "tag": "HIGH_ALTITUDE_CARNAGE",
                "name": "Chinnaswamy 220+ Six Carnival",
                "ind_bias": 1.20, "wi_bias": 1.10,
                "preferred_c": "ind_ishan", "preferred_vc": "wi_hetmyer",
                "gl_potential": "Max Strike Rate",
                "rationale": "Short boundaries produce 24+ sixes; Ishan Kishan and Shimron Hetmyer feast on pace."
            },
            {
                "tag": "LEFT_ARM_ANGLE_PRESSURE",
                "name": "Left-Arm Seam & Spin Geometry",
                "ind_bias": 1.15, "wi_bias": 1.05,
                "preferred_c": "ind_arshdeep", "preferred_vc": "ind_axar",
                "gl_potential": "Angle Leverage",
                "rationale": "Arshdeep and Axar dismantle right-handed West Indies middle order with cramping angles."
            },
            {
                "tag": "FINISHER_LEVERAGE_RUN",
                "name": "Finisher Leverage Over-Indices",
                "ind_bias": 0.95, "wi_bias": 1.25,
                "preferred_c": "wi_rutherford", "preferred_vc": "wi_shepherd",
                "gl_potential": "Syndicate Edge",
                "rationale": "Fades popular openers; banks entirely on Rutherford and Shepherd stealing the show."
            },
            {
                "tag": "EXPRESS_PACE_STRANGLE",
                "name": "150kph Mayank + Joseph Dual Wreckage",
                "ind_bias": 1.10, "wi_bias": 1.10,
                "preferred_c": "ind_mayank", "preferred_vc": "wi_joseph",
                "gl_potential": "Raw Velocity",
                "rationale": "Mayank Yadav and Shamar Joseph bowl express toe-crushers, cleaning up stumps under lights."
            },
            {
                "tag": "MEGA_ANTI_CHALK_SOLO",
                "name": "Mega Contest Anti-Chalk Solo #1",
                "ind_bias": 1.05, "wi_bias": 1.15,
                "preferred_c": "ind_tilak", "preferred_vc": "wi_motie",
                "gl_potential": "Zero Collision Solo",
                "rationale": "Maximum anti-chalk composition (CSP 510%) engineered to guarantee solo 1st rank without splitting."
            }
        ]

