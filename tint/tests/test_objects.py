""" Unit tests for objects module. """

from tint import objects
from tint.testing.sample_objects import grid, record, field
from tint.testing.sample_objects import counter, params
from tint.testing.sample_objects import filtered, filtered_shifted, pairs

import numpy as np
from numpy.testing import assert_almost_equal, assert_allclose


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


def test_init_current_objects():
    current_objects = objects.init_current_objects(filtered, filtered_shifted,
                                                   pairs, counter)[0]
    assert np.all(
            current_objects['id2'] == np.array([1, 2, 3, 5, 0, 6,
                                                7, 8, 9, 10, 11])
            )
