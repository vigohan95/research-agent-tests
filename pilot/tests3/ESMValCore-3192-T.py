"""Regression test: ICON-XPP gpp must be converted to kg of *carbon*."""

import dask.array as da
import numpy as np
import pytest
from iris.coords import DimCoord
from iris.cube import Cube, CubeList

from esmvalcore.cmor._fixes.icon.icon_xpp import AllVars, Gpp
from esmvalcore.cmor.table import get_var_info
from esmvalcore.dataset import Dataset

# Independent reference values (IUPAC conventional standard atomic weights):
# C = 12.011 g/mol, O = 15.999 g/mol.  1 mol CO2 contains 1 mol C, so a flux
# of x mol(CO2) m-2 s-1 equals x * 12.011e-3 kg(C) m-2 s-1.
M_C_KG_PER_MOL = 12.011e-3
M_CO2_KG_PER_MOL = (12.011 + 2 * 15.999) * 1e-3


def _fixes():
    dataset = Dataset(
        project="ICON", dataset="ICON-XPP", mip="Lmon", short_name="gpp"
    )
    extra_facets = dataset._get_extra_facets()
    extra_facets["frequency"] = "mon"
    extra_facets["exp"] = "amip"
    vardef = get_var_info(project="ICON", mip="Lmon", short_name="gpp")
    return (
        Gpp(vardef, extra_facets=extra_facets),
        AllVars(vardef, extra_facets=extra_facets),
    )


def _input_cubes(lazy):
    values = np.array([[[0.5, 1.0], [2.0, 3.0e-6]]])
    data = da.from_array(values) if lazy else values
    cube = Cube(
        data,
        var_name="assimi_gross_assimilation_box",
        units="mol m-2 s-1",
        dim_coords_and_dims=[
            (
                DimCoord(
                    [0],
                    var_name="time",
                    standard_name="time",
                    units="days since 1850-01-01",
                ),
                0,
            ),
            (
                DimCoord(
                    [0.0, 1.0],
                    var_name="clat",
                    standard_name="latitude",
                    units="degrees_north",
                ),
                1,
            ),
            (
                DimCoord(
                    [-1.0, 1.0],
                    var_name="clon",
                    standard_name="longitude",
                    units="degrees_east",
                ),
                2,
            ),
        ],
    )
    return CubeList([cube]), values


@pytest.mark.parametrize("lazy", [False, True])
def test_gpp_converted_to_kg_carbon(lazy):
    gpp_fix, allvars_fix = _fixes()
    cubes, values = _input_cubes(lazy)

    fixed = allvars_fix.fix_metadata(gpp_fix.fix_metadata(cubes))
    assert len(fixed) == 1
    cube = allvars_fix.fix_data(gpp_fix.fix_data(fixed[0]))

    assert cube.var_name == "gpp"
    assert cube.standard_name == (
        "gross_primary_productivity_of_biomass_expressed_as_carbon"
    )
    assert cube.units == "kg m-2 s-1"
    assert cube.has_lazy_data() is lazy

    # rtol 1e-4 tolerates differences in the last digits of the atomic
    # weight of carbon (12.0107 vs 12.011) but not the factor of
    # M_CO2 / M_C ~ 3.66 from using the molar mass of CO2.
    np.testing.assert_allclose(
        cube.data, values * M_C_KG_PER_MOL, rtol=1e-4
    )
    assert not np.allclose(
        cube.data, values * M_CO2_KG_PER_MOL, rtol=1e-2
    )
