import numpy as np
from numpy.testing import assert_allclose
import pytest

from statsmodels.stats.contingency_tables import mcnemar


@pytest.mark.parametrize(
    "table",
    [
        [[10, 5], [5, 20]],
        [[3, 1], [1, 7]],
        [[0, 40], [40, 0]],
        [[12, 0], [0, 30]],
        [[0, 0], [0, 0]],
    ],
)
@pytest.mark.parametrize("correction", [True, False])
def test_mcnemar_chi2_balanced_discordant(table, correction):
    res = mcnemar(table, exact=False, correction=correction)
    assert_allclose(res.statistic, 0.0, atol=1e-14)
    assert_allclose(res.pvalue, 1.0)
    assert np.isfinite(res.statistic)


def test_mcnemar_chi2_unbalanced_unchanged():
    # R: mcnemar.test(matrix(c(10, 2, 9, 20), 2)) -> 3.2727, p = 0.07044
    res = mcnemar([[10, 9], [2, 20]], exact=False, correction=True)
    assert_allclose(res.statistic, (7 - 1) ** 2 / 11.0)
    assert_allclose(res.pvalue, 0.0704404, rtol=1e-5)
    res = mcnemar([[10, 9], [2, 20]], exact=False, correction=False)
    assert_allclose(res.statistic, 49 / 11.0)
