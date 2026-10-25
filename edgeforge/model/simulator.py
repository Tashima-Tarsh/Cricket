"""
EdgeForge – Full Match Simulator + Ownership Field Sampling
===========================================================
Produces joint fantasy-point distributions and realistic opponent fields.
"""
from __future__ import annotations
import numpy as np
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field

from edgeforge.models.schemas import Player, Archetype, DataProvenance
from edgeforge.model.copula import (
    build_cricket_correlation_matrix,
    gaussian_copula_sample,
    verify_correlation,
    CopulaResult,
)


@dataclass
class SimulationResult:
    points_matrix: np.ndarray
    player_ids: List[str]
    player_index: Dict[str, int]
    means: np.ndarray
    stds: np.ndarray
    copula: CopulaResult
    archetype: Archetype
    n_sims: int
    is_valid: bool
    notes: List[str] = field(default_factory=list)


@dataclass
class FieldResult:
    lineups: List[List[str]]
    captain_ids: List[str]
    vice_captain_ids: List[str]
    n_entries: int
    ownership_used: Dict[str, float]


class MatchSimulator:
    def __init__(self, default_n_sims: int = 10_000, seed: Optional[int] = None):
        self.default_n_sims = default_n_sims
        self.seed = seed

    def run(
        self,
        players: List[Player],
        archetype: Archetype = Archetype.PARITY,
        n_sims: Optional[int] = None,
        intensity: float = 0.7,
    ) -> SimulationResult:
        if len(players) < 8:
            raise ValueError("Need at least 8 players to simulate a meaningful match")

        n_sims = n_sims or self.default_n_sims
        notes: List[str] = []

        means = np.zeros(len(players))
        stds = np.zeros(len(players))
        for i, p in enumerate(players):
            if p.projected_points is not None and p.projected_points > 0:
                means[i] = p.projected_points
                stds[i] = max(p.projected_points * 0.45, 12.0)
            else:
                prior = {"WK": 38.0, "BAT": 42.0, "AR": 48.0, "BOWL": 40.0}.get(p.role.value, 40.0)
                means[i] = prior
                stds[i] = 18.0
                notes.append(f"{p.id}: used role prior (no projected_points)")

        target_corr = build_cricket_correlation_matrix(players, archetype, intensity)
        copula = gaussian_copula_sample(
            players=players,
            means=means,
            stds=stds,
            target_corr=target_corr,
            n_sims=n_sims,
            seed=self.seed,
        )

        is_valid = copula.is_valid
        if not is_valid:
            notes.append(
                f"Correlation verification failed (max_err={copula.max_corr_error:.4f}). "
                "Downstream rank numbers are unreliable."
            )

        player_index = {pid: i for i, pid in enumerate(copula.player_ids)}

        return SimulationResult(
            points_matrix=copula.samples,
            player_ids=copula.player_ids,
            player_index=player_index,
            means=means,
            stds=stds,
            copula=copula,
            archetype=archetype,
            n_sims=n_sims,
            is_valid=is_valid,
            notes=notes,
        )


class FieldSampler:
    def __init__(self, seed: Optional[int] = None):
        self.rng = np.random.default_rng(seed)

    def sample(
        self,
        players: List[Player],
        n_entries: int = 5_000,
        team_size: int = 11,
    ) -> FieldResult:
        ids = [p.id for p in players]
        ownership = []
        for p in players:
            if p.ownership_available and p.projected_ownership is not None:
                ownership.append(max(p.projected_ownership, 0.5))
            else:
                ownership.append(2.0)

        ownership = np.array(ownership, dtype=float)
        probs = ownership / ownership.sum()

        lineups: List[List[str]] = []
        captains: List[str] = []
        vcs: List[str] = []

        for _ in range(n_entries):
            chosen_idx = self.rng.choice(len(players), size=team_size, replace=False, p=probs)
            chosen_ids = [ids[i] for i in chosen_idx]
            lineups.append(chosen_ids)

            own_of_chosen = ownership[chosen_idx]
            c_probs = own_of_chosen / own_of_chosen.sum()
            c_local = self.rng.choice(team_size, p=c_probs)
            remaining = [i for i in range(team_size) if i != c_local]
            v_local = self.rng.choice(remaining)
            captains.append(chosen_ids[c_local])
            vcs.append(chosen_ids[v_local])

        own_map = {pid: float(ownership[i]) for i, pid in enumerate(ids)}
        return FieldResult(
            lineups=lineups,
            captain_ids=captains,
            vice_captain_ids=vcs,
            n_entries=n_entries,
            ownership_used=own_map,
        )


def score_lineup_against_sims(
    sim: SimulationResult,
    player_ids: List[str],
    captain_id: str,
    vice_captain_id: str,
) -> np.ndarray:
    idx = sim.player_index
    pts = np.zeros(sim.n_sims)
    for pid in player_ids:
        if pid not in idx:
            continue
        mult = 1.0
        if pid == captain_id:
            mult = 2.0
        elif pid == vice_captain_id:
            mult = 1.5
        pts += sim.points_matrix[:, idx[pid]] * mult
    return pts


def compute_rank_percentiles(
    our_scores: np.ndarray,
    field_scores: np.ndarray,
) -> np.ndarray:
    n_sims = our_scores.shape[0]
    percentiles = np.zeros(n_sims)
    for s in range(n_sims):
        field_s = field_scores[s]
        rank = (field_s < our_scores[s]).sum() + 0.5 * (field_s == our_scores[s]).sum()
        percentiles[s] = 100.0 * rank / len(field_s)
    return percentiles
