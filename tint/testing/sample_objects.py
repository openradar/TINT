""" Sample objects for unit_tests. """

import numpy as np
import pyart
from copy import deepcopy

from tint import Cell_tracks
from tint.grid_utils import extract_grid_data
from tint.matching import get_pairs
from tint.helpers import Record, Counter
from tint.phase_correlation import get_global_shift
from tint.testing.sample_files import SAMPLE_GRID_FILE

# Make some generic objects
grid = pyart.io.read_grid(SAMPLE_GRID_FILE)
record = Record(grid)
counter = Counter()
empty_tracks = Cell_tracks()
field = empty_tracks.field
params = empty_tracks.params
grid_size = record.grid_size
raw, filtered = extract_grid_data(grid, field, grid_size, params)

# Make a shifted version of the sample grid object
grid_data = grid.fields['reflectivity']['data']
raw_image = grid_data.data
shift = (10, 20)
shifted_image = np.roll(raw_image, shift, axis=(1, 2))
shifted_image[:10, :20] = 0
shifted_masked = np.ma.array(shifted_image)

grid_shifted = deepcopy(grid)
grid_shifted.fields['reflectivity']['data'] = shifted_masked
grid_shifted.time['units'] = 'seconds since 2015-07-10T18:40:00Z'
raw_shifted, filtered_shifted = extract_grid_data(grid_shifted, field,
                                                  grid_size, params)

global_shift = get_global_shift(raw, raw_shifted, params)
record.update_scan_and_time(grid, grid_shifted)
pairs = get_pairs(filtered, filtered_shifted, global_shift, None, record,
                  params)
