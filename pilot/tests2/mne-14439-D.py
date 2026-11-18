# Authors: The MNE-Python contributors.
# License: BSD-3-Clause
# Copyright the MNE-Python contributors.

import numpy as np
import pytest

from mne import Annotations, create_info, events_from_annotations
from mne.io import RawArray


@pytest.mark.parametrize("meas_date", [None, 1e9])
def test_crop_reset_first_samp_annotations(meas_date):
    """Test annotations stay on the same samples with reset_first_samp."""
    sfreq = 100.0
    data = np.random.default_rng(0).standard_normal((1, 2000))
    raw = RawArray(data, create_info(1, sfreq, "eeg"), first_samp=50)
    raw.set_meas_date(meas_date)
    onsets = np.array([5.0, 8.0, 12.0])  # relative to first sample
    if meas_date is not None:
        onsets += raw.first_time
    annot = Annotations(onsets, 0.0, "stim", orig_time=raw.info["meas_date"])
    raw.set_annotations(annot)
    events, _ = events_from_annotations(raw)
    want = events[:, 0] - raw.first_samp - 300  # crop removes 300 samples
    raw.crop(3.0, reset_first_samp=True)
    assert raw.first_samp == 0
    events, _ = events_from_annotations(raw)
    np.testing.assert_array_equal(events[:, 0], want)
    np.testing.assert_allclose(raw.get_data()[0, events[:, 0]], data[0, want + 300])
