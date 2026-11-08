import numpy as np

from edge.model.copula import correlated_scores, repair_psd, verify
from edge.model.distributions import Family, Marginal, affine_match


def test_affine_exact():
    x = np.random.default_rng(0).gamma(2, 3, 8000)
    y = affine_match(x, 30.0, 15.0)
    assert abs(y.mean() - 30.0) < 0.05
    assert abs(y.std() - 15.0) < 0.15


def test_psd_repair_is_valid_correlation():
    C = np.array([[1, .9, -.8], [.9, 1, -.7], [-.8, -.7, 1]])
    R = repair_psd(C)
    assert np.allclose(np.diag(R), 1.0, atol=1e-8)
    assert np.linalg.eigvalsh(R).min() > 0


def test_marginals_and_correlation_preserved():
    rng = np.random.default_rng(1)
    fam = Family("gamma", (2.0, 0.0, 1.5), 0.0)
    m = {f"p{i}": Marginal(fam, 20.0 + i, 10.0 + i) for i in range(5)}
    C = np.full((5, 5), 0.35)
    np.fill_diagonal(C, 1.0)
    s, ids = correlated_scores(m, C, 20000, rng)
    assert verify(s, m, ids, C) < 0.06


def test_negative_correlation():
    rng = np.random.default_rng(2)
    fam = Family("gamma", (2.0, 0.0, 1.5), 0.0)
    m = {"a": Marginal(fam, 30, 12), "b": Marginal(fam, 30, 12)}
    C = np.array([[1.0, -0.4], [-0.4, 1.0]])
    s, ids = correlated_scores(m, C, 20000, rng)
    assert np.corrcoef(s.T)[0, 1] < -0.3
