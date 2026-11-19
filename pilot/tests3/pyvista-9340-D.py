from __future__ import annotations

import numpy as np
import pytest

import pyvista as pv


def _rotated_image():
    """Return an image with a non-identity direction matrix and anisotropic spacing."""
    image = pv.ImageData(dimensions=(4, 5, 6), spacing=(1.0, 2.0, 3.0), origin=(1.0, -2.0, 0.5))
    rotation = pv.Transform().rotate_vector((1, -1, 2), 30).matrix[:3, :3]
    image.direction_matrix = rotation
    image.point_data['data'] = np.arange(image.n_points)
    image.cell_data['data'] = np.arange(image.n_cells)
    return image


@pytest.mark.parametrize('method', ['points_to_cells', 'cells_to_points'])
def test_points_cells_remesh_oriented_image(method):
    image = _rotated_image()
    output = getattr(image, method)()

    # Each output point (or cell center) must coincide with the matching input
    # cell center (or point) in world coordinates.
    if method == 'points_to_cells':
        expected = image.points
        actual = output.cell_centers().points
    else:
        expected = image.cell_centers().points
        actual = output.points
    np.testing.assert_allclose(actual, expected, atol=1e-10)
    np.testing.assert_allclose(output.direction_matrix, image.direction_matrix)


@pytest.mark.parametrize('method', ['points_to_cells', 'cells_to_points'])
def test_points_cells_remesh_commutes_with_rotation(method):
    image = _rotated_image()
    axis_aligned = image.copy()
    axis_aligned.direction_matrix = np.eye(3)
    axis_aligned.origin = (0.0, 0.0, 0.0)

    rotated_after = getattr(axis_aligned, method)()
    transform = np.eye(4)
    transform[:3, :3] = image.direction_matrix
    transform[:3, 3] = image.origin
    expected = rotated_after.transform(transform, inplace=False)

    actual = getattr(image, method)()
    np.testing.assert_allclose(actual.points, expected.points, atol=1e-10)
