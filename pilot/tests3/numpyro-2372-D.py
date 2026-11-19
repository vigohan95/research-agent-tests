# Copyright Contributors to the Pyro project.
# SPDX-License-Identifier: Apache-2.0

import numpy as np
import pytest

import jax
import jax.numpy as jnp

import numpyro.distributions as dist
from numpyro.distributions.transforms import SimplexToOrderedTransform


@pytest.mark.parametrize("anchor_point", [0.0, 1.5, -2.0])
def test_simplex_to_ordered_log_det_matches_autodiff(anchor_point):
    x = jnp.array([0.3, 0.1, 0.4, 0.2])
    t = SimplexToOrderedTransform(anchor_point)
    y = t(x)
    # Jacobian of the inverse restricted to the first K-1 simplex coordinates.
    jac = jax.jacobian(lambda y: t.inv(y)[:-1])(y)
    expected = -jnp.linalg.slogdet(jac)[1]
    np.testing.assert_allclose(t.log_abs_det_jacobian(x, y), expected, rtol=1e-5)


def test_simplex_to_ordered_anchor_shift_invariance():
    x = jnp.array([0.3, 0.1, 0.4, 0.2])
    base = dist.Dirichlet(jnp.ones(4))
    d0 = dist.TransformedDistribution(base, SimplexToOrderedTransform(0.0))
    d1 = dist.TransformedDistribution(base, SimplexToOrderedTransform(3.0))
    y0 = SimplexToOrderedTransform(0.0)(x)
    np.testing.assert_allclose(d1.log_prob(y0 + 3.0), d0.log_prob(y0), rtol=1e-5)
