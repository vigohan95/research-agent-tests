import numpy as np
from numpy.testing import assert_allclose
import pytest
from scipy import stats

from statsmodels.stats.rates import confint_poisson_2indep


@pytest.mark.parametrize("exposure1", [5000.0, 20000.0, 123.4])
def test_sqrtcc_ratio_uses_exposures(exposure1):
    # the sqrtcc interval for the rate ratio ignored the exposures and
    # returned an interval for the ratio of counts
    count1, count2, exposure2 = 60, 30, 5000.0
    ratio = count1 / exposure1 / (count2 / exposure2)
    low, upp = confint_poisson_2indep(
        count1, exposure1, count2, exposure2, method="sqrtcc", compare="ratio"
    )
    assert low < ratio < upp

    # equivariance: the interval scales with exposure2 / exposure1
    low0, upp0 = confint_poisson_2indep(
        count1, 1.0, count2, 1.0, method="sqrtcc", compare="ratio"
    )
    assert_allclose([low, upp], np.array([low0, upp0]) * exposure2 / exposure1)

    # close to the other methods
    ci_score = confint_poisson_2indep(
        count1, exposure1, count2, exposure2, method="score", compare="ratio"
    )
    assert_allclose([low, upp], ci_score, rtol=0.05)


def test_sqrtcc_ratio_closed_form():
    # Price, Bonett (2000) eq. (2.4): the bounds r**2 of the count ratio solve
    # (sqrt(a) - r sqrt(b))**2 = z**2 / 4 * (1 + r**2), a = y1 + 0.5,
    # b = y2 + 0.5, and the rate ratio bound is r**2 * n2 / n1
    count1, n1, count2, n2 = 60, 51477.5, 30, 54308.7
    a, b = count1 + 0.5, count2 + 0.5
    z = stats.norm.isf(0.025)
    low, upp = confint_poisson_2indep(
        count1, n1, count2, n2, method="sqrtcc", compare="ratio", alpha=0.05
    )
    for bound in (low, upp):
        r = np.sqrt(bound * n1 / n2)
        lhs = (np.sqrt(a) - r * np.sqrt(b)) ** 2
        assert_allclose(lhs, z**2 / 4 * (1 + r**2), rtol=1e-10)
