"""Regression tests for contiguous events in high-resolution regressors."""

import numpy as np
import pandas as pd
import pytest

from nilearn.glm.first_level import make_first_level_design_matrix
from nilearn.glm.first_level.hemodynamic_models import (
    _sample_condition,
    compute_regressor,
)


def _one_event_per_volume(t_r, n_scans):
    frame_times = np.arange(n_scans) * t_r
    exp_condition = (
        frame_times.copy(),
        np.full(n_scans, t_r),
        np.ones(n_scans),
    )
    return frame_times, exp_condition


@pytest.mark.ai_generated
@pytest.mark.parametrize("n_scans", [100, 333, 400])
def test_sample_condition_contiguous_events_no_gaps(n_scans):
    """Back-to-back events must give a gapless, non-overlapping boxcar.

    The offset of event i (onset_i + duration) and the onset of event i + 1
    can differ by floating point error only; they must map to the same
    high-resolution sample.
    """
    t_r = 0.3
    frame_times, exp_condition = _one_event_per_volume(t_r, n_scans)

    regressor, frame_times_high_res = _sample_condition(
        exp_condition, frame_times, oversampling=50, min_onset=-24
    )

    inside = (frame_times_high_res >= frame_times[0]) & (
        frame_times_high_res < frame_times[-1]
    )
    np.testing.assert_allclose(regressor[inside], 1.0)


@pytest.mark.ai_generated
@pytest.mark.parametrize("hrf_model", ["glover", "spm"])
@pytest.mark.parametrize("n_scans", [333, 400])
def test_compute_regressor_constant_trace_is_flat(hrf_model, n_scans):
    """A constant trace entered as one event per volume gives a flat
    regressor once the HRF has fully risen."""
    t_r = 0.3
    frame_times, exp_condition = _one_event_per_volume(t_r, n_scans)

    regressor, _ = compute_regressor(exp_condition, hrf_model, frame_times)

    steady = (frame_times > 40) & (frame_times < frame_times[-1] - 2)
    np.testing.assert_allclose(regressor[steady, 0], 1.0, atol=1e-8)


@pytest.mark.ai_generated
def test_design_matrix_constant_trace_is_flat():
    """Same check through the public design matrix API."""
    t_r, n_scans = 0.3, 333
    frame_times = np.arange(n_scans) * t_r
    events = pd.DataFrame(
        {
            "onset": frame_times,
            "duration": t_r,
            "trial_type": "physio",
            "modulation": 1.0,
        }
    )

    design = make_first_level_design_matrix(
        frame_times, events, hrf_model="glover", drift_model=None
    )

    steady = (frame_times > 40) & (frame_times < frame_times[-1] - 2)
    np.testing.assert_allclose(
        design["physio"].to_numpy()[steady], 1.0, atol=1e-8
    )
