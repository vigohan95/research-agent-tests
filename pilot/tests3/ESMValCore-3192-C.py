"""Regression test: ICON-XPP gpp must be converted to a carbon mass flux.

CMOR ``gpp`` is a carbon mass flux (kgC m-2 s-1). ICON-XPP outputs the gross
assimilation in mol(CO2) m-2 s-1, so the conversion must use the molar mass of
carbon (12.0107 g/mol), not that of CO2 (44.0095 g/mol). Using CO2 inflates
GPP by a constant factor of ~3.66 everywhere.
"""

import numpy as np
from iris.coords import DimCoord
from iris.cube import Cube, CubeList

from tests.integration.cmor._fixes.icon.test_icon_xpp import (
    fix_data,
    fix_metadata,
)

MOLAR_MASS_C = 12.0107  # g/mol
MOLAR_MASS_CO2 = 44.0095  # g/mol


def _gpp_input_cubes():
    time = DimCoord(
        [0],
        var_name="time",
        standard_name="time",
        units="days since 1850-01-01",
    )
    lat = DimCoord(
        [0.0, 1.0],
        var_name="clat",
        standard_name="latitude",
        units="degrees_north",
    )
    lon = DimCoord(
        [-1.0, 1.0],
        var_name="clon",
        standard_name="longitude",
        units="degrees_east",
    )
    cube = Cube(
        np.arange(4.0, dtype=np.float32).reshape(1, 2, 2),
        var_name="assimi_gross_assimilation_box",
        units="mol m-2 s-1",
        dim_coords_and_dims=[(time, 0), (lat, 1), (lon, 2)],
    )
    return CubeList([cube])


def _fix(cubes):
    fixed = fix_metadata(cubes, "Lmon", "gpp")
    assert len(fixed) == 1
    return fix_data(fixed[0], "Lmon", "gpp")


def test_gpp_converted_with_carbon_molar_mass():
    """1 mol(CO2) m-2 s-1 assimilated = 12.0107e-3 kgC m-2 s-1."""
    cube = _fix(_gpp_input_cubes())

    assert cube.var_name == "gpp"
    assert cube.standard_name == (
        "gross_primary_productivity_of_biomass_expressed_as_carbon"
    )
    assert cube.units == "kg m-2 s-1"

    expected = np.arange(4.0).reshape(1, 2, 2) * MOLAR_MASS_C / 1000.0
    np.testing.assert_allclose(cube.data, expected, rtol=1e-6)


def test_gpp_not_inflated_by_co2_to_carbon_ratio():
    """Guard against the constant ~3.66x (44/12) overestimate."""
    cube = _fix(_gpp_input_cubes())
    one_mol = cube.data[0, 0, 1]
    assert not np.isclose(one_mol, MOLAR_MASS_CO2 / 1000.0)
    np.testing.assert_allclose(one_mol, MOLAR_MASS_C / 1000.0, rtol=1e-6)
