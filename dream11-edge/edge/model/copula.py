"""Gaussian copula + Iman-Conover. Preserves marginals exactly."""
from __future__ import annotations
import numpy as np
from scipy import stats


def repair_psd(c, eps=1e-8):
    c = np.asarray(c, float)
    c = (c + c.T) / 2.0
    w, v = np.linalg.eigh(c)
    c = v @ np.diag(np.clip(w, eps, None)) @ v.T
    d = np.sqrt(np.diag(c))
    return c / np.outer(d, d)


def shrink_fisher(c, n_obs, prior=200.0):
    lam = n_obs / (n_obs + prior)
    return np.tanh(np.arctanh(np.clip(c, -0.999, 0.999)) * lam)


def gaussian_copula(corr, n, rng):
    L = np.linalg.cholesky(repair_psd(corr))
    return stats.norm.cdf(rng.standard_normal((n, corr.shape[0])) @ L.T)


def iman_conover(samples, target, rng):
    n, k = samples.shape
    latent = 2.0 * np.sin(np.pi / 6.0 * target)
    L = np.linalg.cholesky(repair_psd(latent))
    R = rng.standard_normal((n, k)) @ L.T
    out = np.empty_like(samples)
    for j in range(k):
        out[np.argsort(R[:, j], kind="stable"), j] = np.sort(samples[:, j])
    return out


def correlated_scores(marginals, corr, n, rng, pool=20000):
    ids = list(marginals)
    if corr.shape != (len(ids), len(ids)):
        raise ValueError("corr shape mismatch")
    raw = np.empty((n, len(ids)))
    for j, pid in enumerate(ids):
        raw[:, j] = marginals[pid].sample(n, rng)
    out = iman_conover(raw, corr, rng)
    return out, ids


def verify(scores, marginals, ids, corr, tol_m=0.35, tol_c=0.06):
    for j, pid in enumerate(ids):
        assert abs(scores[:, j].mean() - marginals[pid].mean) < tol_m, f"mean {pid}"
        assert abs(scores[:, j].std() - marginals[pid].sd) < tol_m * 2, f"sd {pid}"
    err = float(np.abs(np.corrcoef(scores.T) - corr).max())
    assert err < tol_c, f"corr drift {err:.4f}"
    return err
