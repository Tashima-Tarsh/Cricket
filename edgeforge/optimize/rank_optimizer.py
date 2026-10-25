"""
EdgeForge – Rank-Percentile OR-Tools Portfolio Optimizer
========================================================
Maximises expected rank / uniqueness under real constraints.
No hard-coded teams or players.
"""
from __future__ import annotations
from typing import List, Dict, Optional, Tuple, Any
from dataclasses import dataclass, field
import numpy as np

try:
    from ortools.sat.python import cp_model
    HAS_ORTOOLS = True
except ImportError:
    HAS_ORTOOLS = False

from edgeforge.models.schemas import Player, Archetype, DataProvenance, Lineup
from edgeforge.model.simulator import (
    MatchSimulator,
    FieldSampler,
    SimulationResult,
    score_lineup_against_sims,
    compute_rank_percentiles,
)
from datetime import datetime


@dataclass
class OptimizerConfig:
    max_credits: float = 100.0
    min_unspent: float = 13.0
    max_unspent: float = 19.0
    min_wk: int = 1
    max_wk: int = 4
    min_bat: int = 1
    max_bat: int = 6
    min_ar: int = 1
    max_ar: int = 6
    min_bowl: int = 2
    max_bowl: int = 6
    min_team_players: int = 4
    max_team_players: int = 7
    min_differentials: int = 2
    max_csp: float = 650.0
    min_csp: float = 400.0
    max_cvc_ownership_product: float = 0.05
    n_portfolios: int = 20
    n_sims: int = 5_000
    time_limit_seconds: float = 15.0


@dataclass
class OptimizedPortfolio:
    lineups: List[Dict[str, Any]]
    config_used: OptimizerConfig
    simulation_valid: bool
    notes: List[str] = field(default_factory=list)


class RankOptimizer:
    def __init__(self, config: Optional[OptimizerConfig] = None, seed: Optional[int] = None):
        if not HAS_ORTOOLS:
            raise ImportError("ortools is required: pip install ortools")
        self.config = config or OptimizerConfig()
        self.seed = seed
        self.simulator = MatchSimulator(default_n_sims=self.config.n_sims, seed=seed)
        self.field_sampler = FieldSampler(seed=seed)

    def optimize(
        self,
        players: List[Player],
        archetype: Archetype = Archetype.PARITY,
        fixture_id: str = "unknown",
    ) -> OptimizedPortfolio:
        cfg = self.config
        notes: List[str] = []

        if len(players) < 14:
            raise ValueError(f"Need a reasonable player pool (got {len(players)})")

        sim = self.simulator.run(players, archetype=archetype, n_sims=cfg.n_sims)
        if not sim.is_valid:
            notes.append("Simulation correlation check failed – ranks are approximate")

        field = self.field_sampler.sample(players, n_entries=min(3000, cfg.n_sims))

        field_scores = np.zeros((sim.n_sims, field.n_entries))
        for e in range(field.n_entries):
            field_scores[:, e] = score_lineup_against_sims(
                sim, field.lineups[e], field.captain_ids[e], field.vice_captain_ids[e]
            )

        lineups_out: List[Dict[str, Any]] = []
        used_player_sets = []

        for port_idx in range(cfg.n_portfolios):
            lineup_dict = self._solve_one(
                players, sim, field_scores, cfg, used_player_sets, port_idx
            )
            if lineup_dict is None:
                notes.append(f"Portfolio slot {port_idx} infeasible under constraints")
                break
            lineups_out.append(lineup_dict)
            used_player_sets.append(set(lineup_dict["player_ids"]))

        return OptimizedPortfolio(
            lineups=lineups_out,
            config_used=cfg,
            simulation_valid=sim.is_valid,
            notes=notes,
        )

    def _solve_one(
        self,
        players: List[Player],
        sim: SimulationResult,
        field_scores: np.ndarray,
        cfg: OptimizerConfig,
        previous_sets: List[set],
        port_idx: int,
    ) -> Optional[Dict[str, Any]]:
        model = cp_model.CpModel()
        n = len(players)

        x = [model.NewBoolVar(f"x_{i}") for i in range(n)]
        c = [model.NewBoolVar(f"c_{i}") for i in range(n)]
        v = [model.NewBoolVar(f"v_{i}") for i in range(n)]

        model.Add(sum(x) == 11)

        credits_scaled = [int(round(p.credits * 10)) for p in players]
        total_credits = sum(credits_scaled[i] * x[i] for i in range(n))
        model.Add(total_credits <= int(round(cfg.max_credits * 10)))
        model.Add(total_credits >= int(round((cfg.max_credits - cfg.max_unspent) * 10)))
        model.Add(total_credits <= int(round((cfg.max_credits - cfg.min_unspent) * 10)))

        def role_idx(role: str):
            return [i for i, p in enumerate(players) if p.role.value == role]

        model.Add(sum(x[i] for i in role_idx("WK")) >= cfg.min_wk)
        model.Add(sum(x[i] for i in role_idx("WK")) <= cfg.max_wk)
        model.Add(sum(x[i] for i in role_idx("BAT")) >= cfg.min_bat)
        model.Add(sum(x[i] for i in role_idx("BAT")) <= cfg.max_bat)
        model.Add(sum(x[i] for i in role_idx("AR")) >= cfg.min_ar)
        model.Add(sum(x[i] for i in role_idx("AR")) <= cfg.max_ar)
        model.Add(sum(x[i] for i in role_idx("BOWL")) >= cfg.min_bowl)
        model.Add(sum(x[i] for i in role_idx("BOWL")) <= cfg.max_bowl)

        teams = list({p.team for p in players})
        if len(teams) == 2:
            for t in teams:
                t_idx = [i for i, p in enumerate(players) if p.team == t]
                model.Add(sum(x[i] for i in t_idx) >= cfg.min_team_players)
                model.Add(sum(x[i] for i in t_idx) <= cfg.max_team_players)

        diffs = [i for i, p in enumerate(players) if (p.projected_ownership or 50) < 35.0]
        if diffs:
            model.Add(sum(x[i] for i in diffs) >= cfg.min_differentials)

        model.Add(sum(c) == 1)
        model.Add(sum(v) == 1)
        for i in range(n):
            model.Add(c[i] <= x[i])
            model.Add(v[i] <= x[i])
            model.Add(c[i] + v[i] <= 1)

        for prev in previous_sets:
            overlap_vars = [x[i] for i, p in enumerate(players) if p.id in prev]
            if overlap_vars:
                model.Add(sum(overlap_vars) <= 9)

        obj_terms = []
        for i, p in enumerate(players):
            mean_pts = float(sim.means[i])
            own = (p.projected_ownership or 50.0) / 100.0
            leverage = mean_pts * (1.0 - 0.6 * own)
            obj_terms.append(int(leverage * 100) * x[i])
            obj_terms.append(int(mean_pts * 80) * c[i])
            obj_terms.append(int(mean_pts * 40) * v[i])
        model.Maximize(sum(obj_terms))

        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = cfg.time_limit_seconds
        status = solver.Solve(model)

        if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
            return None

        selected = []
        cap_id = vc_id = None
        for i, p in enumerate(players):
            if solver.Value(x[i]):
                selected.append(p)
                if solver.Value(c[i]):
                    cap_id = p.id
                if solver.Value(v[i]):
                    vc_id = p.id

        if not cap_id or not vc_id:
            return None

        player_ids = [p.id for p in selected]
        our_scores = score_lineup_against_sims(sim, player_ids, cap_id, vc_id)
        percentiles = compute_rank_percentiles(our_scores, field_scores)

        tot_credits = sum(p.credits for p in selected)
        csp = sum((p.projected_ownership or 0) for p in selected)

        return {
            "portfolio_index": port_idx,
            "player_ids": player_ids,
            "players": [
                {
                    "id": p.id,
                    "name": p.name,
                    "team": p.team,
                    "role": p.role.value,
                    "credits": p.credits,
                    "ownership": p.projected_ownership,
                    "is_captain": p.id == cap_id,
                    "is_vice_captain": p.id == vc_id,
                }
                for p in selected
            ],
            "captain_id": cap_id,
            "vice_captain_id": vc_id,
            "total_credits": round(tot_credits, 1),
            "unspent_credits": round(100.0 - tot_credits, 1),
            "csp": round(csp, 1),
            "mean_score": float(np.mean(our_scores)),
            "mean_percentile": float(np.mean(percentiles)),
            "p90_percentile": float(np.percentile(percentiles, 90)),
            "p99_percentile": float(np.percentile(percentiles, 99)),
        }
