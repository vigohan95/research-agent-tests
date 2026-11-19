"""
Regression tests for the chi-square version of McNemar's test.

With the continuity correction, |n1 - n2| - 1 must not go negative:
balanced tables (n1 == n2) gave a positive statistic, and a table with
no discordant pairs divided by zero and returned p = 0.

Reference values: R ``mcnemar.test`` (correct=TRUE applies the Yates
correction only when the table is asymmetric, so balanced tables give
statistic 0, p-value 1), and the closed form
(max(|b - c| - corr, 0))**2 / (b + c) with chi2(1) tail probabilities.
"""
import numpy as np
from numpy.testing import assert_allclose
import pytest
from scipy import stats

from statsmodels.stats.contingency_tables import mcnemar


@pytest.mark.parametrize("correction", [True, False])
@pytest.mark.parametrize(
    "table",
    [
        [[10, 5], [5, 20]],  # balanced discordant counts
        [[3, 1], [1, 7]],  # balanced, small counts
        [[12, 0], [0, 30]],  # no discordant pairs at all
        [[12, 2.5], [2, 30]],  # |b - c| < 1, correction would overshoot
    ],
)
def test_mcnemar_chi2_no_evidence(table, correction):
    res = mcnemar(table, exact=False, correction=correction)
    if correction or table[0][1] == table[1][0]:
        assert_allclose(res.statistic, 0.0, rtol=0, atol=0)
        assert_allclose(res.pvalue, 1.0, rtol=1e-12)
    else:
        # uncorrected, |b - c| = 0.5: closed form 0.25 / 4.5
        stat = 0.25 / 4.5
        assert_allclose(res.statistic, stat, rtol=1e-12)
        assert_allclose(res.pvalue, stats.chi2.sf(stat, 1), rtol=1e-12)
    assert np.isfinite(res.statistic)

    # integer tables agree with the exact test: no evidence of a difference
    if float(table[0][1]).is_integer():
        res_exact = mcnemar(table, exact=True)
        assert_allclose(res_exact.pvalue, 1.0, rtol=1e-12)


@pytest.mark.parametrize(
    "correction, statistic, pvalue",
    [
        # R: mcnemar.test(matrix(c(20, 4, 10, 30), 2), correct=TRUE)
        # McNemar's chi-squared = 1.7857, p-value = 0.1814
        (True, 25 / 14, 0.18144),
        # R: mcnemar.test(matrix(c(20, 4, 10, 30), 2), correct=FALSE)
        # McNemar's chi-squared = 2.5714, p-value = 0.1088
        (False, 36 / 14, 0.10880),
    ],
)
def test_mcnemar_chi2_unbalanced_unchanged(correction, statistic, pvalue):
    res = mcnemar([[20, 10], [4, 30]], exact=False, correction=correction)
    assert_allclose(res.statistic, statistic, rtol=1e-12)
    # R values printed to 4 significant digits
    assert_allclose(res.pvalue, pvalue, rtol=5e-4)
