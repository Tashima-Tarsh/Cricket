"""Correlation engine.

Gaussian copula + Iman-Conover rank reordering, Fisher-z shrinkage and
eigenvalue-clipping PSD repair. Preserves each player's marginal exactly
while hitting the target correlation.
"""
from __future__ import annotations

import numpy as np
from scipy import stats


def repair_psd(corr: np.ndarray, eps: float = 1e-8) -> np.ndarray:
    """Nearest valid correlation matrix by eigenvalue clipping."""
    c = np.asarray(corr, float)
    c = (c + c.T) / 2.0
    w, v = np.linalg.eigh(c)
    c = v @ np.diag(np.clip(w, eps, None)) @ v.T
    d = np.sqrt(np.diag(c))
    return c / np.outer(d, d)


def shrink_fisher(corr: np.ndarray, n_obs: float, prior: float = 200.0) -> np.ndarray:
    """Shrink sample correlations toward zero. Small-sample cricket data lies."""
    lam = n_obs / (n_obs + prior)
    return np.tanh(np.arctanh(np.clip(corr, -0.999, 0.999)) * lam)


def gaussian_copula(corr: np.ndarray, n: int, rng) -> np.ndarray:
    L = np.linalg.cholesky(repair_psd(corr))
    return stats.norm.cdf(rng.standard_normal((n, corr.shape[0])) @ L.T)


def iman_conover(samples: np.ndarray, target_corr: np.ndarray, rng) -> np.ndarray:
    """Induce target rank correlation without touching the marginals."""
    n, k = samples.shape
    L = np.linalg.cholesky(repair_psd(target_corr))
    R = rng.standard_normal((n, k)) @ L.T
    out = np.empty_like(samples)
    for j in range(k):
        out[np.argsort(R[:, j], kind="stable"), j] = np.sort(samples[:, j])
    return out


def correlated_scores(marginals: dict, corr: np.ndarray, n: int, rng,
                      pool: int = 20000):
    """Copula uniforms -> inverse-CDF through each player's marginal.

    Returns (n, n_players) with correct marginals AND correct correlation.
    """
    ids = list(marginals)
    k = len(ids)
    if corr.shape != (k, k):
        raise ValueError(f"corr shape {corr.shape} != {(k, k)}")

    U = gaussian_copula(corr, n, rng)
    out = np.empty((n, k))
    for j, pid in enumerate(ids):
        table = np.sort(marginals[pid].sample(pool, rng))
        out[:, j] = table[np.clip((U[:, j] * pool).astype(np.int64), 0, pool - 1)]
    return out, ids


def verify(scores: np.ndarray, marginals: dict, ids: list, corr: np.ndarray,
           tol_m: float = 0.35, tol_c: float = 0.06) -> float:
    """Hard invariants. If this fails, every downstream number is fiction."""
    for j, pid in enumerate(ids):
        m, s = scores[:, j].mean(), scores[:, j].std()
        assert abs(m - marginals[pid].mean) < tol_m, f"mean drift {pid}: {m:.3f}"
        assert abs(s - marginals[pid].sd) < tol_m * 2, f"sd drift {pid}: {s:.3f}"
    err = float(np.abs(np.corrcoef(scores.T) - corr).max())
    assert err < tol_c, f"correlation drift {err:.4f} > {tol_c}"
    return err
