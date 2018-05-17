""" Unit tests for grid_utils module. """

from datetime import datetime
import numpy as np

from tint import grid_utils
from tint.testing.sample_files import SAMPLE_GRID_FILE
import pyart


grid = pyart.io.read_grid(SAMPLE_GRID_FILE)


def test_parse_grid_datetime():
    dt = grid_utils.parse_grid_datetime(grid)
    assert(dt == datetime(2015, 7, 10, 18, 34, 6))


def test_get_grid_size():
    grid_size = grid_utils.get_grid_size(grid)
    assert(np.all(grid_size == np.array([500., 500., 500.])))
