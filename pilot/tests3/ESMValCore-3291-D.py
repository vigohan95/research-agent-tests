"""Regression tests for a zero ``min_value`` in missing-value masking."""

import dask.array as da
import numpy as np
import pytest

from esmvalcore.preprocessor._mask import count_spells


@pytest.mark.parametrize("lazy", [False, True])
def test_count_spells_zero_threshold(lazy):
    """A threshold of 0 must count only values above 0, not all values."""
    # Column 0 never exceeds 0 ("desert"), column 1 always does.
    data = np.array([[0.0, 1.0], [0.0, 2.0], [0.0, 3.0], [0.0, 4.0]])
    if lazy:
        data = da.from_array(data)

    result = count_spells(data, 0.0, axis=0, spell_length=1)
    if lazy:
        assert isinstance(result, da.Array)
        result = result.compute()

    np.testing.assert_array_equal(result, [0, 4])


def test_count_spells_none_threshold_counts_all():
    """Without a threshold, all (unmasked) values are counted."""
    data = np.zeros((4, 2))
    result = count_spells(data, None, axis=0, spell_length=1)
    np.testing.assert_array_equal(result, [4, 4])
