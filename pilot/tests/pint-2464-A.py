"""Regression test: NumPy modulo / floor-division ufuncs must convert the second
operand to the units of the first when the units are compatible but different.

x1 = 7 m, x2 = 200 cm (= 2 m):
    7 m // 2 m = 3 (dimensionless), 7 m % 2 m = 1 m
"""

import pytest

from pint import UnitRegistry

np = pytest.importorskip("numpy")


@pytest.fixture(scope="module")
def ureg():
    return UnitRegistry()


# (x1 in m, x2 in cm, mod/remainder in m, fmod in m, floor_divide)
# Hand-computed with x2 expressed in metres (200 cm = 2 m):
#   np.mod / np.remainder take the sign of the divisor (Python %),
#   np.fmod takes the sign of the dividend (C fmod),
#   np.floor_divide is floor(x1 / x2).
CASES = [
    (7.0, 200.0, 1.0, 1.0, 3.0),
    (-7.0, 200.0, 1.0, -1.0, -4.0),
    (7.0, -200.0, -1.0, 1.0, -4.0),
    (5.5, 150.0, 1.0, 1.0, 3.0),
]


@pytest.mark.parametrize("a, b, exp_mod, exp_fmod, exp_floordiv", CASES)
def test_mod_like_ufuncs_convert_units(ureg, a, b, exp_mod, exp_fmod, exp_floordiv):
    x1 = ureg.Quantity(a, "m")
    x2 = ureg.Quantity(b, "cm")

    for func in (np.mod, np.remainder):
        res = func(x1, x2)
        assert res.dimensionality == x1.dimensionality
        assert res.to("m").magnitude == pytest.approx(exp_mod), func.__name__

    res = np.fmod(x1, x2)
    assert res.dimensionality == x1.dimensionality
    assert res.to("m").magnitude == pytest.approx(exp_fmod)

    res = np.floor_divide(x1, x2)
    assert res.dimensionless
    assert res.to("").magnitude == pytest.approx(exp_floordiv)


def test_numpy_functions_agree_with_operators(ureg):
    x1 = ureg.Quantity(7, "m")
    x2 = ureg.Quantity(200, "cm")

    assert (x1 % x2).to("m").magnitude == pytest.approx(1.0)
    assert (x1 // x2).to("").magnitude == pytest.approx(3.0)

    assert np.mod(x1, x2).to("m").magnitude == pytest.approx((x1 % x2).to("m").m)
    assert np.remainder(x1, x2).to("m").magnitude == pytest.approx(
        (x1 % x2).to("m").m
    )
    assert np.floor_divide(x1, x2).to("").magnitude == pytest.approx(
        (x1 // x2).to("").m
    )


def test_mod_like_ufuncs_on_arrays(ureg):
    x1 = ureg.Quantity(np.array([7.0, 3.0, 10.0]), "m")
    x2 = ureg.Quantity(200.0, "cm")

    np.testing.assert_allclose(np.mod(x1, x2).to("m").magnitude, [1.0, 1.0, 0.0])
    np.testing.assert_allclose(
        np.remainder(x1, x2).to("m").magnitude, [1.0, 1.0, 0.0]
    )
    np.testing.assert_allclose(np.fmod(x1, x2).to("m").magnitude, [1.0, 1.0, 0.0])
    np.testing.assert_allclose(
        np.floor_divide(x1, x2).to("").magnitude, [3.0, 1.0, 5.0]
    )
