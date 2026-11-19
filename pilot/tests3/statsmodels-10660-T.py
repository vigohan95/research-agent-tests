"""Regression tests for confint_poisson_2indep(method="sqrtcc", compare="ratio").

The sqrtcc interval (Price and Bonett 2000, eq. 2.4) is the interval for the
ratio of counts; the rate ratio interval has to be rescaled by n2 / n1.
"""

import numpy as np
from numpy.testing import assert_allclose
import pytest
from scipy import stats

from statsmodels.stats.rates import confint_poisson_2indep


def _sqrtcc_closed_form(y1, n1, y2, n2, alpha):
    # Fieller-type inversion of
    # (sqrt(a) - t sqrt(b))**2 = z**2 (1 + t**2) / 4, t = sqrt(count ratio),
    # with a = y1 + 0.5, b = y2 + 0.5, solved as a quadratic in t.
    z = stats.norm.isf(alpha / 2)
    a, b = y1 + 0.5, y2 + 0.5
    qa = b - z**2 / 4
    qb = -2 * np.sqrt(a * b)
    qc = a - z**2 / 4
    roots = np.sort(np.roots([qa, qb, qc]).real)
    return roots**2 * n2 / n1


@pytest.mark.parametrize(
    "y1, n1, y2, n2",
    [
        (41, 28010.0, 15, 19017.0),
        (30, 1000.0, 300, 10000.0),  # very different exposures, ratio ~1
        (12, 50.0, 25, 400.0),
        (7, 3.0, 7, 3.0),  # equal exposures
    ],
)
@pytest.mark.parametrize("alpha", [0.05, 0.1])
def test_sqrtcc_matches_closed_form(y1, n1, y2, n2, alpha):
    ci = confint_poisson_2indep(
        y1, n1, y2, n2, method="sqrtcc", compare="ratio", alpha=alpha
    )
    expected = _sqrtcc_closed_form(y1, n1, y2, n2, alpha)
    assert_allclose(ci, expected, rtol=1e-10)


def test_sqrtcc_depends_on_exposure():
    # reported case: rate ratio about 1.02 with very different person-years
    y1, n1, y2, n2 = 51, 1000.0, 500, 10000.0
    est = (y1 / n1) / (y2 / n2)
    low, upp = confint_poisson_2indep(y1, n1, y2, n2, method="sqrtcc")
    assert low < est < upp
    assert low < 1 < upp

    # agrees with the other methods
    for meth in ["score", "wald-log", "score-log", "waldcc", "mover"]:
        ci = confint_poisson_2indep(y1, n1, y2, n2, method=meth)
        assert_allclose([low, upp], ci, rtol=0.05)

    # scaling exposure of sample 1 scales the rate ratio interval inversely
    low2, upp2 = confint_poisson_2indep(y1, 2 * n1, y2, n2, method="sqrtcc")
    assert_allclose([low2, upp2], [low / 2, upp / 2], rtol=1e-12)
