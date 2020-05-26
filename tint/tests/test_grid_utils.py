""" Unit tests for grid_utils module. """

from datetime import datetime
import numpy as np

from tint import grid_utils
from tint.testing.sample_objects import grid, field
from tint.testing.sample_objects import params, grid_size


def test_parse_grid_datetime():
    dt = grid_utils.parse_grid_datetime(grid)
    assert(dt == datetime(2015, 7, 10, 18, 34, 6, 102000))


def test_get_grid_size():
    grid_size = grid_utils.get_grid_size(grid)
    assert np.all(grid_size == np.array([500., 500., 500.]))


def test_extract_grid_data():
    raw, filtered = grid_utils.extract_grid_data(grid, field,
                                                 grid_size, params)
    assert np.max(filtered) == 11
    assert np.min(filtered) == 0
