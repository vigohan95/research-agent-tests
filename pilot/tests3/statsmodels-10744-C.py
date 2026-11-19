import numpy as np
from numpy.testing import assert_allclose

from statsmodels.regression.linear_model import OLS
from statsmodels.tools.tools import add_constant


def test_prediction_cluster_uses_inference_df():
    rng = np.random.default_rng(12345)
    n_groups, n_per = 10, 20
    groups = np.repeat(np.arange(n_groups), n_per)
    x = rng.normal(size=(n_groups * n_per, 2))
    exog = add_constant(x)
    endog = exog.sum(1) + rng.normal(size=n_groups)[groups] + rng.normal(
        size=len(groups))
    res = OLS(endog, exog).fit(cov_type="cluster",
                               cov_kwds={"groups": groups}, use_t=True)
    assert res.df_resid_inference == n_groups - 1

    ex = np.array([[1.0, 0.5, -0.3], [1.0, -1.0, 2.0]])
    pred = res.get_prediction(ex)
    ci = pred.conf_int(alpha=0.05)

    for i in range(ex.shape[0]):
        tt = res.t_test(ex[i:i + 1])
        ci_tt = np.asarray(tt.conf_int(alpha=0.05)).ravel()
        assert_allclose(ci[i], ci_tt, rtol=1e-10)
    assert_allclose(pred.se_mean, np.sqrt(np.diag(ex @ res.cov_params() @
                                                  ex.T)), rtol=1e-10)
    assert pred.df == n_groups - 1
