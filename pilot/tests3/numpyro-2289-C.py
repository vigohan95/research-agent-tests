import numpy as np
from numpy.testing import assert_allclose

import jax.numpy as jnp

import numpyro.distributions as dist


def test_discrete_uniform_icdf_integer_and_in_support():
    d = dist.DiscreteUniform(2, 5)  # support {2, 3, 4, 5}
    q = jnp.array([0.0, 0.1, 0.25, 0.3, 0.5, 0.6, 0.75, 0.9, 1.0])
    x = np.asarray(d.icdf(q))
    expected = np.array([2, 2, 2, 3, 3, 4, 4, 5, 5])
    assert_allclose(x, expected)
    assert np.all(x == np.round(x))
    assert np.all((x >= 2) & (x <= 5))


def test_discrete_uniform_icdf_inverse_transform_balanced():
    d = dist.DiscreteUniform(-1, 3)  # 5 categories
    # stratified (quasi-random-like) uniforms, avoiding exact boundaries
    q = (jnp.arange(1000) + 0.5) / 1000
    x = np.asarray(d.icdf(q))
    values, counts = np.unique(x, return_counts=True)
    assert_allclose(values, np.arange(-1, 4))
    assert np.all(counts == 200)


def test_discrete_uniform_icdf_consistent_with_cdf():
    d = dist.DiscreteUniform(jnp.array([0, 3]), jnp.array([4, 10]))
    q = jnp.linspace(0.01, 0.99, 37)[:, None]
    x = d.icdf(q)
    # generalized inverse: F(x) >= q and F(x - 1) < q
    assert np.all(np.asarray(d.cdf(x)) >= np.asarray(q) - 1e-6)
    assert np.all(np.asarray(d.cdf(x - 1)) < np.asarray(q))
