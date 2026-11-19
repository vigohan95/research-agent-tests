from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

import xarray as xr


@pytest.mark.parametrize("dtype", [np.str_, np.bytes_, object])
def test_zfill_leading_sign_matches_python_and_pandas(dtype: type) -> None:
    raw = ["-5", "+12", "7", "-", "abc", "-12345"]
    values = np.array(raw).astype(dtype)
    if dtype is object:
        values = np.array(raw, dtype=object)
    da = xr.DataArray(values)

    result = da.str.zfill(4)

    expected_str = [s.zfill(4) for s in raw]
    assert expected_str == ["-005", "+012", "0007", "-000", "0abc", "-12345"]
    assert expected_str == pd.Series(raw).str.zfill(4).tolist()
    if dtype is np.bytes_:
        expected = np.array([s.encode() for s in expected_str]).astype(dtype)
    else:
        expected = np.array(expected_str).astype(dtype)
    assert result.dtype == expected.dtype
    np.testing.assert_array_equal(result.values, expected)


def test_zfill_leading_sign_broadcast_width() -> None:
    da = xr.DataArray(["-5", "+5", "5"], dims="x")
    width = xr.DataArray([3, 4], dims="y")

    result = da.str.zfill(width)

    expected = xr.DataArray(
        [["-05", "-005"], ["+05", "+005"], ["005", "0005"]], dims=["x", "y"]
    )
    xr.testing.assert_identical(result, expected)
