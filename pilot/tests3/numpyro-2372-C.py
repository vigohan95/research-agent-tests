import numpy as np
import pytest

import jax
import jax.numpy as jnp

import numpyro.distributions as dist
from numpyro.distributions.transforms import SimplexToOrderedTransform


@pytest.mark.parametrize("anchor", [0.0, 1.5, -2.0, np.array([0.7, -0.3])])
def test_simplex_to_ordered_logdet_matches_autodiff(anchor):
    x = jnp.array([[0.3, 0.1, 0.4, 0.2], [0.1, 0.2, 0.3, 0.4]])
    t = SimplexToOrderedTransform(anchor)
    y = t(x)
    actual = t.log_abs_det_jacobian(x, y)
    # Jacobian of the map on the free coordinates x[..., :-1]
    expected = []
    a = jnp.broadcast_to(jnp.asarray(anchor), (2,))
    for i in range(2):
        f = lambda z, i=i: SimplexToOrderedTransform(a[i])(
            jnp.concatenate([z, 1 - z.sum(keepdims=True)])
        )
        jac = jax.jacobian(f)(x[i, :-1])
        expected.append(jnp.linalg.slogdet(jac)[1])
    np.testing.assert_allclose(actual, jnp.stack(expected), rtol=1e-5, atol=1e-5)


def test_induced_prior_shift_invariant():
    base = dist.Dirichlet(jnp.ones(4))
    x = jnp.array([0.3, 0.1, 0.4, 0.2])
    y0 = SimplexToOrderedTransform(0.0)(x)
    d0 = dist.TransformedDistribution(base, SimplexToOrderedTransform(0.0))
    d1 = dist.TransformedDistribution(base, SimplexToOrderedTransform(2.5))
    np.testing.assert_allclose(d0.log_prob(y0), d1.log_prob(y0 + 2.5), rtol=1e-5)
