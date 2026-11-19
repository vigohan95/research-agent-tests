"""
Regression tests for the chi-square version of the McNemar test when the
off-diagonal (discordant) counts are balanced or absent.

Reference values: R ``mcnemar.test(x, correct=TRUE)`` applies the continuity
correction only if ``any(x - t(x) != 0)``, so for b == c > 0 it reports
statistic 0 and p-value 1, and for b == c == 0 the statistic is 0/0 (NaN).
The exact (binomial) test gives p-value 1 in all of these cases.
"""

import warnings

import numpy as np
from numpy.testing import assert_allclose
import pytest

from statsmodels.stats.contingency_tables import mcnemar


@pytest.mark.parametrize(
    "table",
    [
        [[10, 5], [5, 20]],
        [[0, 1], [1, 0]],
        [[3, 50], [50, 7]],
    ],
)
@pytest.mark.parametrize("correction", [True, False])
def test_mcnemar_chi2_balanced_discordant(table, correction):
    res = mcnemar(table, exact=False, correction=correction)
    assert_allclose(res.statistic, 0.0, atol=1e-15)
    assert_allclose(res.pvalue, 1.0, rtol=1e-12)

    res_exact = mcnemar(table, exact=True)
    assert_allclose(res_exact.pvalue, 1.0, rtol=1e-12)


@pytest.mark.parametrize("correction", [True, False])
def test_mcnemar_chi2_no_discordant(correction):
    # no discordant pairs must not be reported as a significant change
    table = [[12, 0], [0, 8]]
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        res = mcnemar(table, exact=False, correction=correction)
    assert np.isnan(res.statistic)
    assert np.isnan(res.pvalue)

    res_exact = mcnemar(table, exact=True)
    assert_allclose(res_exact.pvalue, 1.0, rtol=1e-12)


def test_mcnemar_chi2_unbalanced_unchanged():
    # R: mcnemar.test(matrix(c(10, 2, 9, 20), 2)) gives
    # McNemar's chi-squared = 3.2727, p-value = 0.07044
    table = [[10, 9], [2, 20]]
    res = mcnemar(table, exact=False, correction=True)
    assert_allclose(res.statistic, (7 - 1) ** 2 / 11, rtol=1e-12)
    assert_allclose(res.pvalue, 0.070440, rtol=1e-4)

    # R: mcnemar.test(matrix(c(10, 2, 9, 20), 2), correct=FALSE)
    res = mcnemar(table, exact=False, correction=False)
    assert_allclose(res.statistic, 49 / 11, rtol=1e-12)

    # difference of exactly 1 is still corrected, as in R
    res = mcnemar([[4, 3], [2, 6]], exact=False, correction=True)
    assert_allclose(res.statistic, 0.0, atol=1e-15)
    assert_allclose(res.pvalue, 1.0, rtol=1e-12)
