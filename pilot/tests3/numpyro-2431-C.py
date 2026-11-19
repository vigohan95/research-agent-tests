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


@pytest.mark.parametrize("coef", [1.0, 0.5, -0.1])
@pytest.mark.parametrize("dim", [2, 3, 5])
def test_cholesky_update_matches_dense(dim, coef):
    rng = np.random.default_rng(dim)
    A = rng.normal(size=(dim, dim))
    S = A @ A.T + dim * np.eye(dim)
    L = np.linalg.cholesky(S)
    x = rng.normal(size=dim)
    R = np.asarray(cholesky_update(jnp.array(L), jnp.array(x), coef))
    assert_allclose(R @ R.T, S + coef * np.outer(x, x), rtol=1e-4, atol=1e-4)
    assert_allclose(R, np.linalg.cholesky(S + coef * np.outer(x, x)), atol=1e-4)


def test_cholesky_update_batched():
    rng = np.random.default_rng(1)
    A = rng.normal(size=(4, 4))
    S = A @ A.T + 4 * np.eye(4)
    L = np.linalg.cholesky(S)
    xs = 0.3 * rng.normal(size=(6, 4))
    R = np.asarray(cholesky_update(jnp.array(L), jnp.array(xs), -0.2))
    for x, r in zip(xs, R):
        assert_allclose(r @ r.T, S - 0.2 * np.outer(x, x), rtol=1e-4, atol=1e-4)


def test_sa_dense_proposal_scale_matches_diagonal_formula():
    # leave-one-out covariance computed by the dense path must equal the direct one
    rng = np.random.default_rng(2)
    zs = rng.normal(size=(6, 3))
    new = rng.normal(size=3)
    loc = zs.mean(0)
    cov = np.cov(zs, rowvar=False, bias=True)
    _, scales = _get_proposal_loc_and_scale(
        jnp.array(zs), jnp.array(loc), jnp.array(np.linalg.cholesky(cov)), jnp.array(new)
    )
    for n in range(zs.shape[0]):
        others = np.concatenate([np.delete(zs, n, 0), new[None]])
        expected = np.cov(others, rowvar=False, bias=True)
        s = np.asarray(scales[n])
        assert_allclose(s @ s.T, expected, rtol=1e-4, atol=1e-4)


def test_sa_dense_mass_standard_normal_variance():
    def model():
        numpyro.sample("x", dist.Normal(jnp.zeros(3), 1.0))

    mcmc = MCMC(
        SA(model, dense_mass=True),
        num_warmup=5000,
        num_samples=40000,
        progress_bar=False,
    )
    mcmc.run(random.PRNGKey(0))
    x = mcmc.get_samples()["x"]
    assert_allclose(jnp.var(x, 0), jnp.ones(3), atol=0.1)
    assert_allclose(jnp.mean(x, 0), jnp.zeros(3), atol=0.1)
