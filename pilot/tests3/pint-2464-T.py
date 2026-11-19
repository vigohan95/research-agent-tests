"""Regression tests: NumPy remainder ufuncs must convert compatible units.

np.remainder / np.mod / np.fmod used to strip units without converting, so
``positions_in_m % track_in_cm`` computed ``magnitude_m % magnitude_cm``.
"""

from __future__ import annotations

import pytest

from pint.testsuite import helpers

np = pytest.importorskip("numpy")

REMAINDER_FUNCS = [np.remainder, np.mod, np.fmod]


@pytest.mark.parametrize("func", REMAINDER_FUNCS, ids=lambda f: f.__name__)
def test_remainder_converts_second_operand(func, module_registry):
    Q_ = module_registry.Quantity
    positions = Q_(np.array([1.0, 2.5, 4.2, 7.9]), "m")
    track = Q_(250.0, "cm")

    result = func(positions, track)

    # Closed form: wrap onto a 2.5 m track.
    expected = Q_(np.array([1.0, 0.0, 1.7, 0.4]), "m")
    assert result.units == positions.units
    helpers.assert_quantity_almost_equal(result, expected, rtol=1e-12)
    # Same answer as the % operator.
    helpers.assert_quantity_almost_equal(result, positions % track, rtol=1e-12)


@pytest.mark.parametrize("func", REMAINDER_FUNCS, ids=lambda f: f.__name__)
def test_remainder_converts_when_first_operand_in_smaller_unit(func, module_registry):
    Q_ = module_registry.Quantity
    positions = Q_(np.array([100.0, 260.0, 790.0]), "cm")
    track = Q_(2.5, "m")

    result = func(positions, track)

    expected = Q_(np.array([100.0, 10.0, 40.0]), "cm")
    assert result.units == positions.units
    helpers.assert_quantity_almost_equal(result, expected, rtol=1e-12)


@pytest.mark.parametrize("func", REMAINDER_FUNCS, ids=lambda f: f.__name__)
def test_remainder_same_units_unchanged(func, module_registry):
    Q_ = module_registry.Quantity
    positions = Q_(np.array([1.0, 2.5, 4.2]), "m")
    track = Q_(2.5, "m")

    expected = Q_(np.array([1.0, 0.0, 1.7]), "m")
    helpers.assert_quantity_almost_equal(func(positions, track), expected, rtol=1e-12)
