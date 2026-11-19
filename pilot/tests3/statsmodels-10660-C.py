import numpy as np
from numpy.testing import assert_allclose
import pytest

from statsmodels.stats.rates import confint_poisson_2indep


@pytest.mark.parametrize("method", ["sqrtcc", "waldcc", "score", "mover"])
def test_confint_ratio_scales_with_exposure(method):
    # rate ratio CI must scale by exposure2 / exposure1
    count1, count2 = 41, 15
    ci_eq = confint_poisson_2indep(count1, 1000, count2, 1000, method=method)
    ci = confint_poisson_2indep(count1, 28010, count2, 19017, method=method)
    factor = 19017 / 28010
    assert_allclose(np.asarray(ci), np.asarray(ci_eq) * factor, rtol=1e-6)


def test_confint_ratio_sqrtcc_unequal_exposure():
    count1, exposure1, count2, exposure2 = 41, 28010, 15, 19017
    ratio = (count1 / exposure1) / (count2 / exposure2)
    low, upp = confint_poisson_2indep(
        count1, exposure1, count2, exposure2, method="sqrtcc"
    )
    assert low < ratio < upp
    low_s, upp_s = confint_poisson_2indep(
        count1, exposure1, count2, exposure2, method="score"
    )
    assert_allclose([low, upp], [low_s, upp_s], rtol=0.1)
