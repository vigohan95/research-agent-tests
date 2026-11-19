"""Regression test: OLS dispersion must use the rank of the design.

A two-group design written as one indicator column per group plus an
intercept is rank deficient; the group-difference t statistic must still
match the classical two-sample t-test (scipy.stats.ttest_ind).
"""

import numpy as np
import pytest
from scipy import stats

from nilearn.glm.regression import OLSModel


@pytest.mark.parametrize("with_intercept", [False, True])
def test_two_sample_ttest_matches_scipy(with_intercept):
    rng = np.random.default_rng(0)
    n1, n2, n_voxels = 7, 9, 5
    y1 = rng.standard_normal((n1, n_voxels)) + 0.5
    y2 = rng.standard_normal((n2, n_voxels))
    Y = np.vstack([y1, y2])

    g1 = np.r_[np.ones(n1), np.zeros(n2)]
    g2 = 1 - g1
    columns = [g1, g2]
    if with_intercept:
        columns.append(np.ones(n1 + n2))
    design = np.column_stack(columns)
    contrast = np.zeros(design.shape[1])
    contrast[:2] = [1, -1]

    model = OLSModel(design)
    results = model.fit(Y)
    t_glm = results.Tcontrast(contrast).t.ravel()

    expected = stats.ttest_ind(y1, y2, axis=0, equal_var=True)
    np.testing.assert_allclose(t_glm, expected.statistic, rtol=1e-10)
    assert results.df_residuals == n1 + n2 - 2
    # dispersion is the pooled variance of the two-sample t-test
    pooled = (
        (n1 - 1) * y1.var(axis=0, ddof=1) + (n2 - 1) * y2.var(axis=0, ddof=1)
    ) / (n1 + n2 - 2)
    np.testing.assert_allclose(results.dispersion, pooled, rtol=1e-10)
