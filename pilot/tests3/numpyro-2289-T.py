# Copyright Contributors to the Pyro project.
# SPDX-License-Identifier: Apache-2.0
"""Regression tests for ``DiscreteUniform.icdf`` (inverse-transform sampling)."""

import numpy as np
from numpy.testing import assert_allclose, assert_array_equal
import pytest
import scipy.stats as osp

import jax.numpy as jnp

import numpyro.distributions as dist


@pytest.mark.parametrize(
    "low, high",
    [(0, 1), (2, 5), (-3, 3), (np.array([0, 2, -4]), np.array([4, 2, 1]))],
)
def test_discrete_uniform_icdf_matches_scipy_ppf(low, high):
    # Reference: scipy.stats.randint(low, high + 1).ppf on (0, 1]. Levels avoid
    # interior jump points k / n, where float32 vs float64 rounding of q could
    # legitimately flip the answer by one.
    q = jnp.array([1e-3, 0.11, 0.23, 0.37, 0.41, 0.55, 0.62, 0.79, 0.93, 0.999, 1.0])
    q = q.reshape((-1,) + (1,) * np.ndim(low))
    d = dist.DiscreteUniform(low, high)
    actual = d.icdf(q)
    expected = osp.randint(low, np.asarray(high) + 1).ppf(np.asarray(q))
    # Quantiles of a discrete distribution are integers; compare exactly.
    assert_array_equal(np.asarray(actual), expected)


@pytest.mark.parametrize("low, high", [(0, 4), (-2, 1), (3, 3)])
def test_discrete_uniform_icdf_at_zero_is_low(low, high):
    # u = 0 must map into the support (to ``low``), not to ``low - 1``.
    d = dist.DiscreteUniform(low, high)
    assert_array_equal(np.asarray(d.icdf(0.0)), low)


@pytest.mark.parametrize("low, high", [(0, 4), (-2, 1), (10, 16)])
def test_discrete_uniform_inverse_transform_is_balanced(low, high):
    # A stratified (quasi-random) grid of u in [0, 1) must use every category
    # exactly equally often and stay inside the support.
    n = high - low + 1
    reps = 50
    u = (jnp.arange(n * reps) + 0.5) / (n * reps)
    values = np.asarray(dist.DiscreteUniform(low, high).icdf(u))
    assert_array_equal(values, np.round(values))
    assert values.min() >= low and values.max() <= high
    counts = np.bincount((values - low).astype(int), minlength=n)
    assert_array_equal(counts, np.full(n, reps))
    # cdf(icdf(u)) >= u (definition of the generalized inverse).
    cdf = np.asarray(dist.DiscreteUniform(low, high).cdf(values))
    assert np.all(cdf >= np.asarray(u) - 1e-6)  # 1e-6: float32 rounding of u
