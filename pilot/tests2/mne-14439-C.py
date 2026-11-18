"""Regression tests for crop(..., reset_first_samp=True) with annotations/epochs."""

from pathlib import Path

import numpy as np
import pytest
from numpy.testing import assert_allclose, assert_array_equal

from mne import Annotations, Epochs, concatenate_raws, events_from_annotations
from mne.io import RawArray, read_raw_fif

raw_fname = Path(__file__).parents[1] / "tests" / "data" / "test_raw.fif"


def _annotate(raw, onsets_rel):
    """Add stimulus annotations at times relative to the data start."""
    annot = Annotations(
        onset=np.asarray(onsets_rel) + raw.first_time,
        duration=0.0,
        description="stim",
        orig_time=raw.info["meas_date"],
    )
    if raw.info["meas_date"] is None:
        annot = Annotations(
            onset=np.asarray(onsets_rel), duration=0.0, description="stim"
        )
    raw.set_annotations(annot)
    return raw


def _evoked(raw):
    events, event_id = events_from_annotations(raw, verbose=False)
    epochs = Epochs(
        raw,
        events,
        event_id,
        tmin=-0.05,
        tmax=0.2,
        baseline=None,
        picks="eeg",
        preload=True,
        verbose=False,
    )
    return events, epochs.average().data


@pytest.mark.parametrize("preload", [False, True])
def test_crop_reset_first_samp_file_epochs(preload):
    """Epoching after crop(reset_first_samp=True) matches untrimmed data."""
    raw = read_raw_fif(raw_fname, preload=preload, verbose=False)
    assert raw.first_samp > 0
    onsets = np.arange(5.0, 12.0, 0.7)
    _annotate(raw, onsets)
    events_orig, ave_orig = _evoked(raw)

    tmin = 3.0
    raw_c = raw.copy().crop(tmin=tmin, reset_first_samp=True)
    assert raw_c.first_samp == 0
    # data must be the same samples as in the original recording
    start = raw.copy().crop(tmin=tmin).first_samp - raw.first_samp
    assert_allclose(
        raw_c.get_data(picks="eeg", stop=1000),
        raw.get_data(picks="eeg", start=start, stop=start + 1000),
    )
    # annotations must still point at the same data
    assert_allclose(
        raw_c.annotations.onset - raw_c.first_time,
        onsets - start / raw.info["sfreq"],
        atol=1e-6,
    )
    events_c, ave_c = _evoked(raw_c)
    assert_array_equal(events_c[:, 0], events_orig[:, 0] - raw.first_samp - start)
    assert_allclose(ave_c, ave_orig, rtol=1e-7, atol=1e-20)


def test_crop_reset_first_samp_no_meas_date():
    """Same check for an in-memory recording without meas_date."""
    raw = read_raw_fif(raw_fname, preload=True, verbose=False)
    raw = RawArray(raw.get_data(), raw.info, first_samp=raw.first_samp, verbose=False)
    raw.set_meas_date(None)
    onsets = np.arange(5.0, 12.0, 0.7)
    _annotate(raw, onsets)
    _, ave_orig = _evoked(raw)
    raw_c = raw.copy().crop(tmin=3.0, reset_first_samp=True)
    assert raw_c.first_samp == 0
    _, ave_c = _evoked(raw_c)
    assert_allclose(ave_c, ave_orig, rtol=1e-7, atol=1e-20)


def test_crop_reset_first_samp_concatenated():
    """Resetting the origin of a concatenated, non-preloaded raw keeps data."""
    raw = read_raw_fif(raw_fname, verbose=False).crop(0, 6)
    raw = concatenate_raws([raw.copy(), raw.copy()])
    ref = raw.copy().load_data()
    raw.crop(tmin=2.0, reset_first_samp=True)
    ref.crop(tmin=2.0)
    assert raw.first_samp == 0
    assert_allclose(raw.get_data(picks="eeg"), ref.get_data(picks="eeg"))
