from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

import xarray as xr
from xarray.tests import assert_identical

RAW = ["-1", "+12", "7", "-", "+", "abc", "-12345", "", "1-2"]


def _expected(raw, width):
    # pandas is the reference behaviour the user joins against
    return list(pd.Series(raw, dtype=object).str.zfill(width))


@pytest.mark.parametrize("width", [1, 4, 6])
@pytest.mark.parametrize(
    "make",
    [
        pytest.param(lambda v: np.array(v, dtype=np.str_), id="str"),
        pytest.param(lambda v: np.array(v, dtype=object), id="object"),
        pytest.param(
            lambda v: np.array([x.encode() for x in v], dtype=np.bytes_), id="bytes"
        ),
    ],
)
def test_zfill_keeps_sign_in_front(make, width) -> None:
    values = xr.DataArray(make(RAW), dims=["station"])
    result = values.str.zfill(width)
    expected = _expected(RAW, width)
    if values.dtype.kind == "S":
        expected = [x.encode() for x in expected]
    assert list(result.values) == expected
    assert result.dtype == values.dtype or values.dtype == object


@pytest.mark.parametrize("dtype", [np.str_, object])
def test_zfill_broadcast_width_with_sign(dtype) -> None:
    values = xr.DataArray(np.array(["-1", "+2", "3"], dtype=dtype), dims=["x"])
    width = xr.DataArray([3, 4, 2], dims=["x"])
    result = values.str.zfill(width)
    expected = xr.DataArray(np.array(["-01", "+002", "03"], dtype=dtype), dims=["x"])
    assert_identical(result.astype(dtype), expected)


def test_zfill_empty_array() -> None:
    values = xr.DataArray(np.array([], dtype=np.str_), dims=["x"])
    result = values.str.zfill(3)
    assert result.size == 0
