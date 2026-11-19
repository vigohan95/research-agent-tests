import numpy as np
import pytest

import jax
import jax.numpy as jnp

from numpyro.distributions.transforms import SimplexToOrderedTransform


@pytest.mark.parametrize("anchor", [0.0, 1.5, -2.0, np.array([0.5, -1.0])])
def test_simplex_to_ordered_logdet_matches_autodiff(anchor):
    # batch of 2 simplices of size 4 -> 3 ordered cutpoints each
    x = jnp.array([[0.3, 0.1, 0.4, 0.2], [0.1, 0.2, 0.3, 0.4]])
    t = SimplexToOrderedTransform(jnp.asarray(anchor))
    y = t(x)
    actual = t.log_abs_det_jacobian(x, y)

    # Reference: log|det dy/ds| where s = cumsum(x[:-1]) are the free coords
    # of the simplex (unit-triangular map x -> s has det 1).
    def f(s, a):
        return jax.scipy.special.logit(s) + a

    s = jnp.cumsum(x[..., :-1], axis=-1)
    anchors = jnp.broadcast_to(jnp.asarray(anchor), (2,))
    expected = jnp.stack(
        [
            jnp.linalg.slogdet(jax.jacobian(f)(s[i], anchors[i]))[1]
            for i in range(2)
        ]
    )
    # closed form: -sum log(s (1 - s)), independent of the anchor
    closed = -jnp.sum(jnp.log(s) + jnp.log1p(-s), axis=-1)
    np.testing.assert_allclose(actual, expected, rtol=1e-5)
    np.testing.assert_allclose(actual, closed, rtol=1e-5)


def test_simplex_to_ordered_logdet_shift_invariant():
    x = jnp.array([0.3, 0.1, 0.4, 0.2])
    t0 = SimplexToOrderedTransform(0.0)
    t1 = SimplexToOrderedTransform(3.0)
    np.testing.assert_allclose(
        t1.log_abs_det_jacobian(x, t1(x)), t0.log_abs_det_jacobian(x, t0(x)), rtol=1e-6
    )
