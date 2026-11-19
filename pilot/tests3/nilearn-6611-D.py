"""Regression tests for dispersion estimation with rank-deficient designs."""

import numpy as np
import pandas as pd
import pytest
from nibabel import Nifti1Image
from numpy.testing import assert_allclose
from scipy import stats

from nilearn.glm.regression import OLSModel
from nilearn.glm.second_level import SecondLevelModel


def _two_groups(n1=10, n2=12, n_voxels=5, seed=0):
    rng = np.random.default_rng(seed)
    Y = rng.standard_normal((n1 + n2, n_voxels))
    Y[:n1] += 0.7
    g1 = np.r_[np.ones(n1), np.zeros(n2)]
    return Y, g1


@pytest.mark.ai_generated
def test_ols_dispersion_uses_rank_for_rank_deficient_design():
    """Redundant intercept must not change dispersion or t statistics."""
    Y, g1 = _two_groups()
    n = Y.shape[0]
    X_full = np.c_[g1, 1 - g1]
    X_redundant = np.c_[g1, 1 - g1, np.ones(n)]

    res_full = OLSModel(X_full).fit(Y)
    res_red = OLSModel(X_redundant).fit(Y)

    assert res_red.df_residuals == n - 2
    assert_allclose(res_red.dispersion, res_red.SSE / (n - 2))
    assert_allclose(res_red.dispersion, res_full.dispersion)

    t_full = res_full.Tcontrast([1, -1]).t
    t_red = res_red.Tcontrast([1, -1, 0]).t
    assert_allclose(t_red, t_full)


@pytest.mark.ai_generated
def test_second_level_group_difference_matches_two_sample_ttest():
    """Group indicators + intercept gives the same t as a two-sample t-test."""
    n1, n2 = 10, 12
    n = n1 + n2
    rng = np.random.default_rng(1)
    data = rng.standard_normal((n, 3, 3, 3))
    data[:n1] += 0.7
    affine = np.eye(4)
    imgs = [Nifti1Image(d, affine) for d in data]
    mask = Nifti1Image(np.ones((3, 3, 3), dtype="uint8"), affine)
    g1 = np.r_[np.ones(n1), np.zeros(n2)]
    design = pd.DataFrame({"g1": g1, "g2": 1 - g1, "intercept": np.ones(n)})

    model = SecondLevelModel(mask_img=mask).fit(imgs, design_matrix=design)
    t_map = model.compute_contrast("g1 - g2", output_type="stat")

    expected = stats.ttest_ind(
        data[:n1].reshape(n1, -1), data[n1:].reshape(n2, -1)
    ).statistic
    assert_allclose(t_map.get_fdata().ravel(), expected, rtol=1e-6)
