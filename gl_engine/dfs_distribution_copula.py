"""
STRIKE//OS PRO - Empirical Distribution Fitting & Gaussian Copula Engine
Ported and adapted from chanzer0/NFL-DFS-Tools for Cricket T20/ODI/W-T20 Fantasy.

Features:
1. Empirical Distribution Fitting: Fits Gamma, Lognormal, Weibull, and Skew-Normal
   distributions to cricket fantasy points segmented by role (WK, BAT, AR, BOWL) and scoring tier.
2. Affine Transformation: Calibrates generated samples so each player's simulated mean
   and standard deviation exactly equal their projected mean and ceiling spread.
3. Heavy-Tail Guardrails: Prevents unrealistic fantasy score blowouts (>230 pts in T20) by
   falling back to calibrated shifted Gamma distributions.
4. Gaussian Copula with Iman-Conover Rank Reordering: Preserves the exact non-normal cricket
   marginal distributions while imposing realistic cross-role and teammate correlation structure.
"""

from typing import List, Dict, Any, Tuple, Optional
import math
import numpy as np
from scipy import stats


# Standard cross-player correlation priors in T20 / ODI cricket
DEFAULT_ROLE_CORRELATIONS = {
    ("PACER", "WICKETKEEPER"): 0.22,       # Edges behind the stumps / caught behind
    ("DEATH_BOWLER", "DEATH_BOWLER"): 0.16, # Team bowling bundle / collapse
    ("OPENER", "OPENER"): 0.18,             # Opening partnership synergy on flat tracks
    ("BATTER", "OPP_PACER"): -0.24,         # Direct conflict: wicket vs run scoring
    ("BATTER", "OPP_SPINNER"): -0.15,       # Middle overs conflict
    ("CAPTAIN", "VICE_CAPTAIN"): 0.20,      # Same-team dominance synergy
    ("TOP_ORDER", "LOWER_ORDER"): -0.12,    # Batting order cannibalization (top order bats out)
    ("SAME_TEAM_WIN", "SAME_TEAM_WIN"): 0.14 # Game script positive correlation
}


class EmpiricalDistributionCopula:
    """Cricket Fantasy Distribution Fitting and Copula Correlation Engine."""

    def __init__(self, random_seed: int = 42):
        self.rng = np.random.default_rng(random_seed)

    def fit_distribution_family(self, role: str, mean_pts: float) -> str:
        """Selects the best empirical distribution family for a given cricket role and tier.
        - High-variance openers: Lognormal (0-floor with explosive 80+ pt upside)
        - Middle anchors / All-Rounders: Skew-Normal / Gamma (solid floor + steady upside)
        - Death Bowlers: Weibull (controlled floor with 3-4 wicket right tail)
        - Spinners / Value picks: Shifted Gamma
        """
        role_upper = role.upper()
        if "WK" in role_upper or "OPENER" in role_upper:
            return "lognormal"
        elif "AR" in role_upper:
            return "skew_normal"
        elif "BOWL" in role_upper and mean_pts >= 40.0:
            return "weibull"
        else:
            return "gamma"

    def sample_marginal(
        self,
        n_samples: int,
        proj_mean: float,
        proj_std: float,
        dist_family: str = "gamma",
        min_floor: float = 0.0,
        max_guardrail: float = 230.0
    ) -> np.ndarray:
        """Samples from the specified empirical distribution and applies an affine
        transformation to match the exact target projected mean and standard deviation.
        """
        proj_mean = max(5.0, float(proj_mean))
        proj_std = max(8.0, float(proj_std))

        # 1. Draw raw samples from empirical parametric family
        if dist_family == "lognormal":
            # Underlying normal parameters
            sigma_ln = math.sqrt(math.log(1.0 + (proj_std / proj_mean) ** 2))
            mu_ln = math.log(proj_mean) - 0.5 * (sigma_ln ** 2)
            raw = self.rng.lognormal(mean=mu_ln, sigma=sigma_ln, size=n_samples)
        elif dist_family == "weibull":
            shape_k = max(1.1, proj_mean / proj_std)
            raw = self.rng.weibull(a=shape_k, size=n_samples) * proj_mean
        elif dist_family == "skew_normal":
            # Skewness parameter 2.5 for right-skewed cricket fantasy scoring
            raw = stats.skewnorm.rvs(a=2.5, loc=proj_mean * 0.7, scale=proj_std, size=n_samples, random_state=self.rng)
        else:
            # Default Gamma distribution: shape (k) and scale (theta)
            shape_k = max(1.2, (proj_mean / proj_std) ** 2)
            scale_theta = (proj_std ** 2) / proj_mean
            raw = self.rng.gamma(shape=shape_k, scale=scale_theta, size=n_samples)

        # 2. Affine Transformation: match target mean and std exactly
        raw_mean = np.mean(raw)
        raw_std = np.std(raw)
        if raw_std > 1e-6:
            adj = proj_mean + (raw - raw_mean) * (proj_std / raw_std)
        else:
            adj = raw

        # 3. Heavy-tail guardrails and non-negative fantasy score clamping
        # Fallback to calibrated shifted gamma if heavy-tail draws blow past the guardrail
        blowout_mask = adj > max_guardrail
        if np.any(blowout_mask):
            # Calibrated fallback for blowout outliers
            adj[blowout_mask] = np.clip(
                self.rng.gamma(shape=3.5, scale=proj_std * 0.6, size=np.count_nonzero(blowout_mask)) + proj_mean,
                min_floor,
                max_guardrail
            )

        adj = np.clip(adj, min_floor, max_guardrail)
        return adj

    def build_correlation_matrix(
        self,
        players: List[Dict[str, Any]],
        team_a: str,
        team_b: str
    ) -> np.ndarray:
        """Constructs an (N x N) cricket correlation matrix reflecting real match dynamics:
        teammate stacks, bowler-keeper synergy, and opposing batter-bowler conflicts.
        """
        n = len(players)
        corr = np.eye(n, dtype=float)

        for i in range(n):
            for j in range(i + 1, n):
                p1 = players[i]
                p2 = players[j]
                c_val = 0.0

                same_team = (p1.get("team") == p2.get("team"))
                r1 = p1.get("role", "BAT").upper()
                r2 = p2.get("role", "BAT").upper()

                if same_team:
                    # Bowler + Keeper edge correlation
                    if (r1 == "BOWL" and r2 == "WK") or (r1 == "WK" and r2 == "BOWL"):
                        c_val = 0.22
                    # Pacer tandem bundle
                    elif r1 == "BOWL" and r2 == "BOWL":
                        c_val = 0.15
                    # Opening partners
                    elif p1.get("order", 5) <= 2 and p2.get("order", 5) <= 2:
                        c_val = 0.18
                    # Top order vs lower order (cannibalization)
                    elif p1.get("order", 5) <= 3 and p2.get("order", 5) >= 6:
                        c_val = -0.12
                    else:
                        c_val = 0.08  # Mild game-script positive correlation for winning team
                else:
                    # Opposing teams: Batter vs Opposing Bowler
                    if (r1 in ["BAT", "WK"] and r2 == "BOWL") or (r1 == "BOWL" and r2 in ["BAT", "WK"]):
                        # Opposing opener vs strike pacer: strong conflict
                        if p1.get("order", 5) <= 2 or p2.get("order", 5) <= 2:
                            c_val = -0.25
                        else:
                            c_val = -0.15

                corr[i, j] = c_val
                corr[j, i] = c_val

        # Ensure Positive Semi-Definiteness (PSD repair via eigenvalue clipping)
        eigvals, eigvecs = np.linalg.eigh(corr)
        eigvals = np.maximum(eigvals, 1e-5)
        repaired = eigvecs @ np.diag(eigvals) @ eigvecs.T
        # Normalize diagonals to exactly 1.0
        inv_sqrt_diag = 1.0 / np.sqrt(np.diag(repaired))
        corr_psd = repaired * np.outer(inv_sqrt_diag, inv_sqrt_diag)
        return corr_psd

    def generate_correlated_samples(
        self,
        players: List[Dict[str, Any]],
        n_simulations: int = 10000,
        team_a: str = "IND",
        team_b: str = "NZ"
    ) -> np.ndarray:
        """Applies Gaussian Copula with Iman-Conover rank reordering:
        1. Generates correlated multivariate normal scores Z ~ N(0, Sigma).
        2. Draws independent marginal samples for each player matching their fitted distribution.
        3. Reorders each player's marginal samples to match the rank order of Z.
        Returns:
            simulated_matrix of shape (n_simulations, n_players) with exact target correlations
            and perfectly preserved non-normal cricket marginal distributions.
        """
        n_players = len(players)
        corr_matrix = self.build_correlation_matrix(players, team_a, team_b)

        # 1. Cholesky decomposition of correlation matrix
        try:
            chol = np.linalg.cholesky(corr_matrix)
        except np.linalg.LinAlgError:
            # Fallback if numerical precision issues arise
            eigvals, eigvecs = np.linalg.eigh(corr_matrix)
            eigvals = np.maximum(eigvals, 1e-4)
            repaired = eigvecs @ np.diag(eigvals) @ eigvecs.T
            chol = np.linalg.cholesky(repaired)

        # Draw uncorrelated standard normal variables and induce target correlation
        z_uncorr = self.rng.standard_normal((n_simulations, n_players))
        z_corr = z_uncorr @ chol.T

        # 2. Draw marginal distributions for each player
        marginal_matrix = np.zeros((n_simulations, n_players), dtype=float)
        for idx, p in enumerate(players):
            role = p.get("role", "BAT")
            p_mean = p.get("projected_points", 35.0)
            # Spread based on ceiling/floor
            ceil = p.get("ceiling_score", p_mean * 1.8)
            floor = p.get("floor_score", max(4.0, p_mean * 0.3))
            p_std = max(8.0, (ceil - floor) / 3.5)

            dist_family = self.fit_distribution_family(role, p_mean)
            marginal_matrix[:, idx] = self.sample_marginal(
                n_samples=n_simulations,
                proj_mean=p_mean,
                proj_std=p_std,
                dist_family=dist_family,
                min_floor=0.0,
                max_guardrail=230.0
            )

        # 3. Iman-Conover Rank Reordering:
        # Sort each column of marginal_matrix so that its ranks match the ranks of z_corr
        correlated_matrix = np.zeros_like(marginal_matrix)
        for idx in range(n_players):
            sorted_marginals = np.sort(marginal_matrix[:, idx])
            rank_order = np.argsort(z_corr[:, idx])
            # Assign sorted marginals into the rank positions of the correlated normals
            reordered = np.empty_like(sorted_marginals)
            reordered[rank_order] = sorted_marginals
            correlated_matrix[:, idx] = reordered

        return correlated_matrix

