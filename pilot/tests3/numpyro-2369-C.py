import numpy as np
from numpy.testing import assert_allclose
import pytest

import jax.numpy as jnp

import numpyro.distributions as dist


def _reference_variance(nu, psi):
    # Var(X_ij) for X ~ InvWishart(psi, nu), e.g. Press (1982) / scipy.stats.invwishart
    p = psi.shape[-1]
    d = np.diag(psi)
    num = (nu - p + 1) * psi**2 + (nu - p - 1) * np.outer(d, d)
    return num / ((nu - p) * (nu - p - 1) ** 2 * (nu - p - 3))


@pytest.mark.parametrize("nu", [6.5, 7.5, 12.0, 40.0])
def test_inverse_wishart_variance_off_diagonal(nu):
    psi = np.array([[2.0, 0.6, -0.3], [0.6, 1.5, 0.4], [-0.3, 0.4, 1.0]])
    d = dist.InverseWishart(jnp.asarray(nu), scale_matrix=jnp.asarray(psi))
    assert_allclose(d.variance, _reference_variance(nu, psi), rtol=1e-5)


def test_inverse_wishart_variance_batched():
    psi = np.array([[1.0, 0.5], [0.5, 2.0]])
    nus = np.array([5.5, 8.0])
    d = dist.InverseWishart(jnp.asarray(nus), scale_matrix=jnp.asarray(psi))
    expected = np.stack([_reference_variance(nu, psi) for nu in nus])
    assert_allclose(d.variance, expected, rtol=1e-5)


def test_inverse_wishart_variance_matches_inverse_of_wishart_samples():
    # Monte Carlo check: X = W^{-1}, W ~ Wishart(psi^{-1}, nu)
    rng = np.random.default_rng(0)
    nu, p = 12, 2
    psi = np.array([[1.0, 0.4], [0.4, 1.0]])
    chol = np.linalg.cholesky(np.linalg.inv(psi))
    n = 400_000
    z = rng.standard_normal((n, nu, p)) @ chol.T
    w = np.einsum("nki,nkj->nij", z, z)
    x = np.linalg.inv(w)
    mc_var = x.var(axis=0)
    d = dist.InverseWishart(jnp.asarray(float(nu)), scale_matrix=jnp.asarray(psi))
    assert_allclose(d.variance, mc_var, rtol=0.03)
