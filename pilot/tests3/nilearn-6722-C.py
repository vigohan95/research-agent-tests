"""Regression tests: back-to-back events must tile the high-res regressor.

A continuous trace entered as one event per volume (duration = TR) should
produce a gap-free, overlap-free boxcar, so a constant trace gives a flat
regressor after convolution.
"""

import numpy as np
import pytest

from nilearn.glm.first_level.hemodynamic_models import (
    _sample_condition,
    compute_regressor,
)


@pytest.mark.parametrize("t_r, n_scans", [(0.8, 200), (0.8, 300)])
@pytest.mark.parametrize("oversampling", [50])
def test_contiguous_events_give_constant_high_res_regressor(
    t_r, n_scans, oversampling
):
    frame_times = np.arange(n_scans) * t_r
    condition = np.vstack(
        [frame_times, np.full(n_scans, t_r), np.ones(n_scans)]
    )

    regressor, frame_times_high_res = _sample_condition(
        condition, frame_times, oversampling
    )

    covered = (frame_times_high_res >= 0) & (
        frame_times_high_res < frame_times[-1]
    )
    np.testing.assert_array_equal(regressor[covered], 1.0)


@pytest.mark.parametrize("t_r", [0.5, 0.72, 0.8, 1.3, 2.0, 2.5])
@pytest.mark.parametrize("n_scans", [157, 200, 300])
def test_constant_trace_gives_flat_convolved_regressor(t_r, n_scans):
    frame_times = np.arange(n_scans) * t_r
    condition = np.vstack(
        [frame_times, np.full(n_scans, t_r), np.ones(n_scans)]
    )

    regressor, _ = compute_regressor(condition, "spm", frame_times)

    # skip the initial HRF rise (~32 s) and the final sample
    steady = regressor[int(np.ceil(40 / t_r)) : -1, 0]
    np.testing.assert_allclose(steady, steady[0], rtol=0, atol=1e-8)
