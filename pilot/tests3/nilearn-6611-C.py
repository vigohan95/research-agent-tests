"""Regression tests: rank-deficient designs must use rank-based dof."""

import numpy as np
from numpy.testing import assert_allclose
from scipy import stats

from nilearn.glm.regression import OLSModel


def _group_data():
    rng = np.random.default_rng(0)
    n1, n2 = 7, 9
    Y = np.concatenate(
        [rng.standard_normal((n1, 5)), rng.standard_normal((n2, 5)) + 0.8]
    )
    g1 = np.r_[np.ones(n1), np.zeros(n2)]
    g2 = 1 - g1
    return Y, g1, g2, n1, n2


def test_rank_deficient_group_design_matches_two_sample_ttest():
    Y, g1, g2, n1, n2 = _group_data()
    # indicator per group + redundant intercept: rank 2, 3 columns
    X = np.column_stack([g1, g2, np.ones_like(g1)])
    results = OLSModel(X).fit(Y)
    assert results.df_residuals == n1 + n2 - 2

    con = results.Tcontrast([1, -1, 0])
    expected = stats.ttest_ind(Y[:n1], Y[n1:], axis=0).statistic
    assert_allclose(con.t, expected, rtol=1e-10)
    assert_allclose(results.dispersion, results.MSE, rtol=1e-12)


def test_rank_deficient_design_same_as_full_rank_design():
    Y, g1, g2, _, _ = _group_data()
    full = OLSModel(np.column_stack([g1, g2])).fit(Y)
    redundant = OLSModel(np.column_stack([g1, g2, np.ones_like(g1)])).fit(Y)
    assert_allclose(redundant.dispersion, full.dispersion, rtol=1e-10)
    assert_allclose(
        redundant.Tcontrast([1, -1, 0]).t,
        full.Tcontrast([1, -1]).t,
        rtol=1e-10,
    )
