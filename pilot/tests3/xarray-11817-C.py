from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

import xarray as xr
from xarray.tests import assert_identical


@pytest.mark.parametrize("dtype", [np.str_, np.bytes_, object])
def test_zfill_keeps_leading_sign(dtype) -> None:
    raw = ["-1", "+23", "7", "-1234", "+", "-"]
    if dtype is np.bytes_:
        values = xr.DataArray(np.array([s.encode() for s in raw], dtype=dtype))
        expected_raw = [s.encode().zfill(4) for s in raw]
    else:
        values = xr.DataArray(np.array(raw, dtype=dtype))
        expected_raw = [s.zfill(4) for s in raw]

    result = values.str.zfill(4)
    expected = xr.DataArray(np.array(expected_raw, dtype=dtype))
    assert_identical(result, expected)
    decoded = [v.decode() if isinstance(v, bytes) else v for v in result.values]
    assert decoded == ["-001", "+023", "0007", "-1234", "+000", "-000"]


def test_zfill_sign_matches_pandas() -> None:
    raw = ["-1", "+23", "7", "abc"]
    result = xr.DataArray(raw, dims="x").str.zfill(5)
    expected = pd.Series(raw).str.zfill(5).tolist()
    assert result.values.tolist() == expected


def test_zfill_sign_broadcast_width() -> None:
    values = xr.DataArray(["-1", "+2", "3"], dims="x")
    width = xr.DataArray([3, 4, 2], dims="x")
    result = values.str.zfill(width)
    expected = xr.DataArray(["-01", "+002", "03"], dims="x")
    assert_identical(result, expected)
