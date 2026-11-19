"""
Regression test: Cox-Snell pseudo R-squared of a GLM fit with freq_weights
must match the fit on the equivalent expanded (one row per unit) data.
"""

import numpy as np
from numpy.testing import assert_allclose
import pytest

import statsmodels.api as sm


@pytest.fixture
def aggregated_and_expanded():
    rng = np.random.default_rng(10684)
    n_rows = 40
    x = rng.normal(size=n_rows)
    exog = sm.add_constant(x)
    prob = 1 / (1 + np.exp(-(0.3 + 0.8 * x)))
    endog = (rng.uniform(size=n_rows) < prob).astype(float)
    freq = rng.integers(1, 8, size=n_rows).astype(float)

    res_agg = sm.GLM(
        endog, exog, family=sm.families.Binomial(), freq_weights=freq
    ).fit()

    idx = np.repeat(np.arange(n_rows), freq.astype(int))
    res_exp = sm.GLM(endog[idx], exog[idx], family=sm.families.Binomial()).fit()
    return res_agg, res_exp


def test_freq_weights_pseudo_rsquared_matches_expanded(aggregated_and_expanded):
    res_agg, res_exp = aggregated_and_expanded

    # sanity: the two fits are the same model
    assert_allclose(res_agg.params, res_exp.params, rtol=1e-8)
    assert_allclose(res_agg.llf, res_exp.llf, rtol=1e-8)
    assert_allclose(res_agg.llnull, res_exp.llnull, rtol=1e-8)

    for kind in ["cs", "mcf"]:
        assert_allclose(
            res_agg.pseudo_rsquared(kind),
            res_exp.pseudo_rsquared(kind),
            rtol=1e-8,
        )

    # closed form with nobs equal to the total frequency weight
    n = res_exp.nobs
    expected = 1 - np.exp(2 * (res_exp.llnull - res_exp.llf) / n)
    assert_allclose(res_agg.pseudo_rsquared("cs"), expected, rtol=1e-8)
