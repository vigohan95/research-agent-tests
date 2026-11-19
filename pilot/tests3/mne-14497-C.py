"""Regression test: complex multitaper output with normalization='full'."""

import numpy as np
import pytest
from numpy.testing import assert_allclose

from mne.time_frequency import psd_array_multitaper
from mne.time_frequency.multitaper import _psd_from_mt


@pytest.mark.parametrize("normalization", ["length", "full"])
@pytest.mark.parametrize("sfreq", [100.0, 512.0])
def test_multitaper_complex_matches_power(normalization, sfreq):
    """Power rebuilt from complex spectra must match power output."""
    rng = np.random.default_rng(0)
    x = rng.standard_normal((3, 1024))
    kw = dict(sfreq=sfreq, adaptive=False, normalization=normalization, verbose=False)
    psd, freqs = psd_array_multitaper(x, output="power", **kw)
    x_mt, freqs_c, weights = psd_array_multitaper(x, output="complex", **kw)
    assert_allclose(freqs, freqs_c)
    psd_from_complex = _psd_from_mt(x_mt, weights)
    assert_allclose(psd_from_complex, psd, rtol=1e-10)
