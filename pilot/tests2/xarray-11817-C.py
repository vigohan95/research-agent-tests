from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

import xarray as xr
from xarray.tests import assert_identical

VALUES = ["-12", "+12", "12", "-", "abcdef", "123456"]


@pytest.mark.parametrize("dtype", [np.str_, np.bytes_, object])
def test_zfill_keeps_sign_prefix(dtype) -> None:
    if dtype is object:
        values = np.array(VALUES, dtype=object)
    else:
        values = np.array(VALUES).astype(dtype)
    da = xr.DataArray(values, dims="x")

    expected_list = [v.zfill(5) for v in VALUES]
    assert expected_list == ["-0012", "+0012", "00012", "-0000", "abcdef", "123456"]
    if dtype is np.bytes_:
        expected_list = [v.encode() for v in expected_list]
    expected = xr.DataArray(np.array(expected_list, dtype=values.dtype), dims="x")
    if dtype is not object:
        expected = expected.astype(dtype)

    result = da.str.zfill(5)
    assert result.values.tolist() == expected.values.tolist()
    assert result.dtype.kind == expected.dtype.kind


def test_zfill_matches_pandas() -> None:
    da = xr.DataArray(VALUES, dims="x")
    expected = pd.Series(VALUES).str.zfill(5).tolist()
    assert da.str.zfill(5).values.tolist() == expected


def test_zfill_broadcast_width_with_sign() -> None:
    da = xr.DataArray(["-1", "+1", "1"], dims="x")
    width = xr.DataArray([3, 4], dims="y")
    result = da.str.zfill(width)
    expected = xr.DataArray(
        [["-01", "-001"], ["+01", "+001"], ["001", "0001"]], dims=["x", "y"]
    )
    assert_identical(result, expected.astype(result.dtype))


def test_zfill_empty_and_object_width() -> None:
    da = xr.DataArray(np.array([], dtype="U3"), dims="x")
    assert da.str.zfill(4).size == 0
    da = xr.DataArray(np.array(["-7", "7"], dtype=object), dims="x")
    assert da.str.zfill(3).values.tolist() == ["-07", "007"]
