# Regression test: InverseWishart.variance for off-diagonal entries.
import numpy as np
import pytest
from scipy.stats import invwishart

import numpyro.distributions as dist

PSI = np.array([[2.0, 0.6, -0.3], [0.6, 1.5, 0.4], [-0.3, 0.4, 1.0]])


@pytest.mark.parametrize("df", [6.5, 7.0, 10.0, 50.0])
@pytest.mark.parametrize("param", ["scale_matrix", "rate_matrix", "scale_tril"])
def test_inverse_wishart_variance_matches_scipy(df, param):
    if param == "scale_matrix":
        d = dist.InverseWishart(df, scale_matrix=PSI)
    elif param == "rate_matrix":
        d = dist.InverseWishart(df, rate_matrix=np.linalg.inv(PSI))
    else:
        d = dist.InverseWishart(df, scale_tril=np.linalg.cholesky(PSI))
    expected = invwishart(df=df, scale=PSI).var()
    actual = np.asarray(d.variance)
    # Off-diagonal entries are where the bug was; check them explicitly too.
    off = ~np.eye(3, dtype=bool)
    np.testing.assert_allclose(actual[off], expected[off], rtol=1e-5)
    np.testing.assert_allclose(actual, expected, rtol=1e-5)


def test_inverse_wishart_variance_batched():
    dfs = np.array([6.5, 9.0, 20.0])
    d = dist.InverseWishart(dfs, scale_matrix=np.broadcast_to(PSI, (3, 3, 3)))
    expected = np.stack([invwishart(df=v, scale=PSI).var() for v in dfs])
    np.testing.assert_allclose(np.asarray(d.variance), expected, rtol=1e-5)


def test_inverse_wishart_variance_nan_below_threshold():
    # Variance is undefined (infinite) for nu <= p + 3.
    d = dist.InverseWishart(5.5, scale_matrix=PSI)
    assert np.all(np.isnan(np.asarray(d.variance)))
