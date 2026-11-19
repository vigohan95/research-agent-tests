# Copyright Contributors to the Pyro project.
# SPDX-License-Identifier: Apache-2.0

import numpy as np
from numpy.testing import assert_allclose
import pytest

from jax import random
import jax.numpy as jnp

import numpyro
import numpyro.distributions as dist
from numpyro.distributions.util import cholesky_update
from numpyro.infer import MCMC, SA
from numpyro.infer.sa import _get_proposal_loc_and_scale


@pytest.mark.parametrize("dim", [1, 2, 4])
@pytest.mark.parametrize("coef", [1.0, 0.3, -0.1])
@pytest.mark.parametrize("batch_shape", [(), (5,)])
def test_cholesky_update_matches_numpy(dim, coef, batch_shape):
    rng = np.random.default_rng(0)
    A = rng.normal(size=(dim, dim))
    cov = A @ A.T + dim * np.eye(dim)
    L = np.linalg.cholesky(cov)
    x = rng.normal(size=batch_shape + (dim,))
    expected = cov + coef * x[..., :, None] * x[..., None, :]
    L_new = np.asarray(cholesky_update(jnp.asarray(L), jnp.asarray(x), coef))
    # result must be a valid Cholesky factor of the updated matrix
    assert_allclose(np.triu(L_new, 1), 0.0, atol=0)  # exact: upper part never touched
    assert_allclose(L_new @ np.swapaxes(L_new, -1, -2), expected, rtol=1e-5)
    assert_allclose(L_new, np.linalg.cholesky(expected), rtol=1e-4)


@pytest.mark.parametrize("dense", [True, False])
def test_sa_leave_one_out_proposal_matches_sample_covariance(dense):
    # Closed form: the proposal for index n is the (biased) covariance of the
    # adaptation set with sample n replaced by the new sample.
    rng = np.random.default_rng(1)
    N, D = 6, 3
    zs = rng.normal(size=(N, D))
    z_new = rng.normal(size=D)
    loc = zs.mean(0)
    cov = np.cov(zs, rowvar=False, bias=True)
    scale = np.linalg.cholesky(cov) if dense else np.sqrt(np.diag(cov))
    locs, scales = _get_proposal_loc_and_scale(
        jnp.asarray(zs), jnp.asarray(loc), jnp.asarray(scale), jnp.asarray(z_new)
    )
    for n in range(N):
        replaced = zs.copy()
        replaced[n] = z_new
        expected_cov = np.cov(replaced, rowvar=False, bias=True)
        assert_allclose(locs[n], replaced.mean(0), rtol=1e-5, atol=1e-6)  # atol: means near 0
        s = np.asarray(scales[n])
        if dense:
            assert_allclose(s @ s.T, expected_cov, rtol=1e-4, atol=1e-6)  # atol: off-diagonals near 0
        else:
            assert_allclose(s**2, np.diag(expected_cov), rtol=1e-4)


@pytest.mark.parametrize("dense_mass", [True, False])
def test_sa_standard_normal_variance(dense_mass):
    def model():
        numpyro.sample("x", dist.Normal(jnp.zeros(3), 1.0))

    kernel = SA(model, dense_mass=dense_mass)
    mcmc = MCMC(kernel, num_warmup=5000, num_samples=40000, progress_bar=False)
    mcmc.run(random.PRNGKey(0))
    x = np.asarray(mcmc.get_samples()["x"])
    # closed form: variance of a standard normal is 1
    assert_allclose(x.var(0), np.ones(3), rtol=0.1)
