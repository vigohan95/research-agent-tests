# Authors: The MNE-Python contributors.
# License: BSD-3-Clause
# Copyright the MNE-Python contributors.

import numpy as np
import pytest
from numpy.testing import assert_allclose

from mne import Annotations, Epochs, create_info, events_from_annotations
from mne.io import RawArray


@pytest.mark.parametrize("meas_date", [None, 1e9])
def test_crop_reset_first_samp_annotations(meas_date):
    """Test annotations stay aligned with data after crop(reset_first_samp)."""
    sfreq = 100.0
    rng = np.random.default_rng(0)
    raw = RawArray(
        rng.standard_normal((1, 2000)),
        create_info(1, sfreq, "eeg"),
        first_samp=50,
        verbose=False,
    )
    raw.set_meas_date(meas_date)
    raw.set_annotations(
        Annotations([3.0, 7.0, 12.0], 0.0, "stim", orig_time=raw.info["meas_date"])
    )
    cropped = raw.copy().crop(2.0, None, reset_first_samp=True)
    assert cropped.first_samp == 0
    evokeds = list()
    for inst in (raw, cropped):
        events, _ = events_from_annotations(inst, verbose=False)
        epochs = Epochs(
            inst, events, tmin=-0.1, tmax=0.2, baseline=None, verbose=False
        )
        evokeds.append(epochs.average().data)
    assert_allclose(evokeds[0], evokeds[1])
