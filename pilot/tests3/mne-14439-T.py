"""Regression test: crop(reset_first_samp=True) must keep annotations aligned."""

from datetime import datetime, timezone

import numpy as np
import pytest
from numpy.testing import assert_allclose, assert_array_equal

from mne import Annotations, Epochs, create_info, events_from_annotations
from mne.io import RawArray


@pytest.mark.parametrize(
    "meas_date", [None, datetime(2020, 1, 1, tzinfo=timezone.utc)]
)
@pytest.mark.parametrize("first_samp", [0, 37])
def test_crop_reset_first_samp_keeps_annotations(meas_date, first_samp):
    """Epochs from annotations match before/after crop with reset_first_samp."""
    sfreq = 100.0
    n_times = 2000
    rng = np.random.default_rng(0)
    data = rng.standard_normal((1, n_times))
    # deterministic "evoked response": a ramp after each stimulus sample
    stim_rel = np.arange(300, 1800, 150)  # samples relative to first sample
    for s in stim_rel:
        data[0, s : s + 20] += np.linspace(5, 0, 20)
    info = create_info(["EEG 001"], sfreq, "eeg")
    raw = RawArray(data, info, first_samp=first_samp, verbose=False)
    raw.set_meas_date(meas_date)
    # onsets relative to the first sample (orig_time=None)
    raw.set_annotations(Annotations(stim_rel / sfreq, 0.0, "stim"))

    def _epochs_data(r):
        events, _ = events_from_annotations(r, verbose=False)
        ep = Epochs(
            r, events, tmin=-0.1, tmax=0.3, baseline=None, preload=True,
            verbose=False,
        )
        return events, ep.get_data()

    events_orig, data_orig = _epochs_data(raw)
    assert len(events_orig) == len(stim_rel)

    tmin = 1.23  # crop off 123 samples
    n_crop = int(round(tmin * sfreq))
    cropped = raw.copy().crop(tmin=tmin, reset_first_samp=True)
    assert cropped.first_samp == 0
    events_crop, data_crop = _epochs_data(cropped)

    # annotation onsets, relative to the new first sample, shifted by the crop
    assert_allclose(
        cropped.annotations.onset - cropped.first_time,
        stim_rel[stim_rel >= n_crop] / sfreq - tmin,
        rtol=1e-12,
        atol=1e-9,  # values are times in s; 1 ns is far below one sample
    )
    # event samples shifted exactly by the cropped amount
    keep = events_orig[:, 0] - first_samp >= n_crop
    assert_array_equal(
        events_crop[:, 0], events_orig[keep, 0] - first_samp - n_crop
    )
    # epochs contain exactly the same data as without cropping
    assert_allclose(data_crop, data_orig[keep], rtol=1e-12)


def test_crop_reset_first_samp_without_annotations():
    """Plain reset still works and keeps an empty annotation set."""
    info = create_info(["EEG 001"], 100.0, "eeg")
    raw = RawArray(np.zeros((1, 500)), info, first_samp=10, verbose=False)
    raw.crop(tmin=1.0, reset_first_samp=True)
    assert raw.first_samp == 0
    assert len(raw.annotations) == 0
