"""Regression tests: back-to-back one-TR events must tile the time axis.

A continuous trace entered as one event per volume (onset = frame time,
duration = TR) is mathematically identical to a single block covering the
whole run when all amplitudes are equal. Floating point errors in the
high resolution grid used to make some events cover one sample more or
less than others, producing a ripple in the convolved regressor.
"""

import numpy as np
import pytest

from nilearn.glm.first_level.hemodynamic_models import (
    _sample_condition,
    compute_regressor,
)

# (t_r, n_scans): with these values some onsets k * t_r and the offsets
# (k - 1) * t_r + t_r of the preceding events differ by floating point
# error around a grid point; 2.0 s / 100 is a control without that issue.
CASES = [(0.6, 100), (0.8, 300), (1.2, 200), (2.0, 100)]


@pytest.mark.parametrize("t_r, n_scans", CASES)
def test_one_tr_events_tile_high_res_grid(t_r, n_scans):
    frame_times = np.arange(n_scans) * t_r
    condition = np.vstack(
        [frame_times, np.full(n_scans, t_r), np.ones(n_scans)]
    )
    regressor, hr_times = _sample_condition(
        condition, frame_times, oversampling=50
    )
    inside = (hr_times >= 0) & (hr_times < frame_times[-1])
    # every sample inside the run is covered by exactly one event
    np.testing.assert_allclose(regressor[inside], 1.0, rtol=1e-12)


@pytest.mark.parametrize("t_r, n_scans", CASES)
def test_constant_trace_equals_single_block(t_r, n_scans):
    frame_times = np.arange(n_scans) * t_r
    per_volume = np.vstack(
        [frame_times, np.full(n_scans, t_r), np.ones(n_scans)]
    )
    block = np.array([[0.0], [n_scans * t_r], [1.0]])
    reg_volumes, _ = compute_regressor(per_volume, "glover", frame_times)
    reg_block, _ = compute_regressor(block, "glover", frame_times)
    np.testing.assert_allclose(reg_volumes, reg_block, rtol=1e-9)
    # after the HRF has risen (32 s kernel) the regressor is flat
    late = reg_volumes[frame_times > 40, 0]
    np.testing.assert_allclose(late, late[0], rtol=1e-9)


def test_off_grid_onsets_rounded_up():
    """Onsets between grid points still map to the next sample."""
    frame_times = np.arange(20) * 2.0
    condition = np.array([[3.013], [1.0], [1.0]])
    regressor, hr_times = _sample_condition(
        condition, frame_times, oversampling=10
    )
    active = hr_times[regressor > 0.5]
    assert active[0] >= 3.013
    assert active[0] - 3.013 < 0.2
    assert active[-1] < 4.013
