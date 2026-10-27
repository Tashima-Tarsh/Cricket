"""
Dream11 Grand League Unique Team Engine - STRIKE//OS PRO
Implementation of the Contrarian GPP Portfolio Pipeline:
1. INGEST & SCORING: Cricsheet ball-by-ball processing to official Dream11 fantasy points.
2. FEATURE ENGINEERING: Opposition, venue, city, batting order, balls bowled, venue avg score, toss impact, recent form.
3. PREDICTION MODEL: Expected points, 10th percentile floor, 90th percentile ceiling.
4. OWNERSHIP MODEL: Predict public % with celebrity/fame multiplier, role convenience, price anchoring, and recency bias.
5. OPTIMIZER: Google OR-Tools CP-SAT + MIP generator (50-200 combos) with 1-WK, 3-BAT, 1-AR, 3-BOWL, max-7 per team, 6-5 split.
6. UNIQUE TEAM RULES:
   - differential_score = predicted_points / max(predicted_ownership, 1.0)
   - Lock 4-5 core picks, fill remaining 6-7 slots from high differential_score players only.
   - Captain = highest differential score, VC = 2nd highest differential score.
   - Avoid chalk clumping (never allow all top-5 most-owned players in one lineup).
7. UNIQUENESS FILTER: Sort by lowest crowd overlap (sum of ownership %).
8. MONTE CARLO RANK-1 SIMULATOR: 10,000 contest trials against Jones-Nick field distribution model.
"""

from typing import List, Dict, Any, Optional, Tuple
import numpy as np
import math
from ortools.sat.python import cp_model

from .models import Player, Lineup
from .cricsheet import CricsheetDatabase
from .ownership_leverage_model import OwnershipLeverageModel
from .dfs_contest_simulator import DFSContestSimulator, Dream11ContestStructure


class UniqueTeamEngine:
    """End-to-end Dream11 Grand League Unique Team Optimizer & Simulator."""

    def __init__(self):
        self.ownership_model = OwnershipLeverageModel()
        self.contest_simulator = DFSContestSimulator(
            contest_structure=Dream11ContestStructure.MEGA_CONTEST_700K,
            pct_field_using_stacks=0.65
        )

    def calculate_differential_scores(self, players: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Calculates differential_score = predicted_points / predicted_ownership for each player."""
        enriched = []
        for p in players:
            p_copy = dict(p)
            pts = float(p_copy.get("predicted_points") or p_copy.get("projected_points") or 30.0)
            own = float(p_copy.get("predicted_ownership") or p_copy.get("ownership") or 30.0)
            own_clamped = max(own, 1.0)
            diff_score = round(pts / own_clamped, 3)
            
            p_copy["predicted_points"] = pts
            p_copy["projected_points"] = pts
            p_copy["predicted_ownership"] = own
            p_copy["differential_score"] = diff_score
            
            # Chalk danger flag
            p_copy["is_chalk"] = own >= 60.0
            p_copy["is_differential_gem"] = (own < 35.0) and (diff_score >= 1.0)
            enriched.append(p_copy)
        return enriched

    def generate_unique_teams(
        self,
        players: List[Dict[str, Any]],
        num_teams: int = 7,
        uniqueness_level: int = 8,  # 1 (chalky) to 10 (max differential)
        risk_appetite: str = "HIGH",  # "LOW", "MEDIUM", "HIGH"
        toss_completed: bool = False,
        locked_player_ids: Optional[List[str]] = None,
        excluded_player_ids: Optional[List[str]] = None,
        contest_spots: int = 1000
    ) -> List[Dict[str, Any]]:
        """Generates unique, low-crowd-overlap Grand League portfolios satisfying all unique team rules."""
        
        # 1. Enrich players with ownership and differential scores
        if not any("predicted_ownership" in p for p in players):
            players = self.ownership_model.predict_ownership(players)
        
        enriched_players = self.calculate_differential_scores(players)
        
        # Sort players by ownership and differential score
        by_ownership = sorted(enriched_players, key=lambda x: x["predicted_ownership"], reverse=True)
        by_diff = sorted(enriched_players, key=lambda x: x["differential_score"], reverse=True)
        
        top5_chalk_ids = set(p["id"] for p in by_ownership[:5])
        
        # Available player pool
        locked_set = set(locked_player_ids or [])
        excluded_set = set(excluded_player_ids or [])
        
        pool = [p for p in enriched_players if p["id"] not in excluded_set]
        n_pool = len(pool)
        # Exclusions are hard constraints. Never restore excluded players.
        if n_pool < 11:
            return []
        if locked_set & excluded_set:
            return []
        if not locked_set.issubset({p["id"] for p in pool}):
            return []
            
        p_index_map = {p["id"]: i for i, p in enumerate(pool)}
        
        # Determine candidate generation budget (50-200 combos based on uniqueness)
        n_candidates = min(200, max(50, num_teams * 15))
        candidate_combos = []
        
        # Scale uniqueness parameters
        # Uniqueness 1 -> allows up to 5 chalk players, credit budget 95-100
        # Uniqueness 10 -> max 3 chalk players, requires 4-5 differential gems (<30% own), credit budget 80-87
        max_chalk_allowed = max(2, 5 - int(uniqueness_level / 3))
        min_gems_required = max(1, int(uniqueness_level / 2.5))
        
        # Teams
        teams_present = sorted({p.get("team") for p in pool if p.get("team")})
        if len(teams_present) != 2:
            return []
        home_team = teams_present[0] if len(teams_present) > 0 else "HOM"
        away_team = teams_present[1] if len(teams_present) > 1 else "AWY"

        # Solve combinatorial formulations with OR-Tools CP-SAT
        for combo_idx in range(n_candidates):
            model = cp_model.CpModel()
            x = [model.NewBoolVar(f"p_{i}") for i in range(n_pool)]
            
            # Constraint 1: Exactly 11 players
            model.Add(sum(x) == 11)
            
            # Constraint 2: Credit cap (default 100 max, with contrarian left-on-table constraint)
            # Higher uniqueness leaves credits on the table to eliminate field duplication
            if uniqueness_level >= 7:
                max_credits = 88.0 + (combo_idx % 7) * 1.5  # 88 - 97 Cr
                min_credits = 78.0
            elif uniqueness_level >= 4:
                max_credits = 94.0 + (combo_idx % 5) * 1.0
                min_credits = 82.0
            else:
                max_credits = 100.0
                min_credits = 88.0
                
            credits_expr = sum(int(round(float(p.get("credits", 8.5)) * 10)) * x[i] for i, p in enumerate(pool))
            model.Add(credits_expr <= int(round(max_credits * 10)))
            model.Add(credits_expr >= int(round(min_credits * 10)))
            
            # Constraint 3: Official Role bounds (min 1 WK, min 3 BAT, min 1 AR, min 3 BOWL)
            wk_vars = [x[i] for i, p in enumerate(pool) if p.get("role") == "WK"]
            bat_vars = [x[i] for i, p in enumerate(pool) if p.get("role") == "BAT"]
            ar_vars = [x[i] for i, p in enumerate(pool) if p.get("role") == "AR"]
            bowl_vars = [x[i] for i, p in enumerate(pool) if p.get("role") == "BOWL"]
            
            # Role bounds are mandatory: insufficient pools are infeasible,
            # never a reason to relax official roster rules.
            model.Add(sum(wk_vars) >= 1)
            model.Add(sum(wk_vars) <= 4)
            model.Add(sum(bat_vars) >= 3)
            model.Add(sum(bat_vars) <= 6)
            model.Add(sum(ar_vars) >= 1)
            model.Add(sum(ar_vars) <= 4)
            model.Add(sum(bowl_vars) >= 3)
            model.Add(sum(bowl_vars) <= 6)

            # Constraint 4: Max 7 players from one team (and base 6-5 split preference)
            home_vars = [x[i] for i, p in enumerate(pool) if p.get("team") == home_team]
            away_vars = [x[i] for i, p in enumerate(pool) if p.get("team") == away_team]
            
            if len(home_vars) > 0 and len(away_vars) > 0:
                model.Add(sum(home_vars) <= 7)
                model.Add(sum(away_vars) <= 7)
                # Enforce 6-5 or 7-4 split
                model.Add(sum(home_vars) >= 4)
                model.Add(sum(away_vars) >= 4)
                
            # Constraint 5: Unique Team Rule - NEVER allow all top-5 most-owned in one team
            top5_vars = [x[i] for i, p in enumerate(pool) if p["id"] in top5_chalk_ids]
            if len(top5_vars) >= 5:
                model.Add(sum(top5_vars) <= max_chalk_allowed)
                
            # Constraint 6: Force minimum differential gems (< 35% ownership)
            gem_vars = [x[i] for i, p in enumerate(pool) if p.get("predicted_ownership", 30.0) < 35.0]
            if len(gem_vars) >= min_gems_required:
                model.Add(sum(gem_vars) >= min_gems_required)
                
            # User locks
            for l_id in locked_set:
                if l_id in p_index_map:
                    model.Add(x[p_index_map[l_id]] == 1)
                    
            # Avoid previous candidate exact duplicates (diversity cut)
            for prev_indices in candidate_combos:
                model.Add(sum(x[idx] for idx in prev_indices) <= 9)
                
            # Objective: Maximize composite score:
            # points + weight_diff * differential_score - weight_chalk * ownership
            diff_weight = 0.4 + (uniqueness_level / 10.0) * 0.8
            chalk_penalty = 0.2 + (uniqueness_level / 10.0) * 0.5
            
            # Add stochastic exploration noise per combo to explore whole Pareto front
            rng_noise = np.random.uniform(0.85, 1.15, n_pool)
            
            obj_terms = []
            for i, p in enumerate(pool):
                pts = float(p.get("predicted_points", 30.0))
                diff = float(p.get("differential_score", 1.0))
                own = float(p.get("predicted_ownership", 30.0))
                
                score = (pts * 1.0 + diff * 12.0 * diff_weight - own * 0.25 * chalk_penalty) * rng_noise[i]
                obj_terms.append(int(round(score * 100)) * x[i])
                
            model.Maximize(sum(obj_terms))
            
            solver = cp_model.CpSolver()
            solver.parameters.max_time_in_seconds = 0.4
            solver.parameters.random_seed = 42 + combo_idx
            
            status = solver.Solve(model)
            if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
                selected_indices = [i for i in range(n_pool) if solver.Value(x[i]) == 1]
                if len(selected_indices) == 11:
                    candidate_combos.append(selected_indices)
                    
        # Solver failure is an infeasible or partial portfolio; never
        # manufacture unchecked combinations to fill the requested count.

        # 6. UNIQUENESS FILTER: rank candidate combos by LOWEST crowd overlap (sum of predicted ownership %)
        scored_combos = []
        for c_indices in candidate_combos:
            combo_players = [pool[i] for i in c_indices]
            crowd_overlap = sum(float(p.get("predicted_ownership", 30.0)) for p in combo_players)
            total_projected_pts = sum(float(p.get("predicted_points", 30.0)) for p in combo_players)
            total_credits = sum(float(p.get("credits", 8.5)) for p in combo_players)
            
            # Differential Captaincy Selection:
            # Captain = highest differential score player in the team
            # VC = 2nd highest differential score player in the team
            sorted_by_diff = sorted(combo_players, key=lambda x: x.get("differential_score", 1.0), reverse=True)
            captain = sorted_by_diff[0]
            vice_captain = sorted_by_diff[1]
            
            # Calculate team score with C (2x) and VC (1.5x) multipliers
            effective_pts = total_projected_pts + (captain["predicted_points"] * 1.0) + (vice_captain["predicted_points"] * 0.5)
            
            scored_combos.append({
                "indices": c_indices,
                "players": combo_players,
                "captain": captain,
                "vice_captain": vice_captain,
                "crowd_overlap_pct": round(crowd_overlap, 1),
                "total_credits": round(total_credits, 1),
                "projected_points": round(effective_pts, 1),
                "uniqueness_rating": round(max(10.0, 1100.0 - crowd_overlap) / 11.0, 1),  # Out of 100
            })
            
        # Sort candidates according to uniqueness level preference:
        # High uniqueness -> prioritize lowest crowd overlap while keeping projected points high
        if uniqueness_level >= 7:
            scored_combos.sort(key=lambda c: (c["crowd_overlap_pct"], -c["projected_points"]))
        else:
            scored_combos.sort(key=lambda c: (-c["projected_points"], c["crowd_overlap_pct"]))
            
        top_combos = scored_combos[:num_teams]
        
        # 7. MONTE CARLO RANK-1 SIMULATOR
        # Simulate each candidate against competitive field to compute Rank-1 probability %
        sim_results = self._simulate_rank1_distribution(top_combos, pool, contest_spots=contest_spots)
        
        # Assemble final team outputs
        final_teams = []
        for idx, item in enumerate(top_combos):
            sim_stat = sim_results[idx] if idx < len(sim_results) else {}
            
            # Mark player roles and C/VC
            team_players = []
            for p in item["players"]:
                p_out = dict(p)
                p_out["is_captain"] = (p["id"] == item["captain"]["id"])
                p_out["is_vice_captain"] = (p["id"] == item["vice_captain"]["id"])
                team_players.append(p_out)
                
            home_count = sum(1 for p in team_players if p.get("team") == home_team)
            away_count = sum(1 for p in team_players if p.get("team") == away_team)
            
            final_teams.append({
                "team_id": f"GL_TEAM_{idx + 1:02d}",
                "name": f"Contrarian XI #{idx + 1}",
                # Field model lacks calibrated real opponent entries and
                # verified selection percentages: no actual rank claim.
                "rank_1_probability_pct": None,
                "rank_10_probability_pct": None,
                "median_rank": None,
                "rank_metrics_status": "UNAVAILABLE_UNCALIBRATED_FIELD",
                "ceiling_p90": sim_stat.get("ceiling_p90"),
                "floor_p10": sim_stat.get("floor_p10"),
                "projected_points": item["projected_points"],
                "crowd_overlap_pct": item["crowd_overlap_pct"],
                "uniqueness_rating": item["uniqueness_rating"],
                "total_credits": item["total_credits"],
                "team_split": f"{home_count}:{away_count}",
                "captain": item["captain"]["name"],
                "captain_id": item["captain"]["id"],
                "captain_differential_score": item["captain"]["differential_score"],
                "vice_captain": item["vice_captain"]["name"],
                "vice_captain_id": item["vice_captain"]["id"],
                "vice_captain_differential_score": item["vice_captain"]["differential_score"],
                "is_toss_locked": toss_completed,
                "toss_status": "lineup_confirmed" if toss_completed else "pre-toss",
                "players": team_players,
                "risk_rating": "BOOM_OR_BUST" if item["crowd_overlap_pct"] < 520 else "BALANCED_GPP"
            })
            
        return final_teams

    def _simulate_rank1_distribution(
        self,
        teams: List[Dict[str, Any]],
        all_players: List[Dict[str, Any]],
        n_sims: int = 2500,
        contest_spots: int = 1000
    ) -> List[Dict[str, Any]]:
        """Fast Monte Carlo contest simulator estimating rank-1 probability against field models."""
        n_players = len(all_players)
        p_ids = {p["id"]: i for i, p in enumerate(all_players)}
        
        # Build stochastic player performance distribution (Log-normal / Gamma skewed for cricket)
        # Cricket fantasy points have high right-tail skew (centuries, 4-fers)
        means = np.array([float(p.get("predicted_points", 30.0)) for p in all_players])
        stds = means * 0.55  # 55% coefficient of variation
        
        # Simulate match outcomes across n_sims (n_sims, n_players)
        # Using Gamma distribution to enforce positive fantasy points and realistic fat tails
        simulated_matrix = np.zeros((n_sims, n_players))
        for j in range(n_players):
            m = max(10.0, means[j])
            s = max(5.0, stds[j])
            shape = (m / s) ** 2
            scale = (s ** 2) / m
            simulated_matrix[:, j] = np.random.gamma(shape, scale, size=n_sims)
            
        # Simulate field distribution (Jones-Nick-93 model)
        # Field weights heavily favor top-owned players
        own_weights = np.array([max(1.0, float(p.get("predicted_ownership", 25.0))) for p in all_players])
        own_probs = own_weights / np.sum(own_weights)
        
        # Generate representative competitor scores
        n_opponents = min(1500, contest_spots)
        opp_scores = np.zeros((n_sims, n_opponents))
        
        for opp_i in range(n_opponents):
            # Sample 11 players weighted by ownership
            sampled_indices = np.random.choice(n_players, size=11, replace=False, p=own_probs)
            # Pick C and VC from top owned in selection
            sub_own = own_weights[sampled_indices]
            c_local = np.argmax(sub_own)
            opp_weights = np.ones(11)
            opp_weights[c_local] = 2.0
            opp_scores[:, opp_i] = simulated_matrix[:, sampled_indices] @ opp_weights
            
        stats_list = []
        for team in teams:
            team_indices = [p_ids[p["id"]] for p in team["players"] if p["id"] in p_ids]
            if len(team_indices) != 11:
                stats_list.append({"rank_1_pct": None, "top_10_pct": None, "median_rank": None})
                continue
                
            c_id = team["captain"]["id"]
            vc_id = team["vice_captain"]["id"]
            
            team_weights = np.ones(11)
            for local_idx, p_idx in enumerate(team_indices):
                p_obj_id = all_players[p_idx]["id"]
                if p_obj_id == c_id:
                    team_weights[local_idx] = 2.0
                elif p_obj_id == vc_id:
                    team_weights[local_idx] = 1.5
                    
            my_scores = simulated_matrix[:, team_indices] @ team_weights
            
            # Compare my scores against opponent scores across all simulations
            # Count how many opponents scored strictly higher
            scale = contest_spots / float(n_opponents)
            higher_counts = np.count_nonzero(opp_scores > my_scores[:, None], axis=1)
            sim_ranks = 1 + np.floor(higher_counts * scale).astype(int)
            
            rank_1_count = np.count_nonzero(sim_ranks == 1)
            top_10_count = np.count_nonzero(sim_ranks <= 10)
            
            rank_1_pct = round((rank_1_count / n_sims) * 100.0, 2)
            top_10_pct = round((top_10_count / n_sims) * 100.0, 1)
            median_rank = int(np.median(sim_ranks))
            
            stats_list.append({
                "rank_1_pct": None,
                "top_10_pct": None,
                "median_rank": None,
                "uncalibrated_rank_1_pct": rank_1_pct,
                "uncalibrated_top_10_pct": top_10_pct,
                "uncalibrated_median_rank": median_rank,
                "ceiling_p90": round(float(np.percentile(my_scores, 90)), 1),
                "floor_p10": round(float(np.percentile(my_scores, 10)), 1),
                "percentiles": [
                    {"percentile": "p10 (Floor)", "points": round(float(np.percentile(my_scores, 10)), 1)},
                    {"percentile": "p25", "points": round(float(np.percentile(my_scores, 25)), 1)},
                    {"percentile": "p50 (Median)", "points": round(float(np.percentile(my_scores, 50)), 1)},
                    {"percentile": "p75", "points": round(float(np.percentile(my_scores, 75)), 1)},
                    {"percentile": "p90 (Ceiling)", "points": round(float(np.percentile(my_scores, 90)), 1)},
                    {"percentile": "p99 (Boom)", "points": round(float(np.percentile(my_scores, 99)), 1)}
                ]
            })
            
        return stats_list


# Singleton instance
unique_team_engine = UniqueTeamEngine()

