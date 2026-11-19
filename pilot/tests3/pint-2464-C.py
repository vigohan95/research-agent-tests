import pytest

from pint import UnitRegistry

np = pytest.importorskip("numpy")


@pytest.mark.parametrize("func", [np.mod, np.remainder, np.fmod])
def test_remainder_ufuncs_convert_second_operand(func):
    ureg = UnitRegistry()
    pos = ureg.Quantity(np.array([1.5, 2.5, 0.5]), "m")
    track = ureg.Quantity(100.0, "cm")
    result = func(pos, track)
    assert result.units == ureg.m
    np.testing.assert_allclose(result.magnitude, [0.5, 0.5, 0.5])
    # Consistent with % operator
    np.testing.assert_allclose(result.to("m").magnitude, (pos % track).to("m").magnitude)


def test_remainder_ufunc_incompatible_units_raises():
    ureg = UnitRegistry()
    with pytest.raises(Exception):
        np.mod(ureg.Quantity(np.array([1.0]), "m"), ureg.Quantity(1.0, "s"))
