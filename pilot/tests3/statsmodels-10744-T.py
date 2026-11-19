"""
Prediction intervals with t-based inference must use the same degrees of
freedom as ``t_test``.  For cluster-robust covariances that is
``df_resid_inference = n_groups - 1``, not ``df_resid``.
"""
import numpy as np
from numpy.testing import assert_allclose
import pytest
from scipy import stats

from statsmodels.discrete.discrete_model import Poisson
from statsmodels.genmod.families import Gaussian
from statsmodels.genmod.generalized_linear_model import GLM
from statsmodels.regression.linear_model import OLS


N_GROUPS = 10


@pytest.fixture(scope="module")
def data():
    rng = np.random.default_rng(10744)
    nobs = 200
    groups = np.repeat(np.arange(N_GROUPS), nobs // N_GROUPS)
    x = rng.normal(size=nobs)
    exog = np.column_stack([np.ones(nobs), x])
    y = 1 + 0.5 * x + rng.normal(size=N_GROUPS)[groups] + rng.normal(size=nobs)
    y_count = rng.poisson(np.exp(0.2 + 0.3 * x))
    return y, y_count, exog, groups


def _fit(model_name, cov, data):
    y, y_count, exog, groups = data
    if cov == "cluster":
        kw = dict(cov_type="cluster", cov_kwds={"groups": groups})
    else:
        kw = dict(cov_type="HC0")
    if model_name == "ols":
        return OLS(y, exog).fit(use_t=True, **kw)
    if model_name == "glm":
        return GLM(y, exog, family=Gaussian()).fit(use_t=True, **kw)
    return Poisson(y_count, exog).fit(disp=False, use_t=True, **kw)


@pytest.mark.parametrize("cov", ["cluster", "HC0"])
@pytest.mark.parametrize(
    "model_name, which",
    [
        ("ols", None),
        ("glm", None),
        ("glm", "mean"),
        ("glm", "linear"),
        ("poisson", "mean"),
    ],
)
def test_prediction_ci_matches_t_test(data, model_name, which, cov):
    res = _fit(model_name, cov, data)
    expected_df = N_GROUPS - 1 if cov == "cluster" else res.df_resid
    exog_new = np.array([[1.0, 0.3], [1.0, -1.2]])

    kwds = {} if which is None else {"which": which}
    pred = res.get_prediction(exog_new, **kwds)
    ci = np.asarray(pred.conf_int(alpha=0.05))

    # Hand computation via a linear contrast test on the linear predictor.
    tt = res.t_test(exog_new)
    assert_allclose(tt.df_denom, expected_df, rtol=1e-12)
    q = stats.t.ppf(0.975, expected_df)
    se_lin = np.sqrt(np.diag(exog_new @ res.cov_params() @ exog_new.T))
    linpred = exog_new @ res.params
    lin_ci = np.column_stack([linpred - q * se_lin, linpred + q * se_lin])

    if model_name == "poisson":
        # default interval for the mean transforms the endpoints of the
        # interval of the linear predictor with the inverse link exp
        expected = np.exp(lin_ci)
    else:
        # identity link: interval for the mean equals the contrast interval
        expected = lin_ci
        assert_allclose(ci, np.asarray(tt.conf_int(alpha=0.05)), rtol=1e-10)
    assert_allclose(ci, expected, rtol=1e-10)
