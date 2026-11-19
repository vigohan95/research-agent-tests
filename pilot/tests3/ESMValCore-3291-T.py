"""Regression tests: a ``min_value`` of zero must act as a real cutoff.

``count_spells`` used ``if not threshold`` to detect "no threshold", so a
threshold of ``0`` (or ``0.0``) was silently treated like ``None`` and every
valid time step was counted. For daily precipitation with ``min_value=0``
this meant cells that never rain were kept by ``mask_fillvalues``.
"""

from pathlib import Path

import dask.array as da
import numpy as np
import pytest
from iris.coords import DimCoord
from iris.cube import Cube

from esmvalcore.preprocessor import PreprocessorFile, mask_fillvalues
from esmvalcore.preprocessor._mask import count_spells

# Daily "rain" on 4 time steps for 3 grid cells (lat=1, lon=3):
#   cell 0: never rains (desert)          -> 0 wet days
#   cell 1: rains every day               -> 4 wet days
#   cell 2: rains on 2 of 4 days          -> 2 wet days
RAIN = np.array(
    [
        [[0.0, 1.0, 1.0]],
        [[0.0, 1.0, 0.0]],
        [[0.0, 1.0, 1.0]],
        [[0.0, 1.0, 0.0]],
    ],
)


def _as(data, lazy):
    return da.from_array(data, chunks=(2, 1, 3)) if lazy else data


@pytest.mark.parametrize("lazy", [False, True])
@pytest.mark.parametrize(
    ("threshold", "expected"),
    [
        # Hand-counted number of days with rain > threshold.
        (0, [0, 4, 2]),
        (0.0, [0, 4, 2]),
        (0.001, [0, 4, 2]),
        # No threshold: every valid time step counts.
        (None, [4, 4, 4]),
    ],
)
def test_count_spells_zero_threshold(threshold, expected, lazy):
    """A zero threshold counts only values strictly above zero."""
    result = count_spells(_as(RAIN, lazy), threshold, axis=0, spell_length=1)
    assert isinstance(result, da.Array) == lazy
    np.testing.assert_array_equal(np.asarray(result), [expected])


def _product(cube, name, mocker):
    product = mocker.create_autospec(
        PreprocessorFile,
        spec_set=True,
        instance=True,
    )
    product.filename = Path(name)
    product.cubes = [cube]
    return product


def _cube(data):
    time = DimCoord(
        [0.5, 1.5, 2.5, 3.5],
        standard_name="time",
        bounds=[[0, 1], [1, 2], [2, 3], [3, 4]],
        units="days since 2000-01-01",
    )
    lat = DimCoord([0.0], standard_name="latitude", units="degrees_north")
    lon = DimCoord(
        [0.0, 1.0, 2.0],
        standard_name="longitude",
        units="degrees_east",
    )
    return Cube(
        data,
        var_name="pr",
        units="mm day-1",
        dim_coords_and_dims=[(time, 0), (lat, 1), (lon, 2)],
    )


@pytest.mark.parametrize("lazy", [False, True])
@pytest.mark.parametrize(
    ("min_value", "masked_cells"),
    [
        # Need >= int(4 * 0.75) = 3 wet days: only cell 1 survives.
        (0, [True, False, True]),
        (0.0, [True, False, True]),
        (0.001, [True, False, True]),
        # No cutoff: all 4 time steps are valid everywhere, nothing masked.
        (None, [False, False, False]),
    ],
)
def test_mask_fillvalues_zero_min_value(mocker, lazy, min_value, masked_cells):
    """``min_value=0`` masks never-raining cells just like 0.001 does."""
    products = {
        _product(_cube(_as(RAIN.copy(), lazy)), "a.nc", mocker),
        _product(_cube(_as(RAIN.copy() * 2.0, lazy)), "b.nc", mocker),
    }
    results = mask_fillvalues(
        products,
        threshold_fraction=0.75,
        min_value=min_value,
    )

    expected = np.broadcast_to(np.array(masked_cells), (4, 1, 3))
    for product in results:
        cube = product.cubes[0]
        assert cube.has_lazy_data() == lazy
        np.testing.assert_array_equal(np.ma.getmaskarray(cube.data), expected)
