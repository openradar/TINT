""" Unit tests for matching module. """

from tint.testing.sample_objects import filtered, filtered_shifted
from tint.testing.sample_objects import global_shift, record, params
from tint.matching import get_pairs

import numpy as np


def test_get_pairs():
    pairs = get_pairs(filtered, filtered_shifted, global_shift, None,
                      record, params)
    assert np.all(pairs == np.array([1, 2, 3, 5, 0, 6, 7, 8, 9, 10, 11]))
