"""Regression tests: points_to_cells / cells_to_points with a rotated direction matrix."""

from __future__ import annotations

import numpy as np
import pytest
from scipy.spatial.transform import Rotation

import pyvista as pv

# Oblique rotation (not a permutation/sign flip) so every world axis is mixed
DIRECTION = Rotation.from_euler('xyz', [30, -20, 45], degrees=True).as_matrix()
RTOL = 1e-10
# Some coordinates are near zero; atol covers float64 round-off of O(10)
# magnitude coordinates after a rotation (~1e-15 * 10).
ATOL = 1e-12

# (dimensions, dimensionality): 3D, 2D with preserved singleton, 2D grown to 3D,
# and an explicit per-axis mask
CASES = [
    ((4, 5, 6), 'preserve'),
    ((4, 5, 1), 'preserve'),
    ((4, 5, 1), '3D'),
    ((4, 1, 6), (True, False, True)),
]


def _image(dimensions, direction):
    image = pv.ImageData(
        dimensions=dimensions,
        spacing=(0.7, 1.3, 2.1),
        origin=(5.0, -3.0, 2.0),
        direction_matrix=direction,
    )
    image.point_data['p'] = np.arange(image.n_points)
    return image


def _rotate_about_origin(ref_origin, image_origin):
    """Origin of an unrotated result after rotating it about the input origin."""
    return image_origin + DIRECTION @ (np.asarray(ref_origin) - image_origin)


@pytest.mark.parametrize(('dimensions', 'dimensionality'), CASES)
def test_points_to_cells_rotated(dimensions, dimensionality):
    image = _image(dimensions, DIRECTION)
    cells = image.points_to_cells(dimensionality=dimensionality)

    # Same step on the unrotated image, rotated afterwards (user's reference)
    ref = _image(dimensions, np.eye(3)).points_to_cells(dimensionality=dimensionality)
    expected = _rotate_about_origin(ref.origin, np.array(image.origin))
    np.testing.assert_allclose(cells.origin, expected, rtol=RTOL, atol=ATOL)
    np.testing.assert_allclose(
        cells.points,
        _rotate_about_origin(ref.points.T, np.array(image.origin)[:, None]).T,
        rtol=RTOL,
        atol=ATOL,
    )


@pytest.mark.parametrize(('dimensions', 'dimensionality'), CASES)
def test_cells_to_points_rotated(dimensions, dimensionality):
    # Build a cell-based image so cells_to_points is valid for every case
    cells = _image(dimensions, DIRECTION).points_to_cells(dimensionality=dimensionality)
    # '3D' grew a singleton axis; the inverse shrinks it back with 'preserve'
    inverse = 'preserve' if dimensionality == '3D' else dimensionality
    points = cells.cells_to_points(dimensionality=inverse)

    # Closed form: output points are exactly the input cell centres
    np.testing.assert_allclose(
        points.points, cells.cell_centers().points, rtol=RTOL, atol=ATOL
    )


def test_cells_to_points_rotated_matches_rotating_unrotated_result():
    image = _image((4, 5, 6), DIRECTION)
    out = image.cells_to_points()
    ref = _image((4, 5, 6), np.eye(3)).cells_to_points()
    expected = _rotate_about_origin(ref.origin, np.array(image.origin))
    np.testing.assert_allclose(out.origin, expected, rtol=RTOL, atol=ATOL)


def test_points_to_cells_rotated_cell_centers_are_input_points():
    image = _image((4, 5, 6), DIRECTION)
    cells = image.points_to_cells()
    np.testing.assert_allclose(cells.cell_centers().points, image.points, rtol=RTOL, atol=ATOL)
