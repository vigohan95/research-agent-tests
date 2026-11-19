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


@pytest.mark.parametrize("coef", [1.0, 0.3, -0.1])
@pytest.mark.parametrize("batch_shape", [(), (5,)])
def test_cholesky_update_matches_full_decomposition(coef, batch_shape):
    rng = np.random.default_rng(0)
    dim = 4
    A = rng.normal(size=(dim, dim))
    cov = A @ A.T + dim * np.eye(dim)
    L = np.linalg.cholesky(cov)
    x = rng.normal(size=batch_shape + (dim,))

    actual = cholesky_update(jnp.asarray(L), jnp.asarray(x), coef)
    expected_cov = cov + coef * np.einsum("...i,...j->...ij", x, x)
    expected = np.linalg.cholesky(expected_cov)
    assert_allclose(np.asarray(actual), expected, atol=1e-4, rtol=1e-4)


def test_sa_dense_mass_standard_normal_variance():
    def model():
        numpyro.sample("x", dist.Normal(0, 1).expand([3]).to_event(1))

    mcmc = MCMC(
        SA(model, dense_mass=True),
        num_warmup=10000,
        num_samples=40000,
        progress_bar=False,
    )
    mcmc.run(random.PRNGKey(0))
    x = np.asarray(mcmc.get_samples()["x"])
    assert_allclose(x.mean(0), np.zeros(3), atol=0.1)
    assert_allclose(x.var(0), np.ones(3), atol=0.1)
