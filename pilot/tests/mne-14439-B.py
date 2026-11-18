# Authors: The MNE-Python contributors.
# License: BSD-3-Clause
# Copyright the MNE-Python contributors.

"""Regression tests for Raw.crop(..., reset_first_samp=True)."""

import numpy as np
import pytest
from numpy.testing import assert_allclose, assert_array_equal

from mne import Annotations, concatenate_raws, create_info
from mne.io import RawArray, read_raw_fif

SFREQ = 1000.0
N_TIMES = 10000


def _make_raw(meas_date, first_samp=0):
    """Make a raw whose single channel value equals the absolute sample index."""
    info = create_info(["CH1"], SFREQ, "eeg")
    data = np.arange(first_samp, first_samp + N_TIMES, dtype=float)[np.newaxis]
    raw = RawArray(data, info, first_samp=first_samp)
    raw.set_meas_date(meas_date)
    # Annotation at 3.0 s after the start of the data, i.e. absolute sample
    # first_samp + 3000; given in the timebase expected by set_annotations.
    onset = 3.0 + (raw.first_time if meas_date is not None else 0.0)
    raw.set_annotations(Annotations([onset], [0.5], ["stim"], orig_time=meas_date))
    return raw


def _annot_sample(raw):
    """Index (relative to the data start) the first annotation points at."""
    return int(round((raw.annotations.onset[0] - raw.first_time) * SFREQ))


@pytest.mark.parametrize("meas_date", [None, 1e9])
@pytest.mark.parametrize("first_samp", [0, 500])
def test_crop_reset_first_samp_annotations(meas_date, first_samp):
    """Annotations must point at the same samples after a resetting crop."""
    raw = _make_raw(meas_date, first_samp)
    idx = _annot_sample(raw)
    assert idx == 3000
    target = raw.get_data()[0, idx]  # = first_samp + 3000
    for reset in (False, True):
        cropped = raw.copy().crop(2.0, 5.0, reset_first_samp=reset)
        # By hand: the annotation is 3.0 s after the old start, the crop
        # starts 2.0 s after it, so it is 1.0 s (1000 samples) after the new
        # start of the data.
        assert _annot_sample(cropped) == 1000, reset
        assert cropped.get_data()[0, _annot_sample(cropped)] == target
        assert len(cropped.annotations) == 1
        assert_allclose(cropped.annotations.duration, [0.5])
    assert cropped.first_samp == 0
    assert cropped.last_samp == 3000
    assert cropped.n_times == 3001


def test_crop_reset_first_samp_not_preloaded(tmp_path):
    """Non-preloaded data must be read from the right place after the crop."""
    raw = _make_raw(1e9, first_samp=500)
    fname = tmp_path / "test_raw.fif"
    raw.save(fname)
    raw = read_raw_fif(fname, preload=False)
    assert raw.first_samp == 500
    cropped = raw.copy().crop(2.0, 5.0, reset_first_samp=True)
    assert cropped.first_samp == 0
    # Values are the absolute sample indices: 500 + 2000 ... 500 + 5000
    expected = np.arange(2500, 5501, dtype=float)
    assert_array_equal(cropped.get_data()[0], expected)
    assert_array_equal(cropped.copy().load_data().get_data()[0], expected)
    assert_array_equal(cropped.get_data(start=10, stop=20)[0], expected[10:20])
    assert cropped.get_data()[0, _annot_sample(cropped)] == 3500


def _make_part(tmp_path, ii, preload):
    """Make a 1000-sample part whose values are 1000 * ii ... 1000 * ii + 999."""
    info = create_info(["CH1"], SFREQ, "eeg")
    data = np.arange(ii * 1000, (ii + 1) * 1000, dtype=float)[np.newaxis]
    raw = RawArray(data, info)
    if not preload:
        fname = tmp_path / f"part{ii}_raw.fif"
        raw.save(fname)
        raw = read_raw_fif(fname, preload=False)
    return raw


@pytest.mark.parametrize("preload", [True, False])
def test_crop_reset_first_samp_concatenated(tmp_path, preload):
    """Concatenated raws cropped with reset_first_samp must start at sample 0."""
    raws = [_make_part(tmp_path, ii, preload) for ii in range(3)]
    other = raws.pop()
    raw = concatenate_raws(raws)
    assert raw.n_times == 2000
    # Crop starting inside the second file: sample 1500 ... 1899
    raw.crop(1.5, 1.899, reset_first_samp=True)
    assert raw.n_times == 400
    assert raw.first_samp == 0
    assert raw.last_samp == 399
    assert_array_equal(raw.get_data()[0], np.arange(1500, 1900, dtype=float))

    # appending something after a reset crop must keep first_samp at 0
    raw.append(other)
    assert raw.first_samp == 0
    assert raw.n_times == 1400
    expected = np.r_[np.arange(1500, 1900), np.arange(2000, 3000)].astype(float)
    assert_array_equal(raw.get_data()[0], expected)
