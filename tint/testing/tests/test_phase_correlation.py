""" Tests operation of phase correlation module. """

import numpy as np
from tint import Cell_tracks
from tint.phase_correlation import get_ambient_flow
from tint.objects import get_obj_extent

empty_tracks = Cell_tracks()
grid_size = np.array([500, 500, 500])  # generic grid size


def test_basic_shift():
    frame1 = np.zeros((100, 100))
    frame2 = np.zeros((100, 100))
    frame1[50, 50] = 1
    frame2[55, 55] = 1
    obj_ext = get_obj_extent(frame1, 1)
    shift = get_ambient_flow(obj_ext, frame1, frame2, empty_tracks.params,
                             grid_size)
    assert(np.all(shift == np.array([6., 6.])))
