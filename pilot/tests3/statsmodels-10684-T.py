"""
Regression test: GLM Cox-Snell pseudo R-squared with freq_weights must use
the number of (weighted) observations, i.e. sum of freq_weights, so that
an aggregated fit agrees with the fit on the expanded individual-level data.
"""
import numpy as np
from numpy.testing import assert_allclose
import pytest

import statsmodels.api as sm


def _data():
    # aggregated binary data: covariate x, outcome y, count of respondents
    x = np.array([0.0, 0.0, 1.0, 1.0, 2.0, 2.0, 3.0, 3.0])
    y = np.array([0.0, 1.0, 0.0, 1.0, 0.0, 1.0, 0.0, 1.0])
    counts = np.array([30, 5, 20, 12, 10, 18, 4, 25])
    return x, y, counts


@pytest.mark.parametrize("kind", ["cs", "mcf"])
def test_pseudo_rsquared_freq_weights_matches_expanded(kind):
    x, y, counts = _data()
    exog = sm.add_constant(x)
    res_agg = sm.GLM(y, exog, family=sm.families.Binomial(),
                     freq_weights=counts).fit()
    exog_exp = np.repeat(exog, counts, axis=0)
    y_exp = np.repeat(y, counts)
    res_exp = sm.GLM(y_exp, exog_exp, family=sm.families.Binomial()).fit()

    assert_allclose(res_agg.llf, res_exp.llf, rtol=1e-10)
    assert_allclose(res_agg.pseudo_rsquared(kind),
                    res_exp.pseudo_rsquared(kind), rtol=1e-8)


def test_pseudo_rsquared_cs_closed_form():
    # Closed form for logistic regression: the null model fits the overall
    # proportion p0; Cox-Snell R2 = 1 - exp(2 (llnull - llf) / N), N = sum
    # of counts.
    x, y, counts = _data()
    exog = sm.add_constant(x)
    res = sm.GLM(y, exog, family=sm.families.Binomial(),
                 freq_weights=counts).fit()
    n = counts.sum()
    p0 = (counts * y).sum() / n
    llnull = n * (p0 * np.log(p0) + (1 - p0) * np.log(1 - p0))
    assert_allclose(res.llnull, llnull, rtol=1e-10)
    expected = 1 - np.exp(2 * (llnull - res.llf) / n)
    assert_allclose(res.pseudo_rsquared("cs"), expected, rtol=1e-10)
