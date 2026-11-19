"""
Regression tests for the degrees of freedom used by ``get_prediction`` with
t-based inference.

The confidence interval of the predicted mean at ``x0`` is the confidence
interval of the linear contrast ``x0 @ params``, so it must agree with
``t_test(x0)``, which uses ``df_resid_inference`` (number of clusters minus
one for cluster robust covariances) when it is defined.
"""
import numpy as np
from numpy.testing import assert_allclose
import pytest
from scipy import stats

from statsmodels.regression.linear_model import OLS, WLS


@pytest.fixture
def data():
    rng = np.random.default_rng(10744)
    n_groups, n_per = 10, 30
    groups = np.repeat(np.arange(n_groups), n_per)
    nobs = groups.shape[0]
    x = rng.standard_normal((nobs, 2))
    exog = np.column_stack([np.ones(nobs), x])
    endog = (
        exog @ np.array([1.0, 0.5, -0.3])
        + rng.standard_normal(n_groups)[groups]
        + rng.standard_normal(nobs)
    )
    weights = rng.uniform(0.5, 2.0, size=nobs)
    return endog, exog, groups, weights


FIT_KWDS = [
    ("cluster", "groups"),
    ("HC1", None),
    ("nonrobust", None),
]


@pytest.mark.parametrize("model_class", [OLS, WLS])
@pytest.mark.parametrize("cov_type, cov_kwds", FIT_KWDS)
def test_prediction_df_matches_t_test(data, model_class, cov_type, cov_kwds):
    endog, exog, groups, weights = data
    kwds = {"weights": weights} if model_class is WLS else {}
    fit_kwds = {"groups": groups} if cov_kwds == "groups" else None
    res = model_class(endog, exog, **kwds).fit(
        cov_type=cov_type, cov_kwds=fit_kwds, use_t=True
    )
    expected_df = getattr(res, "df_resid_inference", res.df_resid)
    if cov_type == "cluster":
        assert expected_df == 9

    x0 = np.array([[1.0, 0.7, -1.2], [1.0, -0.4, 0.3]])
    pred = res.get_prediction(x0)
    assert pred.df == expected_df

    ci_pred = pred.conf_int(alpha=0.05)
    for i in range(x0.shape[0]):
        tt = res.t_test(x0[i])
        assert_allclose(ci_pred[i], tt.conf_int(alpha=0.05)[0], rtol=1e-10)

    # closed form interval with the t quantile of the inference df
    se = pred.se_mean
    q = stats.t.ppf(0.975, expected_df)
    expected = np.column_stack(
        [pred.predicted_mean - q * se, pred.predicted_mean + q * se]
    )
    assert_allclose(ci_pred, expected, rtol=1e-10)

    # summary frame uses the same interval
    sf = pred.summary_frame(alpha=0.05)
    assert_allclose(sf[["mean_ci_lower", "mean_ci_upper"]].to_numpy(), expected,
                    rtol=1e-10)
