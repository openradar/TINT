""" Unit tests for objects module. """

import numpy as np
from numpy.testing import assert_almost_equal, assert_allclose

import pyart

from tint import objects, Cell_tracks
from tint.helpers import Record
from tint.testing.sample_files import SAMPLE_GRID_FILE
from tint.grid_utils import extract_grid_data


# Make some generic objects
grid = pyart.io.read_grid(SAMPLE_GRID_FILE)
record = Record(grid)
empty_tracks = Cell_tracks()
field = empty_tracks.field
params = empty_tracks.params
grid_size = record.grid_size
raw, filtered = extract_grid_data(grid, field, grid_size, params)


def test_get_object_prop():
    """ Test calculation of object properties from grid file. """
    props = objects.get_object_prop(filtered, grid, field, record, params)
    obj1_props = dict([(key, val[0]) for key, val in props.items()])
    assert obj1_props['area'] == 8.5
    assert_allclose(obj1_props['center'], np.array([160., 243.]), rtol=0.0001)
    assert_almost_equal(obj1_props['field_max'], 42.6668, 3)
    assert_almost_equal(obj1_props['grid_x'], 243.1759, 3)
    assert_almost_equal(obj1_props['grid_y'], 160.2940, 3)
    assert obj1_props['id1'] == 1
    assert obj1_props['isolated']
    assert_almost_equal(obj1_props['lat'], 28.387, 2)
    assert_almost_equal(obj1_props['lon'], -93.836, 2)
    assert obj1_props['max_height'] == 4.5
    assert obj1_props['volume'] == 15.5
