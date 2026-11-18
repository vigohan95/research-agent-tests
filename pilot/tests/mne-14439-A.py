"""Regression tests for Raw.crop(..., reset_first_samp=True).

After cropping with ``reset_first_samp=True``:

* ``first_samp`` must be 0,
* the data must be exactly the cropped segment (also for non-preloaded data),
* annotations must point at the same signal samples as before the crop,
* this must hold for concatenated recordings as well.

The data used here encode the original (absolute) sample number of each
sample in the signal value, so that "which sample is this" can be checked
independently of first_samp bookkeeping.
"""

from datetime import datetime, timezone

import numpy as np
import pytest
from numpy.testing import assert_array_equal

from mne import Annotations, concatenate_raws, create_info, events_from_annotations
from mne.io import RawArray, read_raw_fif

SFREQ = 100.0
FIRST_SAMP = 1000
N_SAMP = 1000  # 10 s of data


def _make_raw(meas_date=None, first_samp=FIRST_SAMP, n_samp=N_SAMP, offset=0):
    """Make a raw whose value equals the original data-relative sample index."""
    info = create_info(["CH1"], SFREQ, "eeg")
    data = (np.arange(n_samp, dtype=float) + offset)[np.newaxis]
    raw = RawArray(data, info, first_samp=first_samp, verbose=False)
    if meas_date is not None:
        raw.set_meas_date(meas_date)
    return raw


def _annot_values(raw):
    """Return the signal value at each annotation onset sample."""
    events, _ = events_from_annotations(raw, verbose=False)
    idx = events[:, 0] - raw.first_samp  # index into the data array
    assert np.all(idx >= 0) and np.all(idx < raw.n_times), idx
    return raw.get_data()[0, idx]


@pytest.mark.parametrize(
    "meas_date", [None, datetime(2020, 1, 1, tzinfo=timezone.utc)]
)
def test_crop_reset_first_samp_annotations(meas_date):
    """Annotations stay aligned with data after crop with reset."""
    raw = _make_raw(meas_date)
    # annotations at data-relative samples 300, 450 and 700
    # (times relative to the first sample: 3.0, 4.5, 7.0 s)
    rel_onsets = np.array([3.0, 4.5, 7.0])
    if meas_date is None:
        onset = rel_onsets  # relative to start of data
        orig_time = None
    else:
        onset = rel_onsets + raw.first_time  # relative to meas_date
        orig_time = meas_date
    raw.set_annotations(
        Annotations(onset, [0.1] * 3, ["a", "b", "c"], orig_time=orig_time)
    )
    # sanity: before crop the values are the data-relative sample numbers
    assert_array_equal(_annot_values(raw), [300, 450, 700])

    for reset in (False, True):
        r = raw.copy().crop(tmin=2.0, tmax=8.0, reset_first_samp=reset)
        # cropped data start at original sample 200
        assert r.get_data()[0, 0] == 200
        assert r.n_times == 601
        if reset:
            assert r.first_samp == 0
        else:
            assert r.first_samp == FIRST_SAMP + 200
        assert len(r.annotations) == 3
        # same signal samples as before the crop
        assert_array_equal(_annot_values(r), [300, 450, 700])
        # and the onsets relative to the cropped data start: 1.0, 2.5, 5.0 s
        onset_rel = r.annotations.onset - r.first_time
        if r.annotations.orig_time is not None:
            onset_rel += (
                r.annotations.orig_time - r.info["meas_date"]
            ).total_seconds()
        np.testing.assert_allclose(onset_rel, [1.0, 2.5, 5.0], atol=1e-9)


def test_crop_reset_first_samp_not_preloaded(tmp_path):
    """Non-preloaded data read after crop with reset are the right samples."""
    raw = _make_raw()
    fname = tmp_path / "test_raw.fif"
    raw.save(fname, fmt="double", verbose=False)

    raw_np = read_raw_fif(fname, preload=False, verbose=False)
    assert raw_np.first_samp == FIRST_SAMP
    raw_np.crop(tmin=2.0, tmax=8.0, reset_first_samp=True)
    assert raw_np.first_samp == 0
    assert raw_np.n_times == 601
    assert_array_equal(raw_np.get_data()[0], np.arange(200, 801))
    # partial reads also work
    assert_array_equal(raw_np.get_data(start=10, stop=20)[0], np.arange(210, 220))
    raw_np.load_data()
    assert_array_equal(raw_np.get_data()[0], np.arange(200, 801))


def test_crop_reset_first_samp_concatenated(tmp_path):
    """Crop with reset on concatenated raws (also dropping the first file)."""
    # two files, values continue across the boundary: 0..999, 1000..1999
    raw1 = _make_raw(first_samp=FIRST_SAMP, offset=0)
    raw2 = _make_raw(first_samp=5000, offset=N_SAMP)
    for preload in (True, False):
        if preload:
            r1, r2 = raw1.copy(), raw2.copy()
        else:
            f1, f2 = tmp_path / "a_raw.fif", tmp_path / "b_raw.fif"
            raw1.save(f1, fmt="double", overwrite=True, verbose=False)
            raw2.save(f2, fmt="double", overwrite=True, verbose=False)
            r1 = read_raw_fif(f1, preload=False, verbose=False)
            r2 = read_raw_fif(f2, preload=False, verbose=False)
        raw = concatenate_raws([r1, r2], verbose=False)
        raw.set_annotations(None)  # drop the BAD/EDGE boundary annotations
        # annotation at concatenated sample 1500 (in the second file)
        raw.set_annotations(Annotations([15.0], [0.1], ["x"], orig_time=None))
        assert_array_equal(_annot_values(raw), [1500])

        # crop that keeps only (part of) the second file
        r = raw.copy().crop(tmin=12.0, tmax=18.0, reset_first_samp=True)
        assert r.first_samp == 0
        assert r.n_times == 601
        assert_array_equal(r.get_data()[0], np.arange(1200, 1801))
        assert_array_equal(_annot_values(r), [1500])

        # crop that spans both files
        r = raw.copy().crop(tmin=8.0, tmax=12.0, reset_first_samp=True)
        assert r.first_samp == 0
        assert_array_equal(r.get_data()[0], np.arange(800, 1201))
        assert len(r.annotations) == 0  # 15 s is outside this crop

        # concatenating a reset-cropped raw keeps first_samp == 0
        a = raw.copy().crop(tmin=12.0, tmax=13.0, reset_first_samp=True)
        b = raw.copy().crop(tmin=2.0, tmax=3.0, reset_first_samp=True)
        c = concatenate_raws([a, b], verbose=False)
        assert c.first_samp == 0
        assert_array_equal(
            c.get_data()[0], np.r_[np.arange(1200, 1301), np.arange(200, 301)]
        )
