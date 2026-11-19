import numpy as np
import pytest
from numpy.testing import assert_allclose

from mne.time_frequency import psd_array_multitaper
from mne.time_frequency.multitaper import _psd_from_mt


@pytest.mark.parametrize("normalization", ["length", "full"])
def test_multitaper_complex_matches_power(normalization):
    """Power rebuilt from complex multitaper output matches direct PSD."""
    rng = np.random.default_rng(0)
    sfreq = 256.0
    x = rng.standard_normal((2, 512))
    kw = dict(sfreq=sfreq, adaptive=False, normalization=normalization)
    psd, _ = psd_array_multitaper(x, output="power", **kw)
    coefs, _, weights = psd_array_multitaper(x, output="complex", **kw)
    assert_allclose(_psd_from_mt(coefs, weights), psd, rtol=1e-10)
