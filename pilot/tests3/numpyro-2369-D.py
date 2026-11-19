# Copyright Contributors to the Pyro project.
# SPDX-License-Identifier: Apache-2.0

import numpy as np
from numpy.testing import assert_allclose
import pytest
from scipy import stats

import numpyro.distributions as dist


def _reference_variance(psi, nu):
    p = psi.shape[-1]
    d = np.diag(psi)
    num = (nu - p + 1) * psi**2 + (nu - p - 1) * np.outer(d, d)
    return num / ((nu - p) * (nu - p - 1) ** 2 * (nu - p - 3))


@pytest.mark.parametrize("nu", [6.5, 7.0, 12.0])
def test_inverse_wishart_variance_off_diagonal(nu):
    psi = np.array([[2.0, 0.6, -0.3], [0.6, 1.5, 0.4], [-0.3, 0.4, 1.0]])
    d = dist.InverseWishart(concentration=nu, scale_matrix=psi)
    expected = _reference_variance(psi, nu)
    assert_allclose(d.variance, expected, rtol=1e-5)


def test_inverse_wishart_variance_matches_scipy_monte_carlo():
    psi = np.array([[1.0, 0.5], [0.5, 2.0]])
    nu = 6.0
    d = dist.InverseWishart(concentration=nu, scale_matrix=psi)
    samples = stats.invwishart(df=nu, scale=psi).rvs(
        size=400_000, random_state=np.random.default_rng(0)
    )
    mc_var = samples.var(axis=0)
    # off-diagonal entry: the old formula overstated this by ~40%
    assert_allclose(d.variance[0, 1], mc_var[0, 1], rtol=0.1)
    assert_allclose(np.diag(d.variance), np.diag(mc_var), rtol=0.15)


def test_inverse_wishart_variance_batched():
    psi = np.array([[1.0, 0.8], [0.8, 1.0]])
    nus = np.array([5.5, 8.0])
    d = dist.InverseWishart(concentration=nus, scale_matrix=psi)
    expected = np.stack([_reference_variance(psi, nu) for nu in nus])
    assert_allclose(d.variance, expected, rtol=1e-5)
