"""Regression test: complex multitaper spectra must honour normalization."""

import numpy as np
import pytest
from numpy.testing import assert_allclose

from mne.time_frequency import psd_array_multitaper
from mne.time_frequency.multitaper import _psd_from_mt


@pytest.mark.parametrize("normalization", ["length", "full"])
def test_complex_mt_matches_power(normalization):
    """Power rebuilt from complex tapered spectra equals the returned PSD."""
    rng = np.random.default_rng(0)
    sfreq = 250.0
    x = rng.standard_normal((2, 500))
    kw = dict(sfreq=sfreq, normalization=normalization, adaptive=False)
    psd, freqs = psd_array_multitaper(x, output="power", **kw)
    x_mt, freqs_c, weights = psd_array_multitaper(x, output="complex", **kw)
    assert_allclose(freqs, freqs_c)
    psd_from_complex = _psd_from_mt(x_mt, weights)
    assert_allclose(psd_from_complex, psd, rtol=1e-10)


def test_full_normalization_closed_form():
    """'full' PSD equals 'length' PSD divided by sfreq (closed-form scaling)."""
    rng = np.random.default_rng(1)
    sfreq = 100.0
    x = rng.standard_normal(400)
    common = dict(sfreq=sfreq, adaptive=False)
    p_len, _ = psd_array_multitaper(x, normalization="length", **common)
    c_len, _, w = psd_array_multitaper(
        x, normalization="length", output="complex", **common
    )
    c_full, _, _ = psd_array_multitaper(
        x, normalization="full", output="complex", **common
    )
    assert_allclose(_psd_from_mt(c_full, w)[0], p_len / sfreq, rtol=1e-10)
    assert_allclose(_psd_from_mt(c_len, w)[0], p_len, rtol=1e-10)
