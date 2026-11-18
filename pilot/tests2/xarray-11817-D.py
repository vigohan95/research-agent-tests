from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

import xarray as xr
from xarray.tests import assert_identical

RAW = ["-12", "+3", "7", "-", "", "abc", "-12345"]


@pytest.mark.parametrize(
    "dtype",
    [
        pytest.param(np.str_, id="str"),
        pytest.param(np.bytes_, id="bytes"),
        pytest.param(object, id="object"),
    ],
)
def test_zfill_keeps_leading_sign(dtype: type, use_dask: bool) -> None:
    raw = [s.encode() for s in RAW] if dtype is np.bytes_ else RAW
    values = xr.DataArray(np.array(raw, dtype=dtype), dims="x")
    if use_dask:
        values = values.chunk(x=3)

    result = values.str.zfill(4).compute()

    expected_list = [s.zfill(4) for s in raw]
    assert expected_list[:3] == (
        [b"-012", b"+003", b"0007"] if dtype is np.bytes_ else ["-012", "+003", "0007"]
    )
    expected = xr.DataArray(np.array(expected_list, dtype=dtype), dims="x")
    assert_identical(result, expected)


def test_zfill_matches_pandas() -> None:
    values = xr.DataArray(RAW, dims="x")
    expected = pd.Series(RAW).str.zfill(5).tolist()
    assert values.str.zfill(5).values.tolist() == expected


def test_zfill_sign_broadcast_width() -> None:
    values = xr.DataArray(["-1", "+2", "3"], dims="x")
    width = xr.DataArray([3, 4, 2], dims="x")
    result = values.str.zfill(width)
    expected = xr.DataArray(["-01", "+002", "03"], dims="x")
    assert_identical(result, expected)
