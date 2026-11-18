import pytest

from pint import UnitRegistry

np = pytest.importorskip("numpy")


@pytest.mark.parametrize("func", [np.mod, np.remainder, np.fmod])
def test_remainder_ufuncs_convert_second_operand(func):
    ureg = UnitRegistry()
    positions = ureg.Quantity(np.array([0.5, 3.5, 7.25]), "m")
    track = ureg.Quantity(300.0, "cm")

    result = func(positions, track)

    assert result.units == ureg.m
    np.testing.assert_allclose(result.magnitude, [0.5, 0.5, 1.25])
    # consistent with the % operator
    np.testing.assert_allclose(
        result.magnitude, (positions % track).to("m").magnitude
    )


def test_remainder_ufunc_incompatible_units_raises():
    ureg = UnitRegistry()
    with pytest.raises(Exception):
        np.mod(ureg.Quantity(np.array([1.0, 2.0]), "m"), ureg.Quantity(1.0, "s"))
