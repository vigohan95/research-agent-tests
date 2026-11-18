"""Regression test: ``str.zfill`` must keep a leading sign in front of the zeros.

Python's ``str.zfill``, ``numpy.strings.zfill`` and pandas' ``Series.str.zfill``
insert the padding zeros *after* a leading ``+``/``-`` sign; only the sign at
position 0 is special, everything else is padded on the left.
"""

from __future__ import annotations

import numpy as np
import pytest

import xarray as xr
from xarray.tests import assert_equal

VALUES = ["-12", "+7", "12", "-1234", "a-1"]


@pytest.mark.parametrize(
    "dtype", [pytest.param(np.str_, id="str"), pytest.param(np.bytes_, id="bytes")]
)
@pytest.mark.parametrize(
    ("width", "expected_values"),
    [
        pytest.param(5, ["-0012", "+0007", "00012", "-1234", "00a-1"], id="width5"),
        pytest.param(3, ["-12", "+07", "012", "-1234", "a-1"], id="width3"),
        pytest.param(
            np.array([4, 6, 1, 7, 4]),
            ["-012", "+00007", "12", "-001234", "0a-1"],
            id="broadcast",
        ),
    ],
)
def test_zfill_signed(
    dtype: type, width: int | np.ndarray, expected_values: list[str], use_dask: bool
) -> None:
    values = xr.DataArray(VALUES, dims="x").astype(dtype)
    if use_dask:
        values = values.chunk(x=2)

    result = values.str.zfill(width)
    if use_dask:
        result = result.compute()

    expected = xr.DataArray(expected_values, dims="x").astype(dtype)
    assert result.dtype == expected.dtype
    assert_equal(result, expected)
