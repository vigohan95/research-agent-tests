"""Regression tests: a zero ``min_value`` threshold must not be ignored."""

import dask.array as da
import iris.coords
import iris.cube
import numpy as np
import pytest

from esmvalcore.preprocessor._mask import _get_fillvalues_mask, count_spells


@pytest.mark.parametrize("lazy", [False, True])
def test_count_spells_zero_threshold(lazy):
    # Time axis 0, two cells: one always dry (0), one always wet (>0)
    data = np.ma.array([[0.0, 1.0], [0.0, 2.0], [0.0, 3.0]])
    if lazy:
        data = da.from_array(data)
    result = count_spells(data, 0.0, axis=0, spell_length=1)
    if lazy:
        result = result.compute()
    np.testing.assert_array_equal(result, [0, 3])


def test_count_spells_none_threshold_counts_all():
    data = np.ma.array([[0.0, 1.0], [0.0, 2.0], [0.0, 3.0]])
    result = count_spells(data, None, axis=0, spell_length=1)
    np.testing.assert_array_equal(result, [3, 3])


@pytest.mark.parametrize("lazy", [False, True])
def test_get_fillvalues_mask_zero_min_value(lazy):
    values = np.ma.array(
        [[0.0, 1.0], [0.0, 2.0], [0.0, 0.5], [0.0, 4.0]],
    )
    if lazy:
        values = da.from_array(values)
    time = iris.coords.DimCoord(
        [0.0, 1.0, 2.0, 3.0],
        standard_name="time",
        units="days since 2000-01-01",
    )
    lon = iris.coords.DimCoord(
        [0.0, 10.0],
        standard_name="longitude",
        units="degrees",
    )
    cube = iris.cube.Cube(
        values,
        var_name="pr",
        units="kg m-2 s-1",
        dim_coords_and_dims=[(time, 0), (lon, 1)],
    )
    mask = _get_fillvalues_mask(cube, 0.5, 0.0, 1)
    if lazy:
        mask = mask.compute()
    # Dry cell never exceeds 0 -> masked; wet cell kept.
    np.testing.assert_array_equal(mask, [True, False])
