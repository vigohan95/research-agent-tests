from __future__ import annotations

import numpy as np
import pytest

import pyvista as pv


def _rotation():
    # Oblique rotation about a non-axis direction
    return pv.Transform().rotate_vector((1, 2, 3), 30).matrix[:3, :3]


@pytest.mark.parametrize('method', ['points_to_cells', 'cells_to_points'])
def test_remesh_points_cells_oblique_direction_matrix(method):
    rotation = _rotation()
    kwargs = dict(dimensions=(4, 5, 6), spacing=(0.5, 1.0, 2.0), origin=(1.0, -2.0, 3.0))
    image = pv.ImageData(**kwargs)
    oblique = pv.ImageData(**kwargs, direction_matrix=rotation)
    if method == 'points_to_cells':
        image.point_data['labels'] = np.arange(image.n_points)
        oblique.point_data['labels'] = np.arange(oblique.n_points)
    else:
        image.cell_data['labels'] = np.arange(image.n_cells)
        oblique.cell_data['labels'] = np.arange(oblique.n_cells)

    out_oblique = getattr(oblique, method)()
    out_axis = getattr(image, method)()

    # Doing the conversion on the rotated grid must match rotating the
    # axis-aligned result about the original origin.
    origin = np.array(kwargs['origin'])
    expected_points = (out_axis.points - origin) @ rotation.T + origin
    np.testing.assert_allclose(out_oblique.points, expected_points, atol=1e-10)

    # Converted points/cell centers must coincide with the input's centers/points
    if method == 'points_to_cells':
        np.testing.assert_allclose(out_oblique.cell_centers().points, oblique.points, atol=1e-10)
    else:
        np.testing.assert_allclose(out_oblique.points, oblique.cell_centers().points, atol=1e-10)


def test_remesh_round_trip_oblique_preserves_geometry():
    image = pv.ImageData(
        dimensions=(3, 4, 5), spacing=(1.0, 2.0, 3.0), direction_matrix=_rotation()
    )
    image.point_data['labels'] = np.arange(image.n_points)
    round_trip = image.points_to_cells().cells_to_points()
    np.testing.assert_allclose(round_trip.points, image.points, atol=1e-10)
