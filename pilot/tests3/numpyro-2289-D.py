# Copyright Contributors to the Pyro project.
# SPDX-License-Identifier: Apache-2.0

import numpy as np
from numpy.testing import assert_allclose
import pytest

import numpyro.distributions as dist


@pytest.mark.parametrize("low, high", [(0, 1), (0, 4), (-3, 2), (5, 9)])
def test_discrete_uniform_icdf_integer_and_balanced(low, high):
    d = dist.DiscreteUniform(low, high)
    n = 1000
    # stratified "quasi-random" points in (0, 1)
    q = (np.arange(n) + 0.5) / n
    k = np.asarray(d.icdf(q))
    # integer-valued, inside the support
    assert_allclose(k, np.round(k))
    assert k.min() >= low and k.max() <= high
    # every category used equally often
    counts = np.array([(k == v).sum() for v in range(low, high + 1)])
    assert counts.sum() == n
    assert counts.max() - counts.min() <= 1


@pytest.mark.parametrize("low, high", [(0, 4), (-3, 2)])
def test_discrete_uniform_icdf_is_cdf_inverse(low, high):
    d = dist.DiscreteUniform(low, high)
    values = np.arange(low, high + 1)
    # icdf(cdf(k)) == k on the support
    assert_allclose(np.asarray(d.icdf(d.cdf(values))), values)
    # edge quantiles map to the support endpoints
    assert_allclose(np.asarray(d.icdf(np.array([0.0, 1.0]))), [low, high])
