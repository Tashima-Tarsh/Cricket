"""
EdgeForge – Game-Script Aware Gaussian Copula
==============================================
Produces correlated fantasy-point samples that respect cricket reality.
"""
from __future__ import annotations
import numpy as np
from scipy import stats
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

from edgeforge.models.schemas import Archetype, Player


@dataclass
class CopulaResult:
    samples: np.ndarray          # shape (n_sims, n_players)
    player_ids: List[str]
    realised_corr: np.ndarray
    target_corr: np.ndarray
    max_corr_error: float
    is_valid: bool


def build_cricket_correlation_matrix(
    players: List[Player],
    archetype: Archetype,
    intensity: float = 0.7,
) -> np.ndarray:
    """
    Construct a valid correlation matrix that encodes cricket knowledge.
    intensity: 0-1 how strongly the archetype affects correlations.
    """
    n = len(players)
    R = np.eye(n)

    def set_corr(i: int, j: int, val: float):
        if i != j:
            R[i, j] = R[j, i] = np.clip(val, -0.85, 0.85)

    for i, p in enumerate(players):
        for j, q in enumerate(players):
            if i >= j:
                continue

            same_team = p.team == q.team
            both_bat = p.role in ("BAT", "WK", "AR") and q.role in ("BAT", "WK", "AR")
            both_bowl = p.role in ("BOWL", "AR") and q.role in ("BOWL", "AR")

            base = 0.0

            if same_team and both_bat:
                base = 0.40
                if archetype == Archetype.ROAD:
                    base += 0.12 * intensity
                elif archetype == Archetype.MINEFIELD:
                    base -= 0.08 * intensity

            elif same_team and both_bowl:
                base = 0.15

            elif same_team and (p.role == "BOWL" and q.role in ("BAT", "WK")):
                if archetype == Archetype.ROAD:
                    base = 0.18 * intensity
                else:
                    base = -0.12 * intensity

            elif not same_team and both_bat:
                if archetype == Archetype.MISMATCH:
                    base = -0.10 * intensity

            set_corr(i, j, base)

    R = _nearest_positive_definite(R)
    return R


def _nearest_positive_definite(A: np.ndarray) -> np.ndarray:
    """Simple projection to nearest positive-definite matrix."""
    B = (A + A.T) / 2
    eigval, eigvec = np.linalg.eigh(B)
    eigval[eigval < 1e-6] = 1e-6
    return eigvec @ np.diag(eigval) @ eigvec.T


def gaussian_copula_sample(
    players: List[Player],
    means: np.ndarray,
    stds: np.ndarray,
    target_corr: np.ndarray,
    n_sims: int = 10_000,
    seed: Optional[int] = None,
) -> CopulaResult:
    """
    1. Sample multivariate normal with target correlation.
    2. Convert to uniforms via standard normal CDF.
    3. Inverse-transform through player marginals.
    """
    rng = np.random.default_rng(seed)
    n = len(players)

    try:
        L = np.linalg.cholesky(target_corr)
    except np.linalg.LinAlgError:
        target_corr = _nearest_positive_definite(target_corr)
        L = np.linalg.cholesky(target_corr)

    z = rng.standard_normal(size=(n_sims, n))
    correlated = z @ L.T

    u = stats.norm.cdf(correlated)

    samples = np.zeros_like(u)
    for i in range(n):
        samples[:, i] = stats.norm.ppf(u[:, i], loc=means[i], scale=max(stds[i], 1.0))

    samples = np.clip(samples, -10.0, 250.0)

    realised = np.corrcoef(samples, rowvar=False)
    max_err = float(np.max(np.abs(realised - target_corr)))
    is_valid = max_err <= 0.08

    return CopulaResult(
        samples=samples,
        player_ids=[p.id for p in players],
        realised_corr=realised,
        target_corr=target_corr,
        max_corr_error=max_err,
        is_valid=is_valid,
    )


def verify_correlation(realised: np.ndarray, target: np.ndarray, tol: float = 0.06) -> bool:
    """Hard invariant used by the rest of the pipeline."""
    if realised.shape != target.shape:
        return False
    return float(np.max(np.abs(realised - target))) <= tol
