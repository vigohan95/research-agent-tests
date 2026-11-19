"""Regression test: crop(reset_first_samp=True) must keep annotations aligned."""

from datetime import datetime, timezone

import numpy as np
import pytest
from numpy.testing import assert_allclose, assert_array_equal

import mne
from mne import Annotations, Epochs, events_from_annotations
from mne.io import RawArray


@pytest.mark.parametrize("meas_date", [None, datetime(2020, 1, 1, tzinfo=timezone.utc)])
@pytest.mark.parametrize("first_samp", [0, 37])
def test_crop_reset_first_samp_keeps_annotations(meas_date, first_samp):
    """Events from annotations must hit the same samples after reset."""
    sfreq = 100.0
    n_times = 2000
    rng = np.random.default_rng(0)
    data = rng.standard_normal((1, n_times)) * 1e-6
    onsets_samp = np.array([500, 800, 1100, 1400])
    for s in onsets_samp:
        data[0, s : s + 10] += 1e-3  # clear evoked response at each stim
    info = mne.create_info(["EEG 001"], sfreq, "eeg")
    raw = RawArray(data, info, first_samp=first_samp, verbose=False)
    raw.set_meas_date(meas_date)
    raw.set_annotations(
        Annotations(onsets_samp / sfreq, 0.0, ["stim"] * len(onsets_samp))
    )

    tmin_crop = 2.0
    ref = raw.copy().crop(tmin=tmin_crop)
    reset = raw.copy().crop(tmin=tmin_crop, reset_first_samp=True)
    assert reset.first_samp == 0
    assert_allclose(reset.get_data(), ref.get_data())

    ev_ref, _ = events_from_annotations(ref, verbose=False)
    ev_reset, _ = events_from_annotations(reset, verbose=False)
    assert len(ev_reset) == len(onsets_samp)
    # Positions relative to the start of the (cropped) data must match
    assert_array_equal(
        ev_reset[:, 0] - reset.first_samp, ev_ref[:, 0] - ref.first_samp
    )
    assert_array_equal(
        ev_reset[:, 0], onsets_samp - int(round(tmin_crop * sfreq))
    )

    kw = dict(tmin=-0.05, tmax=0.2, baseline=None, preload=True, verbose=False)
    evk_ref = Epochs(ref, ev_ref, **kw).average()
    evk_reset = Epochs(reset, ev_reset, **kw).average()
    assert_allclose(evk_reset.data, evk_ref.data)
