import numpy as np
from numpy.testing import assert_allclose

import statsmodels.api as sm


def test_pseudo_rsquared_cs_freq_weights():
    # aggregated data with frequency weights must give the same Cox-Snell
    # pseudo R-squared as the expanded individual-level data
    rng = np.random.default_rng(12345)
    n_groups = 20
    x = rng.normal(size=n_groups)
    exog = sm.add_constant(x)
    freq = rng.integers(1, 15, size=n_groups)
    endog = (rng.uniform(size=n_groups) < 1 / (1 + np.exp(-x))).astype(float)

    res_w = sm.GLM(
        endog, exog, family=sm.families.Binomial(), freq_weights=freq
    ).fit()

    endog_e = np.repeat(endog, freq)
    exog_e = np.repeat(exog, freq, axis=0)
    res_e = sm.GLM(endog_e, exog_e, family=sm.families.Binomial()).fit()

    assert_allclose(res_w.params, res_e.params, rtol=1e-8)
    assert_allclose(res_w.llf, res_e.llf, rtol=1e-8)
    assert_allclose(res_w.llnull, res_e.llnull, rtol=1e-8)
    assert_allclose(
        res_w.pseudo_rsquared(kind="mcf"),
        res_e.pseudo_rsquared(kind="mcf"),
        rtol=1e-8,
    )
    assert_allclose(
        res_w.pseudo_rsquared(kind="cs"),
        res_e.pseudo_rsquared(kind="cs"),
        rtol=1e-8,
    )
