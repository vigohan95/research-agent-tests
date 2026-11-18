"""Regression test: DataArray.str.zfill must keep a leading sign before the zeros,
matching Python's str.zfill / numpy.strings.zfill / pandas Series.str.zfill."""

from __future__ import annotations

import numpy as np
import pytest

import xarray as xr
from xarray.testing import assert_identical

# (input, width, expected) -- expected worked out by hand from the definition:
# pad with '0' to `width`; if the string starts with '+' or '-', the zeros go
# after the sign; strings already >= width are unchanged.
CASES = [
    ("-12", 5, "-0012"),
    ("+7", 4, "+007"),
    ("-1", 2, "-1"),
    ("-123", 3, "-123"),
    ("42", 5, "00042"),
    ("-", 3, "-00"),
    ("+", 2, "+0"),
    ("a-1", 5, "00a-1"),
    ("", 2, "00"),
]


@pytest.mark.parametrize("dtype", [np.str_, np.bytes_])
def test_zfill_signed_scalar_width(dtype) -> None:
    values = [c[0] for c in CASES]
    for width in sorted({c[1] for c in CASES}):
        expected_values = []
        for s, _, _ in CASES:
            # independent hand-written reference implementation
            if len(s) >= width:
                out = s
            elif s[:1] in ("+", "-"):
                out = s[0] + "0" * (width - len(s)) + s[1:]
            else:
                out = "0" * (width - len(s)) + s
            expected_values.append(out)
        arr = xr.DataArray(np.array(values).astype(dtype))
        expected = xr.DataArray(np.array(expected_values).astype(dtype))
        assert_identical(arr.str.zfill(width), expected)


@pytest.mark.parametrize("dtype", [np.str_, np.bytes_])
def test_zfill_signed_hand_cases(dtype) -> None:
    for s, width, exp in CASES:
        arr = xr.DataArray(np.array([s]).astype(dtype))
        expected = xr.DataArray(np.array([exp]).astype(dtype))
        assert_identical(arr.str.zfill(width), expected)


@pytest.mark.parametrize("dtype", [np.str_, np.bytes_])
def test_zfill_signed_array_width(dtype) -> None:
    values = xr.DataArray(np.array([s for s, _, _ in CASES]).astype(dtype), dims="x")
    widths = xr.DataArray([w for _, w, _ in CASES], dims="x")
    expected = xr.DataArray(
        np.array([e for _, _, e in CASES]).astype(dtype), dims="x"
    )
    assert_identical(values.str.zfill(widths), expected)
